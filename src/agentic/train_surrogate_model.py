"""Train the RDKit surrogate model for PAMPA permeability prediction with applicability domain."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    matthews_corrcoef,
    recall_score,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler

# Maximum value for float32 to avoid overflow
MAX_FLOAT32 = 3.0e38

def get_rdkit_descriptors(mol):
    """Calculate all standard RDKit descriptors, clipping values to avoid float32 overflow."""
    desc_dict = {}
    for name, func in Descriptors._descList:
        try:
            val = func(mol)
            if val is None or not np.isfinite(val):
                desc_dict[name] = 0.0
            elif val > MAX_FLOAT32:
                desc_dict[name] = MAX_FLOAT32
            elif val < -MAX_FLOAT32:
                desc_dict[name] = -MAX_FLOAT32
            else:
                desc_dict[name] = float(val)
        except Exception:
            desc_dict[name] = 0.0
    return desc_dict


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Train a reproducible RDKit-based surrogate model for PAMPA screening. "
            "The resulting payload stores the Random Forest, scaler and leverage metadata."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("dataset (7).xlsx"),
        help="Excel workbook that contains the Smiles sheet (default: dataset (7).xlsx).",
    )
    parser.add_argument(
        "--sheet",
        default="Smiles",
        help="Sheet name with SMILES, Target and Type columns (default: Smiles).",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path("models/surrogate_rf_pampa.pkl"),
        help="Where to store the trained model payload.",
    )
    parser.add_argument(
        "--metrics-path",
        type=Path,
        default=Path("results/metrics/surrogate_model_metrics.csv"),
        help="Where to store the metrics table.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    print(f"Loading SMILES from {args.input} [{args.sheet}]...")
    df_smiles = pd.read_excel(args.input, sheet_name=args.sheet)
    print(f"Loaded {len(df_smiles)} molecules.")

    print("Calculating RDKit descriptors for all molecules...")
    records = []
    
    for idx, row in df_smiles.iterrows():
        smi = row["smiles"]
        target = row["Target"]
        split_type = row["Type"]
        
        mol = Chem.MolFromSmiles(smi)
        if mol:
            # Strip isotopes for consistency
            for atom in mol.GetAtoms():
                atom.SetIsotope(0)
            
            desc_vals = get_rdkit_descriptors(mol)
            desc_vals["Target"] = int(target)
            desc_vals["Type"] = split_type
            desc_vals["smiles"] = smi
            records.append(desc_vals)
        else:
            print(f"Skipping invalid SMILES at row {idx}: {smi}")

    df_desc = pd.DataFrame(records)
    print(f"Calculated descriptors for {len(df_desc)} molecules.")

    # Split into train and test sets
    train_data = df_desc[df_desc["Type"] == "Train"].copy()
    test_data = df_desc[df_desc["Type"] == "Test"].copy()
    
    feature_cols = [c for c in df_desc.columns if c not in ["Target", "Type", "smiles"]]
    
    print(f"Training set size: {len(train_data)}")
    print(f"Test set size: {len(test_data)}")
    print(f"Number of features: {len(feature_cols)}")

    X_train = train_data[feature_cols].values
    y_train = train_data["Target"].values
    X_test = test_data[feature_cols].values
    y_test = test_data["Target"].values

    # Fit scaler on training set
    print("Fitting StandardScaler on features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Compute leverage threshold h_star and X_T_X pseudo-inverse
    print("Calculating leverage matrix for applicability domain...")
    # Add column of ones for intercept if needed, or compute on scaled features directly
    # Standard leverage is computed on Z = X_train_scaled
    # h = z^T (Z^T Z)^+ z
    Z_train = X_train_scaled
    n_samples, n_features = Z_train.shape
    
    # Compute pseudo-inverse of covariance-like matrix Z^T Z
    # Z_T_Z has shape (n_features, n_features)
    Z_T_Z = Z_train.T @ Z_train
    Z_T_Z_pinv = np.linalg.pinv(Z_T_Z)
    
    # Calculate h_star = 3 * (p + 1) / n
    h_star = 3.0 * (n_features + 1) / n_samples
    print(f"Leverage h* threshold: {h_star:.6f}")

    print("Training Random Forest classifier...")
    rf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    rf.fit(X_train_scaled, y_train)

    # Evaluate
    train_preds = rf.predict(X_train_scaled)
    train_probs = rf.predict_proba(X_train_scaled)[:, 1]
    test_preds = rf.predict(X_test_scaled)
    test_probs = rf.predict_proba(X_test_scaled)[:, 1]

    train_acc = accuracy_score(y_train, train_preds)
    train_auc = roc_auc_score(y_train, train_probs)
    train_mcc = matthews_corrcoef(y_train, train_preds)
    train_f1 = f1_score(y_train, train_preds)

    test_acc = accuracy_score(y_test, test_preds)
    test_auc = roc_auc_score(y_test, test_probs)
    test_mcc = matthews_corrcoef(y_test, test_preds)
    test_f1 = f1_score(y_test, test_preds)

    print("\n--- Training Set Metrics ---")
    print(f"Accuracy: {train_acc:.4f}")
    print(f"AUC:      {train_auc:.4f}")
    print(f"MCC:      {train_mcc:.4f}")
    print(f"F1-Score: {train_f1:.4f}")

    print("\n--- Test Set Metrics ---")
    print(f"Accuracy: {test_acc:.4f}")
    print(f"AUC:      {test_auc:.4f}")
    print(f"MCC:      {test_mcc:.4f}")
    print(f"F1-Score: {test_f1:.4f}")

    # Save the model payload
    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    model_payload = {
        "model": rf,
        "features": feature_cols,
        "scaler": scaler,
        "Z_T_Z_pinv": Z_T_Z_pinv,
        "h_star": h_star,
        "metrics": {
            "train": {"accuracy": train_acc, "auc": train_auc, "mcc": train_mcc, "f1": train_f1},
            "test": {"accuracy": test_acc, "auc": test_auc, "mcc": test_mcc, "f1": test_f1}
        }
    }
    joblib.dump(model_payload, args.model_path)
    print(f"\nSaved surrogate model and metadata to {args.model_path}")

    # Save metrics to CSV
    metrics_df = pd.DataFrame([
        {"Dataset": "Training (Surrogate)", "Accuracy": train_acc, "AUC": train_auc, "MCC": train_mcc, "F1-Score": train_f1},
        {"Dataset": "Test Interno (Surrogate)", "Accuracy": test_acc, "AUC": test_auc, "MCC": test_mcc, "F1-Score": test_f1}
    ])
    args.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(args.metrics_path, index=False)
    print(f"Saved surrogate metrics to {args.metrics_path}")

if __name__ == "__main__":
    main()

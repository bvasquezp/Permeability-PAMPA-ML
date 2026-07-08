"""Train an RDKit surrogate model with an EDA-style feature reduction pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors
from scipy.stats import mannwhitneyu, spearmanr
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE, VarianceThreshold
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler


MAX_FLOAT32 = 3.0e38


def get_rdkit_descriptors(mol: Chem.Mol) -> dict[str, float]:
    desc_dict: dict[str, float] = {}
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
            "Train a PAMPA surrogate using RDKit descriptors plus an EDA-style "
            "reduction chain: variance, Mann-Whitney, Spearman pruning and RFE."
        )
    )
    parser.add_argument("--input", type=Path, default=Path("dataset (7).xlsx"))
    parser.add_argument("--sheet", default="Smiles")
    parser.add_argument(
        "--model-path",
        type=Path,
        default=Path("models/surrogate_rf_pampa_eda.pkl"),
    )
    parser.add_argument(
        "--metrics-path",
        type=Path,
        default=Path("results/metrics/surrogate_eda_metrics.csv"),
    )
    parser.add_argument(
        "--selection-report-path",
        type=Path,
        default=Path("results/feature_selection/rdkit_eda_selection_report.json"),
    )
    parser.add_argument(
        "--selected-features-path",
        type=Path,
        default=Path("results/feature_selection/rdkit_eda_selected_features.csv"),
    )
    parser.add_argument("--variance-threshold", type=float, default=0.05)
    parser.add_argument("--mann-whitney-alpha", type=float, default=0.05)
    parser.add_argument("--spearman-threshold", type=float, default=0.90)
    parser.add_argument("--final-features", type=int, default=11)
    parser.add_argument("--selection-estimators", type=int, default=200)
    parser.add_argument("--final-estimators", type=int, default=500)
    return parser


def load_workbook(path: Path, sheet: str) -> pd.DataFrame:
    frame = pd.read_excel(path, sheet_name=sheet)
    required = {"smiles", "Target", "Type"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
    return frame


def compute_descriptor_frame(frame: pd.DataFrame) -> pd.DataFrame:
    records: list[dict[str, float | int | str]] = []
    invalid = 0
    for _, row in frame.iterrows():
        mol = Chem.MolFromSmiles(str(row["smiles"]))
        if not mol:
            invalid += 1
            continue

        for atom in mol.GetAtoms():
            atom.SetIsotope(0)

        record = get_rdkit_descriptors(mol)
        record["Target"] = int(row["Target"])
        record["Type"] = row["Type"]
        record["smiles"] = row["smiles"]
        records.append(record)

    df = pd.DataFrame(records)
    if invalid:
        print(f"Skipped {invalid} invalid SMILES.")
    return df


def variance_filter(x_train: pd.DataFrame, threshold: float) -> tuple[pd.DataFrame, list[str], list[str]]:
    selector = VarianceThreshold(threshold=threshold)
    x_var = selector.fit_transform(x_train)
    kept = list(x_train.columns[selector.get_support()])
    removed = [col for col in x_train.columns if col not in kept]
    return pd.DataFrame(x_var, columns=kept, index=x_train.index), kept, removed


def mann_whitney_filter(x_train: pd.DataFrame, y_train: pd.Series, alpha: float) -> tuple[pd.DataFrame, list[str], list[str]]:
    keep: list[str] = []
    removed: list[str] = []
    class0 = x_train[y_train == 0]
    class1 = x_train[y_train == 1]
    for col in x_train.columns:
        x0 = class0[col].dropna()
        x1 = class1[col].dropna()
        if len(x0) == 0 or len(x1) == 0:
            removed.append(col)
            continue
        try:
            _, pvalue = mannwhitneyu(x0, x1, alternative="two-sided")
        except Exception:
            pvalue = 1.0
        if pvalue < alpha:
            keep.append(col)
        else:
            removed.append(col)
    return x_train[keep].copy(), keep, removed


def spearman_filter(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    threshold: float,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    target_corr = {}
    for col in x_train.columns:
        try:
            corr, _ = spearmanr(x_train[col], y_train)
            target_corr[col] = 0.0 if corr is None or not np.isfinite(corr) else abs(float(corr))
        except Exception:
            target_corr[col] = 0.0

    ordered = sorted(x_train.columns, key=lambda name: target_corr[name], reverse=True)
    kept: list[str] = []
    removed: list[str] = []

    corr = x_train[ordered].corr(method="spearman").abs()
    for feature in ordered:
        if not kept:
            kept.append(feature)
            continue
        too_close = any(corr.loc[feature, already] > threshold for already in kept)
        if too_close:
            removed.append(feature)
        else:
            kept.append(feature)

    return x_train[kept].copy(), kept, removed


def rfe_filter(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    n_features: int,
    estimators: int,
) -> tuple[pd.DataFrame, list[str], list[str]]:
    if x_train.shape[1] <= n_features:
        return x_train.copy(), list(x_train.columns), []

    estimator = RandomForestClassifier(
        n_estimators=estimators,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    selector = RFE(
        estimator=estimator,
        n_features_to_select=n_features,
        step=0.1,
    )
    selector.fit(x_train, y_train)
    kept = list(x_train.columns[selector.support_])
    removed = [col for col in x_train.columns if col not in kept]
    return x_train[kept].copy(), kept, removed


def evaluate(model: RandomForestClassifier, x: pd.DataFrame, y: pd.Series) -> dict[str, float]:
    pred = model.predict(x)
    prob = model.predict_proba(x)[:, 1]
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "auc": float(roc_auc_score(y, prob)),
        "mcc": float(matthews_corrcoef(y, pred)),
        "f1": float(f1_score(y, pred)),
        "sensitivity": float(recall_score(y, pred, pos_label=1)),
        "specificity": float(recall_score(y, pred, pos_label=0)),
    }


def main() -> None:
    args = build_parser().parse_args()

    print(f"Loading SMILES from {args.input} [{args.sheet}]...")
    raw = load_workbook(args.input, args.sheet)
    print(f"Loaded {len(raw)} molecules.")

    print("Calculating RDKit descriptors...")
    df = compute_descriptor_frame(raw)
    print(f"Calculated descriptors for {len(df)} molecules.")

    train = df[df["Type"] == "Train"].copy()
    test = df[df["Type"] == "Test"].copy()
    y_train = train["Target"].astype(int)
    y_test = test["Target"].astype(int)
    descriptor_cols = [col for col in df.columns if col not in {"Target", "Type", "smiles"}]

    x_train_raw = train[descriptor_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)
    x_test_raw = test[descriptor_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    print(f"Initial descriptor count: {len(descriptor_cols)}")

    x_var, kept_var, removed_var = variance_filter(x_train_raw, args.variance_threshold)
    print(f"Variance filter kept {len(kept_var)} descriptors.")

    x_mw, kept_mw, removed_mw = mann_whitney_filter(x_var, y_train, args.mann_whitney_alpha)
    print(f"Mann-Whitney kept {len(kept_mw)} descriptors.")

    x_sp, kept_sp, removed_sp = spearman_filter(x_mw, y_train, args.spearman_threshold)
    print(f"Spearman filter kept {len(kept_sp)} descriptors.")

    x_rfe, kept_rfe, removed_rfe = rfe_filter(
        x_sp,
        y_train,
        n_features=min(args.final_features, max(1, x_sp.shape[1])),
        estimators=args.selection_estimators,
    )
    print(f"RFE selected {len(kept_rfe)} descriptors.")

    selected_features = list(x_rfe.columns)
    if not selected_features:
        raise SystemExit("EDA pipeline removed all descriptors.")

    scaler = StandardScaler()
    x_train = scaler.fit_transform(train[selected_features].replace([np.inf, -np.inf], np.nan).fillna(0.0))
    x_test = scaler.transform(test[selected_features].replace([np.inf, -np.inf], np.nan).fillna(0.0))

    x_train_df = pd.DataFrame(x_train, columns=selected_features, index=train.index)
    x_test_df = pd.DataFrame(x_test, columns=selected_features, index=test.index)

    model = RandomForestClassifier(
        n_estimators=args.final_estimators,
        random_state=42,
        n_jobs=-1,
        class_weight={0: 1.5, 1: 1},
        max_depth=10,
        max_features="sqrt",
        min_samples_leaf=4,
    )
    model.fit(x_train_df, y_train)

    train_metrics = evaluate(model, x_train_df, y_train)
    test_metrics = evaluate(model, x_test_df, y_test)

    h_star = 3.0 * (len(selected_features) + 1) / len(x_train_df)
    z_t_z_pinv = np.linalg.pinv(x_train_df.values.T @ x_train_df.values)

    print("\n--- Training Set Metrics ---")
    print(pd.Series(train_metrics).round(4).to_string())
    print("\n--- Test Set Metrics ---")
    print(pd.Series(test_metrics).round(4).to_string())
    print(f"\nSelected features ({len(selected_features)}): {selected_features}")

    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": model,
        "features": selected_features,
        "scaler": scaler,
        "Z_T_Z_pinv": z_t_z_pinv,
        "h_star": h_star,
        "metrics": {"train": train_metrics, "test": test_metrics},
        "eda": {
            "variance_threshold": args.variance_threshold,
            "mann_whitney_alpha": args.mann_whitney_alpha,
            "spearman_threshold": args.spearman_threshold,
            "final_features": args.final_features,
            "initial_features": len(descriptor_cols),
            "kept_after_variance": kept_var,
            "kept_after_mann_whitney": kept_mw,
            "kept_after_spearman": kept_sp,
            "kept_after_rfe": kept_rfe,
            "removed_after_variance": removed_var,
            "removed_after_mann_whitney": removed_mw,
            "removed_after_spearman": removed_sp,
            "removed_after_rfe": removed_rfe,
        },
    }
    joblib.dump(payload, args.model_path)
    print(f"\nSaved model payload to {args.model_path}")

    args.metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_df = pd.DataFrame(
        [
            {
                "Dataset": "Training (EDA Surrogate)",
                "Accuracy": train_metrics["accuracy"],
                "AUC": train_metrics["auc"],
                "MCC": train_metrics["mcc"],
                "F1-Score": train_metrics["f1"],
                "Sensitivity": train_metrics["sensitivity"],
                "Specificity": train_metrics["specificity"],
            },
            {
                "Dataset": "Test Interno (EDA Surrogate)",
                "Accuracy": test_metrics["accuracy"],
                "AUC": test_metrics["auc"],
                "MCC": test_metrics["mcc"],
                "F1-Score": test_metrics["f1"],
                "Sensitivity": test_metrics["sensitivity"],
                "Specificity": test_metrics["specificity"],
            },
        ]
    )
    metrics_df.to_csv(args.metrics_path, index=False)
    print(f"Saved metrics to {args.metrics_path}")

    args.selected_features_path.parent.mkdir(parents=True, exist_ok=True)
    pd.Series(selected_features, name="Descriptor").to_csv(args.selected_features_path, index=False)
    print(f"Saved selected features to {args.selected_features_path}")

    args.selection_report_path.parent.mkdir(parents=True, exist_ok=True)
    args.selection_report_path.write_text(
        json.dumps(payload["eda"], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Saved selection report to {args.selection_report_path}")


if __name__ == "__main__":
    main()

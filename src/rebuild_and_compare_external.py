"""Rebuild the external PAMPA bridge table and compare thesis vs surrogate models.

This script:
1. Loads the external bridge workbook that contains PubChem IDs, permeability and SMILES.
2. Reconstructs any missing SMILES from PubChem using the CID.
3. Validates that the bridge labels match the curated thesis external set row by row.
4. Runs the thesis Random Forest and the RDKit surrogate on the same 486 compounds.
5. Writes a reconstructed bridge CSV plus a comparison table and summary JSON.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import requests
from rdkit import Chem
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef, roc_auc_score

if __package__ in {None, ""}:
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.agentic.mcp_server import calculate_rdkit_features


REQUIRED_BRIDGE_COLUMNS = {
    "SMILES",
    "PUBCHEM_SID",
    "PUBCHEM_CID",
    "PUBCHEM_ACTIVITY_OUTCOME",
    "Phenotype (0-10:  Low Permeability; 10-100: Moderate Permeability; >100: High Permeability)",
    "Permeability",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Reconstruct missing external SMILES from PubChem and compare the "
            "thesis model with the RDKit surrogate on the 486-compound external set."
        )
    )
    parser.add_argument(
        "--bridge-xlsx",
        type=Path,
        default=None,
        help=(
            "Workbook with the PubChem bridge table. If omitted, the script will "
            "search common local copies such as BD pampa.xlsx."
        ),
    )
    parser.add_argument(
        "--thesis-external",
        type=Path,
        default=Path("data/raw/external_11.csv"),
        help="Curated thesis external panel with the 11 selected descriptors.",
    )
    parser.add_argument(
        "--thesis-model",
        type=Path,
        default=Path("models/best_rf_pampa.pkl"),
    )
    parser.add_argument(
        "--surrogate-model",
        type=Path,
        default=Path("models/surrogate_rf_pampa_eda.pkl"),
    )
    parser.add_argument(
        "--bridge-output",
        type=Path,
        default=Path("data/processed/external_bridge_reconstructed.csv"),
        help="CSV output with reconstructed SMILES and validated labels.",
    )
    parser.add_argument(
        "--comparison-output",
        type=Path,
        default=Path("results/metrics/external_thesis_vs_surrogate_comparison.csv"),
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("results/metrics/external_thesis_vs_surrogate_summary.json"),
    )
    return parser


def locate_bridge_xlsx(explicit: Path | None) -> Path:
    candidates: list[Path] = []
    if explicit is not None:
        candidates.append(explicit)
    candidates.extend(
        [
            Path("BD pampa.xlsx"),
            Path("external_set (5).xlsx"),
            Path.home() / "Downloads" / "BD pampa.xlsx",
            Path.home() / "Downloads" / "external_set (5).xlsx",
        ]
    )

    checked: set[Path] = set()
    for candidate in candidates:
        if candidate in checked or not candidate.exists():
            continue
        checked.add(candidate)
        try:
            preview = pd.read_excel(candidate, sheet_name=0, nrows=5)
        except Exception:
            continue
        if REQUIRED_BRIDGE_COLUMNS.issubset(preview.columns):
            return candidate

    raise FileNotFoundError(
        "Could not find a bridge workbook containing the required columns. "
        "Pass --bridge-xlsx explicitly."
    )


def normalize_smiles(smiles: str | float | None) -> str | None:
    if smiles is None or (isinstance(smiles, float) and np.isnan(smiles)):
        return None
    text = str(smiles).strip().replace("\u00a0", "")
    if not text:
        return None
    mol = Chem.MolFromSmiles(text)
    if mol is None:
        return None
    for atom in mol.GetAtoms():
        atom.SetIsotope(0)
    return Chem.MolToSmiles(mol, canonical=True)


def fetch_smiles_from_pubchem_cid(cid: int | float) -> str:
    if pd.isna(cid):
        raise ValueError("Missing PubChem CID")
    cid_int = int(cid)
    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
        f"{cid_int}/property/CanonicalSMILES,IsomericSMILES/JSON"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    props = payload["PropertyTable"]["Properties"][0]
    smiles = (
        props.get("SMILES")
        or props.get("CanonicalSMILES")
        or props.get("ConnectivitySMILES")
        or props.get("IsomericSMILES")
    )
    if not smiles:
        raise ValueError(f"No SMILES returned by PubChem for CID {cid_int}")
    return str(smiles)


def reconstruct_bridge_table(bridge: pd.DataFrame) -> pd.DataFrame:
    work = bridge.copy().reset_index(drop=True)
    work["SMILES_original"] = work["SMILES"]
    work["SMILES_reconstructed"] = None
    work["SMILES_source"] = "original"
    work["SMILES_valid"] = False

    reconstructed = 0
    invalid_rows: list[int] = []
    for idx, row in work.iterrows():
        smiles = normalize_smiles(row["SMILES"])
        if smiles is None:
            try:
                smiles = normalize_smiles(fetch_smiles_from_pubchem_cid(row["PUBCHEM_CID"]))
                if smiles is None:
                    raise ValueError("PubChem returned an invalid SMILES")
                work.at[idx, "SMILES_source"] = "pubchem_cid"
                reconstructed += 1
            except Exception as exc:
                invalid_rows.append(idx)
                work.at[idx, "SMILES_source"] = f"missing:{exc}"
                continue
        work.at[idx, "SMILES_reconstructed"] = smiles
        work.at[idx, "SMILES_valid"] = True

    if invalid_rows:
        raise RuntimeError(
            "Failed to reconstruct SMILES for rows: "
            + ", ".join(str(i) for i in invalid_rows)
        )

    work["SMILES"] = work["SMILES_reconstructed"]
    print(f"Reconstructed {reconstructed} missing SMILES from PubChem.")
    return work


def load_thesis_and_validate_order(bridge: pd.DataFrame, thesis_external: pd.DataFrame) -> pd.Series:
    if len(bridge) != len(thesis_external):
        raise ValueError(
            f"Row-count mismatch: bridge has {len(bridge)} rows, "
            f"but thesis external has {len(thesis_external)} rows."
        )

    permeability = pd.to_numeric(
        bridge["Permeability"].astype(str).str.replace(">", "", regex=False),
        errors="coerce",
    )
    bridge_activity = permeability.gt(10).map({True: "Act1", False: "Act-1"}).reset_index(drop=True)
    thesis_activity = thesis_external["Actividad"].reset_index(drop=True).astype(str)
    if not bridge_activity.equals(thesis_activity):
        mismatches = int((bridge_activity != thesis_activity).sum())
        raise ValueError(
            f"Bridge label order does not match the thesis external set "
            f"({mismatches} mismatches)."
        )

    print("Bridge order matches the thesis external labels row by row.")
    return bridge_activity


def score_thesis_model(thesis_external: pd.DataFrame, model_path: Path) -> tuple[np.ndarray, np.ndarray]:
    model = joblib.load(model_path)
    feature_cols = [c for c in thesis_external.columns if c != "Actividad"]
    x = thesis_external[feature_cols]
    prob = model.predict_proba(x)[:, 1]
    pred = model.predict(x)
    return prob, pred


def score_surrogate_model(bridge: pd.DataFrame, model_path: Path) -> tuple[np.ndarray, np.ndarray, list[str]]:
    payload = joblib.load(model_path)
    rf = payload["model"]
    scaler = payload["scaler"]
    feature_cols = list(payload["features"])

    records: list[np.ndarray] = []
    for smiles in bridge["SMILES"].tolist():
        mol = Chem.MolFromSmiles(str(smiles))
        if mol is None:
            raise ValueError(f"Invalid SMILES after reconstruction: {smiles}")
        for atom in mol.GetAtoms():
            atom.SetIsotope(0)
        vec = calculate_rdkit_features(mol, feature_cols)[0]
        records.append(vec)

    x_raw = pd.DataFrame(records, columns=feature_cols)
    x_scaled = scaler.transform(x_raw)
    x_scaled_df = pd.DataFrame(x_scaled, columns=feature_cols)
    prob = rf.predict_proba(x_scaled_df)[:, 1]
    pred = rf.predict(x_scaled_df)
    return prob, pred, feature_cols


def main() -> None:
    args = build_parser().parse_args()

    bridge_xlsx = locate_bridge_xlsx(args.bridge_xlsx)
    print(f"Using bridge workbook: {bridge_xlsx}")

    bridge = pd.read_excel(bridge_xlsx, sheet_name=0)
    missing = REQUIRED_BRIDGE_COLUMNS - set(bridge.columns)
    if missing:
        raise SystemExit(f"Missing required columns in bridge workbook: {sorted(missing)}")

    reconstructed = reconstruct_bridge_table(bridge)
    reconstructed.to_csv(args.bridge_output, index=False)
    print(f"Saved reconstructed bridge to: {args.bridge_output}")

    thesis_external = pd.read_csv(args.thesis_external)
    bridge_activity = load_thesis_and_validate_order(reconstructed, thesis_external)

    thesis_prob, thesis_pred = score_thesis_model(thesis_external, args.thesis_model)
    surrogate_prob, surrogate_pred, surrogate_features = score_surrogate_model(
        reconstructed,
        args.surrogate_model,
    )

    thesis_actual = thesis_external["Actividad"].map({"Act-1": 0, "Act1": 1}).astype(int).to_numpy()
    comparison = pd.DataFrame(
        {
            "row": np.arange(len(reconstructed)),
            "PUBCHEM_CID": reconstructed["PUBCHEM_CID"],
            "PUBCHEM_SID": reconstructed["PUBCHEM_SID"],
            "smiles": reconstructed["SMILES"],
            "thesis_actual": thesis_actual,
            "thesis_pred": thesis_pred,
            "thesis_prob": thesis_prob,
            "surrogate_pred": surrogate_pred,
            "surrogate_prob": surrogate_prob,
        }
    )
    comparison["pred_match"] = comparison["thesis_pred"] == comparison["surrogate_pred"]
    comparison["prob_abs_diff"] = (comparison["thesis_prob"] - comparison["surrogate_prob"]).abs()
    comparison["thesis_correct"] = comparison["thesis_pred"] == comparison["thesis_actual"]
    comparison["surrogate_correct"] = comparison["surrogate_pred"] == comparison["thesis_actual"]
    comparison.to_csv(args.comparison_output, index=False)
    print(f"Saved comparison table to: {args.comparison_output}")

    thesis_acc = float(accuracy_score(comparison["thesis_actual"], comparison["thesis_pred"]))
    surrogate_acc = float(accuracy_score(comparison["thesis_actual"], comparison["surrogate_pred"]))
    thesis_auc = float(roc_auc_score(comparison["thesis_actual"], comparison["thesis_prob"]))
    surrogate_auc = float(roc_auc_score(comparison["thesis_actual"], comparison["surrogate_prob"]))
    thesis_mcc = float(matthews_corrcoef(comparison["thesis_actual"], comparison["thesis_pred"]))
    surrogate_mcc = float(matthews_corrcoef(comparison["thesis_actual"], comparison["surrogate_pred"]))
    thesis_f1 = float(f1_score(comparison["thesis_actual"], comparison["thesis_pred"]))
    surrogate_f1 = float(f1_score(comparison["thesis_actual"], comparison["surrogate_pred"]))

    summary = {
        "bridge_rows": int(len(reconstructed)),
        "reconstructed_smiles": int((reconstructed["SMILES_source"] == "pubchem_cid").sum()),
        "bridge_label_match": bool(bridge_activity.equals(thesis_external["Actividad"].reset_index(drop=True).astype(str))),
        "thesis": {
            "accuracy": thesis_acc,
            "auc": thesis_auc,
            "mcc": thesis_mcc,
            "f1": thesis_f1,
        },
        "surrogate": {
            "accuracy": surrogate_acc,
            "auc": surrogate_auc,
            "mcc": surrogate_mcc,
            "f1": surrogate_f1,
        },
        "model_agreement": {
            "prediction_agreement": float(comparison["pred_match"].mean()),
            "avg_abs_probability_diff": float(comparison["prob_abs_diff"].mean()),
            "max_abs_probability_diff": float(comparison["prob_abs_diff"].max()),
            "probability_correlation": float(comparison["thesis_prob"].corr(comparison["surrogate_prob"])),
        },
        "surrogate_features": surrogate_features,
    }
    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    args.comparison_output.parent.mkdir(parents=True, exist_ok=True)
    with args.summary_output.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
    print(f"Saved summary to: {args.summary_output}")

    print("\nExternal comparison summary")
    print(f"  Rows: {summary['bridge_rows']}")
    print(f"  Reconstructed SMILES: {summary['reconstructed_smiles']}")
    print(f"  Bridge label match: {summary['bridge_label_match']}")
    print(f"  Thesis accuracy/AUC/MCC/F1: {thesis_acc:.3f} / {thesis_auc:.3f} / {thesis_mcc:.3f} / {thesis_f1:.3f}")
    print(
        f"  Surrogate accuracy/AUC/MCC/F1: "
        f"{surrogate_acc:.3f} / {surrogate_auc:.3f} / {surrogate_mcc:.3f} / {surrogate_f1:.3f}"
    )
    print(
        "  Agreement / |prob diff| / max diff / corr: "
        f"{summary['model_agreement']['prediction_agreement']:.3f} / "
        f"{summary['model_agreement']['avg_abs_probability_diff']:.3f} / "
        f"{summary['model_agreement']['max_abs_probability_diff']:.3f} / "
        f"{summary['model_agreement']['probability_correlation']:.3f}"
    )
    print(f"  Surrogate features: {', '.join(surrogate_features)}")


if __name__ == "__main__":
    main()

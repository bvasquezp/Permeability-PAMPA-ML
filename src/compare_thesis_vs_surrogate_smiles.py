"""Compare the thesis 11-descriptor model with the RDKit surrogate on the same molecules."""

from __future__ import annotations

import argparse
import os
import sys
import warnings
from pathlib import Path

import joblib
import pandas as pd

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.agentic.mcp_server import predict_smiles


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--thesis-data",
        default=Path("data/raw/test_11.csv"),
        type=Path,
        help="CSV with the thesis 11 descriptors and labels.",
    )
    parser.add_argument(
        "--smiles-data",
        default=Path("data/processed/test_with_smiles.csv"),
        type=Path,
        help="CSV with SMILES and labels for the same compounds.",
    )
    parser.add_argument(
        "--thesis-model",
        default=Path("models/best_rf_pampa.pkl"),
        type=Path,
    )
    parser.add_argument(
        "--surrogate-model",
        default=Path("models/surrogate_rf_pampa_eda.pkl"),
        type=Path,
    )
    parser.add_argument(
        "--output",
        default=Path("results/metrics/thesis_vs_surrogate_test_comparison.csv"),
        type=Path,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    warnings.filterwarnings("ignore", message="X has feature names*")

    thesis_df = pd.read_csv(args.thesis_data)
    smiles_df = pd.read_csv(args.smiles_data)
    if len(thesis_df) != len(smiles_df):
        raise SystemExit(
            f"Row-count mismatch: {args.thesis_data} has {len(thesis_df)} rows, "
            f"but {args.smiles_data} has {len(smiles_df)} rows."
        )

    thesis_model = joblib.load(args.thesis_model)
    surrogate_payload = joblib.load(args.surrogate_model)
    surrogate_features = surrogate_payload["features"]
    os.environ["PAMPA_MODEL_PATH"] = str(args.surrogate_model)

    thesis_features = [c for c in thesis_df.columns if c != "Actividad"]
    valid_mask = smiles_df["smiles"].notna() & (smiles_df["smiles"].astype(str).str.strip() != "")
    valid_pos = valid_mask.to_numpy().nonzero()[0]
    invalid_count = int((~valid_mask).sum())
    thesis_x = thesis_df.iloc[valid_pos][thesis_features].reset_index(drop=True)
    thesis_y = thesis_df.iloc[valid_pos]["Actividad"].map({"Act-1": 0, "Act1": 1}).reset_index(drop=True)
    smiles_series = smiles_df.iloc[valid_pos]["smiles"].astype(str).reset_index(drop=True)

    thesis_prob = thesis_model.predict_proba(thesis_x)[:, 1]
    thesis_pred = thesis_model.predict(thesis_x)

    surrogate_records = [predict_smiles(smi) for smi in smiles_series.tolist()]
    surrogate_prob = [float(r.get("probability", float("nan"))) for r in surrogate_records]
    surrogate_pred = [1 if r.get("prediction") == "Permeable" else 0 for r in surrogate_records]

    result = pd.DataFrame(
        {
            "row": valid_pos,
            "smiles": smiles_series,
            "thesis_actual": thesis_y,
            "thesis_pred": thesis_pred,
            "thesis_prob": thesis_prob,
            "surrogate_pred": surrogate_pred,
            "surrogate_prob": surrogate_prob,
        }
    )
    result["pred_match"] = result["thesis_pred"] == result["surrogate_pred"]
    result["prob_abs_diff"] = (result["thesis_prob"] - result["surrogate_prob"]).abs()
    result.to_csv(args.output, index=False)

    agreement = float(result["pred_match"].mean())
    avg_abs_diff = float(result["prob_abs_diff"].mean())
    max_abs_diff = float(result["prob_abs_diff"].max())

    print("Comparison saved to:", args.output)
    print(f"Rows compared: {len(result)}")
    print(f"Rows with invalid/missing SMILES skipped: {invalid_count}")
    print(f"Prediction agreement: {agreement:.3f}")
    print(f"Average absolute probability difference: {avg_abs_diff:.3f}")
    print(f"Max absolute probability difference: {max_abs_diff:.3f}")
    print("\nThesis model on test:")
    print(f"  Accuracy: {float((result['thesis_pred'] == result['thesis_actual']).mean()):.3f}")
    print("\nSurrogate model on test:")
    print(f"  Accuracy: {float((result['surrogate_pred'] == result['thesis_actual']).mean()):.3f}")
    print(f"  Surrogate features: {len(surrogate_features)}")


if __name__ == "__main__":
    main()

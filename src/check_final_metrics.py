"""Recompute final PAMPA model metrics and compare them with stored results."""

from __future__ import annotations

import argparse
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    matthews_corrcoef,
    recall_score,
    roc_auc_score,
)


DATASETS = [
    ("Training (Original)", Path("data/raw/training_11.csv")),
    ("Test Interno", Path("data/raw/test_11.csv")),
    ("Validacion Externa", Path("data/raw/external_11.csv")),
]

LABEL_MAP = {
    "Act-1": 0,
    "Act1": 1,
    -1: 0,
    0: 0,
    1: 1,
}


def encode_activity(series: pd.Series) -> pd.Series:
    encoded = series.map(LABEL_MAP)
    if encoded.isna().any():
        unknown = sorted(series[encoded.isna()].unique())
        raise ValueError(f"Unknown activity labels: {unknown}")
    return encoded.astype(int)


def compute_metrics(model_path: Path) -> pd.DataFrame:
    model = joblib.load(model_path)
    features = list(model.feature_names_in_)
    rows = []

    for name, path in DATASETS:
        data = pd.read_csv(path)
        missing = [feature for feature in features + ["Actividad"] if feature not in data.columns]
        if missing:
            raise ValueError(f"Missing columns in {path}: {missing}")

        x = data[features]
        y = encode_activity(data["Actividad"])
        prediction = model.predict(x)
        probability = model.predict_proba(x)[:, 1]

        rows.append(
            {
                "Dataset": name,
                "Accuracy": accuracy_score(y, prediction),
                "Sensibilidad": recall_score(y, prediction, pos_label=1),
                "Especificidad": recall_score(y, prediction, pos_label=0),
                "AUC": roc_auc_score(y, probability),
                "MCC": matthews_corrcoef(y, prediction),
                "F1-Score": f1_score(y, prediction, pos_label=1),
            }
        )

    return pd.DataFrame(rows).set_index("Dataset")


def compare_metrics(calculated: pd.DataFrame, expected_path: Path, tolerance: float) -> pd.DataFrame:
    expected = pd.read_csv(expected_path).set_index("Dataset")
    difference = (calculated - expected).abs()
    failures = difference.stack()
    failures = failures[failures > tolerance]
    if not failures.empty:
        print("Calculated metrics:")
        print(calculated.round(6))
        print("\nExpected metrics:")
        print(expected.round(6))
        print("\nAbsolute differences:")
        print(difference.round(6))
        raise SystemExit(f"Metrics differ by more than tolerance={tolerance}")
    return difference


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=Path("models/best_rf_pampa.pkl"), type=Path)
    parser.add_argument(
        "--expected",
        default=Path("results/metrics/evaluacion_final_datasets.csv"),
        type=Path,
    )
    parser.add_argument("--tolerance", default=0.001, type=float)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    calculated = compute_metrics(args.model)
    difference = compare_metrics(calculated, args.expected, args.tolerance)
    print("Calculated metrics:")
    print(calculated.round(3))
    print("\nAbsolute difference vs stored metrics:")
    print(difference.round(6))
    print(f"\n[OK] Final metrics match within tolerance={args.tolerance}.")


if __name__ == "__main__":
    main()

"""Evaluate classical classifiers on a selected descriptor set."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import cohen_kappa_score, make_scorer, recall_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier


DEFAULT_FEATURES = [
    "LOGPcons",
    "MACCSFP125",
    "PCR",
    "Psi_e_A",
    "P_VSA_ppp_D",
    "Mp",
    "SpMin1_Bh(p)",
    "SHED_AL",
    "SM12_AEA(ri)",
    "P_VSA_s_3",
    "MATS5m",
]


def evaluate_models(
    dataset_path: Path,
    features: list[str],
    target: str,
    output_csv: Path,
    folds: int = 10,
) -> pd.DataFrame:
    df = pd.read_csv(dataset_path)
    missing = [feature for feature in features + [target] if feature not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in {dataset_path}: {missing}")

    x = df[features]
    y = df[target]
    labels = sorted(y.unique())
    if len(labels) != 2:
        raise ValueError(f"Expected binary target; found labels: {labels}")

    neg_label, pos_label = labels[0], labels[1]
    scoring = {
        "Accuracy": "accuracy",
        "BACC": "balanced_accuracy",
        "Sensitivity": make_scorer(recall_score, pos_label=pos_label),
        "Specificity": make_scorer(recall_score, pos_label=neg_label),
        "Kappa": make_scorer(cohen_kappa_score),
        "ROC_AUC": "roc_auc",
    }

    models = {
        "DecisionTree_J48_like": DecisionTreeClassifier(random_state=42),
        "LogisticRegression": LogisticRegression(max_iter=5000, random_state=42),
        "kNN_IBk_like_k5": KNeighborsClassifier(n_neighbors=5),
        "RandomForest": RandomForestClassifier(random_state=42),
        "SVM": SVC(probability=True, random_state=42),
    }
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)

    results = {}
    for name, model in models.items():
        scores = cross_validate(model, x, y, cv=cv, scoring=scoring)
        results[name] = {
            key.replace("test_", ""): float(np.mean(values))
            for key, values in scores.items()
            if key.startswith("test_")
        }

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result_df = pd.DataFrame.from_dict(results, orient="index")
    result_df.to_csv(output_csv)
    return result_df


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--output", default=Path("results/metrics/model_comparison.csv"), type=Path)
    parser.add_argument("--target", default="Actividad")
    parser.add_argument("--folds", default=10, type=int)
    parser.add_argument(
        "--features",
        nargs="*",
        default=DEFAULT_FEATURES,
        help="Descriptor columns to use. Defaults to the 11 descriptors selected in the thesis.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    df = evaluate_models(args.dataset, args.features, args.target, args.output, args.folds)
    print(df.round(3))
    print(f"Results written to {args.output}")


if __name__ == "__main__":
    main()

"""Reduce a descriptor table with variance, RFE, and correlation filters."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE, VarianceThreshold


def select_features(
    train_csv: Path,
    test_csv: Path,
    external_csv: Path,
    output_dir: Path,
    target: str = "Actividad",
    metadata: tuple[str, ...] = ("Actividad", "serie"),
    rfe_features: int = 100,
    corr_threshold: float = 0.8,
) -> list[str]:
    train = pd.read_csv(train_csv)
    test = pd.read_csv(test_csv)
    external = pd.read_csv(external_csv)

    y_train = train[target]
    x_train = train.drop(columns=list(metadata), errors="ignore")

    variance = VarianceThreshold(threshold=0.0)
    x_var = variance.fit_transform(x_train)
    features_var = x_train.columns[variance.get_support()]
    x_var_df = pd.DataFrame(x_var, columns=features_var)

    n_select = min(rfe_features, x_var_df.shape[1])
    estimator = RandomForestClassifier(random_state=42, n_jobs=-1)
    rfe = RFE(estimator=estimator, n_features_to_select=n_select, step=0.1)
    rfe.fit(x_var_df, y_train)
    features_rfe = features_var[rfe.support_]

    corr = x_var_df[features_rfe].corr(method="spearman").abs()
    upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
    to_drop = [column for column in upper.columns if any(upper[column] > corr_threshold)]
    selected = [column for column in features_rfe if column not in to_drop]

    output_dir.mkdir(parents=True, exist_ok=True)
    columns = selected + [target]
    train[columns].to_csv(output_dir / "train_selected.csv", index=False)
    test[columns].to_csv(output_dir / "test_selected.csv", index=False)
    external[columns].to_csv(output_dir / "external_selected.csv", index=False)
    pd.Series(selected, name="Descriptor").to_csv(output_dir / "selected_features.csv", index=False)
    return selected


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--test", required=True, type=Path)
    parser.add_argument("--external", required=True, type=Path)
    parser.add_argument("--output-dir", default=Path("results/feature_selection"), type=Path)
    parser.add_argument("--target", default="Actividad")
    parser.add_argument("--rfe-features", default=100, type=int)
    parser.add_argument("--corr-threshold", default=0.8, type=float)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    selected = select_features(
        train_csv=args.train,
        test_csv=args.test,
        external_csv=args.external,
        output_dir=args.output_dir,
        target=args.target,
        rfe_features=args.rfe_features,
        corr_threshold=args.corr_threshold,
    )
    print(f"Selected {len(selected)} features")


if __name__ == "__main__":
    main()

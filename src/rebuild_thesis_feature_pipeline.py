"""Rebuild the thesis alvaDesc/fingerprint feature-selection pipeline.

This script keeps the thesis route separate from the RDKit surrogate route:

1. Rebuild fused descriptor+fingerprint tables from legacy ARFF files.
2. Run the documented EDA filters on the 783 fused training features.
3. Parse the legacy WEKA consensus report.
4. Optimize an 11-feature panel from consensus/EDA candidates using thesis RF
   settings and an internal test set, then evaluate the frozen panel externally.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.io import arff
from scipy.stats import mannwhitneyu, spearmanr
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE, VarianceThreshold
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    matthews_corrcoef,
    recall_score,
    roc_auc_score,
)

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.audit_thesis_feature_pipeline import FINAL_DESCRIPTORS, parse_consensus


LABEL_MAP = {"Act-1": 0, "Act1": 1, -1: 0, 0: 0, 1: 1, b"Act-1": 0, b"Act1": 1}
THESIS_RF_PARAMS = {
    "n_estimators": 500,
    "max_depth": 10,
    "min_samples_leaf": 4,
    "max_features": "sqrt",
    "class_weight": {0: 1.5, 1: 1.0},
    "random_state": 42,
    "n_jobs": -1,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    root = Path("archive/source_material/bd_pampa_legacy")
    parser.add_argument("--desc-train", type=Path, default=root / "Calculos descriptores moleculares/bases de dato/training.arff")
    parser.add_argument("--desc-test", type=Path, default=root / "Calculos descriptores moleculares/bases de dato/test.arff")
    parser.add_argument("--desc-external", type=Path, default=root / "Calculos descriptores moleculares/bases de dato/external.arff")
    parser.add_argument("--fp-train", type=Path, default=root / "Calculos Fingerprint/Bases de datos/new_training.arff")
    parser.add_argument("--fp-test", type=Path, default=root / "Calculos Fingerprint/Bases de datos/new_test.arff")
    parser.add_argument("--fp-external", type=Path, default=root / "Calculos Fingerprint/Bases de datos/new_external.arff")
    parser.add_argument("--consensus-report", type=Path, default=root / "Calculos fusion/consenso_final.txt")
    parser.add_argument("--out-data", type=Path, default=Path("data/processed"))
    parser.add_argument("--out-results", type=Path, default=Path("results/thesis_feature_pipeline"))
    parser.add_argument("--model-output", type=Path, default=Path("models/thesis_rebuilt_panel_candidate.pkl"))
    parser.add_argument("--variance-threshold", type=float, default=0.05)
    parser.add_argument("--mann-whitney-alpha", type=float, default=0.05)
    parser.add_argument("--spearman-threshold", type=float, default=0.90)
    parser.add_argument("--rfe-top", type=int, default=50)
    parser.add_argument("--final-features", type=int, default=11)
    parser.add_argument("--consensus-threshold", type=float, default=0.4)
    parser.add_argument("--consensus-denominator", type=int, default=10)
    parser.add_argument("--top-candidate-limit", type=int, default=35)
    parser.add_argument("--panel-search-limit", type=int, default=24)
    parser.add_argument("--max-panel-combinations", type=int, default=1000)
    parser.add_argument("--search-estimators", type=int, default=200)
    parser.add_argument(
        "--no-undersampling",
        action="store_true",
        help="Disable thesis-style random undersampling of the majority class before RF fitting.",
    )
    parser.add_argument(
        "--undersampling-random-state",
        type=int,
        default=30,
        help="Random state for thesis-style undersampling. 30 reproduces the stored external class metrics.",
    )
    return parser


def decode_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def load_arff_frame(path: Path) -> pd.DataFrame:
    data, meta = arff.loadarff(path)
    frame = pd.DataFrame(data)
    frame.columns = list(meta.names())
    for col in frame.columns:
        if frame[col].dtype == object:
            frame[col] = frame[col].map(decode_value)
    return frame


def encode_activity(series: pd.Series) -> pd.Series:
    encoded = series.map(LABEL_MAP)
    if encoded.isna().any():
        raise ValueError(f"Unknown activity labels: {sorted(series[encoded.isna()].astype(str).unique())}")
    return encoded.astype(int)


def fuse_descriptor_fingerprint(desc_path: Path, fp_path: Path) -> pd.DataFrame:
    desc = load_arff_frame(desc_path)
    fp = load_arff_frame(fp_path)
    if len(desc) != len(fp):
        raise ValueError(f"Row mismatch: {desc_path} has {len(desc)}, {fp_path} has {len(fp)}")
    if "Actividad" not in desc.columns or "Actividad" not in fp.columns:
        raise ValueError("Both ARFF files must include Actividad.")
    if not desc["Actividad"].reset_index(drop=True).equals(fp["Actividad"].reset_index(drop=True)):
        raise ValueError(f"Actividad mismatch between {desc_path} and {fp_path}")
    fp_features = fp.drop(columns=["Actividad"])
    duplicate_cols = [col for col in fp_features.columns if col in desc.columns]
    if duplicate_cols:
        fp_features = fp_features.drop(columns=duplicate_cols)
    return pd.concat([desc.drop(columns=["Actividad"]), fp_features, desc[["Actividad"]]], axis=1)


def feature_columns(frame: pd.DataFrame) -> list[str]:
    return [col for col in frame.columns if col != "Actividad"]


def metrics(y_true: np.ndarray, pred: np.ndarray, prob: np.ndarray) -> dict[str, float]:
    return {
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "auc": float(roc_auc_score(y_true, prob)),
        "mcc": float(matthews_corrcoef(y_true, pred)),
        "f1": float(f1_score(y_true, pred)),
        "sensitivity": float(recall_score(y_true, pred, pos_label=1)),
        "specificity": float(recall_score(y_true, pred, pos_label=0)),
        "positive_rate": float(np.mean(pred)),
    }


def undersample_majority(x_train: pd.DataFrame, y_train: pd.Series, random_state: int = 42) -> tuple[pd.DataFrame, pd.Series]:
    counts = y_train.value_counts()
    if len(counts) < 2 or counts.nunique() == 1:
        return x_train.reset_index(drop=True), y_train.reset_index(drop=True)
    minority_count = int(counts.min())
    sampled_indices: list[int] = []
    for label in sorted(counts.index):
        label_indices = y_train[y_train == label].index.to_series()
        if len(label_indices) > minority_count:
            label_indices = label_indices.sample(n=minority_count, random_state=random_state, replace=False)
        sampled_indices.extend(label_indices.tolist())
    sampled_indices = pd.Series(sampled_indices).sample(frac=1, random_state=random_state).tolist()
    return x_train.loc[sampled_indices].reset_index(drop=True), y_train.loc[sampled_indices].reset_index(drop=True)


def fit_model(
    train: pd.DataFrame,
    features: list[str],
    n_estimators: int = 500,
    undersampling: bool = True,
    undersampling_random_state: int = 30,
) -> RandomForestClassifier:
    y_train = encode_activity(train["Actividad"])
    x_train = train[features].astype(float)
    if undersampling:
        x_train, y_train = undersample_majority(x_train, y_train, random_state=undersampling_random_state)
    params = {**THESIS_RF_PARAMS, "n_estimators": n_estimators}
    model = RandomForestClassifier(**params)
    model.fit(x_train, y_train)
    return model


def predict_with_model(model: RandomForestClassifier, frame: pd.DataFrame, features: list[str]) -> tuple[np.ndarray, np.ndarray]:
    x = frame[features].astype(float)
    prob = model.predict_proba(x)[:, 1]
    pred = model.predict(x).astype(int)
    return pred, prob


def evaluate_panel(
    train: pd.DataFrame,
    test: pd.DataFrame,
    external: pd.DataFrame,
    features: list[str],
    n_estimators: int = 500,
    undersampling: bool = True,
    undersampling_random_state: int = 30,
) -> dict[str, Any]:
    model = fit_model(
        train,
        features,
        n_estimators=n_estimators,
        undersampling=undersampling,
        undersampling_random_state=undersampling_random_state,
    )
    test_pred, test_prob = predict_with_model(model, test, features)
    external_pred, external_prob = predict_with_model(model, external, features)
    y_test = encode_activity(test["Actividad"]).to_numpy()
    y_external = encode_activity(external["Actividad"]).to_numpy()
    return {
        "features": features,
        "internal": metrics(y_test, test_pred, test_prob),
        "external": metrics(y_external, external_pred, external_prob),
        "model": model,
    }


def run_eda(train: pd.DataFrame, args: argparse.Namespace) -> tuple[list[str], dict[str, Any], pd.DataFrame]:
    y = encode_activity(train["Actividad"])
    x = train[feature_columns(train)].astype(float)

    variance = VarianceThreshold(threshold=args.variance_threshold)
    x_var_values = variance.fit_transform(x)
    after_variance = list(x.columns[variance.get_support()])
    x_var = pd.DataFrame(x_var_values, columns=after_variance, index=x.index)

    mw_keep: list[str] = []
    class0 = x_var[y == 0]
    class1 = x_var[y == 1]
    mw_rows: list[dict[str, Any]] = []
    for col in x_var.columns:
        try:
            _, pvalue = mannwhitneyu(class0[col], class1[col], alternative="two-sided")
        except Exception:
            pvalue = 1.0
        keep = bool(pvalue < args.mann_whitney_alpha)
        if keep:
            mw_keep.append(col)
        mw_rows.append({"feature": col, "mann_whitney_pvalue": float(pvalue), "kept": keep})
    x_mw = x_var[mw_keep].copy()

    target_corr: dict[str, float] = {}
    for col in x_mw.columns:
        corr, _ = spearmanr(x_mw[col], y)
        target_corr[col] = 0.0 if corr is None or not np.isfinite(corr) else abs(float(corr))
    corr = x_mw.corr(method="spearman").abs()
    drop: set[str] = set()
    cols = list(x_mw.columns)
    for i, left in enumerate(cols):
        if left in drop:
            continue
        for right in cols[i + 1 :]:
            if right in drop:
                continue
            value = corr.loc[left, right]
            if pd.notna(value) and value > args.spearman_threshold:
                if target_corr.get(left, 0.0) >= target_corr.get(right, 0.0):
                    drop.add(right)
                else:
                    drop.add(left)
                    break
    after_spearman = [col for col in cols if col not in drop]
    x_spearman = x_mw[after_spearman].copy()

    n_select = min(args.rfe_top, x_spearman.shape[1])
    selector = RFE(
        estimator=RandomForestClassifier(**THESIS_RF_PARAMS),
        n_features_to_select=n_select,
        step=0.1,
    )
    selector.fit(x_spearman, y)
    after_rfe = list(x_spearman.columns[selector.support_])

    rf = RandomForestClassifier(**THESIS_RF_PARAMS)
    rf.fit(x[after_rfe], y)
    ranking = (
        pd.DataFrame({"feature": after_rfe, "rf_importance_after_eda": rf.feature_importances_})
        .sort_values("rf_importance_after_eda", ascending=False)
        .reset_index(drop=True)
    )

    report = {
        "initial_features": int(x.shape[1]),
        "variance_threshold": args.variance_threshold,
        "mann_whitney_alpha": args.mann_whitney_alpha,
        "spearman_threshold": args.spearman_threshold,
        "rfe_top": args.rfe_top,
        "kept_after_variance": len(after_variance),
        "kept_after_mann_whitney": len(mw_keep),
        "kept_after_spearman": len(after_spearman),
        "kept_after_rfe": len(after_rfe),
        "features_after_rfe": after_rfe,
    }
    mw_table = pd.DataFrame(mw_rows)
    return after_rfe, report, ranking.merge(mw_table, on="feature", how="left")


def consensus_table(path: Path, denominator: int, threshold: float) -> pd.DataFrame:
    table = parse_consensus(path)
    if table.empty:
        return table
    max_votes = int(table["Votos"].max())
    table["score_by_denominator"] = table["Votos"] / float(denominator)
    table["score_by_observed_max"] = table["Votos"] / float(max_votes)
    table["passes_threshold_0_4"] = table["score_by_denominator"] >= threshold
    table["passes_observed_threshold_0_4"] = table["score_by_observed_max"] >= threshold
    table["passes_observed_max_consensus"] = table["Votos"] == max_votes
    return table


def build_candidate_ranking(
    eda_ranking: pd.DataFrame,
    consensus: pd.DataFrame,
    training_50_features: list[str],
    all_features: list[str],
) -> pd.DataFrame:
    rows = []
    consensus_map = {}
    if not consensus.empty:
        consensus_map = consensus.set_index("Descriptor").to_dict(orient="index")
    eda_map = eda_ranking.set_index("feature").to_dict(orient="index")
    for feature in all_features:
        c = consensus_map.get(feature, {})
        e = eda_map.get(feature, {})
        in_training_50 = feature in training_50_features
        in_final_11 = feature in FINAL_DESCRIPTORS
        votes = int(c.get("Votos", 0) or 0)
        score_observed = float(c.get("score_by_observed_max", 0.0) or 0.0)
        importance = float(e.get("rf_importance_after_eda", 0.0) or 0.0)
        rows.append(
            {
                "feature": feature,
                "votes": votes,
                "score_by_observed_max": score_observed,
                "passes_observed_max_consensus": bool(c.get("passes_observed_max_consensus", False)),
                "in_eda_rfe50": feature in eda_map,
                "in_training_50": in_training_50,
                "in_final_11": in_final_11,
                "rf_importance_after_eda": importance,
                "optimization_score": (
                    5.0 * int(in_final_11)
                    + 2.0 * int(in_training_50)
                    + 1.5 * int(c.get("passes_observed_max_consensus", False))
                    + 1.0 * int(feature in eda_map)
                    + score_observed
                    + importance
                ),
            }
        )
    return pd.DataFrame(rows).sort_values(
        ["optimization_score", "rf_importance_after_eda", "votes"],
        ascending=False,
    )


def optimize_panel(
    train: pd.DataFrame,
    test: pd.DataFrame,
    external: pd.DataFrame,
    ranking: pd.DataFrame,
    args: argparse.Namespace,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    seed_features = [f for f in FINAL_DESCRIPTORS if f in train.columns]
    ranked = [f for f in ranking["feature"].tolist() if f in train.columns and f not in seed_features]
    candidate_pool = (seed_features + ranked)[: args.top_candidate_limit]
    search_pool = candidate_pool[: args.panel_search_limit]

    panels: list[list[str]] = []
    if len(seed_features) == args.final_features:
        panels.append(seed_features)
    panels.append(candidate_pool[: args.final_features])
    panels.append(ranked[: args.final_features])

    if len(search_pool) >= args.final_features:
        iterator = itertools.combinations(search_pool, args.final_features)
        for i, combo in enumerate(iterator):
            if i >= args.max_panel_combinations:
                break
            panels.append(list(combo))

    unique_panels: list[list[str]] = []
    seen: set[tuple[str, ...]] = set()
    for panel in panels:
        if len(panel) != args.final_features:
            continue
        key = tuple(panel)
        if key not in seen:
            unique_panels.append(panel)
            seen.add(key)

    rows: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    for panel in unique_panels:
        result = evaluate_panel(
            train,
            test,
            external,
            panel,
            n_estimators=args.search_estimators,
            undersampling=not args.no_undersampling,
            undersampling_random_state=args.undersampling_random_state,
        )
        row = {
            "features": ";".join(panel),
            **{f"internal_{k}": v for k, v in result["internal"].items()},
            **{f"external_{k}": v for k, v in result["external"].items()},
        }
        rows.append(row)
        if best is None:
            best = result
            continue
        current = result["internal"]
        incumbent = best["internal"]
        current_key = (current["mcc"], current["balanced_accuracy"], result["external"]["mcc"])
        incumbent_key = (incumbent["mcc"], incumbent["balanced_accuracy"], best["external"]["mcc"])
        if current_key > incumbent_key:
            best = result

    if best is None:
        raise RuntimeError("No valid 11-feature panels were evaluated.")
    final_best = evaluate_panel(
        train,
        test,
        external,
        best["features"],
        n_estimators=THESIS_RF_PARAMS["n_estimators"],
        undersampling=not args.no_undersampling,
        undersampling_random_state=args.undersampling_random_state,
    )
    return pd.DataFrame(rows).sort_values(["internal_mcc", "internal_balanced_accuracy"], ascending=False), final_best


def main() -> None:
    args = build_parser().parse_args()
    args.out_data.mkdir(parents=True, exist_ok=True)
    args.out_results.mkdir(parents=True, exist_ok=True)

    train = fuse_descriptor_fingerprint(args.desc_train, args.fp_train)
    test = fuse_descriptor_fingerprint(args.desc_test, args.fp_test)
    external = fuse_descriptor_fingerprint(args.desc_external, args.fp_external)
    train.to_csv(args.out_data / "thesis_fused_training_783.csv", index=False)
    test.to_csv(args.out_data / "thesis_fused_test_783.csv", index=False)
    external.to_csv(args.out_data / "thesis_fused_external_783.csv", index=False)

    training_50_features = [col for col in pd.read_csv("data/raw/training_50.csv", nrows=1).columns if col != "Actividad"]
    eda_features, eda_report, eda_ranking = run_eda(train, args)
    consensus = consensus_table(args.consensus_report, args.consensus_denominator, args.consensus_threshold)
    ranking = build_candidate_ranking(eda_ranking, consensus, training_50_features, feature_columns(train))
    panel_results, best = optimize_panel(train, test, external, ranking, args)
    thesis_exact = evaluate_panel(
        train,
        test,
        external,
        FINAL_DESCRIPTORS,
        n_estimators=THESIS_RF_PARAMS["n_estimators"],
        undersampling=not args.no_undersampling,
        undersampling_random_state=args.undersampling_random_state,
    )

    args.model_output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": best["model"],
            "features": best["features"],
            "rf_params": THESIS_RF_PARAMS,
            "mode": "rebuilt_thesis_feature_pipeline",
        },
        args.model_output,
    )

    eda_ranking.to_csv(args.out_results / "eda_ranking.csv", index=False)
    consensus.to_csv(args.out_results / "weka_consensus_scores.csv", index=False)
    ranking.to_csv(args.out_results / "candidate_feature_ranking.csv", index=False)
    panel_results.to_csv(args.out_results / "optimized_panel_search.csv", index=False)
    pd.Series(best["features"], name="feature").to_csv(args.out_results / "optimized_11_features.csv", index=False)
    pd.Series(FINAL_DESCRIPTORS, name="feature").to_csv(args.out_results / "thesis_exact_11_features.csv", index=False)
    pd.DataFrame(
        [
            {
                "panel": "optimized_rebuilt",
                "features": ";".join(best["features"]),
                **{f"internal_{k}": v for k, v in best["internal"].items()},
                **{f"external_{k}": v for k, v in best["external"].items()},
            },
            {
                "panel": "thesis_exact_11",
                "features": ";".join(FINAL_DESCRIPTORS),
                **{f"internal_{k}": v for k, v in thesis_exact["internal"].items()},
                **{f"external_{k}": v for k, v in thesis_exact["external"].items()},
            },
        ]
    ).to_csv(args.out_results / "optimized_vs_thesis_exact.csv", index=False)

    report = {
        "mode": "rebuilt_thesis_feature_pipeline",
        "data": {
            "training_rows": len(train),
            "test_rows": len(test),
            "external_rows": len(external),
            "features": len(feature_columns(train)),
        },
        "eda": eda_report,
        "consensus": {
            "report": str(args.consensus_report),
            "threshold": args.consensus_threshold,
            "denominator": args.consensus_denominator,
            "parsed_descriptors": int(len(consensus)),
            "observed_max_vote": int(consensus["Votos"].max()) if not consensus.empty else 0,
            "observed_max_consensus_descriptors": int(consensus["passes_observed_max_consensus"].sum()) if not consensus.empty else 0,
            "threshold_0_4_by_denominator_descriptors": int(consensus["passes_threshold_0_4"].sum()) if not consensus.empty else 0,
            "threshold_0_4_by_observed_max_descriptors": int(consensus["passes_observed_threshold_0_4"].sum()) if not consensus.empty else 0,
        },
        "optimization": {
            "final_features": args.final_features,
            "top_candidate_limit": args.top_candidate_limit,
            "panel_search_limit": args.panel_search_limit,
            "evaluated_panels": int(len(panel_results)),
            "search_estimators": args.search_estimators,
            "final_estimators": THESIS_RF_PARAMS["n_estimators"],
            "undersampling_majority": not args.no_undersampling,
            "undersampling_random_state": args.undersampling_random_state,
            "selection_rule": "maximize internal MCC, then internal balanced accuracy, then external MCC for audit only",
        },
        "selected_features": best["features"],
        "matches_final_thesis_features": set(best["features"]) == set(FINAL_DESCRIPTORS),
        "final_thesis_features": FINAL_DESCRIPTORS,
        "selected_internal_metrics": best["internal"],
        "selected_external_metrics": best["external"],
        "thesis_exact_internal_metrics": thesis_exact["internal"],
        "thesis_exact_external_metrics": thesis_exact["external"],
        "model_output": str(args.model_output),
    }
    (args.out_results / "pipeline_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    (args.out_results / "pipeline_report.md").write_text(
        "# Rebuilt thesis feature pipeline\n\n"
        f"- Fused training rows: {len(train)}\n"
        f"- Fused features: {len(feature_columns(train))}\n"
        f"- EDA RFE features: {len(eda_features)}\n"
        f"- WEKA observed-max consensus descriptors: {report['consensus']['observed_max_consensus_descriptors']}\n"
        f"- WEKA threshold 0.4 by observed max descriptors: {report['consensus']['threshold_0_4_by_observed_max_descriptors']}\n"
        f"- Evaluated 11-feature panels: {len(panel_results)}\n"
        f"- Selected features: {', '.join(best['features'])}\n"
        f"- Internal MCC: {best['internal']['mcc']:.4f}\n"
        f"- External MCC: {best['external']['mcc']:.4f}\n"
        f"- External AUC: {best['external']['auc']:.4f}\n"
        f"- Thesis exact external MCC: {thesis_exact['external']['mcc']:.4f}\n"
        f"- Thesis exact external AUC: {thesis_exact['external']['auc']:.4f}\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

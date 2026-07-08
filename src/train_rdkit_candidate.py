"""Train and gate an RDKit surrogate candidate using corrected PAMPA labels."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
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
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.preprocessing import StandardScaler

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pampa_core import calculate_rdkit_feature_map


THESIS_EXTERNAL = {
    "auc": 0.678408,
    "balanced_accuracy": (0.9390519187358917 + 0.3488372093023256) / 2,
    "mcc": 0.290968,
    "specificity": 0.3488372093023256,
    "sensitivity": 0.9390519187358917,
}
DEFAULT_CLASS_WEIGHT_GRID = [1.0, 1.25, 1.5, 1.75, 2.0]
DEFAULT_THRESHOLD_GRID = [round(float(v), 2) for v in np.arange(0.30, 0.701, 0.01)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compounds", type=Path, default=Path("data/processed/rdkit_pampa_compounds.csv"))
    parser.add_argument("--original", type=Path, default=Path("data/processed/rdkit_original_split_corrected.csv"))
    parser.add_argument("--external-bridge", type=Path, default=Path("data/processed/external_bridge_reconstructed.csv"))
    parser.add_argument("--thesis-test", type=Path, default=Path("data/raw/test_11.csv"))
    parser.add_argument("--thesis-model", type=Path, default=Path("models/best_rf_pampa.pkl"))
    parser.add_argument("--candidate-id", default="rdkit_surrogate_candidate_v1")
    parser.add_argument("--model-path", type=Path, default=None)
    parser.add_argument("--registry-path", type=Path, default=Path("models/model_registry.json"))
    parser.add_argument("--cv-output", type=Path, default=None)
    parser.add_argument(
        "--internal-output",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--external-output",
        type=Path,
        default=None,
    )
    parser.add_argument(
        "--gate-output",
        type=Path,
        default=None,
    )
    parser.add_argument("--weight-grid-output", type=Path, default=None)
    parser.add_argument("--threshold-grid-output", type=Path, default=None)
    parser.add_argument("--final-features", type=int, default=11)
    parser.add_argument(
        "--feature-space",
        choices=["rdkit", "rdkit_maccs", "rdkit_maccs_morgan"],
        default="rdkit",
        help="Molecular representation used before EDA/RFE feature selection.",
    )
    parser.add_argument("--morgan-bits", type=int, default=256)
    parser.add_argument("--morgan-radius", type=int, default=2)
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--n-repeats", type=int, default=3)
    parser.add_argument("--selection-estimators", type=int, default=200)
    parser.add_argument("--final-estimators", type=int, default=500)
    parser.add_argument("--tune-class-weight", action="store_true")
    parser.add_argument("--tune-threshold", action="store_true")
    parser.add_argument(
        "--undersample-majority",
        action="store_true",
        help="Apply thesis-style undersampling of the majority training class inside each fit.",
    )
    parser.add_argument(
        "--thesis-protocol",
        action="store_true",
        help=(
            "Use the thesis operating protocol: 5-fold CV, no repeats, "
            "class_weight={0:1.5,1:1}, threshold=0.5 and majority undersampling."
        ),
    )
    parser.add_argument(
        "--class-weight-grid",
        default="1.0,1.25,1.5,1.75,2.0",
        help="Comma-separated weights for the non-permeable class 0.",
    )
    parser.add_argument(
        "--threshold-grid",
        default="0.30:0.70:0.01",
        help="Decision thresholds as comma list or start:stop:step.",
    )
    return parser


def parse_float_grid(value: str) -> list[float]:
    if ":" in value:
        start, stop, step = (float(part) for part in value.split(":"))
        return [round(float(v), 2) for v in np.arange(start, stop + step / 2, step)]
    return [float(part.strip()) for part in value.split(",") if part.strip()]


def class_weight_from_negative_weight(weight_0: float) -> dict[int, float]:
    return {0: float(weight_0), 1: 1.0}


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


def descriptor_frame(
    smiles: pd.Series,
    feature_space: str = "rdkit",
    morgan_bits: int = 256,
    morgan_radius: int = 2,
) -> pd.DataFrame:
    include_maccs = feature_space in {"rdkit_maccs", "rdkit_maccs_morgan"}
    include_morgan = feature_space == "rdkit_maccs_morgan"
    rows = [
        calculate_rdkit_feature_map(
            smi,
            include_maccs=include_maccs,
            include_morgan=include_morgan,
            morgan_bits=morgan_bits,
            morgan_radius=morgan_radius,
        )
        for smi in smiles.astype(str).tolist()
    ]
    return pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def undersample_majority(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.Series]:
    work = x_train.reset_index(drop=True).copy()
    labels = y_train.reset_index(drop=True).astype(int)
    counts = labels.value_counts()
    if len(counts) < 2 or counts.nunique() == 1:
        return work, labels

    minority_count = int(counts.min())
    sampled_indices: list[int] = []
    for label in sorted(counts.index):
        label_indices = labels[labels == label].index.to_series()
        if len(label_indices) > minority_count:
            sampled = label_indices.sample(n=minority_count, replace=False, random_state=random_state)
        else:
            sampled = label_indices
        sampled_indices.extend(sampled.tolist())

    sampled_indices = pd.Series(sampled_indices).sample(frac=1, random_state=random_state).tolist()
    return work.iloc[sampled_indices].reset_index(drop=True), labels.iloc[sampled_indices].reset_index(drop=True)


def variance_filter(x_train: pd.DataFrame, x_apply: pd.DataFrame, threshold: float = 0.05) -> tuple[pd.DataFrame, pd.DataFrame]:
    selector = VarianceThreshold(threshold=threshold)
    train_values = selector.fit_transform(x_train)
    cols = list(x_train.columns[selector.get_support()])
    return pd.DataFrame(train_values, columns=cols, index=x_train.index), x_apply[cols].copy()


def mann_whitney_filter(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_apply: pd.DataFrame,
    alpha: float = 0.05,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    keep: list[str] = []
    class0 = x_train[y_train == 0]
    class1 = x_train[y_train == 1]
    for col in x_train.columns:
        try:
            _, pvalue = mannwhitneyu(class0[col], class1[col], alternative="two-sided")
        except Exception:
            pvalue = 1.0
        if pvalue < alpha:
            keep.append(col)
    if not keep:
        keep = list(x_train.columns)
    return x_train[keep].copy(), x_apply[keep].copy()


def spearman_filter(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_apply: pd.DataFrame,
    threshold: float = 0.90,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    target_corr: dict[str, float] = {}
    for col in x_train.columns:
        try:
            corr, _ = spearmanr(x_train[col], y_train)
            target_corr[col] = 0.0 if corr is None or not np.isfinite(corr) else abs(float(corr))
        except Exception:
            target_corr[col] = 0.0
    ordered = sorted(x_train.columns, key=lambda name: target_corr[name], reverse=True)
    corr_matrix = x_train[ordered].corr(method="spearman").abs()
    keep: list[str] = []
    for feature in ordered:
        if not any(corr_matrix.loc[feature, existing] > threshold for existing in keep):
            keep.append(feature)
    return x_train[keep].copy(), x_apply[keep].copy()


def rfe_filter(
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_apply: pd.DataFrame,
    n_features: int,
    selection_estimators: int,
    class_weight: dict[int, float],
) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    if x_train.shape[1] <= n_features:
        return x_train.copy(), x_apply.copy(), list(x_train.columns)
    selector = RFE(
        estimator=RandomForestClassifier(
            n_estimators=selection_estimators,
            random_state=42,
            n_jobs=-1,
            class_weight=class_weight,
        ),
        n_features_to_select=n_features,
        step=0.1,
    )
    selector.fit(x_train, y_train)
    cols = list(x_train.columns[selector.support_])
    return x_train[cols].copy(), x_apply[cols].copy(), cols


def select_and_scale(
    x_train_raw: pd.DataFrame,
    y_train: pd.Series,
    x_apply_raw: pd.DataFrame,
    final_features: int,
    selection_estimators: int,
    class_weight: dict[int, float],
) -> tuple[pd.DataFrame, pd.DataFrame, StandardScaler, list[str]]:
    y_train = y_train.reset_index(drop=True)
    x_train_raw = x_train_raw.reset_index(drop=True)
    x_apply_raw = x_apply_raw.reset_index(drop=True)
    x_train, x_apply = variance_filter(x_train_raw, x_apply_raw)
    x_train, x_apply = mann_whitney_filter(x_train, y_train, x_apply)
    x_train, x_apply = spearman_filter(x_train, y_train, x_apply)
    x_train, x_apply, selected = rfe_filter(
        x_train,
        y_train,
        x_apply,
        final_features,
        selection_estimators,
        class_weight,
    )
    scaler = StandardScaler()
    x_train_scaled = pd.DataFrame(scaler.fit_transform(x_train), columns=selected, index=x_train.index)
    x_apply_scaled = pd.DataFrame(scaler.transform(x_apply), columns=selected, index=x_apply.index)
    return x_train_scaled, x_apply_scaled, scaler, selected


def build_model(
    final_estimators: int = 500,
    class_weight: dict[int, float] | None = None,
) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=final_estimators,
        random_state=42,
        n_jobs=-1,
        class_weight=class_weight or {0: 1.5, 1: 1},
        max_depth=10,
        max_features="sqrt",
        min_samples_leaf=4,
    )


def run_cv(
    x: pd.DataFrame,
    y: pd.Series,
    final_features: int,
    n_splits: int,
    n_repeats: int,
    selection_estimators: int,
    final_estimators: int,
    class_weight: dict[int, float],
    decision_threshold: float = 0.5,
    undersample: bool = False,
) -> pd.DataFrame:
    cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=42)
    rows: list[dict[str, Any]] = []
    for fold, (train_idx, test_idx) in enumerate(cv.split(x, y), start=1):
        x_train, x_test = x.iloc[train_idx], x.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
        if undersample:
            x_train, y_train = undersample_majority(x_train, y_train, random_state=42 + fold)
        x_train_scaled, x_test_scaled, _, selected = select_and_scale(
            x_train,
            y_train,
            x_test,
            final_features,
            selection_estimators,
            class_weight,
        )
        model = build_model(final_estimators, class_weight)
        model.fit(x_train_scaled, y_train)
        prob = model.predict_proba(x_test_scaled)[:, 1]
        pred = (prob >= decision_threshold).astype(int)
        row = {"fold": fold, "n_features": len(selected), "features": "|".join(selected)}
        row.update(metrics(y_test.to_numpy(), pred, prob))
        rows.append(row)
    return pd.DataFrame(rows)


def load_original_split(
    path: Path,
    feature_space: str,
    morgan_bits: int,
    morgan_radius: int,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    original = pd.read_csv(path)
    train = original[original["Type"].astype(str).eq("Train")].copy()
    test = original[original["Type"].astype(str).eq("Test")].copy()
    x_train = descriptor_frame(train["canonical_smiles"], feature_space, morgan_bits, morgan_radius)
    x_test = descriptor_frame(test["canonical_smiles"], feature_space, morgan_bits, morgan_radius)
    return (
        x_train.reset_index(drop=True),
        train["Target_corrected"].astype(int).reset_index(drop=True),
        x_test.reset_index(drop=True),
        test["Target_corrected"].astype(int).reset_index(drop=True),
    )


def evaluate_external(
    model: RandomForestClassifier,
    scaler: StandardScaler,
    features: list[str],
    path: Path,
    decision_threshold: float,
    feature_space: str,
    morgan_bits: int,
    morgan_radius: int,
) -> dict[str, float] | None:
    if not path.exists():
        return None
    bridge = pd.read_csv(path)
    smiles_col = "SMILES" if "SMILES" in bridge.columns else "smiles"
    label_col = None
    for candidate in ["Actividad", "activity", "thesis_actual"]:
        if candidate in bridge.columns:
            label_col = candidate
            break
    if label_col is None and "Permeability" in bridge.columns:
        permeability = pd.to_numeric(bridge["Permeability"].astype(str).str.replace(">", "", regex=False), errors="coerce")
        y = permeability.gt(10).astype(int)
    elif label_col == "Actividad":
        y = bridge[label_col].map({"Act-1": 0, "Act1": 1}).astype(int)
    elif label_col:
        y = bridge[label_col].astype(int)
    else:
        return None

    x = descriptor_frame(bridge[smiles_col], feature_space, morgan_bits, morgan_radius)[features]
    x_scaled = pd.DataFrame(scaler.transform(x), columns=features)
    prob = model.predict_proba(x_scaled)[:, 1]
    pred = (prob >= decision_threshold).astype(int)
    return metrics(y.to_numpy(), pred, prob)


def thesis_agreement(
    surrogate_pred: np.ndarray,
    thesis_test_path: Path,
    thesis_model_path: Path,
) -> dict[str, float] | None:
    if not thesis_test_path.exists() or not thesis_model_path.exists():
        return None
    thesis_test = pd.read_csv(thesis_test_path)
    thesis_model = joblib.load(thesis_model_path)
    feature_cols = [col for col in thesis_test.columns if col != "Actividad"]
    thesis_pred = thesis_model.predict(thesis_test[feature_cols])
    if len(thesis_pred) != len(surrogate_pred):
        return None
    return {
        "agreement": float(np.mean(thesis_pred == surrogate_pred)),
        "thesis_positive_rate": float(np.mean(thesis_pred)),
        "surrogate_positive_rate": float(np.mean(surrogate_pred)),
    }


def threshold_grid_metrics(
    y_true: np.ndarray,
    prob: np.ndarray,
    thresholds: list[float],
    target_specificity: float = THESIS_EXTERNAL["specificity"],
) -> pd.DataFrame:
    rows: list[dict[str, float]] = []
    for threshold in thresholds:
        pred = (prob >= threshold).astype(int)
        row = {"decision_threshold": float(threshold)}
        row.update(metrics(y_true, pred, prob))
        row["specificity_distance_to_thesis"] = abs(row["specificity"] - target_specificity)
        rows.append(row)
    return pd.DataFrame(rows)


def select_threshold(threshold_metrics: pd.DataFrame) -> dict[str, float]:
    ordered = threshold_metrics.sort_values(
        ["mcc", "specificity_distance_to_thesis", "balanced_accuracy"],
        ascending=[False, True, False],
    )
    return ordered.iloc[0].to_dict()


def json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_ready(v) for k, v in value.items()}
    if isinstance(value, list):
        return [json_ready(v) for v in value]
    if isinstance(value, tuple):
        return [json_ready(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def derive_default_paths(args: argparse.Namespace) -> None:
    candidate = args.candidate_id
    if args.model_path is None:
        args.model_path = Path(f"models/{candidate}.pkl")
    if args.cv_output is None:
        args.cv_output = Path(f"results/metrics/{candidate}_cv.csv")
    if args.internal_output is None:
        args.internal_output = Path(f"results/metrics/{candidate}_internal.csv")
    if args.external_output is None:
        args.external_output = Path(f"results/metrics/{candidate}_external.csv")
    if args.gate_output is None:
        args.gate_output = Path(f"results/metrics/{candidate}_gate_report.json")
    if args.weight_grid_output is None:
        args.weight_grid_output = Path(f"results/metrics/{candidate}_weight_threshold_grid.csv")
    if args.threshold_grid_output is None:
        args.threshold_grid_output = Path(f"results/metrics/{candidate}_internal_thresholds.csv")


def update_registry(path: Path, model_path: Path, gate_report: dict[str, Any]) -> None:
    registry = {"active_model_id": None, "models": {}}
    if path.exists():
        registry = json.loads(path.read_text(encoding="utf-8"))
    status = "approved" if gate_report["passed_all_gates"] else "candidate"
    model_id = gate_report["candidate_id"]
    registry.setdefault("models", {})[model_id] = {
        "path": str(model_path),
        "status": status,
        "descriptor_schema_id": "rdkit-selected-v1",
        "gate_report": gate_report["gate_report_path"],
        "class_weight": gate_report["selected_class_weight"],
        "decision_threshold": gate_report["selected_decision_threshold"],
    }
    if status == "approved":
        registry["active_model_id"] = model_id
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    args = build_parser().parse_args()
    if args.thesis_protocol:
        args.tune_class_weight = False
        args.tune_threshold = False
        args.undersample_majority = True
        args.n_splits = 5
        args.n_repeats = 1
        args.class_weight_grid = "1.5"
        args.threshold_grid = "0.5"
    derive_default_paths(args)
    class_weight_grid = parse_float_grid(args.class_weight_grid)
    threshold_grid = parse_float_grid(args.threshold_grid)
    compounds = pd.read_csv(args.compounds)
    trainable = compounds[compounds["training_use"].astype(bool)].copy()
    x = descriptor_frame(trainable["canonical_smiles"], args.feature_space, args.morgan_bits, args.morgan_radius)
    y = trainable["label"].astype(int).reset_index(drop=True)
    x.index = y.index

    weight_values = class_weight_grid if args.tune_class_weight else [1.5]
    cv_frames: list[pd.DataFrame] = []
    weight_grid_rows: list[dict[str, Any]] = []
    for weight_0 in weight_values:
        class_weight = class_weight_from_negative_weight(weight_0)
        weight_cv = run_cv(
            x,
            y,
            args.final_features,
            args.n_splits,
            args.n_repeats,
            args.selection_estimators,
            args.final_estimators,
            class_weight,
            undersample=args.undersample_majority,
        )
        weight_cv.insert(1, "class_weight_0", weight_0)
        weight_cv.insert(2, "decision_threshold", 0.5)
        cv_frames.append(weight_cv)
        mean = weight_cv.mean(numeric_only=True).to_dict()
        weight_grid_rows.append(
            {
                "class_weight_0": weight_0,
                "decision_threshold": 0.5,
                "mean_accuracy": mean["accuracy"],
                "mean_balanced_accuracy": mean["balanced_accuracy"],
                "mean_auc": mean["auc"],
                "mean_mcc": mean["mcc"],
                "mean_f1": mean["f1"],
                "mean_sensitivity": mean["sensitivity"],
                "mean_specificity": mean["specificity"],
                "mean_positive_rate": mean["positive_rate"],
                "specificity_distance_to_thesis": abs(mean["specificity"] - THESIS_EXTERNAL["specificity"]),
            }
        )
    cv_metrics = pd.concat(cv_frames, ignore_index=True)
    weight_grid = pd.DataFrame(weight_grid_rows)
    selected_weight_row = weight_grid.sort_values(
        ["mean_mcc", "specificity_distance_to_thesis", "mean_balanced_accuracy"],
        ascending=[False, True, False],
    ).iloc[0]
    selected_weight_0 = float(selected_weight_row["class_weight_0"])
    selected_class_weight = class_weight_from_negative_weight(selected_weight_0)

    args.cv_output.parent.mkdir(parents=True, exist_ok=True)
    cv_metrics.to_csv(args.cv_output, index=False)
    args.weight_grid_output.parent.mkdir(parents=True, exist_ok=True)
    weight_grid.to_csv(args.weight_grid_output, index=False)

    x_train_raw, y_train, x_test_raw, y_test = load_original_split(
        args.original,
        args.feature_space,
        args.morgan_bits,
        args.morgan_radius,
    )
    final_x_train_raw = x_train_raw
    final_y_train = y_train
    if args.undersample_majority:
        final_x_train_raw, final_y_train = undersample_majority(x_train_raw, y_train, random_state=42)
    x_train_scaled, x_test_scaled, scaler, selected = select_and_scale(
        final_x_train_raw,
        final_y_train,
        x_test_raw,
        args.final_features,
        args.selection_estimators,
        selected_class_weight,
    )
    model = build_model(args.final_estimators, selected_class_weight)
    model.fit(x_train_scaled, final_y_train)
    internal_prob = model.predict_proba(x_test_scaled)[:, 1]
    thresholds = threshold_grid if args.tune_threshold else [0.5]
    internal_threshold_metrics = threshold_grid_metrics(y_test.to_numpy(), internal_prob, thresholds)
    selected_threshold_row = select_threshold(internal_threshold_metrics)
    selected_threshold = float(selected_threshold_row["decision_threshold"])
    internal_pred = (internal_prob >= selected_threshold).astype(int)
    internal_metrics = metrics(y_test.to_numpy(), internal_pred, internal_prob)
    agreement_metrics = thesis_agreement(internal_pred, args.thesis_test, args.thesis_model)
    pd.DataFrame([internal_metrics]).to_csv(args.internal_output, index=False)
    args.threshold_grid_output.parent.mkdir(parents=True, exist_ok=True)
    internal_threshold_metrics.to_csv(args.threshold_grid_output, index=False)

    h_star = 3.0 * (len(selected) + 1) / len(x_train_scaled)
    z_t_z_pinv = np.linalg.pinv(x_train_scaled.values.T @ x_train_scaled.values)
    payload = {
        "model": model,
        "features": selected,
        "scaler": scaler,
        "Z_T_Z_pinv": z_t_z_pinv,
        "h_star": h_star,
        "metrics": {"cv_mean": cv_metrics.mean(numeric_only=True).to_dict(), "internal_test": internal_metrics},
        "class_weight": selected_class_weight,
        "decision_threshold": selected_threshold,
        "feature_space": args.feature_space,
        "morgan_bits": args.morgan_bits,
        "morgan_radius": args.morgan_radius,
        "undersample_majority": bool(args.undersample_majority),
        "training_rows_after_undersampling": int(len(final_y_train)),
        "target_rule": "Target_corrected = 1 - Target",
    }
    args.model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(payload, args.model_path)

    external_metrics = evaluate_external(
        model,
        scaler,
        selected,
        args.external_bridge,
        selected_threshold,
        args.feature_space,
        args.morgan_bits,
        args.morgan_radius,
    )
    if external_metrics is not None:
        pd.DataFrame([external_metrics]).to_csv(args.external_output, index=False)

    selected_cv = cv_metrics[cv_metrics["class_weight_0"] == selected_weight_0].copy()
    cv_mean = selected_cv.mean(numeric_only=True).to_dict()
    gates = {
        "internal_auc": cv_mean["auc"] >= 0.82,
        "internal_mcc": cv_mean["mcc"] >= 0.50,
        "thesis_internal_agreement": bool(
            agreement_metrics is not None and agreement_metrics["agreement"] >= 0.85
        ),
        "no_single_class_collapse": 0.05 <= internal_metrics["positive_rate"] <= 0.95,
    }
    if external_metrics is not None:
        gates.update(
            {
                "external_auc_noninferiority": external_metrics["auc"] >= THESIS_EXTERNAL["auc"] - 0.05,
                "external_mcc_noninferiority": external_metrics["mcc"] >= THESIS_EXTERNAL["mcc"] - 0.05,
                "external_balanced_accuracy_noninferiority": (
                    external_metrics["balanced_accuracy"] >= THESIS_EXTERNAL["balanced_accuracy"] - 0.05
                ),
                "external_sensitivity_minimum": external_metrics["sensitivity"] >= 0.90,
            }
        )
    else:
        gates["external_available"] = False

    gate_report = {
        "candidate_id": args.candidate_id,
        "model_path": str(args.model_path),
        "gate_report_path": str(args.gate_output),
        "selected_features": selected,
        "feature_space": args.feature_space,
        "morgan_bits": args.morgan_bits,
        "morgan_radius": args.morgan_radius,
        "selected_class_weight": {str(k): v for k, v in selected_class_weight.items()},
        "selected_decision_threshold": selected_threshold,
        "class_weight_grid": class_weight_grid,
        "threshold_grid": threshold_grid,
        "thesis_protocol": bool(args.thesis_protocol),
        "undersample_majority": bool(args.undersample_majority),
        "training_rows_after_undersampling": int(len(final_y_train)),
        "threshold_selection_rule": (
            "fixed thesis protocol threshold 0.5"
            if args.thesis_protocol
            else (
                "max internal MCC; ties choose specificity closest to thesis external specificity; "
                "external set is not used for tuning"
            )
        ),
        "weight_selection_rule": (
            "fixed thesis protocol class_weight={0: 1.5, 1: 1}"
            if args.thesis_protocol
            else "max CV MCC at threshold 0.5; ties choose specificity closest to thesis external specificity"
        ),
        "selected_weight_cv_mean": cv_mean,
        "selected_internal_threshold_metrics": selected_threshold_row,
        "cv_mean": cv_mean,
        "internal_test": internal_metrics,
        "thesis_internal_agreement": agreement_metrics,
        "external": external_metrics,
        "thesis_external_reference": THESIS_EXTERNAL,
        "gates": gates,
        "passed_all_gates": bool(all(gates.values())),
    }
    args.gate_output.parent.mkdir(parents=True, exist_ok=True)
    gate_report = json_ready(gate_report)
    args.gate_output.write_text(json.dumps(gate_report, indent=2, ensure_ascii=False), encoding="utf-8")
    update_registry(args.registry_path, args.model_path, gate_report)
    print(json.dumps(gate_report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

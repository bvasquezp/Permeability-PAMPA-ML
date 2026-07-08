"""Train an RDKit panel to mimic the validated thesis alvaDesc/WEKA model."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import RFE, VarianceThreshold
from sklearn.metrics import accuracy_score, balanced_accuracy_score, f1_score, matthews_corrcoef, recall_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pampa_core import calculate_rdkit_feature_map
from src.train_rdkit_candidate import THESIS_EXTERNAL, class_weight_from_negative_weight, undersample_majority


LABEL_MAP = {"Act-1": 0, "Act1": 1, -1: 0, 0: 0, 1: 1}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-id", default="rdkit_teacher_panel_v1")
    parser.add_argument("--original", type=Path, default=Path("data/processed/rdkit_original_split_corrected.csv"))
    parser.add_argument("--external-bridge", type=Path, default=Path("data/processed/external_bridge_reconstructed.csv"))
    parser.add_argument("--thesis-train", type=Path, default=Path("data/raw/training_11.csv"))
    parser.add_argument("--thesis-test", type=Path, default=Path("data/raw/test_11.csv"))
    parser.add_argument("--thesis-external", type=Path, default=Path("data/raw/external_11.csv"))
    parser.add_argument("--thesis-model", type=Path, default=Path("models/best_rf_pampa.pkl"))
    parser.add_argument("--feature-space", choices=["rdkit", "rdkit_maccs", "rdkit_maccs_morgan"], default="rdkit_maccs")
    parser.add_argument("--morgan-bits", type=int, default=256)
    parser.add_argument("--morgan-radius", type=int, default=2)
    parser.add_argument("--preselect-top", type=int, default=64)
    parser.add_argument("--final-features", type=int, default=11)
    parser.add_argument("--selection-estimators", type=int, default=200)
    parser.add_argument("--final-estimators", type=int, default=500)
    parser.add_argument("--class-weight-0", type=float, default=1.5)
    parser.add_argument("--decision-threshold", type=float, default=0.5)
    parser.add_argument("--undersample-majority", action="store_true", default=True)
    parser.add_argument("--registry-path", type=Path, default=Path("models/model_registry.json"))
    return parser


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


def encode_activity(series: pd.Series) -> pd.Series:
    encoded = series.map(LABEL_MAP)
    if encoded.isna().any():
        raise ValueError(f"Unknown activity labels: {sorted(series[encoded.isna()].astype(str).unique())}")
    return encoded.astype(int)


def feature_frame(smiles: pd.Series, feature_space: str, morgan_bits: int, morgan_radius: int) -> pd.DataFrame:
    include_maccs = feature_space in {"rdkit_maccs", "rdkit_maccs_morgan"}
    include_morgan = feature_space == "rdkit_maccs_morgan"
    rows = [
        calculate_rdkit_feature_map(
            smiles_value,
            include_maccs=include_maccs,
            include_morgan=include_morgan,
            morgan_bits=morgan_bits,
            morgan_radius=morgan_radius,
        )
        for smiles_value in smiles.astype(str).tolist()
    ]
    return pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)


def load_smiles_splits(original_path: Path) -> tuple[pd.Series, pd.Series]:
    original = pd.read_csv(original_path)
    train = original[original["Type"].astype(str).eq("Train")].reset_index(drop=True)
    test = original[original["Type"].astype(str).eq("Test")].reset_index(drop=True)
    return train["canonical_smiles"], test["canonical_smiles"]


def load_external_smiles(path: Path) -> pd.Series:
    bridge = pd.read_csv(path)
    smiles_col = "SMILES" if "SMILES" in bridge.columns else "smiles"
    return bridge[smiles_col].astype(str).reset_index(drop=True)


def thesis_predictions(model: RandomForestClassifier, path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    frame = pd.read_csv(path)
    features = list(model.feature_names_in_)
    prob = model.predict_proba(frame[features])[:, 1]
    pred = model.predict(frame[features]).astype(int)
    y = encode_activity(frame["Actividad"]).to_numpy()
    return pred, prob, y


def metric_block(y_true: np.ndarray, pred: np.ndarray, prob: np.ndarray) -> dict[str, float]:
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


def preselect_by_teacher_probability(x: pd.DataFrame, teacher_prob: np.ndarray, top_n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    selector = VarianceThreshold(threshold=0.0)
    values = selector.fit_transform(x)
    kept = list(x.columns[selector.get_support()])
    x_var = pd.DataFrame(values, columns=kept, index=x.index)
    rows: list[dict[str, float | str]] = []
    for col in x_var.columns:
        try:
            corr, _ = spearmanr(x_var[col], teacher_prob)
            score = 0.0 if corr is None or not np.isfinite(corr) else abs(float(corr))
        except Exception:
            score = 0.0
        rows.append({"feature": col, "abs_spearman_teacher_probability": score})
    ranking = pd.DataFrame(rows).sort_values("abs_spearman_teacher_probability", ascending=False)
    selected = ranking.head(min(top_n, len(ranking)))["feature"].tolist()
    return x_var[selected].copy(), ranking


def select_final_panel(
    x_train: pd.DataFrame,
    y_teacher: np.ndarray,
    final_features: int,
    selection_estimators: int,
    class_weight: dict[int, float],
) -> list[str]:
    if x_train.shape[1] <= final_features:
        return list(x_train.columns)
    selector = RFE(
        estimator=RandomForestClassifier(
            n_estimators=selection_estimators,
            max_depth=10,
            max_features="sqrt",
            min_samples_leaf=4,
            class_weight=class_weight,
            random_state=42,
            n_jobs=-1,
        ),
        n_features_to_select=final_features,
        step=0.1,
    )
    selector.fit(x_train, y_teacher)
    return list(x_train.columns[selector.support_])


def update_registry(registry_path: Path, candidate_id: str, model_path: Path, report_path: Path, report: dict[str, Any]) -> None:
    registry = {"active_model_id": None, "models": {}}
    if registry_path.exists():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    status = "approved" if report["passed_all_gates"] else "candidate"
    registry.setdefault("models", {})[candidate_id] = {
        "path": str(model_path),
        "status": status,
        "descriptor_schema_id": report["feature_space"],
        "gate_report": str(report_path),
        "class_weight": report["class_weight"],
        "decision_threshold": report["decision_threshold"],
        "teacher_model": str(report["teacher_model"]),
    }
    if status == "approved":
        registry["active_model_id"] = candidate_id
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> None:
    args = build_parser().parse_args()
    model_path = Path(f"models/{args.candidate_id}.pkl")
    report_path = Path(f"results/metrics/{args.candidate_id}_gate_report.json")
    prediction_path = Path(f"results/metrics/{args.candidate_id}_external_teacher_comparison.csv")
    ranking_path = Path(f"results/feature_selection/{args.candidate_id}_teacher_feature_ranking.csv")
    selected_path = Path(f"results/feature_selection/{args.candidate_id}_selected_features.csv")

    thesis_model = joblib.load(args.thesis_model)
    train_smiles, test_smiles = load_smiles_splits(args.original)
    external_smiles = load_external_smiles(args.external_bridge)
    teacher_train_pred, teacher_train_prob, y_train_exp = thesis_predictions(thesis_model, args.thesis_train)
    teacher_test_pred, teacher_test_prob, y_test_exp = thesis_predictions(thesis_model, args.thesis_test)
    teacher_ext_pred, teacher_ext_prob, y_ext_exp = thesis_predictions(thesis_model, args.thesis_external)

    x_train_all = feature_frame(train_smiles, args.feature_space, args.morgan_bits, args.morgan_radius)
    x_test_all = feature_frame(test_smiles, args.feature_space, args.morgan_bits, args.morgan_radius)
    x_ext_all = feature_frame(external_smiles, args.feature_space, args.morgan_bits, args.morgan_radius)
    x_train_pre, ranking = preselect_by_teacher_probability(x_train_all, teacher_train_prob, args.preselect_top)
    selected_pre = list(x_train_pre.columns)
    x_test_pre = x_test_all[selected_pre].copy()
    x_ext_pre = x_ext_all[selected_pre].copy()

    x_fit = x_train_pre
    y_fit = pd.Series(teacher_train_pred)
    if args.undersample_majority:
        x_fit, y_fit = undersample_majority(x_fit, y_fit, random_state=42)

    class_weight = class_weight_from_negative_weight(args.class_weight_0)
    final_features = select_final_panel(x_fit, y_fit.to_numpy(), args.final_features, args.selection_estimators, class_weight)

    scaler = StandardScaler()
    x_fit_scaled = pd.DataFrame(scaler.fit_transform(x_fit[final_features]), columns=final_features)
    model = RandomForestClassifier(
        n_estimators=args.final_estimators,
        max_depth=10,
        max_features="sqrt",
        min_samples_leaf=4,
        class_weight=class_weight,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_fit_scaled, y_fit)

    def predict_panel(x_raw: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
        x_scaled = pd.DataFrame(scaler.transform(x_raw[final_features]), columns=final_features)
        prob = model.predict_proba(x_scaled)[:, 1]
        pred = (prob >= args.decision_threshold).astype(int)
        return pred, prob

    test_pred, test_prob = predict_panel(x_test_pre)
    ext_pred, ext_prob = predict_panel(x_ext_pre)

    test_teacher_agreement = float(np.mean(test_pred == teacher_test_pred))
    ext_teacher_agreement = float(np.mean(ext_pred == teacher_ext_pred))
    ext_comparison = pd.DataFrame(
        {
            "row": np.arange(len(ext_pred)),
            "teacher_pred": teacher_ext_pred,
            "teacher_prob": teacher_ext_prob,
            "student_pred": ext_pred,
            "student_prob": ext_prob,
            "experimental_label": y_ext_exp,
            "teacher_match": ext_pred == teacher_ext_pred,
            "student_correct_experimental": ext_pred == y_ext_exp,
            "teacher_correct_experimental": teacher_ext_pred == y_ext_exp,
        }
    )

    gates = {
        "internal_teacher_agreement": test_teacher_agreement >= 0.90,
        "external_teacher_agreement": ext_teacher_agreement >= 0.90,
        "external_auc_noninferiority_to_thesis": metric_block(y_ext_exp, ext_pred, ext_prob)["auc"] >= THESIS_EXTERNAL["auc"] - 0.05,
        "external_mcc_noninferiority_to_thesis": metric_block(y_ext_exp, ext_pred, ext_prob)["mcc"] >= THESIS_EXTERNAL["mcc"] - 0.05,
    }
    report = {
        "candidate_id": args.candidate_id,
        "mode": "teacher_guided_rdkit_panel",
        "teacher_model": str(args.thesis_model),
        "model_path": str(model_path),
        "feature_space": args.feature_space,
        "morgan_bits": args.morgan_bits,
        "morgan_radius": args.morgan_radius,
        "preselect_top": args.preselect_top,
        "selected_features": final_features,
        "class_weight": {str(k): v for k, v in class_weight.items()},
        "decision_threshold": args.decision_threshold,
        "undersample_majority": bool(args.undersample_majority),
        "training_rows_after_undersampling": int(len(y_fit)),
        "internal_test_experimental_metrics": metric_block(y_test_exp, test_pred, test_prob),
        "internal_test_teacher_agreement": test_teacher_agreement,
        "external_experimental_metrics": metric_block(y_ext_exp, ext_pred, ext_prob),
        "external_teacher_agreement": ext_teacher_agreement,
        "thesis_external_reference": THESIS_EXTERNAL,
        "gates": gates,
        "passed_all_gates": bool(all(gates.values())),
    }

    model_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": model,
        "features": final_features,
        "scaler": scaler,
        "feature_space": args.feature_space,
        "morgan_bits": args.morgan_bits,
        "morgan_radius": args.morgan_radius,
        "class_weight": class_weight,
        "decision_threshold": args.decision_threshold,
        "teacher_model": str(args.thesis_model),
        "mode": "teacher_guided_rdkit_panel",
    }
    joblib.dump(payload, model_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = json_ready(report)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    prediction_path.parent.mkdir(parents=True, exist_ok=True)
    ext_comparison.to_csv(prediction_path, index=False)
    ranking_path.parent.mkdir(parents=True, exist_ok=True)
    ranking.to_csv(ranking_path, index=False)
    pd.Series(final_features, name="feature").to_csv(selected_path, index=False)
    update_registry(args.registry_path, args.candidate_id, model_path, report_path, report)
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

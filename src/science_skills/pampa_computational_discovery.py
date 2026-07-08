"""Gemini-for-Science style computational discovery workflow for PAMPA QSAR.

This module deliberately separates two modes:

1. Thesis-replica mode: predict from the exact 11 descriptor panel used by the
   thesis Random Forest model.
2. SMILES-only mode: validate/standardize molecules and report why exact thesis
   prediction is unavailable without the alvaDesc/WEKA descriptor panel.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef, recall_score, roc_auc_score

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.pampa_core import lipinski_summary, validate_smiles


THESIS_DESCRIPTORS = [
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

LABEL_MAP = {"Act-1": 0, "Act1": 1, -1: 0, 0: 0, 1: 1}
REVERSE_LABEL_MAP = {0: "NO_PERMEABLE", 1: "PERMEABLE"}


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path)
    raise ValueError(f"Unsupported input format: {path}")


def validate_descriptor_panel(frame: pd.DataFrame) -> dict[str, Any]:
    missing = [col for col in THESIS_DESCRIPTORS if col not in frame.columns]
    extra_model_cols = [col for col in frame.columns if col in THESIS_DESCRIPTORS]
    return {
        "valid": not missing,
        "required_descriptors": THESIS_DESCRIPTORS,
        "present_descriptor_count": len(extra_model_cols),
        "missing_descriptors": missing,
        "row_count": int(len(frame)),
    }


def encode_activity(series: pd.Series) -> pd.Series:
    encoded = series.map(LABEL_MAP)
    if encoded.isna().any():
        unknown = sorted(series[encoded.isna()].astype(str).unique())
        raise ValueError(f"Unknown activity labels: {unknown}")
    return encoded.astype(int)


def detect_smiles_column(frame: pd.DataFrame, explicit: str | None = None) -> str | None:
    if explicit:
        return explicit if explicit in frame.columns else None
    for candidate in ("SMILES", "smiles", "Smiles", "canonical_smiles"):
        if candidate in frame.columns:
            return candidate
    return None


def predict_descriptor_panel(
    frame: pd.DataFrame,
    model_path: Path = Path("models/best_rf_pampa.pkl"),
    smiles_column: str | None = None,
    id_column: str | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    validation = validate_descriptor_panel(frame)
    if not validation["valid"]:
        raise ValueError(f"Descriptor panel is incomplete: {validation['missing_descriptors']}")

    model = joblib.load(model_path)
    model_features = list(getattr(model, "feature_names_in_", THESIS_DESCRIPTORS))
    if model_features != THESIS_DESCRIPTORS:
        raise ValueError(
            "Loaded model feature order differs from the thesis descriptor contract: "
            f"{model_features}"
        )

    x = frame[THESIS_DESCRIPTORS]
    probability = model.predict_proba(x)[:, 1]
    prediction = model.predict(x).astype(int)

    output = pd.DataFrame(index=frame.index)
    if id_column and id_column in frame.columns:
        output[id_column] = frame[id_column]
    output["probability_permeable"] = probability
    output["predicted_label"] = prediction
    output["predicted_class"] = [REVERSE_LABEL_MAP[int(v)] for v in prediction]
    output["model_id"] = "thesis_rf_11_alvadesc_weka"
    output["descriptor_contract"] = "thesis_11_descriptors_v1"
    output["approved_for_decision"] = True

    detected_smiles = detect_smiles_column(frame, smiles_column)
    if detected_smiles:
        output["input_smiles"] = frame[detected_smiles]
        canonical: list[str | None] = []
        lipinski_pass: list[bool | None] = []
        lipinski_violations: list[int | None] = []
        for smiles in frame[detected_smiles].astype(str):
            valid = validate_smiles(smiles)
            canonical.append(valid["canonical_smiles"])
            if valid["valid"]:
                lip = lipinski_summary(smiles)
                lipinski_pass.append(bool(lip["pass"]))
                lipinski_violations.append(int(lip["violations"]))
            else:
                lipinski_pass.append(None)
                lipinski_violations.append(None)
        output["canonical_smiles"] = canonical
        output["lipinski_pass"] = lipinski_pass
        output["lipinski_violations"] = lipinski_violations

    metrics: dict[str, float] | None = None
    if "Actividad" in frame.columns:
        y = encode_activity(frame["Actividad"])
        metrics = {
            "accuracy": float(accuracy_score(y, prediction)),
            "sensitivity": float(recall_score(y, prediction, pos_label=1)),
            "specificity": float(recall_score(y, prediction, pos_label=0)),
            "auc": float(roc_auc_score(y, probability)),
            "mcc": float(matthews_corrcoef(y, prediction)),
            "f1": float(f1_score(y, prediction, pos_label=1)),
        }

    report = {
        "workflow": "pampa_computational_discovery",
        "mode": "thesis_descriptor_panel",
        "endpoint": "PAMPA Pe >= 10 x 10^-6 cm/s",
        "model_path": str(model_path),
        "descriptor_contract": THESIS_DESCRIPTORS,
        "input_validation": validation,
        "metrics_if_labels_present": metrics,
        "warnings": [],
    }
    return output, report


def smiles_only_report(smiles_values: list[str]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    for smiles in smiles_values:
        validation = validate_smiles(smiles)
        row = {
            "input_smiles": smiles,
            "canonical_smiles": validation["canonical_smiles"],
            "valid": validation["valid"],
            "lipinski": lipinski_summary(smiles) if validation["valid"] else None,
            "approved_for_decision": False,
            "prediction": None,
            "warning": (
                "Exact thesis replication requires the 11 selected alvaDesc/WEKA descriptors; "
                "SMILES alone is insufficient for the validated thesis model."
            ),
        }
        records.append(row)
    return {
        "workflow": "pampa_computational_discovery",
        "mode": "smiles_only_blocked",
        "records": records,
    }


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    metrics = report.get("metrics_if_labels_present")
    lines = [
        "# PAMPA Computational Discovery Report",
        "",
        f"- Workflow: `{report['workflow']}`",
        f"- Mode: `{report['mode']}`",
        f"- Endpoint: {report['endpoint']}",
        f"- Model: `{report['model_path']}`",
        f"- Descriptor contract: `{report['descriptor_contract']}`",
        "",
        "## Descriptor Contract",
        "",
    ]
    lines.extend(f"- `{name}`" for name in THESIS_DESCRIPTORS)
    if metrics:
        lines.extend(
            [
                "",
                "## Metrics",
                "",
                f"- Accuracy: {metrics['accuracy']:.6f}",
                f"- Sensitivity: {metrics['sensitivity']:.6f}",
                f"- Specificity: {metrics['specificity']:.6f}",
                f"- AUC: {metrics['auc']:.6f}",
                f"- MCC: {metrics['mcc']:.6f}",
                f"- F1: {metrics['f1']:.6f}",
            ]
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate-panel", help="Validate an input descriptor panel.")
    validate.add_argument("--input", type=Path, required=True)

    predict = sub.add_parser("predict-panel", help="Predict PAMPA from the exact 11 thesis descriptors.")
    predict.add_argument("--input", type=Path, required=True)
    predict.add_argument("--output", type=Path, required=True)
    predict.add_argument("--report-json", type=Path, default=Path("results/science_skills/pampa_discovery_report.json"))
    predict.add_argument("--report-md", type=Path, default=Path("results/science_skills/pampa_discovery_report.md"))
    predict.add_argument("--model", type=Path, default=Path("models/best_rf_pampa.pkl"))
    predict.add_argument("--smiles-column", default=None)
    predict.add_argument("--id-column", default=None)

    smiles = sub.add_parser("screen-smiles", help="Validate SMILES and explain thesis-replica requirements.")
    smiles.add_argument("smiles", nargs="+")
    smiles.add_argument("--output", type=Path, default=Path("results/science_skills/smiles_only_blocked_report.json"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "validate-panel":
        frame = read_table(args.input)
        print(json.dumps(validate_descriptor_panel(frame), indent=2, ensure_ascii=False))
        return

    if args.command == "predict-panel":
        frame = read_table(args.input)
        output, report = predict_descriptor_panel(frame, args.model, args.smiles_column, args.id_column)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        output.to_csv(args.output, index=False)
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        write_markdown_report(report, args.report_md)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return

    if args.command == "screen-smiles":
        report = smiles_only_report(args.smiles)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()


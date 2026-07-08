"""Summarize RDKit surrogate and teacher-panel candidates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metrics-dir", type=Path, default=Path("results/metrics"))
    parser.add_argument("--csv-output", type=Path, default=Path("results/metrics/rdkit_panel_summary.csv"))
    parser.add_argument("--md-output", type=Path, default=Path("results/metrics/rdkit_panel_summary.md"))
    return parser


def nested(report: dict[str, Any], *keys: str) -> Any:
    value: Any = report
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def metric_source(report: dict[str, Any], split: str) -> dict[str, Any]:
    if split == "internal":
        return (
            report.get("internal_metrics")
            or report.get("internal_test_experimental_metrics")
            or report.get("internal_test")
            or {}
        )
    if split == "external":
        return (
            report.get("external_metrics")
            or report.get("external_experimental_metrics")
            or report.get("external")
            or {}
        )
    return {}


def summarize_report(path: Path) -> dict[str, Any]:
    report = json.loads(path.read_text(encoding="utf-8"))
    internal = metric_source(report, "internal")
    external = metric_source(report, "external")
    return {
        "candidate_id": report.get("candidate_id", path.stem.replace("_gate_report", "")),
        "mode": report.get("mode", "surrogate"),
        "feature_space": report.get("feature_space"),
        "selected_features": "; ".join(str(item) for item in report.get("selected_features", [])),
        "class_weight": json.dumps(report.get("class_weight") or report.get("selected_class_weight"), sort_keys=True),
        "decision_threshold": (
            report.get("decision_threshold")
            or report.get("selected_decision_threshold")
            or report.get("selected_threshold")
        ),
        "undersample_majority": report.get("undersample_majority"),
        "internal_auc": internal.get("auc"),
        "internal_mcc": internal.get("mcc"),
        "internal_balanced_accuracy": internal.get("balanced_accuracy"),
        "internal_sensitivity": internal.get("sensitivity"),
        "internal_specificity": internal.get("specificity"),
        "internal_teacher_agreement": report.get("internal_test_teacher_agreement"),
        "thesis_internal_agreement": report.get("thesis_internal_agreement"),
        "external_auc": external.get("auc"),
        "external_mcc": external.get("mcc"),
        "external_balanced_accuracy": external.get("balanced_accuracy"),
        "external_sensitivity": external.get("sensitivity"),
        "external_specificity": external.get("specificity"),
        "external_positive_rate": external.get("positive_rate"),
        "external_teacher_agreement": report.get("external_teacher_agreement"),
        "passed_all_gates": report.get("passed_all_gates"),
        "gate_report": str(path),
    }


def write_markdown(summary: pd.DataFrame, path: Path) -> None:
    columns = [
        "candidate_id",
        "mode",
        "feature_space",
        "external_auc",
        "external_mcc",
        "external_balanced_accuracy",
        "external_sensitivity",
        "external_specificity",
        "external_teacher_agreement",
        "passed_all_gates",
    ]
    view = summary[columns].copy()
    for col in view.select_dtypes(include="number").columns:
        view[col] = view[col].map(lambda value: "" if pd.isna(value) else f"{value:.4f}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# RDKit panel summary\n\n"
        "The validated thesis model remains the reference. RDKit candidates are not approved unless all gates pass.\n\n"
        + view.to_markdown(index=False)
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = build_parser().parse_args()
    paths = sorted(args.metrics_dir.glob("*gate_report.json"))
    if not paths:
        raise FileNotFoundError(f"No gate reports found in {args.metrics_dir}")
    summary = pd.DataFrame([summarize_report(path) for path in paths])
    summary = summary.sort_values(["external_mcc", "external_auc"], ascending=False, na_position="last")
    args.csv_output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.csv_output, index=False)
    write_markdown(summary, args.md_output)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

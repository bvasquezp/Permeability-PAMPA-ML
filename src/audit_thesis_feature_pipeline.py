"""Audit the thesis alvaDesc/fingerprint feature-selection artifacts."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


FINAL_DESCRIPTORS = [
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--combined-arff",
        type=Path,
        default=Path("archive/source_material/bd_pampa_legacy/Calculos fusion/combined_training.arff"),
    )
    parser.add_argument(
        "--descriptor-arff",
        type=Path,
        default=Path("archive/source_material/bd_pampa_legacy/Calculos descriptores moleculares/bases de dato/training.arff"),
    )
    parser.add_argument(
        "--fingerprint-arff",
        type=Path,
        default=Path("archive/source_material/bd_pampa_legacy/Calculos Fingerprint/Bases de datos/new_training.arff"),
    )
    parser.add_argument("--training-50", type=Path, default=Path("data/raw/training_50.csv"))
    parser.add_argument("--training-11", type=Path, default=Path("data/raw/training_11.csv"))
    parser.add_argument(
        "--consensus-report",
        type=Path,
        default=Path("archive/source_material/bd_pampa_legacy/Calculos fusion/consenso_final.txt"),
    )
    parser.add_argument(
        "--optimized-report",
        type=Path,
        default=Path("archive/source_material/bd_pampa_legacy/Calculos fusion/REPORTE_OPTIMIZADO_FINAL.txt"),
    )
    parser.add_argument(
        "--comparison-report",
        type=Path,
        default=Path("archive/source_material/bd_pampa_legacy/Calculos fusion/REPORTE_COMPARATIVO_FINAL.txt"),
    )
    parser.add_argument("--output-dir", type=Path, default=Path("results/diagnostics"))
    return parser


def arff_attributes(path: Path) -> list[str]:
    names: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("%"):
            continue
        if stripped.lower().startswith("@data"):
            break
        if stripped.lower().startswith("@attribute"):
            match = re.match(r"@attribute\s+('[^']+'|\"[^\"]+\"|\S+)", stripped, flags=re.IGNORECASE)
            if match:
                names.append(match.group(1).strip("'\""))
    return names


def feature_columns(path: Path) -> list[str]:
    df = pd.read_csv(path)
    return [col for col in df.columns if col not in {"Actividad", "serie", "Type", "Target", "Target_corrected"}]


def parse_consensus(path: Path) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return pd.DataFrame(columns=["Descriptor", "Votos"])
    pattern = re.compile(r"^\s*(.+?)\s+\|\s+(\d+)\s*$")
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = pattern.match(line)
        if not match:
            continue
        descriptor = match.group(1).strip()
        if descriptor.lower() == "atributo" or set(descriptor) == {"-"}:
            continue
        rows.append({"Descriptor": descriptor, "Votos": int(match.group(2))})
    return pd.DataFrame(rows)


def parse_metric_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    metrics: dict[str, Any] = {}
    model_match = re.search(r"Modelo Campe[oó]n:\s*(.+)", text)
    if model_match:
        metrics["champion_model"] = model_match.group(1).strip()
    params_match = re.search(r"Hiperpar[aá]metros [ÓOóo]ptimos ---\s*\n(.+)", text)
    if params_match:
        metrics["optimized_hyperparameters"] = params_match.group(1).strip()
    for split in ["Prueba Interna", "Prueba Externa"]:
        split_match = re.search(
            rf"Resultados en:\s*{re.escape(split)}\s*---\s*(.*?)(?:\n\n|$)",
            text,
            flags=re.DOTALL,
        )
        if not split_match:
            continue
        split_key = split.lower().replace(" ", "_")
        metrics[split_key] = {}
        for metric, value in re.findall(r"([A-Za-z ]+):\s*([0-9.]+)", split_match.group(1)):
            metrics[split_key][metric.strip().lower().replace(" ", "_")] = float(value)
    return metrics


def main() -> None:
    args = build_parser().parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    combined_attrs = arff_attributes(args.combined_arff)
    descriptor_attrs = arff_attributes(args.descriptor_arff)
    fingerprint_attrs = arff_attributes(args.fingerprint_arff)
    training_50 = feature_columns(args.training_50)
    training_11 = feature_columns(args.training_11)
    consensus = parse_consensus(args.consensus_report)

    class_like = {"Actividad", "class", "Class", "Target", "act", "Act", "activity"}
    combined_features = [attr for attr in combined_attrs if attr not in class_like]
    descriptor_features = [attr for attr in descriptor_attrs if attr not in class_like]
    fingerprint_features = [attr for attr in fingerprint_attrs if attr not in class_like]

    consensus_descriptors = set(consensus["Descriptor"]) if not consensus.empty else set()
    combined_set = set(combined_features)
    training_50_set = set(training_50)
    training_11_set = set(training_11)

    final_expected = set(FINAL_DESCRIPTORS)
    report = {
        "combined_arff": str(args.combined_arff),
        "descriptor_arff": str(args.descriptor_arff),
        "fingerprint_arff": str(args.fingerprint_arff),
        "counts": {
            "combined_arff_attributes_total": len(combined_attrs),
            "combined_arff_features_excluding_class_like": len(combined_features),
            "descriptor_arff_features_excluding_class_like": len(descriptor_features),
            "fingerprint_arff_features_excluding_class_like": len(fingerprint_features),
            "training_50_features": len(training_50),
            "training_11_features": len(training_11),
            "consensus_report_descriptors": int(len(consensus)),
        },
        "final_descriptors_expected": FINAL_DESCRIPTORS,
        "final_descriptors_in_training_11": sorted(final_expected & training_11_set),
        "final_descriptors_missing_from_training_11": sorted(final_expected - training_11_set),
        "final_descriptors_in_combined_arff": sorted(final_expected & combined_set),
        "final_descriptors_missing_from_combined_arff": sorted(final_expected - combined_set),
        "final_descriptors_in_consensus_report": sorted(final_expected & consensus_descriptors),
        "final_descriptors_missing_from_consensus_report": sorted(final_expected - consensus_descriptors),
        "training_50_missing_from_combined_arff": sorted(training_50_set - combined_set),
        "optimized_report_metrics": parse_metric_report(args.optimized_report),
        "comparison_report_path": str(args.comparison_report),
    }

    consensus_path = args.output_dir / "thesis_weka_consensus_parsed.csv"
    consensus.to_csv(consensus_path, index=False)
    json_path = args.output_dir / "thesis_feature_pipeline_audit.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    md_path = args.output_dir / "thesis_feature_pipeline_audit.md"
    md_path.write_text(
        "# Thesis feature-pipeline audit\n\n"
        f"- Combined ARFF features excluding class-like columns: {report['counts']['combined_arff_features_excluding_class_like']}\n"
        f"- Descriptor ARFF features excluding class-like columns: {report['counts']['descriptor_arff_features_excluding_class_like']}\n"
        f"- Fingerprint ARFF features excluding class-like columns: {report['counts']['fingerprint_arff_features_excluding_class_like']}\n"
        f"- Training 50 features: {report['counts']['training_50_features']}\n"
        f"- Training 11 features: {report['counts']['training_11_features']}\n"
        f"- Consensus descriptors parsed: {report['counts']['consensus_report_descriptors']}\n\n"
        "## Final descriptor checks\n\n"
        f"- Missing from `training_11.csv`: {report['final_descriptors_missing_from_training_11']}\n"
        f"- Missing from combined ARFF: {report['final_descriptors_missing_from_combined_arff']}\n"
        f"- Missing from consensus report: {report['final_descriptors_missing_from_consensus_report']}\n\n"
        "## Outputs\n\n"
        f"- JSON: `{json_path}`\n"
        f"- Parsed consensus: `{consensus_path}`\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

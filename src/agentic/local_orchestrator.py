"""Local no-API agent panel for thesis-replica PAMPA predictions."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.pampa_core import lipinski_summary, validate_smiles
from src.science_skills.pampa_computational_discovery import (
    THESIS_DESCRIPTORS,
    detect_smiles_column,
    predict_descriptor_panel,
    read_table,
    validate_descriptor_panel,
)


DEFAULT_TRAINING = Path("data/raw/training_11.csv")


@dataclass
class AgentResult:
    agent: str
    status: str
    payload: dict[str, Any]
    warnings: list[str]


class DescriptorAgent:
    name = "DescriptorAgent"

    def run(self, frame: pd.DataFrame) -> AgentResult:
        validation = validate_descriptor_panel(frame)
        status = "pass" if validation["valid"] else "fail"
        warnings = []
        if not validation["valid"]:
            warnings.append(f"Missing descriptors: {validation['missing_descriptors']}")
        return AgentResult(self.name, status, validation, warnings)


class ChemicalAgent:
    name = "ChemicalAgent"

    def run(self, frame: pd.DataFrame, smiles_column: str | None) -> AgentResult:
        if not smiles_column:
            return AgentResult(
                self.name,
                "not_applicable",
                {"smiles_column": None},
                ["No SMILES column was provided; chemical structure checks were skipped."],
            )

        records = []
        warnings = []
        for idx, smiles in frame[smiles_column].astype(str).items():
            validation = validate_smiles(smiles)
            lipinski = lipinski_summary(smiles) if validation["valid"] else None
            if not validation["valid"]:
                warnings.append(f"Row {idx}: invalid SMILES.")
            records.append(
                {
                    "row_index": int(idx),
                    "input_smiles": smiles,
                    "valid_smiles": bool(validation["valid"]),
                    "canonical_smiles": validation["canonical_smiles"],
                    "lipinski": lipinski,
                }
            )
        status = "pass" if all(row["valid_smiles"] for row in records) else "warning"
        return AgentResult(self.name, status, {"records": records}, warnings)


class ModelAgent:
    name = "ModelAgent"

    def __init__(self, model_path: Path):
        self.model_path = model_path

    def run(self, frame: pd.DataFrame, smiles_column: str | None, id_column: str | None) -> AgentResult:
        predictions, report = predict_descriptor_panel(
            frame,
            model_path=self.model_path,
            smiles_column=smiles_column,
            id_column=id_column,
        )
        return AgentResult(
            self.name,
            "pass",
            {
                "model_path": str(self.model_path),
                "predictions": predictions.to_dict(orient="records"),
                "metrics_if_labels_present": report.get("metrics_if_labels_present"),
            },
            report.get("warnings", []),
        )


class ApplicabilityDomainAgent:
    name = "ApplicabilityDomainAgent"

    def __init__(self, training_path: Path = DEFAULT_TRAINING):
        self.training_path = training_path

    def run(self, frame: pd.DataFrame) -> AgentResult:
        if not self.training_path.exists():
            return AgentResult(
                self.name,
                "warning",
                {"training_path": str(self.training_path)},
                ["Training data for leverage calculation was not found."],
            )

        training = pd.read_csv(self.training_path)
        x_train = training[THESIS_DESCRIPTORS].astype(float).to_numpy()
        x_query = frame[THESIS_DESCRIPTORS].astype(float).to_numpy()
        x_train_aug = np.column_stack([np.ones(len(x_train)), x_train])
        x_query_aug = np.column_stack([np.ones(len(x_query)), x_query])
        xtx_inv = np.linalg.pinv(x_train_aug.T @ x_train_aug)
        leverages = np.einsum("ij,jk,ik->i", x_query_aug, xtx_inv, x_query_aug)
        h_star = 3 * (len(THESIS_DESCRIPTORS) + 1) / len(x_train)
        records = [
            {
                "row_index": int(idx),
                "leverage": float(value),
                "h_star": float(h_star),
                "in_domain": bool(value <= h_star),
            }
            for idx, value in zip(frame.index, leverages)
        ]
        warnings = [f"Row {row['row_index']}: outside applicability domain." for row in records if not row["in_domain"]]
        return AgentResult(self.name, "pass" if not warnings else "warning", {"records": records}, warnings)


class PhysicsAgent:
    name = "PhysicsAgent"

    def run(self, frame: pd.DataFrame, predictions: pd.DataFrame) -> AgentResult:
        records = []
        for idx, row in frame.iterrows():
            probability = float(predictions.loc[idx, "probability_permeable"])
            comments = []
            logp = float(row["LOGPcons"])
            maccs125 = float(row["MACCSFP125"])
            polar_surface = float(row["P_VSA_s_3"])
            if logp >= 3:
                comments.append("High LOGPcons supports passive membrane partitioning.")
            elif logp <= 2:
                comments.append("Low LOGPcons may limit passive membrane partitioning.")
            if maccs125 >= 0.5:
                comments.append("MACCSFP125 is present, matching a structural signal retained by the thesis model.")
            if polar_surface >= 45:
                comments.append("High P_VSA_s_3 suggests relevant polar surface contribution.")
            if probability >= 0.7:
                interpretation = "strong_permeability_signal"
            elif probability >= 0.5:
                interpretation = "borderline_permeability_signal"
            else:
                interpretation = "non_permeability_signal"
            records.append(
                {
                    "row_index": int(idx),
                    "probability_permeable": probability,
                    "interpretation": interpretation,
                    "comments": comments,
                }
            )
        return AgentResult(self.name, "pass", {"records": records}, [])


class ReportAgent:
    name = "ReportAgent"

    @staticmethod
    def _dataframe_to_markdown(frame: pd.DataFrame) -> str:
        """Render a small Markdown table without requiring tabulate."""
        if frame.empty:
            return "_No rows to display._"
        text_frame = frame.copy()
        for column in text_frame.columns:
            text_frame[column] = text_frame[column].map(lambda value: "" if pd.isna(value) else str(value))
        headers = list(text_frame.columns)
        lines = [
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(["---"] * len(headers)) + " |",
        ]
        for row in text_frame.values.tolist():
            lines.append("| " + " | ".join(str(value).replace("\n", " ") for value in row) + " |")
        return "\n".join(lines)

    def run(
        self,
        frame: pd.DataFrame,
        predictions: pd.DataFrame,
        agent_results: list[AgentResult],
        id_column: str | None,
    ) -> tuple[pd.DataFrame, dict[str, Any], str]:
        row_report = predictions.copy()
        for result in agent_results:
            if result.agent == "ApplicabilityDomainAgent":
                domain = pd.DataFrame(result.payload.get("records", []))
                if not domain.empty:
                    domain = domain.set_index("row_index")
                    row_report["leverage"] = [domain.loc[idx, "leverage"] if idx in domain.index else np.nan for idx in row_report.index]
                    row_report["h_star"] = [domain.loc[idx, "h_star"] if idx in domain.index else np.nan for idx in row_report.index]
                    row_report["in_domain"] = [domain.loc[idx, "in_domain"] if idx in domain.index else None for idx in row_report.index]
            if result.agent == "PhysicsAgent":
                physics = pd.DataFrame(result.payload.get("records", []))
                if not physics.empty:
                    physics = physics.set_index("row_index")
                    row_report["physics_interpretation"] = [
                        physics.loc[idx, "interpretation"] if idx in physics.index else "" for idx in row_report.index
                    ]
                    row_report["physics_comments"] = [
                        "; ".join(physics.loc[idx, "comments"]) if idx in physics.index else "" for idx in row_report.index
                    ]
            if result.agent == "ChemicalAgent":
                chemical = pd.DataFrame(result.payload.get("records", []))
                if not chemical.empty:
                    chemical = chemical.set_index("row_index")
                    row_report["valid_smiles"] = [
                        chemical.loc[idx, "valid_smiles"] if idx in chemical.index else None for idx in row_report.index
                    ]
                    row_report["canonical_smiles"] = [
                        chemical.loc[idx, "canonical_smiles"] if idx in chemical.index else None for idx in row_report.index
                    ]
                    row_report["lipinski_pass"] = [
                        chemical.loc[idx, "lipinski"].get("pass") if idx in chemical.index and chemical.loc[idx, "lipinski"] else None
                        for idx in row_report.index
                    ]

        row_report["local_agent_decision"] = np.where(
            row_report["approved_for_decision"]
            & (row_report["predicted_label"].astype(int) == 1)
            & row_report.get("in_domain", pd.Series(True, index=row_report.index)).fillna(True).astype(bool),
            "CANDIDATE_PERMEABLE",
            "LOW_PRIORITY_OR_NON_PERMEABLE",
        )
        if "Actividad" in frame.columns:
            row_report["experimental_label"] = frame["Actividad"].values
        if id_column and id_column in frame.columns and id_column not in row_report.columns:
            row_report.insert(0, id_column, frame[id_column].values)

        summary = {
            "workflow": "local_no_api_agent_panel",
            "api_required": False,
            "row_count": int(len(frame)),
            "agents": [
                {
                    "agent": result.agent,
                    "status": result.status,
                    "warnings": result.warnings,
                }
                for result in agent_results
            ],
            "approved_predictions": int(row_report["approved_for_decision"].sum()),
            "predicted_permeable": int((row_report["predicted_label"].astype(int) == 1).sum()),
            "predicted_non_permeable": int((row_report["predicted_label"].astype(int) == 0).sum()),
        }
        markdown = self._markdown(summary, row_report)
        return row_report, summary, markdown

    @staticmethod
    def _markdown(summary: dict[str, Any], row_report: pd.DataFrame) -> str:
        lines = [
            "# Local PAMPA Agent Panel",
            "",
            "- API required: `False`",
            "- Model: `models/best_rf_pampa.pkl`",
            "- Mode: thesis 11-descriptor panel",
            f"- Rows: {summary['row_count']}",
            f"- Predicted permeable: {summary['predicted_permeable']}",
            f"- Predicted non-permeable: {summary['predicted_non_permeable']}",
            "",
            "## Agent Status",
            "",
        ]
        for agent in summary["agents"]:
            lines.append(f"- `{agent['agent']}`: {agent['status']}")
            for warning in agent["warnings"]:
                lines.append(f"  - Warning: {warning}")
        lines.extend(["", "## Predictions", ""])
        display_cols = [
            col
            for col in [
                "example_id",
                "name",
                "probability_permeable",
                "predicted_class",
                "in_domain",
                "physics_interpretation",
                "local_agent_decision",
            ]
            if col in row_report.columns
        ]
        if not display_cols:
            display_cols = ["probability_permeable", "predicted_class", "local_agent_decision"]
        lines.append(ReportAgent._dataframe_to_markdown(row_report[display_cols]))
        return "\n".join(lines) + "\n"


class LocalPampaOrchestrator:
    def __init__(self, model_path: Path, training_path: Path = DEFAULT_TRAINING):
        self.descriptor_agent = DescriptorAgent()
        self.chemical_agent = ChemicalAgent()
        self.model_agent = ModelAgent(model_path)
        self.domain_agent = ApplicabilityDomainAgent(training_path)
        self.physics_agent = PhysicsAgent()
        self.report_agent = ReportAgent()

    def run(self, frame: pd.DataFrame, smiles_column: str | None = None, id_column: str | None = None) -> tuple[pd.DataFrame, dict[str, Any], str]:
        smiles_column = detect_smiles_column(frame, smiles_column)
        results: list[AgentResult] = []

        descriptor_result = self.descriptor_agent.run(frame)
        results.append(descriptor_result)
        if descriptor_result.status == "fail":
            summary = {
                "workflow": "local_no_api_agent_panel",
                "api_required": False,
                "row_count": int(len(frame)),
                "agents": [{"agent": result.agent, "status": result.status, "warnings": result.warnings} for result in results],
                "approved_predictions": 0,
                "error": "Descriptor panel is incomplete.",
            }
            return pd.DataFrame(), summary, json.dumps(summary, indent=2, ensure_ascii=False)

        results.append(self.chemical_agent.run(frame, smiles_column))
        model_result = self.model_agent.run(frame, smiles_column, id_column)
        results.append(model_result)
        predictions = pd.DataFrame(model_result.payload["predictions"], index=frame.index)
        results.append(self.domain_agent.run(frame))
        results.append(self.physics_agent.run(frame, predictions))
        return self.report_agent.run(frame, predictions, results, id_column)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/agentic/local_agent_predictions.csv"))
    parser.add_argument("--report-json", type=Path, default=Path("results/agentic/local_agent_report.json"))
    parser.add_argument("--report-md", type=Path, default=Path("results/agentic/local_agent_report.md"))
    parser.add_argument("--model", type=Path, default=Path("models/best_rf_pampa.pkl"))
    parser.add_argument("--training", type=Path, default=DEFAULT_TRAINING)
    parser.add_argument("--smiles-column", default=None)
    parser.add_argument("--id-column", default=None)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    frame = read_table(args.input)
    orchestrator = LocalPampaOrchestrator(model_path=args.model, training_path=args.training)
    predictions, summary, markdown = orchestrator.run(frame, smiles_column=args.smiles_column, id_column=args.id_column)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.output, index=False)
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    args.report_md.parent.mkdir(parents=True, exist_ok=True)
    args.report_md.write_text(markdown, encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

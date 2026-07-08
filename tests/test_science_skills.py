from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.science_skills.pampa_computational_discovery import (
    THESIS_DESCRIPTORS,
    predict_descriptor_panel,
    smiles_only_report,
    validate_descriptor_panel,
)
from src.science_skills.pampa_literature_insights import audit_manuscript


def test_descriptor_contract_matches_thesis_csv() -> None:
    frame = pd.read_csv("data/raw/test_11.csv", nrows=3)
    validation = validate_descriptor_panel(frame)
    assert validation["valid"] is True
    assert validation["required_descriptors"] == THESIS_DESCRIPTORS


def test_predict_descriptor_panel_uses_thesis_model() -> None:
    frame = pd.read_csv("data/raw/test_11.csv", nrows=5)
    predictions, report = predict_descriptor_panel(frame)
    assert len(predictions) == 5
    assert predictions["approved_for_decision"].all()
    assert report["mode"] == "thesis_descriptor_panel"
    assert report["metrics_if_labels_present"] is not None


def test_smiles_only_report_blocks_exact_thesis_prediction() -> None:
    report = smiles_only_report(["CCO"])
    record = report["records"][0]
    assert record["valid"] is True
    assert record["approved_for_decision"] is False
    assert "SMILES alone is insufficient" in record["warning"]


def test_literature_audit_finds_undefined_citation(tmp_path: Path) -> None:
    tex = tmp_path / "paper.tex"
    bib = tmp_path / "refs.bib"
    tex.write_text(r"\cite{Known2020,Missing2021}", encoding="utf-8")
    bib.write_text(
        """
@article{Known2020,
  title = {Known paper},
  doi = {10.1000/example}
}
""",
        encoding="utf-8",
    )
    audit = audit_manuscript(tex, bib)
    assert audit["undefined_citations"] == ["Missing2021"]

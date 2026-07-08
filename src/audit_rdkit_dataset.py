"""Audit and rebuild the RDKit PAMPA dataset with corrected labels.

The source workbook ``dataset (7).xlsx`` stores a ``Target`` column with the
opposite convention of the thesis CSV files. The validated convention in this
project is:

* ``Act1`` -> 1, permeable
* ``Act-1`` -> 0, non-permeable
* ``Target_corrected = 1 - Target`` for the RDKit workbook
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
from rdkit import Chem


ACTIVITY_MAP = {"Act-1": 0, "Act1": 1}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("dataset (7).xlsx"))
    parser.add_argument("--sheet", default="Smiles")
    parser.add_argument("--training-11", type=Path, default=Path("data/raw/training_11.csv"))
    parser.add_argument("--test-11", type=Path, default=Path("data/raw/test_11.csv"))
    parser.add_argument("--external-11", type=Path, default=Path("data/raw/external_11.csv"))
    parser.add_argument(
        "--external-bridge",
        type=Path,
        default=Path("data/processed/external_bridge_reconstructed.csv"),
    )
    parser.add_argument(
        "--diagnostics-dir",
        type=Path,
        default=Path("results/diagnostics"),
    )
    parser.add_argument(
        "--original-output",
        type=Path,
        default=Path("data/processed/rdkit_original_split_corrected.csv"),
    )
    parser.add_argument(
        "--compound-output",
        type=Path,
        default=Path("data/processed/rdkit_pampa_compounds.csv"),
    )
    return parser


def canonicalize_smiles(smiles: Any) -> str | None:
    if pd.isna(smiles):
        return None
    mol = Chem.MolFromSmiles(str(smiles).strip())
    if mol is None:
        return None
    for atom in mol.GetAtoms():
        atom.SetIsotope(0)
    return Chem.MolToSmiles(mol, canonical=True)


def load_thesis_labels(path: Path) -> pd.Series:
    frame = pd.read_csv(path)
    if "Actividad" not in frame.columns:
        raise ValueError(f"{path} does not contain required column 'Actividad'.")
    labels = frame["Actividad"].map(ACTIVITY_MAP)
    if labels.isna().any():
        bad = sorted(frame.loc[labels.isna(), "Actividad"].astype(str).unique())
        raise ValueError(f"{path} contains unknown activity labels: {bad}")
    return labels.astype(int).reset_index(drop=True)


def validate_target_inversion(raw: pd.DataFrame, training_11: Path, test_11: Path) -> dict[str, Any]:
    corrected = (1 - raw["Target"].astype(int)).reset_index(drop=True)
    train_mask = raw["Type"].astype(str).eq("Train")
    test_mask = raw["Type"].astype(str).eq("Test")

    train_corrected = corrected.loc[train_mask].reset_index(drop=True)
    test_corrected = corrected.loc[test_mask].reset_index(drop=True)
    train_labels = load_thesis_labels(training_11)
    test_labels = load_thesis_labels(test_11)

    if len(train_corrected) != len(train_labels):
        raise ValueError(
            f"Training row-count mismatch: RDKit={len(train_corrected)} thesis={len(train_labels)}"
        )
    if len(test_corrected) != len(test_labels):
        raise ValueError(f"Test row-count mismatch: RDKit={len(test_corrected)} thesis={len(test_labels)}")

    train_mismatches = int((train_corrected != train_labels).sum())
    test_mismatches = int((test_corrected != test_labels).sum())
    if train_mismatches or test_mismatches:
        raise ValueError(
            "Target inversion validation failed: "
            f"train mismatches={train_mismatches}, test mismatches={test_mismatches}"
        )

    return {
        "target_rule": "Target_corrected = 1 - Target",
        "train_rows": int(len(train_corrected)),
        "test_rows": int(len(test_corrected)),
        "train_mismatches_after_inversion": train_mismatches,
        "test_mismatches_after_inversion": test_mismatches,
    }


def build_compound_level(original: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []

    for canonical, group in original.groupby("canonical_smiles", dropna=False):
        labels = group["Target_corrected"].astype(int).tolist()
        counts = Counter(labels)
        split_values = sorted(group["Type"].astype(str).unique())
        label_conflict = len(counts) > 1
        most_common = counts.most_common()
        top_label, top_count = most_common[0]
        tied = len(most_common) > 1 and most_common[0][1] == most_common[1][1]

        if tied:
            final_label = pd.NA
            training_use = False
        else:
            final_label = int(top_label)
            training_use = True

        row_count = int(len(group))
        if row_count > 1 or label_conflict or len(split_values) > 1:
            duplicates.append(
                {
                    "canonical_smiles": canonical,
                    "rows": row_count,
                    "splits": "|".join(split_values),
                    "labels": json.dumps(dict(counts), sort_keys=True),
                    "label_conflict": bool(label_conflict),
                    "tie_excluded": bool(tied),
                }
            )

        rows.append(
            {
                "canonical_smiles": canonical,
                "source_rows": row_count,
                "source_splits": "|".join(split_values),
                "label": final_label,
                "label_conflict": bool(label_conflict),
                "tie_excluded": bool(tied),
                "training_use": bool(training_use),
            }
        )

    compounds = pd.DataFrame(rows).sort_values("canonical_smiles").reset_index(drop=True)
    duplicate_report = pd.DataFrame(duplicates).sort_values(
        ["label_conflict", "rows", "canonical_smiles"],
        ascending=[False, False, True],
    )

    duplicated = original[original.duplicated("canonical_smiles", keep=False)]
    cross_split = (
        duplicated.groupby("canonical_smiles")["Type"]
        .nunique()
        .reset_index(name="n_splits")
        .query("n_splits > 1")
    )
    conflicts = (
        duplicated.groupby("canonical_smiles")["Target_corrected"]
        .nunique()
        .reset_index(name="n_labels")
        .query("n_labels > 1")
    )

    summary = {
        "compound_rows": int(len(compounds)),
        "training_use_rows": int(compounds["training_use"].sum()),
        "tie_excluded_rows": int(compounds["tie_excluded"].sum()),
        "duplicate_rows": int(len(duplicated)),
        "duplicate_groups": int(duplicated["canonical_smiles"].nunique()),
        "cross_split_duplicate_groups": int(len(cross_split)),
        "label_conflict_groups": int(len(conflicts)),
    }
    return compounds, duplicate_report, summary


def main() -> None:
    args = build_parser().parse_args()

    raw = pd.read_excel(args.input, sheet_name=args.sheet)
    required = {"smiles", "Target", "Type"}
    missing = required - set(raw.columns)
    if missing:
        raise SystemExit(f"Missing required columns in {args.input}: {sorted(missing)}")

    inversion = validate_target_inversion(raw, args.training_11, args.test_11)
    original = raw.copy()
    original["Target_corrected"] = 1 - original["Target"].astype(int)
    original["canonical_smiles"] = original["smiles"].map(canonicalize_smiles)
    invalid = original["canonical_smiles"].isna()
    if invalid.any():
        raise ValueError(f"Found {int(invalid.sum())} invalid SMILES in {args.input}.")

    compounds, duplicate_report, compound_summary = build_compound_level(original)

    external_summary: dict[str, Any] = {
        "external_11_exists": args.external_11.exists(),
        "external_bridge_exists": args.external_bridge.exists(),
    }
    if args.external_11.exists():
        external_summary["external_11_rows"] = int(len(pd.read_csv(args.external_11)))
    if args.external_bridge.exists():
        external_summary["external_bridge_rows"] = int(len(pd.read_csv(args.external_bridge)))

    summary = {
        "input": str(args.input),
        "sheet": args.sheet,
        "source_rows": int(len(original)),
        "type_counts": original["Type"].astype(str).value_counts().to_dict(),
        "target_counts_raw": original["Target"].astype(int).value_counts().sort_index().to_dict(),
        "target_counts_corrected": original["Target_corrected"].astype(int).value_counts().sort_index().to_dict(),
        "target_validation": inversion,
        "compound_level": compound_summary,
        "external": external_summary,
    }

    args.diagnostics_dir.mkdir(parents=True, exist_ok=True)
    args.original_output.parent.mkdir(parents=True, exist_ok=True)
    args.compound_output.parent.mkdir(parents=True, exist_ok=True)

    original.to_csv(args.original_output, index=False)
    compounds.to_csv(args.compound_output, index=False)
    duplicate_csv = args.diagnostics_dir / "rdkit_dataset_duplicates.csv"
    duplicate_report.to_csv(duplicate_csv, index=False)

    json_path = args.diagnostics_dir / "rdkit_dataset_audit.json"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_path = args.diagnostics_dir / "rdkit_dataset_audit.md"
    md_path.write_text(
        "\n".join(
            [
                "# RDKit Dataset Audit",
                "",
                f"- Source rows: {summary['source_rows']}",
                f"- Target rule: `{inversion['target_rule']}`",
                f"- Train mismatches after inversion: {inversion['train_mismatches_after_inversion']}",
                f"- Test mismatches after inversion: {inversion['test_mismatches_after_inversion']}",
                f"- Compound-level rows: {compound_summary['compound_rows']}",
                f"- Training-use compound rows: {compound_summary['training_use_rows']}",
                f"- Duplicate groups: {compound_summary['duplicate_groups']}",
                f"- Cross-split duplicate groups: {compound_summary['cross_split_duplicate_groups']}",
                f"- Label-conflict groups: {compound_summary['label_conflict_groups']}",
                f"- Tie-excluded rows: {compound_summary['tie_excluded_rows']}",
                "",
                "Generated files:",
                f"- `{args.original_output}`",
                f"- `{args.compound_output}`",
                f"- `{duplicate_csv}`",
                f"- `{json_path}`",
            ]
        ),
        encoding="utf-8",
    )

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

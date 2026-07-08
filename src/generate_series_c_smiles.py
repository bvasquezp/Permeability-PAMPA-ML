"""Backward-compatible wrapper for generating series C SMILES."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--r-groups", type=Path, default=None)
    parser.add_argument("--output-smiles", type=Path, default=Path("data/query/serie_C_preliminary_smiles.csv"))
    parser.add_argument("--output-triage", type=Path, default=Path("results/screening/serie_C_rdkit_triage.csv"))
    parser.add_argument("--output-template", type=Path, default=Path("data/query/serie_C_alvadesc_11_template.csv"))
    parser.add_argument("--output-figure", type=Path, default=Path("results/figures/serie_C_structures.png"))
    parser.add_argument("--output-report", type=Path, default=Path("results/screening/serie_C_smiles_generation_report.json"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    command = [
        sys.executable,
        "src/prepare_candidate_smiles.py",
        "--output-prefix",
        "serie_C",
        "--output-smiles",
        str(args.output_smiles),
        "--output-triage",
        str(args.output_triage),
        "--output-template",
        str(args.output_template),
        "--output-figure",
        str(args.output_figure),
        "--output-report",
        str(args.output_report),
    ]
    if args.r_groups:
        command.extend(["--input", str(args.r_groups)])
    else:
        default_input = Path("data/query/serie_C_default_r_groups.csv")
        default_input.parent.mkdir(parents=True, exist_ok=True)
        default_input.write_text(
            "compound_id,series,scaffold,r_group,yield_percent,substituent\n"
            "C1,C,C,4-F,40,F\n"
            "C2,C,C,4-Cl,61,Cl\n"
            "C3,C,C,4-Br,55,Br\n"
            "C4,C,C,4-I,52,I\n",
            encoding="utf-8",
        )
        command.extend(["--input", str(default_input)])
    subprocess.run(command, check=True)


if __name__ == "__main__":
    main()

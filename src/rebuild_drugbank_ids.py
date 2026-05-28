"""Rebuild the MoleculeN to DrugBank ID table from an SDF file."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def rebuild_ids(sdf_path: Path, output_csv: Path) -> int:
    text = sdf_path.read_text(encoding="utf-8", errors="replace")
    records = text.split("$$$$")
    rows = []
    for index, record in enumerate(records, start=1):
        match = re.search(r">\s*<DRUGBANK_ID>\s*\n\s*(DB\d+)\s*\n", record)
        if match:
            rows.append((index, match.group(1)))

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Orden", "DrugBank_ID"])
        writer.writerows(rows)
    return len(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdf", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    count = rebuild_ids(args.sdf, args.output)
    print(f"Wrote {count} DrugBank IDs to {args.output}")


if __name__ == "__main__":
    main()

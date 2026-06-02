"""Build a data-lineage manifest for core PAMPA QSAR artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd


DEFAULT_PATHS = [
    Path("data/raw/training_11.csv"),
    Path("data/raw/test_11.csv"),
    Path("data/raw/external_11.csv"),
    Path("data/raw/training_50.csv"),
    Path("data/raw/test_50.csv"),
    Path("data/raw/external_50.csv"),
    Path("data/processed/train_11_processed.csv"),
    Path("data/processed/test_11_processed.csv"),
    Path("data/processed/external_11_processed.csv"),
    Path("models/best_rf_pampa.pkl"),
    Path("results/metrics/evaluacion_final_datasets.csv"),
    Path("results/metrics/cv_results_comparison.csv"),
    Path("results/screening/Pre_Cribado_5_Moleculas.csv"),
    Path("results/screening/Reporte_Lipinski_Candidatos.csv"),
    Path("results/screening/DrugBank_Candidatos_Tesis.csv"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def csv_shape(path: Path) -> tuple[int | None, int | None]:
    if path.suffix.lower() != ".csv":
        return None, None
    data = pd.read_csv(path)
    return int(data.shape[0]), int(data.shape[1])


def build_manifest(paths: Iterable[Path]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in paths:
        record: dict[str, object] = {
            "path": path.as_posix(),
            "exists": path.exists(),
            "size_bytes": None,
            "sha256": None,
            "rows": None,
            "columns": None,
        }
        if path.exists():
            record["size_bytes"] = path.stat().st_size
            record["sha256"] = sha256(path)
            rows_count, columns_count = csv_shape(path)
            record["rows"] = rows_count
            record["columns"] = columns_count
        rows.append(record)
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--paths",
        nargs="*",
        default=DEFAULT_PATHS,
        type=Path,
        help="Files to include in the manifest.",
    )
    parser.add_argument(
        "--output-json",
        default=Path("results/pipeline/data_manifest.json"),
        type=Path,
    )
    parser.add_argument(
        "--output-csv",
        default=Path("results/pipeline/data_manifest.csv"),
        type=Path,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    manifest = build_manifest(args.paths)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "artifact_count": len(manifest),
        "artifacts": manifest,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    pd.DataFrame(manifest).to_csv(args.output_csv, index=False)

    missing = [row["path"] for row in manifest if not row["exists"]]
    if missing:
        raise SystemExit(f"Missing manifest artifacts: {missing}")

    print(f"[OK] Data manifest written to {args.output_json} and {args.output_csv}")


if __name__ == "__main__":
    main()

"""Run the reproducibility pipeline used by the PAMPA QSAR project."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def run_step(name: str, command: list[str]) -> dict[str, object]:
    print(f"\n=== {name} ===")
    print(" ".join(command))
    start = time.perf_counter()
    completed = subprocess.run(command, check=False)
    duration = time.perf_counter() - start
    record = {
        "name": name,
        "command": command,
        "returncode": completed.returncode,
        "duration_seconds": round(duration, 3),
    }
    if completed.returncode != 0:
        raise SystemExit(f"Pipeline step failed: {name}")
    return record


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-model-comparison", action="store_true")
    parser.add_argument("--skip-manuscript-assets", action="store_true")
    parser.add_argument("--mlflow-preview", action="store_true")
    parser.add_argument(
        "--report",
        default=Path("results/pipeline/pipeline_run.json"),
        type=Path,
        help="JSON report with executed steps and durations.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    python = sys.executable
    steps: list[tuple[str, list[str]]] = [
        ("data_manifest", [python, "src/build_data_manifest.py"]),
        ("validate_project", [python, "src/validate_project.py"]),
        ("reproduce_final_metrics", [python, "src/check_final_metrics.py"]),
    ]

    if not args.skip_model_comparison:
        steps.append(
            (
                "compare_models",
                [
                    python,
                    "src/evaluate_models.py",
                    "--dataset",
                    "data/raw/training_11.csv",
                    "--output",
                    "results/metrics/model_comparison.csv",
                ],
            )
        )

    if args.mlflow_preview:
        steps.append(("mlflow_payload_preview", [python, "src/mlflow_tracking.py", "--dry-run"]))

    if not args.skip_manuscript_assets:
        steps.extend(
            [
                ("generate_manuscript_assets", [python, "manuscript/generate_python_assets.py"]),
                ("build_manuscript_docx", [python, "manuscript/build_docx_with_assets.py"]),
            ]
        )

    executed = [run_step(name, command) for name, command in steps]
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": python,
        "steps": executed,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\n[OK] Pipeline completed. Report written to {args.report}")


if __name__ == "__main__":
    main()

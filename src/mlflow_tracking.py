"""Log the reproducible PAMPA QSAR run to MLflow, or preview the payload."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from check_final_metrics import compute_metrics


DEFAULT_ARTIFACTS = [
    Path("models/best_rf_pampa.pkl"),
    Path("results/metrics/evaluacion_final_datasets.csv"),
    Path("results/metrics/cv_results_comparison.csv"),
    Path("results/metrics/model_comparison.csv"),
    Path("results/screening/Pre_Cribado_5_Moleculas.csv"),
    Path("results/screening/DrugBank_Candidatos_Tesis.csv"),
    Path("results/pipeline/data_manifest.json"),
]


def sanitize_metric_name(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def load_params(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        return {}
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def flatten_params(data: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        name = f"{prefix}.{key}" if prefix else str(key)
        if isinstance(value, dict):
            flattened.update(flatten_params(value, name))
        elif isinstance(value, list):
            flattened[name] = ",".join(str(item) for item in value)
        else:
            flattened[name] = value
    return flattened


def build_payload(model_path: Path, params_path: Path) -> dict[str, Any]:
    metrics = compute_metrics(model_path)
    metric_payload: dict[str, float] = {}
    for dataset_name, row in metrics.iterrows():
        dataset_key = sanitize_metric_name(str(dataset_name))
        for metric_name, value in row.items():
            metric_key = sanitize_metric_name(str(metric_name))
            metric_payload[f"{dataset_key}_{metric_key}"] = float(value)

    params = flatten_params(load_params(params_path))
    if not params:
        params = {
            "model.path": model_path.as_posix(),
            "validation.metric_tolerance": 0.001,
            "validation.cv_folds": 10,
            "screening.probability_threshold": 0.60,
        }

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "params": params,
        "metrics": metric_payload,
        "artifacts": [artifact.as_posix() for artifact in DEFAULT_ARTIFACTS if artifact.exists()],
    }


def write_preview(payload: dict[str, Any], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[OK] MLflow payload preview written to {output}")
    print(pd.Series(payload["metrics"]).round(3).to_string())


def log_to_mlflow(payload: dict[str, Any], tracking_uri: str, experiment_name: str) -> None:
    try:
        import mlflow
    except ImportError as exc:
        raise SystemExit(
            "MLflow is not installed. Install optional MLOps dependencies with "
            "`python -m pip install -r requirements-mlops.txt`, or run with --dry-run."
        ) from exc

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run(run_name="pampa_qsar_reproducibility") as run:
        for key, value in payload["params"].items():
            mlflow.log_param(key, value)
        for key, value in payload["metrics"].items():
            mlflow.log_metric(key, value)
        for artifact in payload["artifacts"]:
            path = Path(artifact)
            if path.exists():
                mlflow.log_artifact(str(path))
        print(f"[OK] Logged MLflow run {run.info.run_id} in experiment {experiment_name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default=Path("models/best_rf_pampa.pkl"), type=Path)
    parser.add_argument("--params", default=Path("params.yaml"), type=Path)
    parser.add_argument("--tracking-uri", default="mlruns")
    parser.add_argument("--experiment-name", default="pampa_qsar_reproducibility")
    parser.add_argument("--dry-run", action="store_true", help="Write the MLflow payload without requiring MLflow.")
    parser.add_argument(
        "--preview-output",
        default=Path("results/mlflow/mlflow_payload_preview.json"),
        type=Path,
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = build_payload(args.model, args.params)
    if args.dry_run:
        write_preview(payload, args.preview_output)
    else:
        log_to_mlflow(payload, args.tracking_uri, args.experiment_name)


if __name__ == "__main__":
    main()

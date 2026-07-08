"""Screen one or more SMILES strings through the PAMPA surrogate workflow."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.agentic.mcp_server import evaluate_screening_candidate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate candidate molecules with the PAMPA surrogate Random Forest, "
            "Lipinski rules and applicability-domain leverage."
        )
    )
    parser.add_argument(
        "smiles",
        nargs="*",
        help="One or more SMILES strings to evaluate.",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Optional CSV file containing a SMILES column.",
    )
    parser.add_argument(
        "--smiles-column",
        default="smiles",
        help="Name of the SMILES column when using --csv (default: smiles).",
    )
    parser.add_argument(
        "--id-column",
        default=None,
        help="Optional identifier column to carry through to the output table.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional CSV output path for the screening results.",
    )
    parser.add_argument(
        "--model-path",
        type=Path,
        default=None,
        help="Optional model payload path to evaluate against instead of the default surrogate.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the full result payload as JSON instead of a compact table.",
    )
    return parser


def load_smiles(args: argparse.Namespace) -> pd.DataFrame:
    if args.csv:
        df = pd.read_csv(args.csv)
        if args.smiles_column not in df.columns:
            raise SystemExit(
                f"Column '{args.smiles_column}' was not found in {args.csv}. "
                f"Available columns: {', '.join(df.columns)}"
            )
        keep_cols = [args.smiles_column]
        if args.id_column and args.id_column in df.columns:
            keep_cols.insert(0, args.id_column)
        elif args.id_column:
            raise SystemExit(
                f"Column '{args.id_column}' was not found in {args.csv}. "
                f"Available columns: {', '.join(df.columns)}"
            )
        work = df[keep_cols].copy()
    else:
        work = pd.DataFrame({args.smiles_column: [s.strip() for s in args.smiles if s.strip()]})

    work = work.dropna(subset=[args.smiles_column])
    work[args.smiles_column] = work[args.smiles_column].astype(str).str.strip()
    work = work[work[args.smiles_column] != ""]

    if work.empty:
        raise SystemExit("No SMILES were provided.")
    return work


def flatten_result(result: dict) -> dict:
    if "error" in result:
        return {"error": result["error"], "smiles": result.get("smiles", "")}

    return {
        "name": result.get("name", ""),
        "smiles": result.get("smiles", ""),
        "prediction": result.get("prediction", ""),
        "probability": result.get("probability", None),
        "candidate_status": result.get("candidate_status", ""),
        "lipinski_pass": result.get("lipinski", {}).get("pass", None),
        "lipinski_violations": result.get("lipinski", {}).get("violations", None),
        "mw": result.get("lipinski", {}).get("mw", None),
        "logp": result.get("lipinski", {}).get("logp", None),
        "hbd": result.get("lipinski", {}).get("hbd", None),
        "hba": result.get("lipinski", {}).get("hba", None),
        "leverage": result.get("applicability_domain", {}).get("leverage", None),
        "h_star": result.get("applicability_domain", {}).get("h_star", None),
        "in_domain": result.get("applicability_domain", {}).get("in_domain", None),
    }


def main() -> None:
    args = build_parser().parse_args()
    if args.model_path:
        os.environ["PAMPA_MODEL_PATH"] = str(args.model_path)
    frame = load_smiles(args)

    if args.csv and args.id_column and args.id_column in frame.columns:
        pairs = list(frame[[args.id_column, args.smiles_column]].itertuples(index=False, name=None))
    else:
        pairs = [(None, smiles) for smiles in frame[args.smiles_column].tolist()]

    results = []
    for record_id, smiles in pairs:
        result = evaluate_screening_candidate(smiles)
        if record_id is not None and "error" not in result:
            result["name"] = record_id
        results.append(result)

    if args.output:
        pd.DataFrame([flatten_result(result) for result in results]).to_csv(args.output, index=False)
        print(args.output.resolve())

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    rows = [flatten_result(result) for result in results]
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()

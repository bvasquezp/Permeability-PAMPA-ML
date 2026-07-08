"""Merge alvaDesc descriptor exports into the 11-descriptor PAMPA model panel."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


THESIS_DESCRIPTORS = [
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

DEFAULT_COMPOUND_IDS = [
    "A1",
    "A2",
    "A3",
    "A4",
    "A5",
    "A6",
    "B1",
    "B2",
    "B3",
    "B4",
    "B5",
    "B6",
    "B7",
    "B8",
    "C1",
    "C2",
    "C3",
    "C4",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--descriptors", type=Path, required=True, help="alvaDesc 0D/2D descriptor TXT export.")
    parser.add_argument("--maccs", type=Path, required=True, help="alvaDesc MACCS fingerprint TXT export.")
    parser.add_argument(
        "--ids",
        type=Path,
        default=None,
        help="Optional CSV with compound_id in the same order as alvaDesc rows.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/query/candidate_compounds_alvadesc_11_from_exports.csv"),
    )
    parser.add_argument(
        "--merged-output",
        type=Path,
        default=Path("data/query/candidate_compounds_alvadesc_merged_full.csv"),
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("results/screening/candidate_compounds_alvadesc_merge_report.json"),
    )
    return parser


def read_alvadesc_txt(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, sep="\t")
    required = {"No.", "NAME"}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"{path} is missing required columns: {missing}")
    return frame


def load_compound_ids(path: Path | None, n_rows: int) -> list[str]:
    if path is None:
        if n_rows != len(DEFAULT_COMPOUND_IDS):
            raise ValueError(
                f"No --ids provided and row count is {n_rows}; default A/B/C mapping requires "
                f"{len(DEFAULT_COMPOUND_IDS)} rows."
            )
        return DEFAULT_COMPOUND_IDS
    frame = pd.read_csv(path)
    if "compound_id" not in frame.columns:
        raise ValueError("--ids CSV must include a compound_id column.")
    ids = frame["compound_id"].astype(str).tolist()
    if len(ids) != n_rows:
        raise ValueError(f"--ids has {len(ids)} rows but alvaDesc export has {n_rows} rows.")
    return ids


def main() -> None:
    args = build_parser().parse_args()
    descriptors = read_alvadesc_txt(args.descriptors)
    maccs = read_alvadesc_txt(args.maccs)

    key = ["No.", "NAME"]
    if descriptors[key].astype(str).agg("|".join, axis=1).tolist() != maccs[key].astype(str).agg("|".join, axis=1).tolist():
        raise ValueError("Descriptor and MACCS exports do not have identical No./NAME row order.")

    merged = descriptors.merge(maccs, on=key, how="inner", validate="one_to_one")
    if len(merged) != len(descriptors):
        raise ValueError("Merge changed row count; check alvaDesc export files.")

    missing_descriptors = [name for name in THESIS_DESCRIPTORS if name not in merged.columns]
    if missing_descriptors:
        raise ValueError(f"Missing thesis descriptors after merge: {missing_descriptors}")

    compound_ids = load_compound_ids(args.ids, len(merged))
    panel = pd.DataFrame({"compound_id": compound_ids, "alvadesc_name": merged["NAME"]})
    for descriptor in THESIS_DESCRIPTORS:
        panel[descriptor] = pd.to_numeric(merged[descriptor], errors="raise")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.merged_output.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(args.output, index=False)
    merged.insert(2, "compound_id", compound_ids)
    merged.to_csv(args.merged_output, index=False)

    report = {
        "records": int(len(panel)),
        "descriptor_source": str(args.descriptors),
        "maccs_source": str(args.maccs),
        "output": str(args.output),
        "merged_output": str(args.merged_output),
        "compound_id_mapping": "provided_by_ids_csv" if args.ids else "default_A1-A6_B1-B8_C1-C4_order",
        "required_descriptors": THESIS_DESCRIPTORS,
        "missing_descriptors": missing_descriptors,
    }
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

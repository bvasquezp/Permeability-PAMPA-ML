"""Compare the thesis 11-descriptor panel against the RDKit+EDA surrogate panel."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--final-metrics",
        default=Path("results/metrics/evaluacion_final_datasets.csv"),
        type=Path,
    )
    parser.add_argument(
        "--eda-metrics",
        default=Path("results/metrics/surrogate_eda_metrics.csv"),
        type=Path,
    )
    parser.add_argument(
        "--final-features",
        default=Path("data/raw/external_11.csv"),
        type=Path,
    )
    parser.add_argument(
        "--eda-features",
        default=Path("results/feature_selection/rdkit_eda_selected_features.csv"),
        type=Path,
    )
    return parser


def load_feature_names(path: Path) -> list[str]:
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
        if "Descriptor" in df.columns:
            return df["Descriptor"].dropna().astype(str).tolist()
        return [c for c in df.columns if c != "Actividad" and c != "Target"]
    raise ValueError(f"Unsupported feature file: {path}")


def main() -> None:
    args = build_parser().parse_args()

    final_metrics = pd.read_csv(args.final_metrics).set_index("Dataset")
    eda_metrics = pd.read_csv(args.eda_metrics).set_index("Dataset")

    final_panel = [
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
    eda_panel = load_feature_names(args.eda_features)
    external_frame = pd.read_csv(args.final_features)
    external_missing = [feature for feature in final_panel if feature not in external_frame.columns]
    external_class_counts = (
        external_frame["Actividad"].value_counts(dropna=False).to_dict()
        if "Actividad" in external_frame.columns
        else {}
    )

    overlap = [feature for feature in eda_panel if feature in final_panel]

    print("Thesis final panel (11 descriptors):")
    print(", ".join(final_panel))
    print("\nRDKit+EDA panel (11 descriptors):")
    print(", ".join(eda_panel))
    print("\nExact overlap:")
    print(", ".join(overlap) if overlap else "(none)")

    print("\nThesis panel in external dataset:")
    print("all present" if not external_missing else f"missing: {', '.join(external_missing)}")
    if external_class_counts:
        print("external class counts:")
        print(external_class_counts)

    print("\nFinal model external validation:")
    print(final_metrics.loc["Validacion Externa"].to_string())

    print("\nRDKit+EDA surrogate internal test:")
    print(eda_metrics.loc["Test Interno (EDA Surrogate)"].to_string())

    print("\nInterpretation:")
    print(
        "The external validation already uses the thesis panel of 11 descriptors. "
        "The RDKit+EDA surrogate is a different 11-variable panel, so descriptor-level "
        "comparison is not one-to-one. For a fair external comparison of the RDKit panel, "
        "we would need the external compounds' SMILES to recompute the same RDKit features."
    )


if __name__ == "__main__":
    main()

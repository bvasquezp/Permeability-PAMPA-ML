"""Prepare candidate molecules for PAMPA screening.

Input can contain either:

- `smiles`: direct structure input for any compound.
- `scaffold` + `substituent`: scaffold templates for series B/C from
  `compuestos.pdf`.

The script validates structures, computes RDKit/Lipinski triage, generates a
structure figure, and writes an alvaDesc/WEKA 11-descriptor template for the
validated thesis PAMPA model.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, Draw, Lipinski

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.pampa_core import lipinski_summary, validate_smiles


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

DEFAULT_ABC = [
    {"compound_id": "A1", "series": "A", "scaffold": "A", "r_group": "N(CH3)2", "yield_percent": 66, "substituent": "N(CH3)2"},
    {"compound_id": "A2", "series": "A", "scaffold": "A", "r_group": "pyrrolidine", "yield_percent": 87, "substituent": "pyrrolidine"},
    {"compound_id": "A3", "series": "A", "scaffold": "A", "r_group": "piperidine", "yield_percent": 53, "substituent": "piperidine"},
    {"compound_id": "A4", "series": "A", "scaffold": "A", "r_group": "morpholine", "yield_percent": 47, "substituent": "morpholine"},
    {"compound_id": "A5", "series": "A", "scaffold": "A", "r_group": "piperazine", "yield_percent": 45, "substituent": "piperazine"},
    {"compound_id": "A6", "series": "A", "scaffold": "A", "r_group": "thiomorpholine", "yield_percent": 17, "substituent": "thiomorpholine"},
    {"compound_id": "B1", "series": "B", "scaffold": "B", "r_group": "4-F", "yield_percent": 93, "substituent": "F"},
    {"compound_id": "B2", "series": "B", "scaffold": "B", "r_group": "4-Cl", "yield_percent": 96, "substituent": "Cl"},
    {"compound_id": "B3", "series": "B", "scaffold": "B", "r_group": "4-Br", "yield_percent": 87, "substituent": "Br"},
    {"compound_id": "B4", "series": "B", "scaffold": "B", "r_group": "4-I", "yield_percent": 92, "substituent": "I"},
    {"compound_id": "B5", "series": "B", "scaffold": "B", "r_group": "4-H", "yield_percent": 93, "substituent": "H"},
    {"compound_id": "B6", "series": "B", "scaffold": "B", "r_group": "4-OCH3", "yield_percent": 41, "substituent": "OCH3"},
    {"compound_id": "B7", "series": "B", "scaffold": "B", "r_group": "4-N(CH3)2", "yield_percent": 25, "substituent": "N(CH3)2"},
    {
        "compound_id": "B8",
        "series": "B",
        "smiles": "Cc1noc(/C=C/c2ccc(-c3ccc(N(c4ccccc4)c4ccccc4)cc3)cc2)c1[N+](=O)[O-]",
        "r_group": "4-(4-diphenylaminophenyl)",
        "yield_percent": 19,
        "source": "direct preliminary SMILES interpreted from compuestos.pdf scheme 2; confirm against original structure",
    },
    {"compound_id": "C1", "series": "C", "scaffold": "C", "r_group": "4-F", "yield_percent": 40, "substituent": "F"},
    {"compound_id": "C2", "series": "C", "scaffold": "C", "r_group": "4-Cl", "yield_percent": 61, "substituent": "Cl"},
    {"compound_id": "C3", "series": "C", "scaffold": "C", "r_group": "4-Br", "yield_percent": 55, "substituent": "Br"},
    {"compound_id": "C4", "series": "C", "scaffold": "C", "r_group": "4-I", "yield_percent": 52, "substituent": "I"},
]


SUBSTITUENT_SMARTS = {
    "F": "F",
    "Cl": "Cl",
    "Br": "Br",
    "I": "I",
    "H": "[H]",
    "OCH3": "OC",
    "N(CH3)2": "N(C)C",
}

A_SERIES_SMILES = {
    "N(CH3)2": "CN(C)/C=C/c1onc(C)c([N+](=O)[O-])1",
    "pyrrolidine": "C1CCN(/C=C/c2onc(C)c([N+](=O)[O-])2)C1",
    "piperidine": "C1CCN(/C=C/c2onc(C)c([N+](=O)[O-])2)CC1",
    "morpholine": "C1COCCN1/C=C/c2onc(C)c([N+](=O)[O-])2",
    "piperazine": "C1CNCCN1/C=C/c2onc(C)c([N+](=O)[O-])2",
    "thiomorpholine": "C1CSCCN1/C=C/c2onc(C)c([N+](=O)[O-])2",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help=(
            "Optional CSV. For generic compounds include compound_id and smiles. "
            "For scaffold mode include compound_id, scaffold and substituent."
        ),
    )
    parser.add_argument("--output-prefix", default="series_BC", help="Prefix used for default output filenames.")
    parser.add_argument("--output-smiles", type=Path, default=None)
    parser.add_argument("--output-triage", type=Path, default=None)
    parser.add_argument("--output-template", type=Path, default=None)
    parser.add_argument("--output-figure", type=Path, default=None)
    parser.add_argument("--output-report", type=Path, default=None)
    return parser


def default_path(path: Path | None, fallback: str) -> Path:
    return path if path is not None else Path(fallback)


def load_input(path: Path | None) -> pd.DataFrame:
    if path is None:
        return pd.DataFrame(DEFAULT_ABC)
    frame = pd.read_csv(path)
    if "compound_id" not in frame.columns:
        raise ValueError("Input CSV must include compound_id.")
    if "scaffold" not in frame.columns and "series" in frame.columns:
        frame["scaffold"] = frame["series"]

    has_smiles = "smiles" in frame.columns
    if has_smiles:
        smiles_present = frame["smiles"].notna() & frame["smiles"].astype(str).str.strip().ne("")
    else:
        smiles_present = pd.Series(False, index=frame.index)

    scaffold_required = ~smiles_present
    missing = []
    for column in ["scaffold", "substituent"]:
        if column not in frame.columns and scaffold_required.any():
            missing.append(column)
    if missing:
        raise ValueError(f"Rows without smiles must include scaffold/substituent. Missing: {missing}")

    if scaffold_required.any():
        empty_scaffold = frame.loc[scaffold_required, "scaffold"].isna() | frame.loc[scaffold_required, "scaffold"].astype(str).str.strip().eq("")
        empty_substituent = frame.loc[scaffold_required, "substituent"].isna() | frame.loc[scaffold_required, "substituent"].astype(str).str.strip().eq("")
        if empty_scaffold.any() or empty_substituent.any():
            bad_rows = frame.loc[scaffold_required].index[empty_scaffold | empty_substituent].tolist()
            raise ValueError(f"Rows without smiles need non-empty scaffold and substituent. Bad row indexes: {bad_rows}")
    return frame


def scaffold_smiles(scaffold: str, substituent: str) -> str:
    scaffold = str(scaffold).strip().upper()
    substituent = str(substituent).strip()
    if scaffold == "A":
        if substituent not in A_SERIES_SMILES:
            raise ValueError(
                f"Unsupported series A substituent '{substituent}'. Supported: {sorted(A_SERIES_SMILES)}"
            )
        return A_SERIES_SMILES[substituent]
    if substituent not in SUBSTITUENT_SMARTS:
        raise ValueError(f"Unsupported substituent '{substituent}'. Add it to SUBSTITUENT_SMARTS.")
    para = SUBSTITUENT_SMARTS[substituent]
    if scaffold == "B":
        return f"Cc1noc(/C=C/c2ccc({para})cc2)c1[N+](=O)[O-]"
    if scaffold == "C":
        return f"Cc1noc(/C=C/c2ccc({para})cc2)c1N"
    raise ValueError(f"Unsupported scaffold '{scaffold}'. Supported scaffolds: A, B, C.")


def build_smiles_table(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame.copy()
    preliminary = []
    sources = []
    for _, row in work.iterrows():
        smiles = row.get("smiles", None)
        if pd.notna(smiles) and str(smiles).strip():
            preliminary.append(str(smiles).strip())
            sources.append(row.get("source", "direct input SMILES"))
        else:
            preliminary.append(scaffold_smiles(row.get("scaffold"), row.get("substituent")))
            sources.append(row.get("source", "scaffold template encoded in src/prepare_candidate_smiles.py"))
    work["preliminary_smiles"] = preliminary
    work["source"] = sources
    for optional in ["series", "r_group", "yield_percent", "scaffold", "substituent"]:
        if optional not in work.columns:
            work[optional] = ""
    columns = [
        "compound_id",
        "series",
        "scaffold",
        "r_group",
        "substituent",
        "yield_percent",
        "preliminary_smiles",
        "source",
    ]
    return work[columns].copy()


def triage_record(row: pd.Series) -> dict[str, Any]:
    smiles = row["preliminary_smiles"]
    validation = validate_smiles(smiles)
    mol = Chem.MolFromSmiles(validation["canonical_smiles"]) if validation["valid"] else None
    lipinski = lipinski_summary(smiles) if validation["valid"] else {}
    return {
        **row.to_dict(),
        "valid_smiles": bool(validation["valid"]),
        "canonical_smiles": validation["canonical_smiles"],
        "mw": lipinski.get("mw"),
        "logp": lipinski.get("logp"),
        "tpsa": round(float(Descriptors.TPSA(mol)), 3) if mol else None,
        "hbd": lipinski.get("hbd"),
        "hba": lipinski.get("hba"),
        "rotatable_bonds": int(Lipinski.NumRotatableBonds(mol)) if mol else None,
        "heavy_atoms": int(mol.GetNumHeavyAtoms()) if mol else None,
        "lipinski_violations": lipinski.get("violations"),
        "lipinski_pass": lipinski.get("pass"),
    }


def write_alvadesc_template(smiles: pd.DataFrame, path: Path) -> None:
    template = smiles[["compound_id", "preliminary_smiles"]].copy()
    for descriptor in THESIS_DESCRIPTORS:
        template[descriptor] = ""
    path.parent.mkdir(parents=True, exist_ok=True)
    template.to_csv(path, index=False)


def write_figure(smiles: pd.DataFrame, path: Path) -> None:
    valid = smiles[smiles["preliminary_smiles"].map(lambda value: Chem.MolFromSmiles(str(value)) is not None)]
    if valid.empty:
        return
    mols = [Chem.MolFromSmiles(value) for value in valid["preliminary_smiles"]]
    legends = [str(row.compound_id) for row in valid.itertuples()]
    image = Draw.MolsToGridImage(mols, molsPerRow=4, subImgSize=(260, 220), legends=legends)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def main() -> None:
    args = build_parser().parse_args()
    prefix = args.output_prefix
    output_smiles = default_path(args.output_smiles, f"data/query/{prefix}_preliminary_smiles.csv")
    output_triage = default_path(args.output_triage, f"results/screening/{prefix}_rdkit_triage.csv")
    output_template = default_path(args.output_template, f"data/query/{prefix}_alvadesc_11_template.csv")
    output_figure = default_path(args.output_figure, f"results/figures/{prefix}_structures.png")
    output_report = default_path(args.output_report, f"results/screening/{prefix}_preparation_report.json")

    frame = load_input(args.input)
    smiles = build_smiles_table(frame)
    output_smiles.parent.mkdir(parents=True, exist_ok=True)
    smiles.to_csv(output_smiles, index=False)

    triage = pd.DataFrame([triage_record(row) for _, row in smiles.iterrows()])
    output_triage.parent.mkdir(parents=True, exist_ok=True)
    triage.to_csv(output_triage, index=False)

    write_alvadesc_template(smiles, output_template)
    write_figure(smiles, output_figure)

    report = {
        "mode": "candidate_smiles_preparation",
        "records": int(len(smiles)),
        "valid_smiles": int(triage["valid_smiles"].sum()),
        "outputs": {
            "smiles": str(output_smiles),
            "triage": str(output_triage),
            "alvadesc_template": str(output_template),
            "figure": str(output_figure),
        },
        "warning": (
            "Template-generated SMILES should be confirmed against original MOL/SDF/ChemDraw structures "
            "before final experimental decisions. The thesis PAMPA model still requires the 11 alvaDesc/WEKA descriptors."
        ),
    }
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_report.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

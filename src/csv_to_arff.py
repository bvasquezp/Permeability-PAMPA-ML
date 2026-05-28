"""Convert CSV datasets to ARFF files for WEKA."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def _clean_attribute_name(name: str) -> str:
    return (
        str(name)
        .strip()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace("[", "")
        .replace("]", "")
        .replace("/", "_")
    )


def read_csv_auto(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if df.shape[1] == 1:
        df = pd.read_csv(path, sep=";")
    return df


def csv_to_arff(csv_path: Path, arff_path: Path, relation: str) -> None:
    df = read_csv_auto(csv_path)
    arff_path.parent.mkdir(parents=True, exist_ok=True)

    with arff_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(f"@relation {relation}\n\n")

        for column in df.columns:
            name = _clean_attribute_name(column)
            if pd.api.types.is_numeric_dtype(df[column]):
                handle.write(f"@attribute {name} numeric\n")
                continue

            values = [
                str(value).replace("'", "").replace('"', "").replace(",", "_")
                for value in pd.Series(df[column].dropna().unique()).sort_values()
            ]
            handle.write(f"@attribute {name} {{{','.join(values)}}}\n")

        handle.write("\n@data\n")
        for _, row in df.iterrows():
            values = []
            for value in row:
                if pd.isna(value):
                    values.append("?")
                else:
                    values.append(str(value).replace(",", "_"))
            handle.write(",".join(values) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path, help="Input CSV file.")
    parser.add_argument("arff", type=Path, help="Output ARFF file.")
    parser.add_argument("--relation", default="pampa_dataset", help="WEKA relation name.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    csv_to_arff(args.csv, args.arff, args.relation)
    print(f"ARFF written to {args.arff}")


if __name__ == "__main__":
    main()

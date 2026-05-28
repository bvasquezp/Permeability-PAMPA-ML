"""Validate core files required to reproduce the PAMPA QSAR workflow."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class FileCheck:
    path: Path
    rows: int | None
    columns: int | None
    sha256: str


CHECKS = [
    FileCheck(
        Path("data/raw/training_11.csv"),
        4357,
        12,
        "fe73947fc0244441c4ec0eb2a772ed9557a235b77aeb461bcd03485a0ff2a398",
    ),
    FileCheck(
        Path("data/raw/test_11.csv"),
        1090,
        12,
        "7848b86e9d681d0b7c1486e3a07b692f7c763cbf182cc3b8ac1fe8f5df3b4d40",
    ),
    FileCheck(
        Path("data/raw/external_11.csv"),
        486,
        12,
        "71ea363dcb399a2b2da111096a18e4e3ef7cc9cd15a5c40a91c3ba771f696a25",
    ),
    FileCheck(
        Path("data/raw/training_50.csv"),
        4357,
        51,
        "e0d460076a19bb6a0cc4bc34fc95aaa3de3ea5302271de423fbe9cabf8613520",
    ),
    FileCheck(
        Path("data/raw/test_50.csv"),
        1090,
        51,
        "ff25e702a50396c52bd4afe4ff81a8ae1cbb6a72181999516527f4f25286e51f",
    ),
    FileCheck(
        Path("data/raw/external_50.csv"),
        486,
        51,
        "1d710212b82144e3a1176b6c5545d5e122e01a8db87eb9ce74df275d3ce265a9",
    ),
    FileCheck(
        Path("results/screening/Pre_Cribado_5_Moleculas.csv"),
        5,
        13,
        "3b5125795edef96fb2e37b94ce7378a89aa627cc0aa96e3876fae4f0cb48e7fb",
    ),
    FileCheck(
        Path("results/screening/DrugBank_Candidatos_Tesis.csv"),
        863,
        8,
        "9dcad5cdcdf7ab1378dda3b5d177c83ae5ae4d1573a8c5f7c66123a0c5367d58",
    ),
    FileCheck(
        Path("models/best_rf_pampa.pkl"),
        None,
        None,
        "947a37694b9bb2e973dc05469711363a8b231aa577d877735e8514e680afd2b3",
    ),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate() -> None:
    failures: list[str] = []
    for check in CHECKS:
        if not check.path.exists():
            failures.append(f"Missing file: {check.path}")
            continue

        observed_hash = sha256(check.path)
        if observed_hash != check.sha256:
            failures.append(f"Hash mismatch: {check.path}")

        if check.rows is not None and check.columns is not None:
            data = pd.read_csv(check.path)
            if data.shape != (check.rows, check.columns):
                failures.append(
                    f"Shape mismatch: {check.path} expected "
                    f"{check.rows}x{check.columns}, observed {data.shape[0]}x{data.shape[1]}"
                )

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        raise SystemExit(1)

    print(f"[OK] Validated {len(CHECKS)} core files.")


if __name__ == "__main__":
    validate()

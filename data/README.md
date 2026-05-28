# Data

This directory contains the curated datasets used by the reproducible QSAR
workflow.

## Provenance

The six raw CSV files are the same curated databases published in the original
repository `bvasquezp/Permeability-PAMPA`, renamed for clarity:

| Current file | Original file | Rows | Columns | SHA256 |
| --- | --- | ---: | ---: | --- |
| `raw/training_11.csv` | `FINAL_Training.csv` | 4357 | 12 | `fe73947fc0244441c4ec0eb2a772ed9557a235b77aeb461bcd03485a0ff2a398` |
| `raw/test_11.csv` | `FINAL_Test.csv` | 1090 | 12 | `7848b86e9d681d0b7c1486e3a07b692f7c763cbf182cc3b8ac1fe8f5df3b4d40` |
| `raw/external_11.csv` | `FINAL_External.csv` | 486 | 12 | `71ea363dcb399a2b2da111096a18e4e3ef7cc9cd15a5c40a91c3ba771f696a25` |
| `raw/training_50.csv` | `training_final.csv` | 4357 | 51 | `e0d460076a19bb6a0cc4bc34fc95aaa3de3ea5302271de423fbe9cabf8613520` |
| `raw/test_50.csv` | `test_final.csv` | 1090 | 51 | `ff25e702a50396c52bd4afe4ff81a8ae1cbb6a72181999516527f4f25286e51f` |
| `raw/external_50.csv` | `external_final.csv` | 486 | 51 | `1d710212b82144e3a1176b6c5545d5e122e01a8db87eb9ce74df275d3ce265a9` |

`processed/` contains copies formatted for the notebooks and final model
workflow.

## Target

The classification target is `Actividad`, where the model distinguishes PAMPA
permeable and non-permeable compounds.

## Validation

Run this command from the repository root to verify dataset integrity:

```powershell
python src/validate_project.py
```

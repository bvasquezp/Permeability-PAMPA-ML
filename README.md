# Permeability-PAMPA

QSAR workflow for predicting passive intestinal permeability measured by PAMPA
using molecular descriptors, fingerprints and machine learning models.

This repository (`bvasquezp/Permeability-PAMPA-ML`) is the reproducible version
prepared to accompany the manuscript. The final thesis PDF is stored in
`docs/thesis/Tesis_QSAR.pdf`, and the curated databases were verified against the
historical repository `bvasquezp/Permeability-PAMPA`.

## Project Summary

The goal is to identify molecules with favorable passive intestinal permeability
using PAMPA as the experimental reference. The final model is a Random Forest
classifier trained on selected physicochemical and structural descriptors. The
workflow also includes external validation, applicability-domain analysis,
SHAP-based interpretability and virtual screening of DrugBank candidates.

## Repository Structure

- `data/`: final datasets used by the clean workflow.
- `notebooks/`: main notebooks for preparation, modeling and virtual screening.
- `src/`: maintained scripts that replace exploratory code from the thesis work.
- `models/`: serialized final model.
- `results/`: metrics, figures and final screening outputs.
- `references/papers/`: papers and PDF documents used as bibliography/background.
- `docs/`: thesis, poster and auxiliary tables.
- `archive/source_material/`: ordered archive of historical material from
  `BD PAMPA` and `QSAR`.
- `requirements.txt` / `environment.yml`: reproducible Python environments.

## Installation

Using conda:

```powershell
conda env create -f environment.yml
conda activate permeability-pampa
```

Using pip:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Validate that the core datasets, screening outputs and final model match this
repository version:

```powershell
python src/validate_project.py
```

Recompute the final model metrics and compare them with the stored thesis
results:

```powershell
python src/check_final_metrics.py
```

## Final Model

The selected thesis model is a `RandomForestClassifier` trained with 11 final
descriptors:

- `LOGPcons`
- `MACCSFP125`
- `PCR`
- `Psi_e_A`
- `P_VSA_ppp_D`
- `Mp`
- `SpMin1_Bh(p)`
- `SHED_AL`
- `SM12_AEA(ri)`
- `P_VSA_s_3`
- `MATS5m`

Serialized model:

- `models/best_rf_pampa.pkl`

## Main Data

- `data/raw/training_11.csv`: training set with the 11 final descriptors.
- `data/raw/test_11.csv`: internal validation set.
- `data/raw/external_11.csv`: independent external validation set.
- `data/raw/*_50.csv`: previous feature-selection/reduction stage.
- `data/processed/*_11_processed.csv`: processed copies used by the notebooks.

The original names in the first repository were `FINAL_Training.csv`,
`FINAL_Test.csv`, `FINAL_External.csv`, `training_final.csv`, `test_final.csv`
and `external_final.csv`. The file mapping and SHA256 hashes are documented in
`data/README.md`.

## Final Results

Metrics:

- `results/metrics/evaluacion_final_datasets.csv`
- `results/metrics/cv_results_comparison.csv`

Figures:

- `results/figures/`

Screening:

- `results/screening/Pre_Cribado_5_Moleculas.csv`: prospective test with five
  molecules unseen by the model.
- `results/screening/Reporte_Lipinski_Candidatos.csv`: Lipinski evaluation for
  the pre-screening candidates.
- `results/screening/DrugBank_Candidatos_Tesis.csv`: final DrugBank screening
  output after applicability-domain, probability and drug-likeness filters.

The complete DrugBank source used for screening contained more than 10000
compounds. Historical screening inputs are stored in
`archive/source_material/qsar_inputs/`. Large local DrugBank exports over 100 MB
are intentionally ignored by Git and are not required to validate the final
screening output.

## Reproducible Scripts

Convert CSV to ARFF for WEKA:

```powershell
python src/csv_to_arff.py data/raw/training_11.csv results/weka/training_11.arff --relation pampa_11
```

Generate WEKA commands equivalent to the historical `weka_cmd1.py`:

```powershell
python src/weka_feature_selection.py generate --weka-jar D:/Weka-3-6/weka.jar --input-arff results/weka/training_11.arff --output results/weka/commandlines.txt
```

Run the 10 WEKA selector combinations in parallel:

```powershell
python src/weka_feature_selection.py run --weka-jar D:/Weka-3-6/weka.jar --input-arff results/weka/training_11.arff --logs-dir results/weka/logs --workers 4
```

Build the descriptor-vote consensus table from WEKA logs:

```powershell
python src/weka_feature_selection.py consensus --input-arff results/weka/training_11.arff --logs-dir results/weka/logs --output results/weka/descriptor_consensus.csv
```

Compare classical classifiers on the 11 final descriptors:

```powershell
python src/evaluate_models.py --dataset data/raw/training_11.csv --output results/metrics/model_comparison.csv
```

Check that the serialized Random Forest reproduces the final training, internal
test and external validation metrics:

```powershell
python src/check_final_metrics.py
```

Rebuild the `MoleculeN -> DrugBank_ID` translator from the SDF:

```powershell
python src/rebuild_drugbank_ids.py --sdf archive/source_material/qsar_inputs/allCOR3D.sdf --output archive/source_material/qsar_inputs/Lista_DrugBank_IDs.csv
```

## Notebooks

- `notebooks/01_Analisis_y_preparacion_datos.ipynb`
- `notebooks/02_Entrenamiento_RandomForest.ipynb`
- `notebooks/03_Cribado_Virtual_PAMPA.ipynb`

## Historical Material

`archive/source_material/` contains the historical files that were previously
dispersed across `BD PAMPA/` and `QSAR/`. They are preserved for traceability,
while the reproducible workflow lives in `data/`, `notebooks/`, `src/`,
`models/` and `results/`.

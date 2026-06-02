# Manual de reproducibilidad y MLOps

Este manual describe como ejecutar, validar y auditar el proyecto
`Permeability-PAMPA-ML` desde cero. Esta pensado para investigadores que quieren
replicar los resultados del modelo QSAR PAMPA y revisar la trazabilidad de los
datos, metricas y artefactos.

## 1. Preparar el entorno

Desde la raiz del repositorio:

```powershell
cd "c:\Users\benja\OneDrive - utem.cl\Documentos\Permeability-PAMPA"
```

Con conda:

```powershell
conda env create -f environment.yml
conda activate permeability-pampa
```

Con pip:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Para usar MLflow y DVC:

```powershell
python -m pip install -r requirements-mlops.txt
```

## 2. Validacion rapida

Usa este comando para verificar que los archivos principales, el modelo y los
resultados finales siguen coincidiendo con la version reproducible del proyecto:

```powershell
python src/run_reproducibility_pipeline.py --skip-model-comparison --skip-manuscript-assets --mlflow-preview
```

Este comando ejecuta:

- manifiesto de datos y artefactos;
- validacion de hashes, filas y columnas;
- reproduccion de metricas finales;
- generacion de un payload compatible con MLflow.

Los resultados se escriben en:

- `results/pipeline/data_manifest.json`
- `results/pipeline/data_manifest.csv`
- `results/pipeline/pipeline_run.json`
- `results/mlflow/mlflow_payload_preview.json`

## 3. Reproducir metricas finales

Para comprobar solo las metricas del modelo Random Forest final:

```powershell
python src/check_final_metrics.py
```

El script carga:

- `models/best_rf_pampa.pkl`
- `data/raw/training_11.csv`
- `data/raw/test_11.csv`
- `data/raw/external_11.csv`
- `results/metrics/evaluacion_final_datasets.csv`

La ejecucion es correcta si termina con:

```text
[OK] Final metrics match within tolerance=0.001.
```

## 4. Auditar datos y artefactos

Para generar un inventario reproducible de los archivos principales:

```powershell
python src/build_data_manifest.py
```

El manifiesto registra:

- ruta del archivo;
- existencia;
- tamano en bytes;
- SHA256;
- filas y columnas para archivos CSV.

Este paso funciona como una capa ETL/ELT de auditoria: confirma que los datos
curados, los resultados y el modelo cargado corresponden a la misma version del
proyecto.

## 5. Comparar modelos clasicos

Para reproducir la comparacion de clasificadores con los 11 descriptores finales:

```powershell
python src/evaluate_models.py --dataset data/raw/training_11.csv --output results/metrics/model_comparison.csv
```

El archivo generado es:

```text
results/metrics/model_comparison.csv
```

Este paso compara clasificadores tipo J48, Logistic Regression, IBk/kNN, Random
Forest y SVM usando validacion cruzada estratificada.

## 6. Usar MLflow

Para probar el registro sin instalar ni abrir MLflow:

```powershell
python src/mlflow_tracking.py --dry-run
```

Para registrar una corrida real:

```powershell
python -m pip install -r requirements-mlops.txt
python src/mlflow_tracking.py
```

Para abrir la interfaz local:

```powershell
mlflow ui --backend-store-uri mlruns
```

Luego abrir:

```text
http://127.0.0.1:5000
```

MLflow registra:

- parametros desde `params.yaml`;
- metricas finales de entrenamiento, test interno y validacion externa;
- modelo serializado y archivos de resultados disponibles.

## 7. Usar DVC

El archivo `dvc.yaml` define etapas reproducibles para:

- generar el manifiesto de datos;
- validar integridad del proyecto;
- reproducir metricas finales;
- comparar modelos;
- generar payload de MLflow.

Con DVC instalado:

```powershell
dvc repro
```

Actualmente DVC se usa como definicion de pipeline y trazabilidad local. Si se
quiere versionar archivos grandes fuera de Git, se puede agregar un remoto DVC
para DrugBank, alvaDesc u otras matrices descriptoras pesadas.

## 8. Regenerar tablas e imagenes del manuscrito

Para regenerar figuras, tablas y version Word con assets:

```powershell
python manuscript/generate_python_assets.py
python manuscript/build_docx_with_assets.py
```

Archivos principales:

- `manuscript/pampa_qsar_manuscript.tex`
- `manuscript/pampa_qsar_manuscript_with_python_assets.docx`
- `manuscript/pampa_qsar_overleaf_package.zip`

Para Overleaf, subir el ZIP completo. No subir solo el `.tex`, porque necesita
`references.bib`, `figures/` y `tables/`.

## 9. Comando recomendado para revision diaria

Para revisar que el proyecto sigue sano antes de trabajar o antes de hacer
commit:

```powershell
python src/run_reproducibility_pipeline.py --skip-manuscript-assets --mlflow-preview
```

Para una revision mas rapida:

```powershell
python src/run_reproducibility_pipeline.py --skip-model-comparison --skip-manuscript-assets --mlflow-preview
```

## 10. Errores comunes

Si falta `scikit-learn`, instalar dependencias:

```powershell
python -m pip install -r requirements.txt
```

Si MLflow no esta instalado, usar:

```powershell
python src/mlflow_tracking.py --dry-run
```

Si una validacion de hash falla, revisar si el archivo fue editado o reemplazado.
Los hashes esperados estan definidos en `src/validate_project.py` y documentados
en `data/README.md`.

Si Overleaf no encuentra figuras o tablas, subir el paquete completo:

```text
manuscript/pampa_qsar_overleaf_package.zip
```

## 11. Que demuestra esta automatizacion

La automatizacion permite demostrar que:

- los archivos curados usados por el modelo son identificables y auditables;
- las metricas finales se reproducen desde el modelo serializado;
- los resultados de screening y pre-screening estan disponibles como artefactos;
- el proyecto tiene una ruta clara para CI/CD mediante GitHub Actions;
- MLflow y DVC pueden incorporarse sin cambiar los resultados cientificos.

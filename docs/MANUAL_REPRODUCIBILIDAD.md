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

## 6. Reconstruir seleccion alvaDesc/WEKA de tesis

La ruta cientifica validada no depende de RDKit. Parte de los descriptores
alvaDesc y fingerprints historicos, fusionados en un ARFF de 783 atributos.

Auditar que los artefactos legacy contienen los 50 atributos intermedios y los
11 descriptores finales:

```powershell
python src/audit_thesis_feature_pipeline.py
```

Reconstruir el pipeline completo:

```powershell
python src/rebuild_thesis_feature_pipeline.py
```

Este paso:

- reconstruye `thesis_fused_training_783.csv`, `thesis_fused_test_783.csv` y
  `thesis_fused_external_783.csv`;
- aplica EDA: varianza `0.05`, Mann-Whitney `alpha=0.05`, Spearman `|r|>0.90`
  y RFE hasta 50 atributos;
- parsea el consenso WEKA legacy desde `consenso_final.txt`;
- aplica el umbral historico `0.4` sobre el maximo observado de votos, que
  recupera 92 atributos de consenso;
- evalua paneles optimizados de 11 atributos;
- compara el panel optimizado contra los 11 descriptores exactos de tesis.

Los resultados quedan en:

- `results/thesis_feature_pipeline/pipeline_report.json`
- `results/thesis_feature_pipeline/pipeline_report.md`
- `results/thesis_feature_pipeline/optimized_vs_thesis_exact.csv`
- `results/thesis_feature_pipeline/weka_consensus_scores.csv`
- `results/thesis_feature_pipeline/eda_ranking.csv`

El pipeline usa undersampling de la clase mayoritaria y
`class_weight={0: 1.5, 1: 1}`. La semilla de undersampling `30` reproduce las
metricas externas de clase del modelo final de tesis.

## 7. Usar MLflow

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

## 8. Usar DVC

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

## 9. Regenerar tablas e imagenes del manuscrito

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

## 10. Notebooks paso a paso

Los notebooks `01` a `07` funcionan como manual secuencial para revision,
docencia o demostracion frente a un evaluador que no programa habitualmente.
Cada notebook incluye una celda de configuracion editable con las rutas que se
pueden cambiar.

- `notebooks/01_Analisis_y_preparacion_datos.ipynb`: revisar bases curatoriales.
- `notebooks/02_Entrenamiento_RandomForest.ipynb`: validar modelo final y
  metricas.
- `notebooks/03_Cribado_Virtual_PAMPA.ipynb`: predecir nuevas moleculas desde
  un CSV con los 11 descriptores.
- `notebooks/04_Reconstruccion_dataset_tesis.ipynb`: reconstruir matriz
  fusionada de 783 atributos desde ARFF.
- `notebooks/05_EDA_WEKA_seleccion_descriptores.ipynb`: revisar EDA, RFE,
  consenso WEKA y seleccion de 11 atributos.
- `notebooks/06_Validacion_modelo_tesis.ipynb`: comparar modelo serializado con
  resultados finales guardados.
- `notebooks/07_Prediccion_nuevas_moleculas_agentes_locales.ipynb`: ejecutar
  panel local de agentes sin API.
- `notebooks/08_Herramienta_interactiva_serie_C.ipynb`: generar SMILES
  preliminares para series A/B/C o compuestos con SMILES directo, revisar
  RDKit/Lipinski, preparar la plantilla de 11 descriptores e inyectar la tabla
  completa al modelo.

Orden recomendado:

```text
01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08
```

Para evaluar una nueva base, el caso mas comun es cambiar `INPUT_FILE` en el
notebook `03` o `07` por un CSV con las 5 moleculas nuevas y los 11
descriptores alvaDesc/WEKA.

Para trabajar especificamente con las series A/B/C recibidas en `compuestos.pdf`,
usar el notebook `08`. Este notebook genera la tabla preliminar desde
sustituyentes R o desde SMILES directos, pero la prediccion final queda
bloqueada hasta completar los 11 descriptores alvaDesc/WEKA.

## 11. Surrogate RDKit gobernado

El modelo validado de tesis sigue siendo `models/best_rf_pampa.pkl`, entrenado
con 11 descriptores alvaDesc/WEKA. El surrogate RDKit es una ruta de
automatizacion desde SMILES y solo puede usarse para decisiones si pasa gates
internos y externos.

Auditar y reconstruir los datos RDKit corregidos:

```powershell
python src/audit_rdkit_dataset.py
```

Este paso valida que `Target_corrected = 1 - Target` coincide fila por fila con
`training_11.csv` y `test_11.csv`, genera el dataset a nivel compuesto y reporta
duplicados/conflictos.

Entrenar el candidato formal:

```powershell
python src/train_rdkit_candidate.py
```

Entrenar el candidato v2 calibrado, comparable con la estrategia operativa de la
tesis (`class_weight={0: 1.5, 1: 1}` y busqueda de umbral interno):

```powershell
python src/train_rdkit_candidate.py --candidate-id rdkit_surrogate_candidate_v2 --tune-class-weight --tune-threshold
```

Entrenar una replica estricta del protocolo de tesis para el surrogate RDKit
con 5-fold, undersampling, `class_weight={0: 1.5, 1: 1}` y umbral `0.5`:

```powershell
python src/train_rdkit_candidate.py --candidate-id rdkit_surrogate_candidate_v3_thesis_protocol --thesis-protocol
```

Entrenar el mismo protocolo ampliando el panel a RDKit+MACCS antes de la
seleccion EDA/RFE:

```powershell
python src/train_rdkit_candidate.py --candidate-id rdkit_surrogate_candidate_v4_rdkit_maccs_thesis_protocol --thesis-protocol --feature-space rdkit_maccs
```

Prueba rapida de desarrollo:

```powershell
python src/train_rdkit_candidate.py --candidate-id rdkit_surrogate_candidate_v2 --tune-class-weight --tune-threshold --n-splits 2 --n-repeats 1 --selection-estimators 30 --final-estimators 80
```

El reporte de gates queda en:

```text
results/metrics/rdkit_surrogate_candidate_v2_gate_report.json
```

Si `passed_all_gates=false`, `models/model_registry.json` marca el modelo como
`candidate` y el MCP devuelve `approved_for_decision=false`.

Probar el adaptador MCP:

```powershell
python src/agentic/mcp_server.py predict "CC(=O)Oc1ccccc1C(=O)O"
```

## 12. Science Skills locales

El proyecto incluye dos workflows locales inspirados en Google DeepMind Science
Skills, pero ajustados al contrato cientifico de la tesis:

- `skills/pampa_computational_discovery/SKILL.md`
- `skills/pampa_literature_insights/SKILL.md`

Prediccion exacta con los 11 descriptores de tesis:

```powershell
python -m src.science_skills.pampa_computational_discovery predict-panel --input data/raw/test_11.csv --output results/science_skills/test_11_predictions.csv
```

Panel local de agentes sin API:

```powershell
python src/agentic/local_orchestrator.py --input data/query/example_positive_negative_11.csv --output results/agentic/local_agent_predictions.csv --report-json results/agentic/local_agent_report.json --report-md results/agentic/local_agent_report.md --id-column example_id
```

Este panel es deterministico y no llama a Gemini, OpenAI ni Claude. Ejecuta:

- `DescriptorAgent`: valida los 11 descriptores alvaDesc/WEKA.
- `ChemicalAgent`: valida SMILES y Lipinski si hay columna SMILES.
- `ModelAgent`: predice con `models/best_rf_pampa.pkl`.
- `ApplicabilityDomainAgent`: calcula leverage frente al entrenamiento.
- `PhysicsAgent`: interpreta senales fisicoquimicas basicas.
- `ReportAgent`: genera CSV, JSON y Markdown.

Entrada solo SMILES:

```powershell
python -m src.science_skills.pampa_computational_discovery screen-smiles "CC(=O)Oc1ccccc1C(=O)O"
```

Este modo no entrega prediccion aprobada porque la replica exacta requiere los
11 descriptores seleccionados con alvaDesc/WEKA.

Auditoria de referencias:

```powershell
python -m src.science_skills.pampa_literature_insights audit-manuscript --tex manuscript/pampa_qsar_manuscript.tex --bib manuscript/references.bib
```

Busqueda opcional en Europe PMC:

```powershell
python -m src.science_skills.pampa_literature_insights search-europepmc --query "PAMPA QSAR permeability Random Forest" --max-results 10
```

Los artefactos quedan en `results/science_skills/`.

## 13. Comando recomendado para revision diaria

Para revisar que el proyecto sigue sano antes de trabajar o antes de hacer
commit:

```powershell
python src/run_reproducibility_pipeline.py --skip-manuscript-assets --mlflow-preview
```

Para una revision mas rapida:

```powershell
python src/run_reproducibility_pipeline.py --skip-model-comparison --skip-manuscript-assets --mlflow-preview
```

## 14. Errores comunes

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

## 15. Que demuestra esta automatizacion

La automatizacion permite demostrar que:

- los archivos curados usados por el modelo son identificables y auditables;
- las metricas finales se reproducen desde el modelo serializado;
- los resultados de screening y pre-screening estan disponibles como artefactos;
- el proyecto tiene una ruta clara para CI/CD mediante GitHub Actions;
- MLflow y DVC pueden incorporarse sin cambiar los resultados cientificos.

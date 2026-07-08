# Contexto completo del proyecto Permeability-PAMPA-ML

Actualizado: 22 de junio de 2026.

Este documento sirve como handoff tecnico y cientifico para continuar el
proyecto con otro agente. Distingue entre el modelo reproducible de la tesis,
que usa descriptores alvaDesc y seleccion WEKA, y la linea experimental basada
en RDKit, MCP y agentes.

## 1. Objetivo cientifico

El proyecto desarrolla un modelo QSAR de clasificacion para predecir
permeabilidad intestinal pasiva medida mediante PAMPA. El endpoint es binario:

- `Act1`: compuesto permeable.
- `Act-1`: compuesto no permeable.
- Umbral experimental: `P_eff = 10 x 10^-6 cm/s`.

PAMPA aproxima difusion pasiva mediante una membrana artificial. El modelo no
representa transporte activo, metabolismo, formulacion, exposicion sistemica ni
absorcion intestinal completa in vivo. Sus resultados deben interpretarse como
priorizacion de compuestos, no como una afirmacion farmacocinetica definitiva.

## 2. Repositorios y organizacion

- Repositorio historico inicial: `bvasquezp/Permeability-PAMPA`.
- Repositorio reproducible y destinado al paper:
  `bvasquezp/Permeability-PAMPA-ML`.
- Remoto actual: `https://github.com/bvasquezp/Permeability-PAMPA-ML`.
- Rama local actual: `main`.
- Ultimo commit observado: `291f1d2 Add reproducibility manual and MLOps pipeline`.
- La tesis final esta en `docs/thesis/Tesis_QSAR.pdf`.
- Los materiales historicos de las carpetas originales `BD PAMPA` y `QSAR`
  fueron reunidos bajo `archive/source_material/`.
- El flujo mantenido debe vivir en `data/`, `src/`, `models/`, `results/`,
  `notebooks/`, `manuscript/` y `docs/`.

El arbol de trabajo esta sucio y contiene muchos cambios aun no incluidos en el
ultimo commit. No ejecutar limpieza destructiva ni restaurar archivos sin
revisar primero `git status` y la procedencia de cada cambio.

## 3. Procedencia y particion de los datos

El conjunto de desarrollo proviene del trabajo de Parasar et al. citado en el
manuscrito. Esta fuente contiene 5447 compuestos y se dividio de forma
estratificada en:

| Conjunto | Total | Permeables | No permeables | Funcion |
| --- | ---: | ---: | ---: | --- |
| Entrenamiento | 4357 | 2332 | 2025 | Ajuste y seleccion |
| Prueba interna | 1090 | 583 | 507 | Evaluacion interna |
| Validacion externa | 486 | 443 | 43 | Validacion independiente |

Los 486 compuestos externos pertenecen a una base separada y no estan incluidos
en los 5447 de Parasar. Por eso:

- Desarrollo y prueba interna: `4357 + 1090 = 5447`.
- Total de archivos curados disponibles: `5447 + 486 = 5933`.
- No debe escribirse que Parasar aporto 5933 compuestos.

Archivos curados principales:

- `data/raw/training_11.csv`
- `data/raw/test_11.csv`
- `data/raw/external_11.csv`
- `data/raw/training_50.csv`
- `data/raw/test_50.csv`
- `data/raw/external_50.csv`

`data/README.md` documenta los nombres originales, dimensiones y hashes SHA256.
`src/validate_project.py` valida esos hashes y dimensiones.

## 4. Flujo original de la tesis

### 4.1 Representacion molecular

Las estructuras se normalizaron como SMILES y se procesaron con alvaDesc
v2.0.10. Se calcularon descriptores 0D-2D y fingerprints estructurales, entre
ellos MACCS y representaciones tipo ECFP. No se utilizaron descriptores 3D en el
flujo final descrito para el paper.

En el material historico se calcularon por separado descriptores y fingerprints
para entrenamiento, prueba y validacion externa. Luego se fusionaron las tablas
respetando el orden de las filas. El usuario recuerda una matriz fusionada de
aproximadamente 785 atributos; el manuscrito actual declara 783 descriptores
despues del filtrado inicial de alvaDesc. Esta diferencia `785 vs 783` debe
reconciliarse contra los ARFF, notebooks y logs antes de cerrar el paper.

### 4.2 EDA y reduccion de dimensionalidad

La narrativa actual del manuscrito es:

1. Verificacion de faltantes, infinitos, tipos y distribucion de clases.
2. Filtro de varianza con umbral `0.05`: 5 variables eliminadas.
3. Mann-Whitney con `alpha = 0.05`: 126 variables eliminadas.
4. Spearman absoluto con `|r| > 0.90`: 122 variables redundantes eliminadas.
5. RFE con importancia Gini de Random Forest: reduccion a 50 atributos.
6. Consenso WEKA: seleccion final de 11 descriptores.

Estos conteos estan incorporados al manuscrito y a los esquemas generados, pero
deben mantenerse trazables a los scripts/notebooks originales antes de una
publicacion definitiva.

### 4.3 Consenso WEKA

El script historico `weka_cmd1.py` ejecutaba conjuntamente los evaluadores. La
implementacion mantenida es `src/weka_feature_selection.py`.

Se combinan dos clasificadores con cinco estrategias de busqueda:

- Clasificadores: J48 e IBk.
- Busquedas: BestFirst, GeneticSearch, LinearForwardSelection, RankSearch y
  SubsetSizeForwardSelection.
- Total: 10 combinaciones/evaluadores.
- Umbral preliminar de consenso: al menos 4 votos de 10, equivalente a 40%.
- Luego se aplica parsimonia para conservar los 11 descriptores finales.

Los ARFF y logs historicos estan bajo
`archive/source_material/bd_pampa_legacy/`. En el estado Git actual aparecen
eliminados `WEKA_Train.arff`, `WEKA_Test.arff` y `WEKA_Ext.arff` que estaban en
la raiz de esa carpeta, mientras existen otros ARFF dentro de subdirectorios.
No asumir que esas eliminaciones son correctas hasta auditar duplicados y rutas.

## 5. Modelo final de la tesis

El artefacto validado es `models/best_rf_pampa.pkl`.

Los 11 descriptores finales son:

1. `LOGPcons`
2. `MACCSFP125`
3. `PCR`
4. `Psi_e_A`
5. `P_VSA_ppp_D`
6. `Mp`
7. `SpMin1_Bh(p)`
8. `SHED_AL`
9. `SM12_AEA(ri)`
10. `P_VSA_s_3`
11. `MATS5m`

Configuracion documentada del Random Forest:

- `n_estimators = 500`
- `max_depth = 10`
- criterio Gini
- `min_samples_leaf = 4`
- `max_features = sqrt`
- pesos de clase: 1.5 para no permeable y 1.0 para permeable
- `random_state = 42`
- optimizacion historica mediante grid search y validacion cruzada de 5 folds

Metricas reproducidas desde el modelo serializado:

| Conjunto | Accuracy | Sensibilidad | Especificidad | AUC | MCC | F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Entrenamiento | 0.863 | 0.852 | 0.877 | 0.940 | 0.727 | 0.870 |
| Test interno | 0.751 | 0.760 | 0.742 | 0.830 | 0.501 | 0.766 |
| Externo | 0.887 | 0.939 | 0.349 | 0.678 | 0.291 | 0.938 |

La validacion externa esta fuertemente desbalanceada: 443 permeables y 43 no
permeables. La accuracy y el F1 alto no deben citarse solos. La especificidad de
0.349, el MCC de 0.291 y el AUC de 0.678 muestran una capacidad limitada para
discriminar la clase minoritaria externa.

El dominio de aplicabilidad usa leverage con `h* = 0.0083`.

## 6. Interpretabilidad

El proyecto incluye:

- importancia de variables de Random Forest;
- curvas ROC y matrices de confusion;
- SHAP global en barra;
- SHAP beeswarm con direccion de efectos;
- interpretacion mecanistica de lipofilicidad, topologia, superficie polar,
  polarizabilidad y motivos estructurales.

Figuras principales:

- `manuscript/figures/Importancia_Variables_PAMPA.png`
- `manuscript/figures/SHAP_Bar_PAMPA.png`
- `manuscript/figures/SHAP_Beeswarm_PAMPA.png`
- `manuscript/figures/Curvas_ROC_PAMPA.png`
- `manuscript/figures/python_confusion_matrices.png`

## 7. Precribado de cinco moleculas

El precribado fue realizado en la tesis con cinco compuestos no usados para
entrenar el modelo. No constituye una nueva validacion experimental del paper.
Se estan coordinando ensayos de otros compuestos priorizados.

| ID | Nombre/control | Probabilidad | Prediccion | PAMPA experimental |
| --- | --- | ---: | --- | --- |
| Molecule3 | Compuesto 7 | 0.696 | Permeable | 11.7 +/- 0.51 |
| Molecule2 | Compuesto 3 | 0.695 | Permeable | 12.1 +/- 0.27 |
| Molecule4 | Donepezilo, control positivo | 0.659 | Permeable | 22.4 +/- 0.49 |
| Molecule1 | Compuesto 2 | 0.648 | Permeable | 11.1 +/- 0.43 |
| Molecule5 | Norfloxacino, control negativo | 0.045 | No permeable | 1.43 +/- 0.08 |

Los compuestos 2, 3 y 7 son derivados de 4-hidrazono-pirazolidinediona del
trabajo de Waheed citado. Los valores experimentales corresponden a PAMPA-BBB,
mientras el endpoint del modelo es PAMPA intestinal. La comparacion es
cualitativa y debe describirse como prueba de transferencia, no como validacion
equivalente del endpoint.

Archivos:

- `results/screening/Pre_Cribado_5_Moleculas.csv`
- `results/screening/Reporte_Lipinski_Candidatos.csv`
- `manuscript/tables/pre_screening_named.csv`
- `manuscript/figures/python_pre_screening_structures.png`

## 8. Cribado DrugBank

La fuente completa tenia mas de 10000 entradas. El flujo historico aplico
disponibilidad de descriptores, prediccion, probabilidad, dominio de
aplicabilidad y Lipinski.

| Etapa | Compuestos |
| --- | ---: |
| Biblioteca fuente | >10000 |
| Probabilidad >= 0.60 | 863 |
| Dentro del dominio de aplicabilidad | 850 |
| Lipinski viable | 778 |
| Dentro del dominio y Lipinski viable | 770 |

El archivo preservado con 863 candidatos es
`results/screening/DrugBank_Candidatos_Tesis.csv`.

Existe una discrepancia importante en la tabla top 10 de la tesis: varios
DrugBank ID no corresponden al nombre generico reportado cuando se contrastan
con el SDF local. La auditoria esta en
`manuscript/tables/drugbank_thesis_reported_top10.csv`. Coinciden, por ejemplo,
Prasugrel, Calcipotriol, Gefitinib y Lucanthone; otros pares como
`DB01656/Vatalanib`, `DB00838/Clopidogrel`, `DB00401/Propranolol`,
`DB00559/Verapamil` y `DB00269/Chlorpromazine` requieren revision. No corregir
IDs o nombres por intuicion: verificar contra la fuente DrugBank utilizada y
documentar cualquier cambio.

## 9. Manuscrito y documentos

Versiones principales:

- `manuscript/pampa_qsar_manuscript.tex`: manuscrito completo en ingles.
- `manuscript/pampa_qsar_manuscript.docx`: Word completo.
- `manuscript/pampa_qsar_manuscript_es.tex`: manuscrito completo en espanol.
- `manuscript/pampa_qsar_manuscript_es.docx`: Word completo en espanol.
- `manuscript/pampa_qsar_manuscript_es_intro_metodos.tex`: paquete reducido de
  introduccion y materiales/metodos en espanol, sin marcas rojas.
- `manuscript/pampa_qsar_overleaf_package.zip`: paquete Overleaf ingles.
- `manuscript/pampa_qsar_overleaf_package_es.zip`: paquete Overleaf espanol.
- `manuscript/pampa_qsar_overleaf_package_es_intro_metodos.zip`: paquete
  reducido en espanol.

El titulo y abstract del manuscrito completo principal estan en ingles. La
afiliacion actual es:

`Instituto Universitario de Investigacion y Desarrollo IDT, Universidad
Tecnologica Metropolitana, Santiago, Chile`.

Las versiones completas inglesa y espanola aun contienen 15 bloques `\rev{}`
en rojo. La version reducida espanola no contiene esas marcas. Hay al menos un
problema editorial pendiente en ingles: `Due to, the workflow...` es
gramaticalmente incorrecto y debe reformularse, por ejemplo como `Because the
workflow...` o reescribir la frase completa.

Los assets se generan mediante:

- `manuscript/generate_python_assets.py`
- `manuscript/build_docx_with_assets.py`
- `manuscript/build_docx_from_latex.py`

Las tablas generadas estan en `manuscript/tables/` y las figuras en
`manuscript/figures/`. El paquete Overleaf debe subirse completo con
`references.bib`, `figures/` y `tables/`. La compilacion LaTeX completa no fue
revalidada durante la generacion de este handoff.

## 10. Reproducibilidad y MLOps

Se implemento una capa ligera de MLOps:

- `params.yaml`: rutas, parametros, descriptores, umbrales y semilla.
- `src/build_data_manifest.py`: inventario, dimensiones y SHA256.
- `src/validate_project.py`: validacion de artefactos principales.
- `src/check_final_metrics.py`: reproduccion de metricas con tolerancia 0.001.
- `src/run_reproducibility_pipeline.py`: orquestador de validacion.
- `src/mlflow_tracking.py`: registro MLflow o preview sin MLflow.
- `dvc.yaml`: etapas reproducibles y dependencias.
- `.github/workflows/ci.yml`: CI en Windows para manifiesto, hashes, metricas y
  preview MLflow.
- `docs/MANUAL_REPRODUCIBILIDAD.md`: manual de uso.

Comando rapido:

```powershell
python src/run_reproducibility_pipeline.py --skip-model-comparison --skip-manuscript-assets --mlflow-preview
```

Limitaciones actuales:

- CI no prueba la ruta RDKit, MCP, agentes ni compilacion del manuscrito.
- `mcp_server.py` y los agentes importan `requests`, pero `requirements.txt`
  debe revisarse para asegurar que la dependencia quede declarada.
- DVC define la tuberia, pero no hay un remoto DVC configurado para artefactos
  grandes o propietarios.

## 11. Surrogate RDKit para reemplazar alvaDesc

El objetivo adicional es aceptar un SMILES nuevo y ejecutar automaticamente:

1. validacion estructural con RDKit;
2. calculo de descriptores RDKit;
3. prediccion de permeabilidad;
4. reglas de Lipinski;
5. dominio de aplicabilidad;
6. priorizacion del candidato.

Hay dos modelos experimentales:

- `models/surrogate_rf_pampa.pkl`: surrogate directo.
- `models/surrogate_rf_pampa_eda.pkl`: surrogate con reduccion EDA.

El surrogate EDA parte de 217 descriptores RDKit y aplica:

- varianza `0.05`;
- Mann-Whitney `alpha = 0.05`;
- Spearman `|r| > 0.90`;
- RFE a 11 variables.

Sus 11 descriptores son:

1. `MolLogP`
2. `VSA_EState6`
3. `BertzCT`
4. `AvgIpc`
5. `BalabanJ`
6. `MolMR`
7. `BCUT2D_MRLOW`
8. `VSA_EState3`
9. `BCUT2D_LOGPLOW`
10. `MinEStateIndex`
11. `TPSA`

Metricas internas del surrogate EDA:

- Entrenamiento: accuracy 0.851, AUC 0.930, MCC 0.716, F1 0.817.
- Test interno: accuracy 0.750, AUC 0.831, MCC 0.507, F1 0.684.

El surrogate directo obtuvo entrenamiento casi perfecto, accuracy 0.989 y AUC
1.000, pero test interno de accuracy 0.744 y AUC 0.832. Esto sugiere mayor
sobreajuste que la version EDA.

## 12. Reconstruccion de la base externa y comparacion de modelos

La planilla `BD pampa.xlsx` contenia las 486 moleculas externas con SMILES,
PubChem SID/CID, actividad y permeabilidad. Faltaban tres SMILES. Se recuperaron
por PubChem CID y se canonicalizaron con RDKit.

Archivos creados:

- `src/rebuild_and_compare_external.py`
- `data/processed/external_bridge_reconstructed.csv`
- `results/metrics/external_thesis_vs_surrogate_comparison.csv`
- `results/metrics/external_thesis_vs_surrogate_summary.json`

Validaciones realizadas:

- 486 filas en ambas tablas.
- 3 SMILES recuperadas desde PubChem.
- 0 SMILES faltantes despues de reconstruir.
- La etiqueta derivada de `Permeability > 10` coincide fila por fila con
  `data/raw/external_11.csv`: 486 de 486.

Comparacion externa:

| Modelo | Accuracy | AUC | MCC | F1 |
| --- | ---: | ---: | ---: | ---: |
| Tesis alvaDesc/WEKA | 0.887 | 0.678 | 0.291 | 0.938 |
| Surrogate RDKit EDA | 0.084 | 0.362 | -0.244 | 0.013 |

Otros resultados:

- Acuerdo de prediccion: 0.070.
- Diferencia absoluta media de probabilidad: 0.556.
- Diferencia maxima: 0.819.
- Correlacion de probabilidades: -0.773.
- El surrogate predijo 478/486 compuestos como no permeables.

Conclusion operativa: el surrogate RDKit actual no reemplaza al modelo de la
tesis. Su validacion interna es razonable, pero su comportamiento externo es
incompatible con el modelo original y con las etiquetas. No usarlo para
conclusiones cientificas o screening de produccion hasta investigar cambio de
dominio, representacion, balance, calibracion y posible inversion/semantica de
la etiqueta. La base externa debe seguir siendo independiente; no entrenar o
ajustar hiperparametros directamente contra sus etiquetas.

## 13. MCP, agentes y loop engineering

`src/agentic/mcp_server.py` expone herramientas para:

- `predict_smiles`: surrogate, Lipinski y leverage.
- `calculate_descriptors`: propiedades RDKit basicas.
- `query_external_databases`: consulta PubChem.
- `evaluate_screening_candidate`: umbral 0.60, dominio y Lipinski.

Puede ejecutarse con FastMCP si el paquete `mcp` esta instalado; de lo contrario
usa un fallback CLI limitado.

`src/agentic/agents.py` define agentes conectados por REST a Gemini:

- orquestador QSAR;
- selector de caracteristicas;
- optimizador de modelo;
- disenador de moleculas;
- explicador quimico.

`src/agentic/loops.py` contiene un loop de optimizacion de modelo y otro de
diseno molecular. `ultrathink.py` implementa un debate multiagente y
`ultracode.py` un prototipo de autocorreccion de scripts.

Estas piezas son prototipos, no infraestructura validada:

- requieren `GEMINI_API_KEY` para trabajo real;
- sin clave, varias rutas simulan metricas o moleculas;
- el loop de modelo contiene fallbacks y entrenamiento simplificado;
- no deben presentarse como evidencia cientifica ni como sistema autonomo de
  diseno molecular validado.

La ruta funcional mas concreta es:

```powershell
python src/agentic/screen_smiles.py --model-path models/surrogate_rf_pampa_eda.pkl "CC(=O)Oc1ccccc1C(=O)O"
```

Sin embargo, hereda la limitacion externa grave del surrogate.

## 14. Estado Git actual

El ultimo commit no incluye toda la linea RDKit/manuscrito reciente. Entre los
cambios sin commit observados hay:

- modificaciones de README, manuscrito, referencias y generadores de assets;
- eliminacion de tres ARFF WEKA historicos;
- modelos surrogate sin seguimiento;
- datasets con SMILES y workbooks locales sin seguimiento;
- resultados de seleccion y comparacion sin seguimiento;
- paquetes espanoles y figuras nuevas sin seguimiento;
- scripts `src/agentic/`, comparadores y reconstructores sin seguimiento;
- varios scripts `scratch_*` de inspeccion temporal.

Antes de hacer commit:

1. Separar cambios por tema: manuscrito, surrogate RDKit, puente externo y
   limpieza de material temporal.
2. Revisar archivos grandes y posibles datos que no deban publicarse.
3. Confirmar las eliminaciones de ARFF.
4. No usar `git add .` sin inspeccion.
5. Ejecutar validacion reproducible y comprobar el paquete LaTeX.

## 15. Prioridades recomendadas para continuar

1. Congelar y proteger la linea validada de tesis. Debe seguir reproduciendo
   hashes y metricas antes de cualquier refactor.
2. Corregir el manuscrito: resolver marcas `\rev{}`, la frase `Due to,`, la
   discrepancia 783/785, la auditoria DrugBank y compilar todos los paquetes.
3. Auditar el surrogate antes de expandir agentes: distribuciones de cada
   descriptor, semantica del target, balance de clases, dominio de aplicabilidad,
   calibracion y causas de las 478 predicciones negativas externas.
4. No utilizar la externa para entrenar. Mejorar con CV interna, un conjunto de
   calibracion separado o nuevos datos experimentales.
5. Convertir MCP/agentes en una capa opcional sobre una API de prediccion bien
   testeada. El modelo y la quimioinformatica deben funcionar sin LLM.
6. Agregar tests unitarios para SMILES invalidos, orden de features, clases,
   leverage, reconstruccion PubChem y reproducibilidad batch/individual.
7. Ampliar CI para RDKit y, si es viable, compilacion LaTeX y verificacion de
   enlaces de figuras/tablas.
8. Limpiar los scripts `scratch_*` solo despues de decidir si contienen
   evidencia util para trazabilidad.

## 16. Comandos de referencia

Validar el modelo de tesis:

```powershell
python src/validate_project.py
python src/check_final_metrics.py
```

Ejecutar la tuberia reproducible:

```powershell
python src/run_reproducibility_pipeline.py --skip-model-comparison --skip-manuscript-assets --mlflow-preview
```

Entrenar el surrogate EDA:

```powershell
python src/agentic/train_rdkit_eda_surrogate.py
```

Reconstruir y comparar la externa:

```powershell
python src/rebuild_and_compare_external.py
```

Regenerar assets del manuscrito:

```powershell
python manuscript/generate_python_assets.py
python manuscript/build_docx_with_assets.py
```

## 17. Regla central para el siguiente agente

No mezclar estos dos productos:

- **Producto cientifico validado:** Random Forest de tesis con 11 descriptores
  alvaDesc/WEKA, hashes y metricas reproducibles.
- **Experimento de automatizacion:** surrogate RDKit, MCP, Gemini y loops.

El objetivo futuro puede ser reemplazar alvaDesc por RDKit y automatizar el
ingreso de nuevos SMILES, pero los resultados actuales demuestran que esa
equivalencia todavia no se logro.

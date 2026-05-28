# Archive

Material historico usado para reconstruir el proyecto limpio.

- `source_material/qsar_inputs/`: insumos provenientes de la carpeta `QSAR`, incluyendo
  DrugBank, fingerprints, SDF, calculos de cribado y listas de variables.
- `source_material/bd_pampa_legacy/`: scripts, ARFF, logs, reportes y calculos
  exploratorios provenientes de `BD PAMPA`.

La version mantenible de los scripts principales esta en `../src/`. En particular,
`../src/weka_feature_selection.py` reemplaza el uso manual de `weka_cmd1.py` y permite:

- generar comandos WEKA,
- ejecutar los diez evaluadores/buscadores,
- leer los logs,
- construir una tabla de consenso de descriptores por votos.

Nota para GitHub: los archivos locales `source_material/qsar_inputs/Drugbank.txt`
y `source_material/qsar_inputs/drugbank.xlsx` superan 100 MB y estan ignorados por
`.gitignore`. El resultado final del cribado se conserva en
`../results/screening/DrugBank_Candidatos_Tesis.csv`.

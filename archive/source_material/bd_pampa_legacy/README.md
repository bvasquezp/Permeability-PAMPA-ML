# BD PAMPA Legacy

Respaldo historico de scripts, ARFF, logs y reportes usados durante el desarrollo de
la tesis.

Los scripts mantenibles equivalentes estan ahora en `../../../src/`:

- `csv_to_arff.py`: reemplaza los convertidores CSV a ARFF.
- `weka_feature_selection.py`: reemplaza y mejora `weka_cmd1.py`.
- `evaluate_models.py`: generaliza las comparaciones de clasificadores.
- `select_features.py`: automatiza reduccion por varianza, RFE y correlacion.
- `rebuild_drugbank_ids.py`: reconstruye el traductor DrugBank desde el SDF.

Esta carpeta se conserva para trazabilidad, no como punto principal de ejecucion.

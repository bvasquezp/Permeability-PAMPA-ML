# Scripts

Scripts mantenibles para reproducir las tareas que antes estaban repartidas en
`BD PAMPA` y `QSAR`.

- `csv_to_arff.py`: convierte CSV a ARFF para WEKA.
- `weka_feature_selection.py`: genera comandos WEKA, ejecuta los 10 selectores
  J48/IBk y construye una tabla de consenso por votos.
- `evaluate_models.py`: compara modelos clasicos sobre un conjunto de descriptores.
- `select_features.py`: reduce descriptores por varianza, RFE y correlacion.
- `rebuild_drugbank_ids.py`: reconstruye `Lista_DrugBank_IDs.csv` desde el SDF.

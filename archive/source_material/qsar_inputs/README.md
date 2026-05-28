# QSAR

Esta carpeta conserva solo los insumos historicos que sirvieron para reconstruir el
proyecto ordenado en la raiz del repositorio.

## Conservado

- `Drugbank.txt`, `drugbank.xlsx`: tabla original de descriptores moleculares de
  DrugBank.
- `fingerprints.txt`: fingerprints calculados para el cribado.
- `allCOR3D.sdf`: estructuras 3D de DrugBank con metadatos.
- `Lista_DrugBank_IDs.csv`: traductor reconstruido desde `allCOR3D.sdf`
  (`MoleculeN -> DrugBank_ID`).
- `calculos-screening*.txt`: archivos de descriptores/fingerprints usados por el
  precribado y cribado exploratorio.
- `Calculos Fingerprint/`, `Descriptores Moleculares/`, `FP+DM/`: listas finales de
  variables y comandos WEKA que respaldan la seleccion de atributos.
- `imagenes/`: figuras fuente usadas como apoyo visual.

## Eliminado

Se eliminaron notebooks exploratorios, logs, ARFF, resultados intermedios, CSV
duplicados y figuras de corridas antiguas. La version reproducible y documentada del
trabajo esta en `../../../data`, `../../../notebooks`, `../../../models` y
`../../../results`.

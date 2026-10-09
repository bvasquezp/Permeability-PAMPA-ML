# Python Data Automation · Freelance portfolio

![Resultado visual de datos sintéticos](assets/resultado_demo.svg)

**Clean data, reconcile records and deliver repeatable Excel reports.**

**[Ver el caso en español (Workana)](CASE_STUDY_ES.md)** · **[English case study (Upwork)](CASE_STUDY_EN.md)**

> **Evaluación rápida (2 minutos):** abre el caso en tu idioma, revisa el antes/después y los entregables, y mira el código/las pruebas. Los datos de demostración son sintéticos y **no representan trabajo contratado**.

## Problemas que resuelve esta demostración

| Problema habitual | Ejemplo implementado | Evidencia |
| --- | --- | --- |
| CSV con duplicados, montos o fechas inválidas | 6 registros → 3 válidos + 3 rechazados con razón | `demo.py`, `rejected_records.csv` |
| Conciliación manual de pagos y facturas | Coincidencias exactas, pagos parciales y casos sin asignación | `reconciliation.csv` |
| Reportes periódicos | Resumen Excel por categoría | `summary.xlsx` |
| Necesidad de trazabilidad | Informe JSON y tests automatizados | `quality_summary.json`, `test_demo.py` |

### Ejecutar la demostración

Requiere Python 3.10 o posterior. Desde la raíz del repositorio:

```bash
python -m pip install -r portfolio/requirements.txt
python portfolio/demo.py --output portfolio/output
python -m unittest discover -s portfolio -p "test_*.py" -v
```

Después de ejecutar, abre `portfolio/output/summary.xlsx` y examina los cuatro archivos CSV/JSON de la misma carpeta. **El código de muestra utiliza datos ficticios integrados**, no lee automáticamente CSV arbitrarios ni conecta cuentas.

### Servicio comercial

- **Paquete de referencia: US$180–350** por una automatización pequeña y definida (cotización según datos).
- Incluye limpieza/validación, registro de excepciones, reporte y documentación.
- Para un proyecto real se adaptan esquemas, validaciones y fuentes a los ejemplos anonimizados del cliente.

[Alcance y precio en español](CASE_STUDY_ES.md#oferta-comercial-de-referencia) · [Scope in English](CASE_STUDY_EN.md#example-scope-and-indicative-price)

### Otras necesidades que puedo abordar (por cotización)

- Ingesta desde Excel, CSV o APIs; ETL y validación de datos.
- Extracción y generación de documentos PDF/Word (OCR solo si se acuerda).
- Dashboards y reportes recurrentes.
- Curación científica de datasets y quimioinformática con RDKit.

**Estas cuatro extensiones no están implementadas en esta demostración.** No se confunden con características existentes.

### Evidencia de especialización

El [proyecto principal PAMPA/QSAR](../README.md) demuestra experiencia con pipelines científicos, trazabilidad, validación de modelos y análisis químico. El portfolio comercial y el proyecto científico tienen objetivos diferentes.

### Privacidad y límites

- No se incluyen datos de clientes, credenciales ni información privada de AtomForge.
- No se infieren pagos no identificados ni se promete contabilidad sin intervención humana.
- En proyectos reales deben definirse condiciones de aceptación, confidencialidad y derechos de uso antes de compartir datos.

[Estudio de necesidades y segmentación](MARKET_FIT.md).

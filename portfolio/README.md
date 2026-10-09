# Portfolio | Python Data Automation & Scientific Computing

Commercial demonstrations with **synthetic data**. These demos are separate from the scientific validation of the PAMPA-QSAR research in the repository root.

## What I can deliver

| Client problem | Demonstration / deliverable | Status |
| --- | --- | --- |
| Messy CSV exports, duplicate records, invalid values | Clean CSV, rejection log, data-quality summary | Runnable demo below |
| Manual reconciliation of invoices and payments | Exact invoice-ID matching; unpaid/partial/overpaid status and unmatched IDs | Runnable demo below |
| Recurring reports | Formatted Excel summary with category subtotals | Runnable demo below |
| Spreadsheet/PDF report automation | Client-specific template extraction/generation | Proposed, scoped separately |
| SQL/API data pipelines and dashboards | Dataset integration, automated refresh, validation | Proposed, not included in demo |
| Scientific data curation, RDKit/QSAR | Traceable datasets, descriptors, validation and reproducible analysis | See [PAMPA-ML research](../README.md) |

### Run locally

From the repository root, with Python 3.10+:

```bash
python portfolio/demo.py --output portfolio/output
python -m unittest discover -s portfolio -p 'test_*.py' -v
```

The Excel export requires `openpyxl` (`pip install openpyxl`). The demo uses no private data, external APIs, finance credentials, or AtomForge technology. The generated output folder is local; do not commit real client records.

### Scope limitations

- Matching is exact on explicit invoice IDs; ambiguous records are for human review.
- This is a synthetic workflow example, **not** production accounting or financial software.
- No scraping, OCR, SQL, API connector, automated Power BI report, or document-generation feature is implemented in this example. These would need separately scoped engineering work.
- No published model's predictive performance should be inferred from the synthetic data.

See [services and market positioning](MARKET_FIT.md).

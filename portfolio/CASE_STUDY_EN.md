# Portfolio case study | Python CSV automation and Excel reports

![Illustrative results from synthetic demo data](assets/resultado_demo.svg)

> **Synthetic demonstration, not paid client work.** Review time: approximately two minutes.

## The problem

Teams receive exports containing duplicate record IDs, invalid dates, malformed amounts and disconnected invoice/payment records. Manual cleanup and reconciliation are time consuming and error prone.

## What the demo does

A reproducible Python script (1) validates records, (2) writes a clean CSV and a separate rejection log, (3) matches payments to invoices using **exact invoice IDs**, (4) marks missing or partial payments for review, and (5) produces a category-level Excel summary if `openpyxl` is available.

| Demo metric | Example result |
|---|---|
| Input | 6 synthetic rows |
| Data quality | 3 accepted / 3 flagged with reasons |
| Matching | 1 matched invoice, 1 partial, 1 unpaid, 1 unmatched payment |
| Excel | Valid-record category totals, aggregate 291.70 currency units |
| Audit trail | Quality summary JSON, detailed rejected-record CSV |

This demo does **not** guess unknown payments or provide certified accounting automation. It runs on embedded sample values, not arbitrary client uploads.

## Example deliverables

Cleaned records, rejected-record log, reconciliation result, Excel summary, validation JSON, reusable Python script and handover guide.

[**Source and quick start**](README.md) · [**Tests**](test_demo.py)

## Example scope and indicative price

**US$180–350** for a defined small automation package; final estimate after reviewing actual files.

- Up to two CSV/Excel sources, at most 5,000 rows combined.
- Up to six agreed validation rules.
- One standard report, source code, documentation and one revision.
- Indicative turnaround: 3–5 working days after receiving complete inputs.

**Not included by default:** OCR, scanned PDFs, API/SQL connectors, live dashboards, production bank reconciliation, tax/accounting advice, or unsupervised processing of sensitive information. Real Excel ingestion and arbitrary client schemas would be implemented and tested as part of the scoped project.

### Acceptance criteria

Outputs reconcile against agreed examples; rejected records remain traceable; no missing invoice is silently allocated to a payment.

**To request a quote:** provide anonymized input samples, desired output examples and business rules.

[Spanish version for Workana](CASE_STUDY_ES.md).

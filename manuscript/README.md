# Manuscript Draft

First manuscript draft derived from the thesis results and the reproducible
project files.

- `pampa_qsar_manuscript.tex`: LaTeX article draft.
- `pampa_qsar_manuscript.docx`: editable Word version.
- `pampa_qsar_manuscript_with_python_assets.docx`: Word version with generated
  tables and figures appended.
- `references.bib`: BibTeX references used by the LaTeX draft.
- `figures/`: copied and Python-generated figures used by the manuscript,
  including SHAP plots, pre-screening structures and DrugBank funnel plots.
- `tables/`: CSV and LaTeX tables generated from project results, including
  named pre-screening results, named DrugBank candidates and the thesis-reported
  DrugBank top-10 audit.
- `generate_python_assets.py`: regenerates manuscript tables and figures from
  `data/`, `results/`, and `models/`.
- `build_docx_with_assets.py`: creates the Word manuscript version with generated
  assets appended.
- `overleaf_package/`: ready-to-upload Overleaf project folder. Its root contains
  `main.tex`, `references.bib`, `figures/`, and `tables/`.
- `pampa_qsar_overleaf_package.zip`: ZIP version of the Overleaf project.

Regenerate assets from the repository root with:

```powershell
python manuscript/generate_python_assets.py
python manuscript/build_docx_with_assets.py
```

For Overleaf, upload `pampa_qsar_overleaf_package.zip` as a complete project and
select `main.tex` as the main document. Uploading only the `.tex` file will fail
because the project also needs `references.bib`, `figures/`, and `tables/`.

Before journal submission, confirm:

- final author order and affiliations;
- target journal format;
- funding and conflict-of-interest statements;
- whether the thesis PDF should be cited formally or only used as internal source;
- exact wording for compounds and DrugBank candidates to avoid overclaiming
  experimental validation.

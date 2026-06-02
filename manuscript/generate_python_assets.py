"""Generate manuscript tables and figures from the reproducible project files."""

from __future__ import annotations

import re
import shutil
import unicodedata
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import confusion_matrix


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
FIGURES = MANUSCRIPT / "figures"
TABLES = MANUSCRIPT / "tables"

DATASETS = [
    ("Training", ROOT / "data/raw/training_11.csv"),
    ("Internal test", ROOT / "data/raw/test_11.csv"),
    ("External validation", ROOT / "data/raw/external_11.csv"),
]

LABEL_MAP = {"Act-1": 0, "Act1": 1}
SDF_PATH = ROOT / "archive/source_material/qsar_inputs/allCOR3D.sdf"
THESIS_PDF = ROOT / "docs/thesis/Tesis_QSAR.pdf"

PRESCREENING_METADATA = {
    "Molecule1": {
        "Compound": "Compound 2",
        "Role": "Waheed derivative",
        "Experimental PAMPA": "11.1 +/- 0.43",
    },
    "Molecule2": {
        "Compound": "Compound 3",
        "Role": "Waheed derivative",
        "Experimental PAMPA": "12.1 +/- 0.27",
    },
    "Molecule3": {
        "Compound": "Compound 7",
        "Role": "Waheed derivative",
        "Experimental PAMPA": "11.7 +/- 0.51",
    },
    "Molecule4": {
        "Compound": "Donepezil",
        "Role": "Positive PAMPA control",
        "Experimental PAMPA": "22.4 +/- 0.49",
    },
    "Molecule5": {
        "Compound": "Norfloxacin",
        "Role": "Negative PAMPA control",
        "Experimental PAMPA": "1.43 +/- 0.08",
    },
}

THESIS_DRUGBANK_TOP10 = [
    {"DrugBank ID": "DB06209", "Thesis-reported name": "Prasugrel", "Thesis probability": 0.980},
    {"DrugBank ID": "DB01656", "Thesis-reported name": "Vatalanib", "Thesis probability": 0.978},
    {"DrugBank ID": "DB00838", "Thesis-reported name": "Clopidogrel", "Thesis probability": 0.976},
    {"DrugBank ID": "DB02300", "Thesis-reported name": "Calcipotriol", "Thesis probability": 0.970},
    {"DrugBank ID": "DB00317", "Thesis-reported name": "Gefitinib", "Thesis probability": 0.970},
    {"DrugBank ID": "DB00401", "Thesis-reported name": "Propranolol", "Thesis probability": 0.970},
    {"DrugBank ID": "DB00559", "Thesis-reported name": "Verapamil", "Thesis probability": 0.970},
    {"DrugBank ID": "DB04967", "Thesis-reported name": "Lucanthone", "Thesis probability": 0.970},
    {"DrugBank ID": "DB04715", "Thesis-reported name": "Imidazopyridazine", "Thesis probability": 0.970},
    {"DrugBank ID": "DB00269", "Thesis-reported name": "Chlorpromazine", "Thesis probability": 0.960},
]


def ensure_dirs() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)


def normalize_ascii(value: object) -> str:
    text = str(value)
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")


def lipinski_to_english(value: object) -> str:
    normalized = normalize_ascii(value).upper()
    if normalized == "SI":
        return "Yes"
    if normalized == "NO":
        return "No"
    if normalized == "NO EVALUABLE":
        return "Not evaluable"
    return str(value)


def parse_sdf_drugbank_metadata(path: Path = SDF_PATH) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}

    fields = {
        "DRUGBANK_ID": "DrugBank ID",
        "DRUGBANK_GENERIC_NAME": "Generic name",
        "DRUGBANK_CANONICAL_SMILES": "SMILES",
    }
    records: dict[str, dict[str, str]] = {}
    for block in path.read_text(encoding="utf-8", errors="ignore").split("$$$$"):
        values: dict[str, str] = {}
        for tag, column in fields.items():
            match = re.search(rf"> <{re.escape(tag)}>\s*\n(.*?)(?:\n\n|\Z)", block, flags=re.S)
            if match:
                values[column] = match.group(1).strip().replace("\n", " ")
        drugbank_id = values.get("DrugBank ID")
        if drugbank_id:
            records[drugbank_id] = values
    return records


def escape_latex(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def write_csv_and_latex_table(
    df: pd.DataFrame,
    stem: str,
    caption: str,
    label: str,
    alignment: str | None = None,
) -> None:
    csv_path = TABLES / f"{stem}.csv"
    tex_path = TABLES / f"{stem}.tex"
    df.to_csv(csv_path, index=False)

    alignment = alignment or ("l" + "r" * (len(df.columns) - 1))
    with tex_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\\begin{table}[H]\n")
        handle.write("\\centering\n")
        handle.write(f"\\caption{{{escape_latex(caption)}}}\n")
        handle.write(f"\\label{{{label}}}\n")
        handle.write(f"\\begin{{tabular}}{{{alignment}}}\n")
        handle.write("\\toprule\n")
        handle.write(" & ".join(escape_latex(col) for col in df.columns) + " \\\\\n")
        handle.write("\\midrule\n")
        for _, row in df.iterrows():
            handle.write(" & ".join(escape_latex(value) for value in row.tolist()) + " \\\\\n")
        handle.write("\\bottomrule\n")
        handle.write("\\end{tabular}\n")
        handle.write("\\end{table}\n")


def dataset_composition() -> pd.DataFrame:
    rows = []
    for name, path in DATASETS:
        data = pd.read_csv(path)
        counts = data["Actividad"].value_counts()
        rows.append(
            {
                "Dataset": name,
                "Total": len(data),
                "Permeable": int(counts.get("Act1", 0)),
                "Non-permeable": int(counts.get("Act-1", 0)),
                "Permeable (%)": round(100 * counts.get("Act1", 0) / len(data), 1),
            }
        )
    df = pd.DataFrame(rows)
    write_csv_and_latex_table(
        df,
        "dataset_composition",
        "Dataset composition generated from the curated CSV files.",
        "tab:py_dataset_composition",
    )
    return df


def final_metrics_table() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "results/metrics/evaluacion_final_datasets.csv")
    rounded = df.copy()
    for col in rounded.columns:
        if col != "Dataset":
            rounded[col] = rounded[col].map(lambda value: f"{value:.3f}")
    write_csv_and_latex_table(
        rounded,
        "final_metrics",
        "Final model metrics generated from the stored evaluation table.",
        "tab:py_final_metrics",
        alignment="lrrrrrr",
    )
    return df


def cv_metrics_table() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "results/metrics/cv_results_comparison.csv")
    cols = ["K", "Accuracy_mean", "Sensibilidad_mean", "Especificidad_mean", "AUC_mean", "F1-Score_mean"]
    out = df[cols].copy()
    out.columns = ["K", "Accuracy", "Sensitivity", "Specificity", "AUC", "F1-score"]
    for col in out.columns:
        if col != "K":
            out[col] = out[col].map(lambda value: f"{value:.3f}")
    write_csv_and_latex_table(
        out,
        "cross_validation_metrics",
        "Cross-validation metrics generated from the reproducible results.",
        "tab:py_cross_validation",
        alignment="rrrrrr",
    )
    return df


# Kept only as a comparison point for the first manuscript draft; main() uses
# drugbank_summary_tables_named(), which normalizes Lipinski labels and adds names.
def drugbank_summary_tables_legacy() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "results/screening/DrugBank_Candidatos_Tesis.csv")
    lipinski_map = {"SÍ": "Yes", "SI": "Yes", "NO": "No", "No evaluable": "Not evaluable"}
    df = df.copy()
    df["Lipinski_English"] = df["Lipinski_Viable"].map(lipinski_map).fillna(df["Lipinski_Viable"])
    summary = pd.DataFrame(
        [
            {"Metric": "Final candidates", "Value": len(df)},
            {"Metric": "Inside applicability domain", "Value": int((df["Dominio_AD"] == "DENTRO").sum())},
            {"Metric": "Outside applicability domain", "Value": int((df["Dominio_AD"] == "FUERA").sum())},
            {"Metric": "Lipinski viable", "Value": int((df["Lipinski_English"] == "Yes").sum())},
            {"Metric": "Lipinski non-viable", "Value": int((df["Lipinski_English"] == "No").sum())},
            {"Metric": "Not evaluable by Lipinski", "Value": int((df["Lipinski_English"] == "Not evaluable").sum())},
            {"Metric": "Median probability", "Value": f"{df['Probabilidad'].median():.3f}"},
            {"Metric": "Maximum probability", "Value": f"{df['Probabilidad'].max():.3f}"},
        ]
    )
    write_csv_and_latex_table(
        summary,
        "drugbank_screening_summary",
        "DrugBank screening summary generated from the final candidate table.",
        "tab:py_drugbank_summary",
        alignment="lr",
    )

    top = df[["DrugBank_ID", "Probabilidad", "Leverage", "MW", "LogP", "Lipinski_English"]].head(10).copy()
    top.columns = ["DrugBank ID", "Probability", "Leverage", "MW", "LogP", "Lipinski"]
    for col in ["Probability", "Leverage", "MW", "LogP"]:
        top[col] = top[col].map(lambda value: f"{value:.3f}" if col != "MW" else f"{value:.2f}")
    write_csv_and_latex_table(
        top,
        "top_drugbank_candidates",
        "Top ten DrugBank candidates ranked by predicted PAMPA permeability probability.",
        "tab:py_top_drugbank",
        alignment="lrrrrl",
    )
    return df


def drugbank_summary_tables_named() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "results/screening/DrugBank_Candidatos_Tesis.csv")
    df = df.copy()
    df["Lipinski_English"] = df["Lipinski_Viable"].map(lipinski_to_english)
    inside_ad = df["Dominio_AD"] == "DENTRO"
    lipinski_yes = df["Lipinski_English"] == "Yes"

    summary = pd.DataFrame(
        [
            {"Metric": "Final candidates", "Value": len(df)},
            {"Metric": "Inside applicability domain", "Value": int(inside_ad.sum())},
            {"Metric": "Outside applicability domain", "Value": int((df["Dominio_AD"] == "FUERA").sum())},
            {"Metric": "Lipinski viable", "Value": int(lipinski_yes.sum())},
            {"Metric": "Lipinski non-viable", "Value": int((df["Lipinski_English"] == "No").sum())},
            {"Metric": "Not evaluable by Lipinski", "Value": int((df["Lipinski_English"] == "Not evaluable").sum())},
            {"Metric": "Inside AD and Lipinski viable", "Value": int((inside_ad & lipinski_yes).sum())},
            {"Metric": "Median probability", "Value": f"{df['Probabilidad'].median():.3f}"},
            {"Metric": "Maximum probability", "Value": f"{df['Probabilidad'].max():.3f}"},
        ]
    )
    write_csv_and_latex_table(
        summary,
        "drugbank_screening_summary",
        "DrugBank screening summary generated from the final candidate table.",
        "tab:py_drugbank_summary",
        alignment="lr",
    )

    flow = pd.DataFrame(
        [
            {
                "Stage": "Complete DrugBank source",
                "Compounds": ">10000",
                "Criterion": "Starting screening library before descriptor availability and curation",
            },
            {
                "Stage": "High-probability candidates",
                "Compounds": len(df),
                "Criterion": "Predicted permeable probability >= 0.60",
            },
            {
                "Stage": "Inside applicability domain",
                "Compounds": int(inside_ad.sum()),
                "Criterion": "Leverage h <= 0.0083",
            },
            {
                "Stage": "Final prioritized candidates",
                "Compounds": int((inside_ad & lipinski_yes).sum()),
                "Criterion": "Inside AD and Lipinski viable",
            },
        ]
    )
    write_csv_and_latex_table(
        flow,
        "drugbank_filtering_flow",
        "DrugBank virtual-screening funnel generated from the final candidate table.",
        "tab:py_drugbank_flow",
        alignment="lrp{0.52\\textwidth}",
    )

    metadata = parse_sdf_drugbank_metadata()
    df["Generic name"] = df["DrugBank_ID"].map(
        lambda drugbank_id: metadata.get(str(drugbank_id), {}).get("Generic name", "Not available")
    )
    top = df[["DrugBank_ID", "Generic name", "Probabilidad", "Leverage", "MW", "LogP", "Lipinski_English"]].head(10).copy()
    top.columns = ["DrugBank ID", "Generic name", "Probability", "Leverage", "MW", "LogP", "Lipinski"]
    for col in ["Probability", "Leverage", "MW", "LogP"]:
        top[col] = top[col].map(lambda value: f"{value:.3f}" if col != "MW" else f"{value:.2f}")
    write_csv_and_latex_table(
        top,
        "top_drugbank_candidates",
        "Top ten DrugBank candidates ranked by predicted PAMPA permeability probability with names recovered from the local DrugBank SDF metadata.",
        "tab:py_top_drugbank",
        alignment="lp{0.28\\textwidth}rrrrl",
    )
    return df


def set_plot_style() -> None:
    sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
    plt.rcParams["figure.dpi"] = 150
    plt.rcParams["savefig.dpi"] = 300
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["axes.spines.right"] = False


def plot_dataset_distribution(composition: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    x = np.arange(len(composition))
    ax.bar(x, composition["Non-permeable"], label="Non-permeable", color="#5B667A")
    ax.bar(
        x,
        composition["Permeable"],
        bottom=composition["Non-permeable"],
        label="Permeable",
        color="#2A9D8F",
    )
    for index, row in composition.iterrows():
        ax.text(index, row["Total"] + 60, str(row["Total"]), ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x)
    ax.set_xticklabels(composition["Dataset"])
    ax.set_ylabel("Number of compounds")
    ax.set_title("Class distribution of PAMPA datasets")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "python_dataset_class_distribution.png", bbox_inches="tight")
    plt.close(fig)


def plot_metric_heatmap(metrics: pd.DataFrame) -> None:
    plot_df = metrics.set_index("Dataset")
    fig, ax = plt.subplots(figsize=(8.2, 3.7))
    sns.heatmap(
        plot_df,
        annot=True,
        fmt=".3f",
        cmap="viridis",
        vmin=0,
        vmax=1,
        linewidths=0.4,
        cbar_kws={"label": "Metric value"},
        ax=ax,
    )
    ax.set_title("Final model performance across validation levels")
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    fig.savefig(FIGURES / "python_final_metrics_heatmap.png", bbox_inches="tight")
    plt.close(fig)


def plot_confusion_matrices() -> None:
    model = joblib.load(ROOT / "models/best_rf_pampa.pkl")
    features = list(model.feature_names_in_)
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.3))
    for ax, (name, path) in zip(axes, DATASETS, strict=True):
        data = pd.read_csv(path)
        x = data[features]
        y = data["Actividad"].map(LABEL_MAP).astype(int)
        pred = model.predict(x)
        cm = confusion_matrix(y, pred, labels=[1, 0])
        sns.heatmap(
            cm,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            xticklabels=["Pred. permeable", "Pred. non-perm."],
            yticklabels=["Obs. permeable", "Obs. non-perm."],
            linewidths=0.5,
            ax=ax,
        )
        ax.set_title(name)
        ax.set_xlabel("")
        ax.set_ylabel("")
    fig.suptitle("Confusion matrices for the final PAMPA model", y=1.05)
    fig.tight_layout()
    fig.savefig(FIGURES / "python_confusion_matrices.png", bbox_inches="tight")
    plt.close(fig)


def plot_drugbank_probability_distribution(drugbank: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    sns.histplot(drugbank["Probabilidad"], bins=24, color="#457B9D", edgecolor="white", ax=ax)
    ax.axvline(drugbank["Probabilidad"].median(), color="#E76F51", linestyle="--", label="Median")
    ax.set_xlabel("Predicted permeability probability")
    ax.set_ylabel("Number of candidates")
    ax.set_title("Probability distribution of final DrugBank candidates")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES / "python_drugbank_probability_distribution.png", bbox_inches="tight")
    plt.close(fig)


def plot_drugbank_leverage(drugbank: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6))
    palette = {"DENTRO": "#2A9D8F", "FUERA": "#E76F51"}
    sns.scatterplot(
        data=drugbank,
        x="Leverage",
        y="Probabilidad",
        hue="Dominio_AD",
        style="Lipinski_Viable",
        palette=palette,
        alpha=0.8,
        s=45,
        ax=ax,
    )
    ax.axvline(0.0083, color="#30343F", linestyle="--", linewidth=1, label="h* = 0.0083")
    ax.set_xlabel("Leverage")
    ax.set_ylabel("Predicted permeability probability")
    ax.set_title("Applicability-domain profile of DrugBank candidates")
    ax.legend(frameon=False, bbox_to_anchor=(1.02, 1), loc="upper left")
    fig.tight_layout()
    fig.savefig(FIGURES / "python_drugbank_leverage_probability.png", bbox_inches="tight")
    plt.close(fig)


def pre_screening_named_table() -> pd.DataFrame:
    pre = pd.read_csv(ROOT / "results/screening/Pre_Cribado_5_Moleculas.csv")
    rows = []
    for _, row in pre.iterrows():
        metadata = PRESCREENING_METADATA[str(row["ID_Molecula"])]
        probability = float(row["Probabilidad_Permeable"])
        rows.append(
            {
                "Internal ID": row["ID_Molecula"],
                "Compound/control": metadata["Compound"],
                "Role": metadata["Role"],
                "Probability": f"{probability:.3f}",
                "Model call": "Permeable" if probability >= 0.5 else "Non-permeable",
                "Experimental PAMPA": metadata["Experimental PAMPA"],
            }
        )
    out = pd.DataFrame(rows).sort_values("Probability", ascending=False)
    write_csv_and_latex_table(
        out,
        "pre_screening_named",
        "Five-molecule prospective pre-screening with thesis compound/control names and experimental PAMPA values.",
        "tab:py_prescreening_named",
        alignment="llp{0.22\\textwidth}rll",
    )
    return out


def drugbank_thesis_top10_table(drugbank: pd.DataFrame) -> pd.DataFrame:
    metadata = parse_sdf_drugbank_metadata()
    rows = []
    indexed = drugbank.set_index("DrugBank_ID")
    for item in THESIS_DRUGBANK_TOP10:
        drugbank_id = item["DrugBank ID"]
        current = indexed.loc[drugbank_id] if drugbank_id in indexed.index else None
        sdf_name = metadata.get(drugbank_id, {}).get("Generic name", "Not available")
        thesis_name = item["Thesis-reported name"]
        rows.append(
            {
                "DrugBank ID": drugbank_id,
                "Thesis-reported name": thesis_name,
                "SDF-verified name": sdf_name,
                "Thesis probability": f"{item['Thesis probability']:.3f}",
                "Current probability": "Not in CSV" if current is None else f"{float(current['Probabilidad']):.3f}",
                "Name audit": "Match" if normalize_ascii(thesis_name).lower() == normalize_ascii(sdf_name).lower() else "Check ID/name",
            }
        )
    out = pd.DataFrame(rows)
    write_csv_and_latex_table(
        out,
        "drugbank_thesis_reported_top10",
        "DrugBank top-ten list reported in the thesis, cross-checked against local DrugBank SDF metadata and the current reproducible candidate table.",
        "tab:py_drugbank_thesis_top10",
        alignment="lp{0.18\\textwidth}p{0.24\\textwidth}rrl",
    )
    return out


def plot_drugbank_filtering_flow(drugbank: pd.DataFrame) -> None:
    lipinski_yes = drugbank["Lipinski_English"] == "Yes"
    inside_ad = drugbank["Dominio_AD"] == "DENTRO"
    stages = [
        ("Source", 10000),
        ("P >= 0.60", len(drugbank)),
        ("Inside AD", int(inside_ad.sum())),
        ("AD + Lipinski", int((inside_ad & lipinski_yes).sum())),
    ]
    labels = [stage for stage, _ in stages]
    values = [value for _, value in stages]

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    colors = ["#5B667A", "#457B9D", "#2A9D8F", "#264653"]
    bars = ax.bar(labels, values, color=colors)
    for bar, value in zip(bars, values, strict=True):
        display_value = ">10000" if value == 10000 else str(value)
        ax.text(bar.get_x() + bar.get_width() / 2, value * 1.02, display_value, ha="center", va="bottom", fontsize=9)
    ax.set_yscale("log")
    ax.set_ylabel("Compounds (log scale)")
    ax.set_title("DrugBank virtual-screening funnel")
    fig.tight_layout()
    fig.savefig(FIGURES / "python_drugbank_filtering_flow.png", bbox_inches="tight")
    plt.close(fig)


def export_pre_screening_structure_crop() -> None:
    try:
        import pypdfium2 as pdfium
        from PIL import ImageEnhance
    except ImportError as exc:
        raise RuntimeError("pypdfium2 and pillow are required to regenerate the thesis structure crop") from exc

    pdf = pdfium.PdfDocument(str(THESIS_PDF))
    page = pdf[42]
    image = page.render(scale=3.0).to_pil()
    crop = image.crop((135, 555, 1650, 1715))
    crop = ImageEnhance.Contrast(crop).enhance(1.08)
    crop.save(FIGURES / "python_pre_screening_structures.png")


def copy_static_figures() -> None:
    for filename in ["SHAP_Bar_PAMPA.png", "SHAP_Beeswarm_PAMPA.png"]:
        source = ROOT / "results/figures" / filename
        if source.exists():
            shutil.copy2(source, FIGURES / filename)


def plot_pre_screening() -> None:
    pre = pd.read_csv(ROOT / "results/screening/Pre_Cribado_5_Moleculas.csv")
    pre["Compound"] = pre["ID_Molecula"].map(lambda value: PRESCREENING_METADATA[str(value)]["Compound"])
    pre = pre.sort_values("Probabilidad_Permeable", ascending=True)
    colors = ["#E76F51" if value < 0.5 else "#2A9D8F" for value in pre["Probabilidad_Permeable"]]
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.barh(pre["Compound"], pre["Probabilidad_Permeable"], color=colors)
    ax.axvline(0.5, color="#30343F", linestyle="--", linewidth=1, label="Decision threshold")
    for y, value in enumerate(pre["Probabilidad_Permeable"]):
        ax.text(value + 0.015, y, f"{value:.3f}", va="center", fontsize=9)
    ax.set_xlim(0, 0.8)
    ax.set_xlabel("Predicted permeability probability")
    ax.set_ylabel("")
    ax.set_title("Prospective pre-screening predictions")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIGURES / "python_pre_screening_probabilities.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    ensure_dirs()
    set_plot_style()

    composition = dataset_composition()
    metrics = final_metrics_table()
    cv_metrics_table()
    pre_screening_named_table()
    drugbank = drugbank_summary_tables_named()
    drugbank_thesis_top10_table(drugbank)

    copy_static_figures()
    export_pre_screening_structure_crop()
    plot_dataset_distribution(composition)
    plot_metric_heatmap(metrics)
    plot_confusion_matrices()
    plot_drugbank_probability_distribution(drugbank)
    plot_drugbank_leverage(drugbank)
    plot_drugbank_filtering_flow(drugbank)
    plot_pre_screening()

    print(f"Tables written to {TABLES}")
    print(f"Figures written to {FIGURES}")


if __name__ == "__main__":
    main()

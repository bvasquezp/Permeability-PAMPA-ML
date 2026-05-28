"""Generate, run, and summarize WEKA attribute-selection votes.

This is the maintained replacement for the exploratory `weka_cmd1.py`.
It runs ten selector combinations:

- WrapperSubsetEval + J48 with five search strategies.
- WrapperSubsetEval + IBk with the same five search strategies.

The resulting logs can be converted into a consensus table where each
selected descriptor receives one vote per WEKA run.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

import pandas as pd


CLASSIFIERS = {
    "J48": "weka.classifiers.trees.J48",
    "IBk": "weka.classifiers.lazy.IBk",
}

SEARCHERS = {
    "BestFirst": "weka.attributeSelection.BestFirst",
    "GeneticSearch": "weka.attributeSelection.GeneticSearch",
    "LinearForwardSelection": "weka.attributeSelection.LinearForwardSelection",
    "RankSearch": "weka.attributeSelection.RankSearch",
    "SubsetSizeForwardSelection": "weka.attributeSelection.SubsetSizeForwardSelection",
}


@dataclass(frozen=True)
class WekaRun:
    classifier_name: str
    classifier: str
    search_name: str
    search: str

    @property
    def log_name(self) -> str:
        return f"{self.classifier_name}_{self.search_name}.log"


def default_runs() -> list[WekaRun]:
    return [
        WekaRun(classifier_name, classifier, search_name, search)
        for classifier_name, classifier in CLASSIFIERS.items()
        for search_name, search in SEARCHERS.items()
    ]


def build_command(weka_jar: Path, input_arff: Path, run: WekaRun) -> list[str]:
    return [
        "java",
        "-cp",
        str(weka_jar),
        "weka.attributeSelection.WrapperSubsetEval",
        "-B",
        run.classifier,
        "-F",
        "5",
        "-T",
        "0.01",
        "-R",
        "1",
        "-s",
        run.search,
        "-i",
        str(input_arff),
    ]


def write_commandlines(weka_jar: Path, input_arff: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        for run in default_runs():
            handle.write(" ".join(f'"{part}"' if " " in part else part for part in build_command(weka_jar, input_arff, run)))
            handle.write("\n")


def run_weka_command(weka_jar: Path, input_arff: Path, run: WekaRun, logs_dir: Path) -> Path:
    logs_dir.mkdir(parents=True, exist_ok=True)
    command = build_command(weka_jar, input_arff, run)
    log_path = logs_dir / run.log_name

    start = time.time()
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    end = time.time()

    with log_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("=== Run information ===\n")
        handle.write(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start))}\n")
        handle.write(f"Duration_seconds: {end - start:.2f}\n")
        handle.write(f"Classifier: {run.classifier_name}\n")
        handle.write(f"Search: {run.search_name}\n")
        handle.write(f"Return_code: {result.returncode}\n")
        handle.write(f"Command: {' '.join(command)}\n\n")
        handle.write("=== STDOUT ===\n")
        handle.write(result.stdout)
        handle.write("\n=== STDERR ===\n")
        handle.write(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"WEKA failed for {run.log_name}; see {log_path}")
    return log_path


def run_all(weka_jar: Path, input_arff: Path, logs_dir: Path, workers: int) -> list[Path]:
    logs = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(run_weka_command, weka_jar, input_arff, run, logs_dir): run
            for run in default_runs()
        }
        for future in as_completed(futures):
            logs.append(future.result())
    return sorted(logs)


def parse_index_selection(text: str) -> list[int]:
    """Parse WEKA-like index strings such as `1,4,6-8`."""
    selected: set[int] = set()
    for token in re.findall(r"\d+(?:-\d+)?", text):
        if "-" in token:
            start, end = token.split("-", 1)
            selected.update(range(int(start), int(end) + 1))
        else:
            selected.add(int(token))
    return sorted(selected)


def selected_indices_from_log(path: Path) -> list[int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    patterns = [
        r"Selected attributes:\s*([0-9,\-\s]+)",
        r"Selected attributes are:\s*([0-9,\-\s]+)",
        r"Selected attributes\s*\n\s*([0-9,\-\s]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return parse_index_selection(match.group(1))
    return []


def attribute_names_from_arff(path: Path) -> list[str]:
    names = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.lower().startswith("@data"):
            break
        if stripped.lower().startswith("@attribute"):
            parts = stripped.split(maxsplit=2)
            if len(parts) >= 2:
                names.append(parts[1].strip("'\""))
    return names


def consensus_from_logs(logs_dir: Path, arff_path: Path, output_csv: Path) -> pd.DataFrame:
    names = attribute_names_from_arff(arff_path)
    votes: Counter[str] = Counter()
    source_runs: dict[str, list[str]] = {}

    for log_path in sorted(logs_dir.glob("*.log")):
        for index in selected_indices_from_log(log_path):
            if 1 <= index <= len(names):
                descriptor = names[index - 1]
            else:
                descriptor = f"INDEX_OUT_OF_RANGE_{index}"
            votes[descriptor] += 1
            source_runs.setdefault(descriptor, []).append(log_path.stem)

    rows = [
        {
            "Descriptor": descriptor,
            "Votos": count,
            "Frecuencia (%)": round((count / max(1, len(list(logs_dir.glob('*.log'))))) * 100, 3),
            "Runs": ";".join(source_runs.get(descriptor, [])),
        }
        for descriptor, count in votes.most_common()
    ]
    df = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False, quoting=csv.QUOTE_MINIMAL)
    return df


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate", help="Write the ten WEKA command lines.")
    generate.add_argument("--weka-jar", required=True, type=Path)
    generate.add_argument("--input-arff", required=True, type=Path)
    generate.add_argument("--output", default=Path("results/weka/commandlines.txt"), type=Path)

    run = subparsers.add_parser("run", help="Run all WEKA selector combinations.")
    run.add_argument("--weka-jar", required=True, type=Path)
    run.add_argument("--input-arff", required=True, type=Path)
    run.add_argument("--logs-dir", default=Path("results/weka/logs"), type=Path)
    run.add_argument("--workers", default=4, type=int)

    consensus = subparsers.add_parser("consensus", help="Build a descriptor-vote table from WEKA logs.")
    consensus.add_argument("--logs-dir", default=Path("results/weka/logs"), type=Path)
    consensus.add_argument("--input-arff", required=True, type=Path)
    consensus.add_argument("--output", default=Path("results/weka/descriptor_consensus.csv"), type=Path)

    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "generate":
        write_commandlines(args.weka_jar, args.input_arff, args.output)
        print(f"Command lines written to {args.output}")
    elif args.command == "run":
        logs = run_all(args.weka_jar, args.input_arff, args.logs_dir, args.workers)
        print(f"WEKA finished. Logs: {len(logs)}")
    elif args.command == "consensus":
        df = consensus_from_logs(args.logs_dir, args.input_arff, args.output)
        print(f"Consensus written to {args.output} ({len(df)} descriptors)")


if __name__ == "__main__":
    main()

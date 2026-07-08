"""Literature-insight utilities for the PAMPA QSAR manuscript."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import requests


CITE_RE = re.compile(r"\\(?:cite|citep|citet|parencite|textcite)\{([^}]+)\}")
BIB_ENTRY_RE = re.compile(r"@\w+\s*\{\s*([^,\s]+)\s*,", re.MULTILINE)
FIELD_RE = re.compile(r"^\s*(\w+)\s*=\s*[\{\"](.+?)[\}\"],?\s*$")


def parse_bibtex(path: Path) -> dict[str, dict[str, str]]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    entries: dict[str, dict[str, str]] = {}
    matches = list(BIB_ENTRY_RE.finditer(text))
    for idx, match in enumerate(matches):
        key = match.group(1).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        body = text[start:end]
        fields: dict[str, str] = {}
        for line in body.splitlines():
            field = FIELD_RE.match(line)
            if field:
                fields[field.group(1).lower()] = field.group(2).strip()
        entries[key] = fields
    return entries


def parse_citations(tex_path: Path) -> set[str]:
    text = tex_path.read_text(encoding="utf-8", errors="ignore")
    keys: set[str] = set()
    for match in CITE_RE.finditer(text):
        keys.update(key.strip() for key in match.group(1).split(",") if key.strip())
    return keys


def audit_manuscript(tex_path: Path, bib_path: Path) -> dict[str, Any]:
    entries = parse_bibtex(bib_path)
    cited = parse_citations(tex_path)
    bib_keys = set(entries)
    missing_doi_or_url = [
        key for key, fields in entries.items() if not fields.get("doi") and not fields.get("url")
    ]
    doi_to_keys: dict[str, list[str]] = {}
    for key, fields in entries.items():
        doi = fields.get("doi")
        if doi:
            doi_to_keys.setdefault(doi.lower(), []).append(key)
    duplicate_dois = {doi: keys for doi, keys in doi_to_keys.items() if len(keys) > 1}
    return {
        "tex_path": str(tex_path),
        "bib_path": str(bib_path),
        "bib_entries": len(entries),
        "cited_keys": len(cited),
        "undefined_citations": sorted(cited - bib_keys),
        "unused_bib_entries": sorted(bib_keys - cited),
        "entries_missing_doi_or_url": sorted(missing_doi_or_url),
        "duplicate_dois": duplicate_dois,
    }


def write_audit_markdown(audit: dict[str, Any], output: Path) -> None:
    lines = [
        "# PAMPA Literature Insights Audit",
        "",
        f"- TeX: `{audit['tex_path']}`",
        f"- BibTeX: `{audit['bib_path']}`",
        f"- Bibliography entries: {audit['bib_entries']}",
        f"- Cited keys: {audit['cited_keys']}",
        f"- Undefined citations: {len(audit['undefined_citations'])}",
        f"- Unused bibliography entries: {len(audit['unused_bib_entries'])}",
        f"- Entries missing DOI/URL: {len(audit['entries_missing_doi_or_url'])}",
        f"- Duplicate DOIs: {len(audit['duplicate_dois'])}",
        "",
        "## Undefined Citations",
        "",
    ]
    lines.extend(f"- `{key}`" for key in audit["undefined_citations"] or ["None"])
    lines.extend(["", "## Entries Missing DOI Or URL", ""])
    lines.extend(f"- `{key}`" for key in audit["entries_missing_doi_or_url"] or ["None"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def search_europepmc(query: str, max_results: int = 10) -> dict[str, Any]:
    params = {
        "query": f"({query}) OPEN_ACCESS:y",
        "format": "json",
        "pageSize": max_results,
        "resultType": "core",
        "sort": "CITED desc",
    }
    response = requests.get("https://www.ebi.ac.uk/europepmc/webservices/rest/search", params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    result_list = payload.get("resultList", {}).get("result", [])
    slim = [
        {
            "title": item.get("title"),
            "year": item.get("pubYear"),
            "journal": item.get("journalTitle"),
            "doi": item.get("doi"),
            "pmid": item.get("pmid"),
            "pmcid": item.get("pmcid"),
            "cited_by": item.get("citedByCount"),
            "url": f"https://europepmc.org/article/MED/{item.get('pmid')}" if item.get("pmid") else None,
        }
        for item in result_list
    ]
    return {
        "source": "Europe PMC",
        "query": query,
        "open_access_filter": True,
        "hit_count": int(payload.get("hitCount", 0)),
        "results": slim,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    audit = sub.add_parser("audit-manuscript", help="Audit citations against a BibTeX file.")
    audit.add_argument("--tex", type=Path, default=Path("manuscript/pampa_qsar_manuscript.tex"))
    audit.add_argument("--bib", type=Path, default=Path("manuscript/references.bib"))
    audit.add_argument("--output-json", type=Path, default=Path("results/science_skills/literature_audit.json"))
    audit.add_argument("--output-md", type=Path, default=Path("results/science_skills/literature_audit.md"))

    search = sub.add_parser("search-europepmc", help="Search open-access Europe PMC literature.")
    search.add_argument("--query", required=True)
    search.add_argument("--max-results", type=int, default=10)
    search.add_argument("--output-json", type=Path, default=Path("results/science_skills/europepmc_search.json"))
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "audit-manuscript":
        audit = audit_manuscript(args.tex, args.bib)
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(audit, indent=2, ensure_ascii=False), encoding="utf-8")
        write_audit_markdown(audit, args.output_md)
        print(json.dumps(audit, indent=2, ensure_ascii=False))
        return

    if args.command == "search-europepmc":
        result = search_europepmc(args.query, args.max_results)
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()


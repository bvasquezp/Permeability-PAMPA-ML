"""Model Context Protocol adapter for PAMPA QSAR molecular tools."""

from __future__ import annotations

import sys
from pathlib import Path

import requests

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.pampa_core import (
    calculate_all_rdkit_descriptors,
    calculate_descriptors as core_calculate_descriptors,
    evaluate_candidate,
    predict_permeability,
)

try:
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("PAMPA QSAR Server")
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("Warning: 'mcp' package not found. Running in CLI/fallback mode.", file=sys.stderr)

    class MockFastMCP:
        def __init__(self, name: str):
            self.name = name
            self.tools_dict = {}

        def tool(self):
            def decorator(func):
                self.tools_dict[func.__name__] = func
                return func

            return decorator

    mcp = MockFastMCP("PAMPA QSAR Server")


def calculate_rdkit_features(mol, feature_names):
    """Compatibility helper for legacy scripts that scored surrogate payloads directly."""
    from rdkit import Chem
    import numpy as np

    for atom in mol.GetAtoms():
        atom.SetIsotope(0)
    smiles = Chem.MolToSmiles(mol, canonical=True)
    descriptors = calculate_all_rdkit_descriptors(smiles)
    return np.array([float(descriptors.get(name, 0.0)) for name in feature_names]).reshape(1, -1)


@mcp.tool()
def predict_smiles(smiles: str, model_id: str = "active") -> dict:
    """Predict PAMPA permeability for a SMILES string through the governed core."""
    result = predict_permeability(smiles, model_id=model_id)
    if result["probability_permeable"] is None:
        return result
    result["prediction"] = "Permeable" if result["predicted_label"] == 1 else "Non-permeable"
    result["probability"] = result["probability_permeable"]
    return result


@mcp.tool()
def calculate_descriptors(smiles: str, descriptor_schema_id: str = "rdkit-basic") -> dict:
    """Calculate RDKit descriptors for a SMILES string."""
    return core_calculate_descriptors(smiles, descriptor_schema_id=descriptor_schema_id)


@mcp.tool()
def query_external_databases(query: str, db: str = "pubchem") -> dict:
    """Query PubChem for compound properties by name or SMILES."""
    db_lower = db.lower()
    if db_lower != "pubchem":
        return {"error": f"Unsupported database '{db}'. Only 'pubchem' is supported."}

    search_type = "smiles" if ("=" in query or "c" in query.lower() or "n" in query.lower()) else "name"
    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/"
        f"{search_type}/{query}/property/MolecularWeight,MolecularFormula,IUPACName,XLogP,TPSA/JSON"
    )
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return {"error": f"PubChem API returned status code {response.status_code}"}
        data = response.json()
        props = data["PropertyTable"]["Properties"][0]
        return {
            "source": "PubChem",
            "query": query,
            "properties": {
                "cid": props.get("CID"),
                "formula": props.get("MolecularFormula"),
                "mw": props.get("MolecularWeight"),
                "iupac_name": props.get("IUPACName"),
                "xlogp": props.get("XLogP"),
                "tpsa": props.get("TPSA"),
            },
        }
    except Exception as exc:
        return {"error": f"Request to PubChem failed: {exc}"}


@mcp.tool()
def evaluate_screening_candidate(smiles: str, model_id: str = "active") -> dict:
    """Evaluate a screening candidate with permeability, Lipinski and AD checks."""
    return evaluate_candidate(smiles, model_id=model_id)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        if HAS_MCP:
            mcp.run()
        else:
            print("Cannot run FastMCP server: 'mcp' package missing.", file=sys.stderr)
            sys.exit(1)
    else:
        print("PAMPA QSAR MCP Tool CLI. Usage: python mcp_server.py [predict|calc|query] [arguments]")
        if len(sys.argv) > 2:
            cmd = sys.argv[1]
            arg = sys.argv[2]
            if cmd == "predict":
                print(predict_smiles(arg))
            elif cmd == "calc":
                print(calculate_descriptors(arg))
            elif cmd == "query":
                print(query_external_databases(arg))
        else:
            aspirin = "CC(=O)Oc1ccccc1C(=O)O"
            print(predict_smiles(aspirin))


if __name__ == "__main__":
    main()

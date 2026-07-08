"""Core PAMPA QSAR operations used by CLI, MCP and agents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Crippen, Descriptors, Lipinski, MACCSkeys, rdFingerprintGenerator


MAX_FLOAT32 = 3.0e38
DEFAULT_REGISTRY = Path("models/model_registry.json")


def validate_smiles(smiles: str) -> dict[str, Any]:
    mol = Chem.MolFromSmiles(str(smiles))
    if mol is None:
        return {"valid": False, "canonical_smiles": None, "error": "Invalid SMILES structure"}
    for atom in mol.GetAtoms():
        atom.SetIsotope(0)
    return {"valid": True, "canonical_smiles": Chem.MolToSmiles(mol, canonical=True), "error": None}


def _mol_from_validated(smiles: str) -> Chem.Mol:
    validation = validate_smiles(smiles)
    if not validation["valid"]:
        raise ValueError(validation["error"])
    mol = Chem.MolFromSmiles(validation["canonical_smiles"])
    if mol is None:
        raise ValueError("Canonical SMILES could not be parsed.")
    return mol


def calculate_all_rdkit_descriptors(smiles: str) -> dict[str, float]:
    mol = _mol_from_validated(smiles)
    values: dict[str, float] = {}
    for name, func in Descriptors._descList:
        try:
            value = func(mol)
            if value is None or not np.isfinite(value):
                value = 0.0
            elif value > MAX_FLOAT32:
                value = MAX_FLOAT32
            elif value < -MAX_FLOAT32:
                value = -MAX_FLOAT32
            values[name] = float(value)
        except Exception:
            values[name] = 0.0
    return values


def calculate_rdkit_feature_map(
    smiles: str,
    include_maccs: bool = True,
    include_morgan: bool = False,
    morgan_bits: int = 256,
    morgan_radius: int = 2,
) -> dict[str, float]:
    mol = _mol_from_validated(smiles)
    values = calculate_all_rdkit_descriptors(smiles)
    if include_maccs:
        maccs = MACCSkeys.GenMACCSKeys(mol)
        for bit in range(1, maccs.GetNumBits()):
            values[f"MACCS_{bit:03d}"] = float(int(maccs.GetBit(bit)))
    if include_morgan:
        generator = rdFingerprintGenerator.GetMorganGenerator(radius=morgan_radius, fpSize=morgan_bits)
        morgan = generator.GetFingerprint(mol)
        for bit in range(morgan_bits):
            values[f"Morgan{morgan_radius}_{bit:04d}"] = float(int(morgan.GetBit(bit)))
    return values


def calculate_descriptors(smiles: str, descriptor_schema_id: str = "rdkit-basic") -> dict[str, Any]:
    validation = validate_smiles(smiles)
    if not validation["valid"]:
        return validation
    mol = _mol_from_validated(smiles)
    basic = {
        "canonical_smiles": validation["canonical_smiles"],
        "mw": float(Descriptors.MolWt(mol)),
        "logp": float(Crippen.MolLogP(mol)),
        "tpsa": float(Descriptors.TPSA(mol)),
        "hbd": int(Lipinski.NumHDonors(mol)),
        "hba": int(Lipinski.NumHAcceptors(mol)),
        "rotatable_bonds": int(Lipinski.NumRotatableBonds(mol)),
        "heavy_atoms": int(mol.GetNumHeavyAtoms()),
    }
    if descriptor_schema_id == "rdkit-all":
        basic["descriptors"] = calculate_all_rdkit_descriptors(smiles)
    return basic


def lipinski_summary(smiles: str) -> dict[str, Any]:
    desc = calculate_descriptors(smiles)
    if desc.get("valid") is False:
        return desc
    violations = int(desc["mw"] >= 500) + int(desc["logp"] >= 5.0) + int(desc["hbd"] >= 5) + int(desc["hba"] >= 10)
    return {
        "mw": round(float(desc["mw"]), 3),
        "logp": round(float(desc["logp"]), 3),
        "hbd": int(desc["hbd"]),
        "hba": int(desc["hba"]),
        "violations": violations,
        "pass": violations <= 1,
    }


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    if not path.exists():
        return {"active_model_id": None, "models": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_model(model_id: str = "active", registry_path: Path = DEFAULT_REGISTRY) -> tuple[str, dict[str, Any]]:
    registry = load_registry(registry_path)
    resolved_id = registry.get("active_model_id") if model_id == "active" else model_id
    if not resolved_id:
        raise ValueError("No active SMILES model is registered.")
    models = registry.get("models", {})
    if resolved_id not in models:
        raise ValueError(f"Model '{resolved_id}' is not present in {registry_path}.")
    return str(resolved_id), models[resolved_id]


def _feature_vector(smiles: str, feature_names: list[str]) -> pd.DataFrame:
    all_desc = calculate_rdkit_feature_map(smiles, include_maccs=True, include_morgan=True)
    row = {name: float(all_desc.get(name, 0.0)) for name in feature_names}
    return pd.DataFrame([row], columns=feature_names)


def predict_permeability(
    smiles: str,
    model_id: str = "active",
    registry_path: Path = DEFAULT_REGISTRY,
) -> dict[str, Any]:
    validation = validate_smiles(smiles)
    warnings: list[str] = []
    if not validation["valid"]:
        return {
            "canonical_smiles": None,
            "model_id": model_id,
            "model_status": "unavailable",
            "probability_permeable": None,
            "predicted_label": None,
            "lipinski": None,
            "applicability_domain": None,
            "approved_for_decision": False,
            "warnings": [validation["error"]],
        }

    try:
        resolved_id, entry = resolve_model(model_id, registry_path)
    except Exception as exc:
        return {
            "canonical_smiles": validation["canonical_smiles"],
            "model_id": model_id,
            "model_status": "unavailable",
            "probability_permeable": None,
            "predicted_label": None,
            "lipinski": lipinski_summary(smiles),
            "applicability_domain": None,
            "approved_for_decision": False,
            "warnings": [str(exc)],
        }

    status = str(entry.get("status", "candidate"))
    approved = status == "approved"
    if not approved:
        warnings.append(f"Model '{resolved_id}' status is '{status}', not approved.")

    payload = joblib.load(entry["path"])
    features = list(payload["features"])
    x_raw = _feature_vector(validation["canonical_smiles"], features)
    x_scaled = payload["scaler"].transform(x_raw)
    x_scaled_df = pd.DataFrame(x_scaled, columns=features)
    prob = float(payload["model"].predict_proba(x_scaled_df)[0, 1])
    decision_threshold = float(payload.get("decision_threshold", entry.get("decision_threshold", 0.5)))
    pred = int(prob >= decision_threshold)

    applicability = None
    if "Z_T_Z_pinv" in payload and "h_star" in payload:
        z = x_scaled_df.iloc[0].to_numpy()
        leverage = float(z.T @ payload["Z_T_Z_pinv"] @ z)
        h_star = float(payload["h_star"])
        applicability = {
            "leverage": round(leverage, 6),
            "h_star": round(h_star, 6),
            "in_domain": bool(leverage <= h_star),
        }
        if leverage > h_star:
            warnings.append("Molecule is outside the model applicability domain.")

    return {
        "canonical_smiles": validation["canonical_smiles"],
        "model_id": resolved_id,
        "model_status": status,
        "probability_permeable": prob,
        "predicted_label": pred,
        "decision_threshold": decision_threshold,
        "lipinski": lipinski_summary(smiles),
        "applicability_domain": applicability,
        "approved_for_decision": bool(approved and not warnings),
        "warnings": warnings,
    }


def evaluate_candidate(smiles: str, model_id: str = "active") -> dict[str, Any]:
    result = predict_permeability(smiles, model_id=model_id)
    if result["probability_permeable"] is None:
        result["candidate_status"] = "Unavailable"
        return result
    in_domain = bool((result["applicability_domain"] or {}).get("in_domain", False))
    lipinski_pass = bool((result["lipinski"] or {}).get("pass", False))
    is_candidate = result["probability_permeable"] >= 0.6 and in_domain and lipinski_pass
    result["candidate_status"] = "Approved" if is_candidate and result["approved_for_decision"] else "Experimental/Rejected"
    return result

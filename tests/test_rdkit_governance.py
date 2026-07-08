from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

from src.audit_rdkit_dataset import canonicalize_smiles, validate_target_inversion
from src.pampa_core import calculate_rdkit_feature_map, predict_permeability, validate_smiles
from src.train_rdkit_candidate import descriptor_frame, undersample_majority


def test_validate_smiles_canonicalizes_isotopes() -> None:
    result = validate_smiles("[13CH4]")
    assert result["valid"] is True
    assert result["canonical_smiles"] == "C"


def test_invalid_smiles_is_blocked() -> None:
    result = predict_permeability("not-a-smiles")
    assert result["approved_for_decision"] is False
    assert result["probability_permeable"] is None
    assert result["warnings"]


def test_candidate_model_is_not_approved_for_decision(tmp_path: Path) -> None:
    x = pd.DataFrame({"MolWt": [46.0, 180.0, 300.0, 500.0], "TPSA": [20.0, 40.0, 80.0, 120.0]})
    y = np.array([0, 0, 1, 1])
    scaler = StandardScaler().fit(x)
    xs = pd.DataFrame(scaler.transform(x), columns=x.columns)
    model = RandomForestClassifier(n_estimators=10, random_state=42).fit(xs, y)
    payload = {
        "model": model,
        "features": list(x.columns),
        "scaler": scaler,
        "Z_T_Z_pinv": np.linalg.pinv(xs.values.T @ xs.values),
        "h_star": 10.0,
    }
    model_path = tmp_path / "candidate.pkl"
    registry_path = tmp_path / "model_registry.json"
    joblib.dump(payload, model_path)
    registry_path.write_text(
        json.dumps(
            {
                "active_model_id": "toy",
                "models": {"toy": {"path": str(model_path), "status": "candidate"}},
            }
        ),
        encoding="utf-8",
    )

    result = predict_permeability("CCO", registry_path=registry_path)
    assert result["model_status"] == "candidate"
    assert result["approved_for_decision"] is False
    assert result["applicability_domain"]["in_domain"] is True


def test_registered_model_uses_payload_decision_threshold(tmp_path: Path) -> None:
    x = pd.DataFrame({"MolWt": [46.0, 180.0, 300.0, 500.0], "TPSA": [20.0, 40.0, 80.0, 120.0]})
    y = np.array([0, 0, 1, 1])
    scaler = StandardScaler().fit(x)
    xs = pd.DataFrame(scaler.transform(x), columns=x.columns)
    model = RandomForestClassifier(n_estimators=10, random_state=42).fit(xs, y)
    payload = {
        "model": model,
        "features": list(x.columns),
        "scaler": scaler,
        "Z_T_Z_pinv": np.linalg.pinv(xs.values.T @ xs.values),
        "h_star": 10.0,
        "decision_threshold": 0.99,
    }
    model_path = tmp_path / "approved.pkl"
    registry_path = tmp_path / "model_registry.json"
    joblib.dump(payload, model_path)
    registry_path.write_text(
        json.dumps(
            {
                "active_model_id": "toy",
                "models": {"toy": {"path": str(model_path), "status": "approved"}},
            }
        ),
        encoding="utf-8",
    )

    result = predict_permeability("CCO", registry_path=registry_path)
    assert result["decision_threshold"] == 0.99
    assert result["predicted_label"] == 0


def test_thesis_model_parameters_match_documented_operating_point() -> None:
    model = joblib.load("models/best_rf_pampa.pkl")
    params = model.get_params()
    assert params["class_weight"] == {0: 1.5, 1: 1}
    assert params["n_estimators"] == 500
    assert params["max_depth"] == 10
    assert params["min_samples_leaf"] == 4
    assert params["max_features"] == "sqrt"


def test_undersample_majority_balances_training_classes() -> None:
    x = pd.DataFrame({"value": range(10)})
    y = pd.Series([1, 1, 1, 1, 1, 1, 0, 0, 0, 0])
    x_bal, y_bal = undersample_majority(x, y)
    assert len(x_bal) == 8
    assert y_bal.value_counts().to_dict() == {0: 4, 1: 4}


def test_rdkit_maccs_feature_space_includes_structural_bits() -> None:
    features = calculate_rdkit_feature_map("CCO", include_maccs=True, include_morgan=False)
    assert "MolLogP" in features
    assert "MACCS_125" in features


def test_descriptor_frame_supports_rdkit_maccs_space() -> None:
    frame = descriptor_frame(pd.Series(["CCO"]), feature_space="rdkit_maccs")
    assert "MolLogP" in frame.columns
    assert "MACCS_125" in frame.columns


def test_canonicalize_smiles_strips_isotopes() -> None:
    assert canonicalize_smiles("[13CH4]") == "C"


@pytest.mark.skipif(not Path("dataset (7).xlsx").exists(), reason="local source workbook is not present")
def test_target_inversion_matches_thesis_csvs() -> None:
    raw = pd.read_excel("dataset (7).xlsx", sheet_name="Smiles")
    result = validate_target_inversion(raw, Path("data/raw/training_11.csv"), Path("data/raw/test_11.csv"))
    assert result["train_mismatches_after_inversion"] == 0
    assert result["test_mismatches_after_inversion"] == 0

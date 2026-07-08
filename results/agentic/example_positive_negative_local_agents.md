# Local PAMPA Agent Panel

- API required: `False`
- Model: `models/best_rf_pampa.pkl`
- Mode: thesis 11-descriptor panel
- Rows: 2
- Predicted permeable: 2
- Predicted non-permeable: 0

## Agent Status

- `DescriptorAgent`: pass
- `ChemicalAgent`: not_applicable
  - Warning: No SMILES column was provided; chemical structure checks were skipped.
- `ModelAgent`: pass
- `ApplicabilityDomainAgent`: pass
- `PhysicsAgent`: pass

## Predictions

| example_id                |   probability_permeable | predicted_class   | in_domain   | physics_interpretation         | local_agent_decision   |
|:--------------------------|------------------------:|:------------------|:------------|:-------------------------------|:-----------------------|
| positive_external_example |                0.775021 | PERMEABLE         | True        | strong_permeability_signal     | CANDIDATE_PERMEABLE    |
| negative_external_example |                0.546394 | PERMEABLE         | True        | borderline_permeability_signal | CANDIDATE_PERMEABLE    |

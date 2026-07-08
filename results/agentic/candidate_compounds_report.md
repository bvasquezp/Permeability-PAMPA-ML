# Local PAMPA Agent Panel

- API required: `False`
- Model: `models/best_rf_pampa.pkl`
- Mode: thesis 11-descriptor panel
- Rows: 18
- Predicted permeable: 12
- Predicted non-permeable: 6

## Agent Status

- `DescriptorAgent`: pass
- `ChemicalAgent`: not_applicable
  - Warning: No SMILES column was provided; chemical structure checks were skipped.
- `ModelAgent`: pass
- `ApplicabilityDomainAgent`: pass
- `PhysicsAgent`: pass

## Predictions

| probability_permeable | predicted_class | in_domain | physics_interpretation | local_agent_decision |
| --- | --- | --- | --- | --- |
| 0.06442354414682572 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.32533199049244105 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.29944823510656865 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.1441517844275893 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.12836190902802494 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.3930054499176119 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.6540957244734746 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.6471465136170265 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.664816232403008 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.6553399612228997 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.579243853735288 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.682360030527385 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.7114561609583783 | PERMEABLE | True | strong_permeability_signal | CANDIDATE_PERMEABLE |
| 0.5350740003458576 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.5934937802579234 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.6737682154735934 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.7165027171680152 | PERMEABLE | True | strong_permeability_signal | CANDIDATE_PERMEABLE |
| 0.6773479497755212 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |

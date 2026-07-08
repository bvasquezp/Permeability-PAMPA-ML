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
| 0.2994482351065686 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.14415178442758927 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.1283619090280249 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.3930054499176119 | NO_PERMEABLE | True | non_permeability_signal | LOW_PRIORITY_OR_NON_PERMEABLE |
| 0.6540957244734741 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.6471465136170261 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.664816232403008 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.6553399612228993 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.5792438537352879 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.682360030527385 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.7114561609583782 | PERMEABLE | True | strong_permeability_signal | CANDIDATE_PERMEABLE |
| 0.5350740003458574 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.5934937802579235 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.6737682154735937 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |
| 0.7165027171680153 | PERMEABLE | True | strong_permeability_signal | CANDIDATE_PERMEABLE |
| 0.677347949775521 | PERMEABLE | True | borderline_permeability_signal | CANDIDATE_PERMEABLE |

"""UltraThink reasoning engine: Multi-agent debate panels for molecular QSAR decisions."""

import json
from src.agentic.agents import (
    OrchestratorAgent,
    ModelOptimizerAgent,
    MoleculeDesignerAgent,
    ChemicalExplainerAgent,
)

def run_molecule_synthesis_debate(smiles: str) -> str:
    """Run a multi-agent debate panel to evaluate a molecule before recommending synthesis."""
    print(f"\n[UltraThink] Initializing panel debate for candidate: {smiles}")
    
    # 1. Initialize agents
    orchestrator = OrchestratorAgent()
    chemist = MoleculeDesignerAgent()
    statistician = ModelOptimizerAgent()
    explainer = ChemicalExplainerAgent()
    
    # Check if Gemini key is available
    if not orchestrator.llm.is_available():
        return (
            f"GEMINI_API_KEY not set. Cannot run panel debate for {smiles}.\n"
            "Simulating debate: Chemist approves structure, Statistician approves validation, Orchestrator recommends synthesis."
        )

    # 2. Explainer provides base descriptor profile
    base_explanation_prompt = (
        f"Provide a short physical-chemical profile of this SMILES: {smiles}. "
        "Summarize its Lipinski profile, polar surface, and structure."
    )
    explanation = explainer.run(base_explanation_prompt)
    print("\n[Chemical Profile]:\n", explanation)

    # 3. Chemist evaluates synthetic feasibility and medicinal chemistry drug-likeness
    chemist_prompt = (
        f"As a Medicinal Chemist, evaluate the synthetic feasibility and safety/ADME profile of {smiles}.\n"
        f"Chemical profile: {explanation}\n"
        "Provide your evaluation highlighting arguments for and against synthesis."
    )
    chemist_arguments = chemist.run(chemist_prompt)
    print("\n[Medicinal Chemist Arguments]:\n", chemist_arguments)

    # 4. Statistician evaluates QSAR reliability and applicability domain
    statistician_prompt = (
        f"As a Data Scientist / Statistician, evaluate the statistical confidence of predicting {smiles}.\n"
        f"Chemical profile: {explanation}\n"
        "Consider leverage, application domain checks, and model precision. Highlight potential pitfalls (e.g. out-of-domain risk)."
    )
    statistician_arguments = statistician.run(statistician_prompt)
    print("\n[Data Scientist Arguments]:\n", statistician_arguments)

    # 5. Orchestrator moderates and makes the final recommendation
    orchestrator_prompt = (
        f"You are the Moderator. Based on the following arguments, deliver the final synthesis decision for compound: {smiles}.\n\n"
        f"Medicinal Chemist Perspective:\n{chemist_arguments}\n\n"
        f"Data Scientist Perspective:\n{statistician_arguments}\n\n"
        "Synthesize both perspectives and output a final markdown report recommending whether to proceed with synthesis."
    )
    final_report = orchestrator.run(orchestrator_prompt)
    print("\n[Orchestrator Final Report]:\n", final_report)
    
    return final_report

if __name__ == "__main__":
    # Test panel debate
    run_molecule_synthesis_debate("CC(=O)Oc1ccccc1C(=O)O")

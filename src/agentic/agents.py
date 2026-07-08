"""Sub-agents definitions and Gemini API integration for QSAR Loop Engineering."""

import os
import json
import requests
import sys

class GeminiLLM:
    """Zero-dependency Gemini API client via REST."""
    def __init__(self, model_name="gemini-1.5-pro"):
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model_name = model_name
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def is_available(self):
        return len(self.api_key) > 0

    def generate(self, prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
        """Call Gemini API and return generated text."""
        if not self.api_key:
            return json.dumps({"error": "GEMINI_API_KEY environment variable not set."}) if json_mode else "Error: GEMINI_API_KEY not set."
            
        url = f"{self.base_url}/{self.model_name}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        
        contents = [{
            "parts": [{"text": prompt}]
        }]
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
            
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                resp_json = response.json()
                try:
                    text = resp_json["candidates"][0]["content"]["parts"][0]["text"]
                    return text.strip()
                except KeyError:
                    return json.dumps({"error": "Unexpected JSON response structure from Gemini API."}) if json_mode else "Error parsing Gemini response."
            else:
                err_msg = f"HTTP Error {response.status_code}: {response.text}"
                return json.dumps({"error": err_msg}) if json_mode else f"Error: {err_msg}"
        except Exception as e:
            return json.dumps({"error": str(e)}) if json_mode else f"Error making request: {str(e)}"

class BaseAgent:
    def __init__(self, name: str, role: str, system_instruction: str, model_name: str = "gemini-1.5-pro"):
        self.name = name
        self.role = role
        self.system_instruction = system_instruction
        self.llm = GeminiLLM(model_name=model_name)

    def run(self, prompt: str, json_mode: bool = False) -> str:
        sys_inst = f"You are {self.name}, acting as a {self.role}.\nInstructions:\n{self.system_instruction}"
        return self.llm.generate(prompt, system_instruction=sys_inst, json_mode=json_mode)

class OrchestratorAgent(BaseAgent):
    def __init__(self, model_name="gemini-1.5-pro"):
        super().__init__(
            name="QSAR Orchestrator",
            role="QSAR Project Manager and Workflow Coordinator",
            system_instruction=(
                "You coordinate the workflow between specialized sub-agents: FeatureSelector, ModelOptimizer, "
                "MoleculeDesigner, and ChemicalExplainer. Your goal is to design a molecular screening pipeline "
                "or model optimization run. Analyze tasks, delegate to agents, and consolidate findings into a final report."
            ),
            model_name=model_name
        )

class FeatureSelectorAgent(BaseAgent):
    def __init__(self, model_name="gemini-1.5-pro"):
        super().__init__(
            name="Feature Selector",
            role="Cheminformatics and Dimensionality Reduction Expert",
            system_instruction=(
                "You select molecular descriptors and fingerprints to retain for QSAR modeling. "
                "You optimize representation dimensionality, perform variance/correlation filtering, "
                "suggest consensus ranking based on machine learning importance, and evaluate feature redundancies."
            ),
            model_name=model_name
        )

class ModelOptimizerAgent(BaseAgent):
    def __init__(self, model_name="gemini-1.5-pro"):
        super().__init__(
            name="Model Optimizer",
            role="Machine Learning and QSAR Tuning Expert",
            system_instruction=(
                "You train, tune, and evaluate machine learning models (Random Forest, XGBoost, etc.) on tabular QSAR datasets. "
                "You propose hyperparameter tuning grids, check validation metrics (AUC, MCC, F1, Accuracy), "
                "assess model overfitting, and recommend parameters for serialization."
            ),
            model_name=model_name
        )

class MoleculeDesignerAgent(BaseAgent):
    def __init__(self, model_name="gemini-1.5-pro"):
        super().__init__(
            name="Molecule Designer",
            role="Medicinal Chemist and De Novo Molecular Designer",
            system_instruction=(
                "You generate new chemical compounds as SMILES. Based on feedback from the QSAR predictive model, "
                "you propose modifications, substitutions, or scaffold-based iterations to improve target probability. "
                "Ensure generated SMILES are syntactically valid and represent realistic chemical structures."
            ),
            model_name=model_name
        )

class ChemicalExplainerAgent(BaseAgent):
    def __init__(self, model_name="gemini-1.5-pro"):
        super().__init__(
            name="Chemical Explainer",
            role="Medicinal Chemistry Reasoning Agent",
            system_instruction=(
                "You analyze why a molecule is predicted as permeable or non-permeable. "
                "You relate calculated descriptors (LogP, TPSA, charge distribution, hydrogen bonds, leverage) "
                "to physiological absorption mechanisms (passive membrane diffusion, Lipinski rules). "
                "Provide detailed, chemically sound explanations."
            ),
            model_name=model_name
        )

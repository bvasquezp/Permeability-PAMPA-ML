"""UltraCode execution environment: Self-correction code generation, linting, and run execution."""

import os
import sys
import subprocess
import tempfile
from src.agentic.agents import OrchestratorAgent

class UltraCodeWorkspace:
    """A self-correcting environment for executing and validating agent-written scripts."""
    def __init__(self, model_name="gemini-1.5-pro"):
        self.orchestrator = OrchestratorAgent(model_name=model_name)

    def execute_script(self, script_path: str) -> dict:
        """Run the script and return completion status, stdout, and stderr."""
        python_exe = sys.executable
        try:
            result = subprocess.run(
                [python_exe, script_path],
                capture_output=True,
                text=True,
                timeout=15
            )
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "returncode": -1,
                "stdout": "",
                "stderr": "Execution timed out (exceeded 15 seconds)."
            }
        except Exception as e:
            return {
                "success": False,
                "returncode": -2,
                "stdout": "",
                "stderr": f"Subprocess start failed: {str(e)}"
            }

    def self_correct_code(self, task_description: str, target_path: str, initial_code: str, max_attempts: int = 3) -> bool:
        """Write, run, and iteratively correct code until it succeeds or max_attempts is reached."""
        print(f"\n[UltraCode] Starting self-correction loop for: {target_path}")
        
        current_code = initial_code
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        
        for attempt in range(max_attempts):
            print(f"--- Attempt {attempt+1} / {max_attempts} ---")
            
            # Write code to file
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(current_code)
                
            # Execute code
            res = self.execute_script(target_path)
            
            if res["success"]:
                print(f"[UltraCode] Script executed successfully in attempt {attempt+1}!")
                print(f"Stdout output:\n{res['stdout']}")
                return True
            else:
                print(f"[UltraCode] Script failed. Return code: {res['returncode']}")
                print(f"Stderr error:\n{res['stderr']}")
                
                if attempt == max_attempts - 1:
                    print("[UltraCode] Max attempts reached. Self-correction failed.")
                    return False
                    
                # If Gemini key is not set, we cannot do AI self-correction
                if not self.orchestrator.llm.is_available():
                    print("Error: GEMINI_API_KEY not set. Cannot run AI self-correction loop.")
                    return False
                    
                # Generate corrected code using LLM
                prompt = (
                    f"We are writing a script to accomplish the following task:\n"
                    f"{task_description}\n\n"
                    f"The code we wrote in the previous attempt was:\n"
                    f"```python\n{current_code}\n```\n\n"
                    f"When we ran it, it failed with the following error:\n"
                    f"```\n{res['stderr']}\n```\n\n"
                    f"Please rewrite the python script to fix the error. Return ONLY the code in a raw code block format. "
                    "Make sure it handles any missing variables, incorrect imports, or type errors."
                )
                
                resp = self.orchestrator.run(prompt)
                
                # Extract code from code block if returned with markdown
                if "```python" in resp:
                    current_code = resp.split("```python")[1].split("```")[0].strip()
                elif "```" in resp:
                    current_code = resp.split("```")[1].split("```")[0].strip()
                else:
                    current_code = resp.strip()
                    
        return False

if __name__ == "__main__":
    # Self-test workspace
    ws = UltraCodeWorkspace()
    # Let's write a buggy script and try to run it
    buggy = "import non_existent_library_pampa\nprint('hello')"
    ws.self_correct_code("Print hello and import a mock library", "scratch/test_buggy.py", buggy, max_attempts=1)

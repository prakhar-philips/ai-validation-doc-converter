import subprocess
import os
import tempfile

# Local LLM runner and model path
LLM_BINARY_PATH = r"C:\Users\320290805\Downloads\llama-b5849-bin-win-cpu-x64\main.exe"
MODEL_PATH = r"C:\Users\320290805\Downloads\llama-b5849-bin-win-cpu-x64\mistral-7b-instruct-v0.1.Q4_K_M.gguf"

def run_llm_with_prompt(prompt_text: str, input_text: str) -> str:
    if not os.path.exists(LLM_BINARY_PATH):
        return "❌ LLM binary not found."

    if not os.path.exists(MODEL_PATH):
        return "❌ Model file (.gguf) not found."

    try:
        # 👇 Use a better structured instruction prompt
        full_prompt = f"""You are an AI assistant trained to generate structured documentation.

Generate a Functional Requirements Specification (FRS) document from the provided User Requirement (URS).

The FRS should include:
- Purpose
- Functional Requirements
- Inputs
- Outputs
- Validation Criteria

--- USER PROMPT ---
{prompt_text}

--- URS CONTENT ---
{input_text}
"""

        # Save the full prompt to a temp file
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as tmpfile:
            tmpfile.write(full_prompt)
            tmpfile_path = tmpfile.name

        # 🛠️ Adjust prediction limit to avoid timeout
        command = [
            LLM_BINARY_PATH,
            "-m", MODEL_PATH,
            "--temp", "0.7",
            "--n-predict", "256",
            "--file", tmpfile_path
        ]

        result = subprocess.run(command, capture_output=True, text=True, timeout=180)

        # Clean up temp file
        os.remove(tmpfile_path)

        # Debug: print raw output (can be removed later)
        print("🔍 Raw LLM Output:\n", result.stdout)

        # Return full cleaned output (not split by ANSWER:)
        output = result.stdout.strip()
        return output if output else "[No meaningful output received.]"

    except subprocess.TimeoutExpired:
        return "❌ LLaMA generation timed out."
    except Exception as e:
        return f"[LLM Error] {e}"

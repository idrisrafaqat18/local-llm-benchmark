import sys
import ollama

# Updated to match your local Ollama inventory
REQUIRED_MODELS = [
    "qwen2.5-coder:3b",
    "qwen2.5:latest",
    "mistral:latest",
    "llama3.1:8b"
]

def verify_ollama_environment():
    """Verify Ollama connection and check if required models are pulled."""
    print("[*] Checking Ollama service availability...")
    try:
        response = ollama.list()
        # Handle response format across ollama-python library versions
        if isinstance(response, dict) and "models" in response:
            installed_models = [m.get("name", "") for m in response["models"]]
        elif hasattr(response, "models"):
            installed_models = [m.model for m in response.models]
        else:
            installed_models = []

        print(f"[+] Ollama daemon active. Found {len(installed_models)} model(s).")
        
        missing_models = []
        for model in REQUIRED_MODELS:
            # Match base model name prefix
            if not any(model in m for m in installed_models):
                missing_models.append(model)

        if missing_models:
            print(f"[!] Warning: Missing target benchmark models: {missing_models}")
            print(f"[!] Run 'ollama pull <model_name>' to install them.")
        else:
            print("[+] All target benchmark models are ready!")

        return True

    except Exception as e:
        print(f"[-] Error connecting to Ollama daemon: {e}")
        print("[-] Ensure Ollama service is running locally (`ollama serve`).")
        sys.exit(1)

if __name__ == "__main__":
    verify_ollama_environment()
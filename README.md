# Local LLM Evaluation & Benchmarking Pipeline

An offline, privacy-first AI benchmarking harness for local Large Language Models running on Ollama. This project evaluates model performance across latency, schema validation compliance via Pydantic, and generation reliability without relying on external cloud APIs.

## Key Features
- **Offline Inference**: Powered by local GGUF models via Ollama runtime.
- **Strict Schema Enforcement**: Pydantic validation for reliable JSON structured outputs.
- **Automated Benchmarking**: Measures latency, token completion speed, and schema pass/fail rates across custom test datasets.
- **Resilient Execution**: Retry mechanisms with validation error feedback loops.

## Tech Stack
- **Runtime**: Ollama
- **Language**: Python 3.10+
- **Data Validation**: Pydantic v2
- **Models Evaluated**: Qwen 2.5, Llama 3.2, Mistral

## Getting Started
1. Clone the repository.
2. Activate your virtual environment and run `pip install -r requirements.txt`.
3. Ensure Ollama is running locally with required models pulled (`ollama pull qwen2.5:3b`).
4. Execute `python main.py` to run the evaluation suite.
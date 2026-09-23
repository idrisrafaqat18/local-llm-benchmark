# Local LLM Benchmark

> A privacy-first, production-minded evaluation harness for structured local LLM inference.
>
> Compare Ollama models on schema compliance, latency, and recovery from malformed JSON without sending prompts to a cloud API.

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Runtime-Ollama-black?logo=ollama)](https://ollama.com/)
[![Pydantic](https://img.shields.io/badge/Validation-Pydantic%20v2-E92063)](https://docs.pydantic.dev/)
[![Offline](https://img.shields.io/badge/Inference-Offline%20after%20model%20download-2ea44f)](#privacy-and-reproducibility)

## Why this project?

A model that produces fluent prose is not automatically safe to deploy in an application. Production systems need predictable, machine-readable responses and a way to recover when generation breaks.

This project makes those operational concerns measurable. It sends the same three prompts to multiple local models, validates each response against a Pydantic v2 schema, feeds validation errors back to the model when needed, and records the final outcome as structured data.

## Empirical results

The included benchmark run evaluated three software-engineering and AI tasks per model:

| Model | Scale | Schema pass rate | Average latency | Retries |
| :--- | :---: | ---: | ---: | ---: |
| **qwen2.5-coder:3b** | 3B | **100.0%** | **133.45 s** | **0** |
| **qwen2.5:latest** | 7B | **100.0%** | **173.95 s** | **0** |
| **llama3.1:8b** | 8B | **100.0%** | **201.74 s** | **1** |
| **mistral:latest** | 7B | **100.0%** | **219.27 s** | **0** |

### What the run suggests

- **Best efficiency:** `qwen2.5-coder:3b` achieved full schema compliance with the lowest average latency—about 35% faster than the 7B/8B models in this run.
- **Recovery in action:** `llama3.1:8b` needed one retry after an initial schema failure, then produced a valid response after receiving the Pydantic validation feedback.
- **Interpret results with care:** latency depends heavily on hardware, model versions, Ollama configuration, and prompt length. Treat these figures as a useful baseline rather than a universal leaderboard.

## How it works

```text
fixed prompts
     │
     ▼
Ollama chat(format="json")
     │
     ▼
Pydantic v2 validation ── valid ──► record PASS + latency
     │
   invalid
     │
     ▼
append validation feedback ──► retry (up to 2 times)
     │
     ▼
record PASS/FAIL + retries + error details
```

### Included components

| Path | Responsibility |
| :--- | :--- |
| `src/check_system.py` | Confirms the Ollama daemon is reachable and reports missing target models. |
| `src/schemas.py` | Defines the nested `BenchmarkTaskOutput` and `QuestionItem` Pydantic schemas. |
| `src/engine.py` | Performs JSON-mode inference, validation, timing, and feedback-driven retries. |
| `src/benchmark.py` | Runs the fixed dataset across all target models and writes the summary artifact. |
| `results/` | Stores benchmark output such as `benchmark_run.json`. |
| `decisions.md` | Records the architectural decisions behind the project. |

## Getting started

### Prerequisites

- Python 3.10 or newer
- [Ollama](https://ollama.com/download) installed and running
- Enough RAM/VRAM for the models you want to evaluate

### 1. Clone and install

```bash
git clone https://github.com/idrisrafaqat18/local-llm-benchmark.git
cd local-llm-benchmark

python3 -m venv venv
source venv/bin/activate           # Windows: venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Download the benchmark models

```bash
ollama pull qwen2.5-coder:3b
ollama pull qwen2.5:latest
ollama pull mistral:latest
ollama pull llama3.1:8b
```

If needed, start the local Ollama daemon:

```bash
ollama serve
```

### 3. Verify the environment

```bash
python src/check_system.py
```

This check confirms the Ollama daemon is reachable and reports missing target models. It does not require all benchmark models to be installed before you start.

### 4. Run the benchmark

```bash
python src/benchmark.py
```

The terminal displays a markdown-style summary table. Detailed task-level results are written to:

```text
results/benchmark_run.json
```

## Metrics and methodology

Each model processes the same fixed tasks:

1. Python virtual environments and dependency isolation
2. Structured outputs and Pydantic validation
3. Local deployments versus cloud API services

For every task, the harness records:

- **Pass rate:** whether the final response validates against the Pydantic schema
- **Latency:** wall-clock time for the initial attempt and any retries
- **Retry count:** validation retries used before success or final failure
- **Error details:** the final validation or runtime error when a task fails

The default retry budget is two retries after the initial attempt. A successful retry still counts as a pass and remains visible in the retry data.

## Privacy and reproducibility

Prompts and inference stay inside the local Ollama runtime after the required model files are downloaded. This project does not use OpenAI, Gemini, Anthropic, or another hosted inference API.

For comparable runs, record the machine, operating system, Ollama version, model tags, and quantization. Model tags such as `latest` can change over time, so pin exact tags or digests when strict reproducibility matters.

## Limitations and next steps

This is an operational benchmark, not a broad measure of intelligence or answer quality. It uses a small three-task dataset and validates structure rather than deeply scoring factuality, semantic quality, or throughput.

Useful extensions include:

- pinning exact model versions and recording hardware metadata;
- adding warm-up runs and repeated trials with mean/median/p95 latency;
- measuring tokens per second and memory usage;
- adding semantic or task-specific quality checks;
- moving the dataset and benchmark configuration into external files.

## License

No license is currently specified. Add a license file before redistributing the project.

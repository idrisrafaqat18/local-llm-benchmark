# Decisions Log — Project : Local LLM Evaluation & Benchmarking Pipeline

**Pattern for every entry:** What / Why / Trade-off

---

## D1: Local Ollama Runtime over Cloud API Endpoints

- **What:** Models run entirely offline via Ollama GGUF binaries rather than external cloud APIs (OpenAI, Gemini, Anthropic).
- **Why:** 
  - Simulates enterprise data-privacy constraints (fintech, healthcare, legal) where proprietary data cannot leave local infrastructure.
  - Zero API usage costs during iterative testing and high-volume benchmark runs.
  - Exposes local engineering challenges such as latency, VRAM allocation, and tokens-per-second constraints.
- **Trade-off:** Inference speed is capped by local hardware specifications (CPU/GPU/VRAM) compared to cloud-hosted infrastructure.

---

## D2: Strict Output Schema Enforcement using Pydantic v2

- **What:** All model generation tasks pass through Pydantic v2 `BaseModel` classes to enforce structured JSON output formats (`format="json"` in Ollama).
- **Why:** 
  - Large Language Models are non-deterministic; unstructured text outputs break downstream application logic.
  - Pydantic provides runtime validation, strict type casting, and granular field-level error messages.
  - Establishes a baseline metric for measuring schema compliance across different local model architectures.
- **Trade-off:** Strict validation causes total task failure if the model outputs missing keys or invalid types, requiring retry mechanisms.

---

## D3: Self-Healing Auto-Retry Feedback Loop

- **What:** When a model's raw output fails Pydantic schema validation, the validation error message is injected back into the chat history as a user prompt for up to 2 retries.
- **Why:** 
  - Allows models to self-correct formatting mistakes (e.g., missing quotes, improper array formatting, missing schema keys) without crashing the pipeline.
  - Provides a metric to evaluate model instruction-following and error-recovery capability.
- **Trade-off:** Extends total latency when validation fails, but prevents unhandled runtime exceptions in production scripts.

---

## D4: Standardized Benchmark Dataset and Operational Metrics

- **What:** Models are evaluated across a fixed set of test prompts measuring three core operational metrics: Latency (seconds), Retry Count, and Schema Pass/Fail Rate.
- **Why:** 
  - Shifts evaluation away from subjective "vibes" toward reproducible, quantitative engineering data.
  - Helps determine which model offers the optimal trade-off between inference speed and output precision for specific tasks.
- **Trade-off:** Does not measure human readability or semantic nuance, focusing strictly on operational system compliance and speed.

---

## D5: Multi-Model Architecture Matrix Selection

- **What:** Benchmarking target includes diverse open-source model families: `qwen2.5-coder:3b`, `qwen2.5:latest`, `mistral:latest`, and `llama3.1:8b`.
- **Why:** 
  - Compares parameter scales (3B vs. 7B vs. 8B) and domain specializations (general instruction vs. code-oriented fine-tuning).
  - Demonstrates how smaller, domain-specific models can outperform larger models on specific structured outputs with significantly lower latency.
- **Trade-off:** Running larger models locally requires higher system memory (VRAM/RAM) and increases individual benchmark completion times.

---

## D6: Environment Hygiene and Repository Structure

- **What:** Python dependencies managed via isolated `venv/`, project source structured under `src/`, with strict `.gitignore` rules excluding virtual environments and raw benchmark outputs.
- **Why:** 
  - Ensures clean repository commit history and prevents committing temporary execution artifacts or system cache files.
  - Guarantees seamless setup for collaborators or recruiters cloning the repository.
- **Trade-off:** None. Non-negotiable software engineering practice.

---

## D7: Standardized Dataset & Empirical Benchmark Metrics

- **What:** `src/benchmark.py` evaluates local models across a fixed 3-task dataset (`T1`, `T2`, `T3`), logging output to `results/benchmark_run.json`.
- **Why:** 
  - Generates reproducible, empirical engineering data (latency in seconds, retry counts, pass rates) rather than relying on qualitative impressions.
  - Proves the effectiveness of the Pydantic retry feedback loop when larger models (e.g., `llama3.1:8b`) fail initial JSON formatting.
- **Trade-off:** Running 7B and 8B models locally on CPU leads to elevated latency (~130s–220s per prompt), but provides zero-cost, 100% private execution.
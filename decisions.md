# Decisions Log — Local LLM Benchmark

This log records the main architectural decisions behind the local evaluation harness.

**Entry format:** What / Why / Trade-off

---

## D1: Use Ollama for local inference instead of a hosted API

- **What:** Run the benchmark through Ollama using locally downloaded open-source models. The inference process does not call OpenAI, Gemini, Anthropic, or another hosted model API.
- **Why:**
  - Models and prompts remain on the local machine after model downloads complete.
  - Repeated benchmark runs do not incur per-request cloud API charges.
  - The setup exposes practical deployment constraints such as RAM/VRAM availability and local inference latency.
- **Trade-off:** Local speed and model capacity depend on the user's hardware and Ollama configuration. Initial model downloads require network access, so “offline” describes inference after setup rather than the installation step itself.

---

## D2: Validate structured responses with Pydantic v2

- **What:** Define the expected response as nested Pydantic v2 `BaseModel` classes and validate each Ollama response with `model_validate_json()`. Ollama is asked to return JSON with `format="json"`.
- **Why:**
  - Downstream code can consume a known data shape instead of parsing free-form prose.
  - Pydantic provides field-level validation errors that can be measured and used in recovery logic.
  - Schema compliance becomes a concrete benchmark metric.
- **Trade-off:** JSON mode alone does not guarantee that every field is present or correctly typed. Validation adds a strict acceptance gate, so malformed responses require retries or are marked as failures.

---

## D3: Recover from validation failures with a feedback loop

- **What:** When validation fails, append the model's previous response and a user message containing the Pydantic error to the conversation, then retry up to two times.
- **Why:**
  - Models can often repair missing fields or malformed JSON when shown a precise failure reason.
  - Retry count distinguishes between first-pass reliability and eventual recoverability.
- **Trade-off:** Retries increase latency and token use. The loop handles schema validation failures; unrelated runtime errors are returned immediately rather than retried blindly.

---

## D4: Measure operational reliability with a fixed dataset

- **What:** Run the same three tasks for every model and record pass rate, wall-clock latency, retry count, and error details.
- **Why:**
  - A fixed workload enables a direct comparison between model configurations.
  - Quantitative operational metrics are more reproducible than subjective impressions alone.
- **Trade-off:** Three tasks cannot represent the full range of real workloads. This benchmark emphasizes structured-output reliability and execution behavior rather than broad general knowledge or semantic quality.

---

## D5: Compare multiple model families and parameter scales

- **What:** Evaluate `qwen2.5-coder:3b`, `qwen2.5:latest`, `mistral:latest`, and `llama3.1:8b`.
- **Why:**
  - The matrix compares a code-specialized 3B model with general-purpose 7B/8B models.
  - It illustrates whether a smaller, domain-aligned model can provide an effective speed/reliability trade-off for structured tasks.
- **Trade-off:** Model families, tags, quantization, and hardware are not perfectly equivalent. Results should be reported with the exact model tags and environment details rather than generalized into a universal ranking.

---

## D6: Keep dependencies and source code isolated

- **What:** Install Python packages into a project-local virtual environment, keep implementation under `src/`, and maintain benchmark artifacts under `results/`.
- **Why:**
  - Isolation reduces dependency conflicts and makes setup easier to reproduce.
  - A predictable layout separates executable code from generated results and documentation.
- **Trade-off:** Contributors must activate the environment or use its interpreter explicitly. Generated result files can also contain machine-specific measurements and should be reviewed before commit.

---

## D7: Persist detailed benchmark artifacts

- **What:** `src/benchmark.py` writes a JSON artifact containing aggregate model summaries and task-level records to `results/benchmark_run.json`.
- **Why:**
  - The terminal table is convenient for humans, while JSON supports later analysis and comparison.
  - Persisting individual errors and retries makes reliability claims auditable.
- **Trade-off:** Result files are tied to the local machine, model versions, and run conditions. They should include environment metadata in future iterations, and filenames or run directories should be versioned when multiple experiments need to be compared.

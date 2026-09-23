import json
import os
import time
from tabulate import tabulate
from engine import run_structured_inference
from schemas import BenchmarkTaskOutput

# Target models available in your Ollama environment
BENCHMARK_MODELS = [
    "qwen2.5-coder:3b",
    "qwen2.5:latest",
    "mistral:latest",
    "llama3.1:8b"
]

# Fixed dataset to ensure reproducible evaluations
TEST_DATASET = [
    {
        "id": "T1",
        "topic": "Python Virtual Environments & Dependency Isolation",
        "prompt": "Explain python virtual environments (venv), why isolated environments matter in production, and how pip requirements files guarantee build reproducibility."
    },
    {
        "id": "T2",
        "topic": "Structured Outputs and Pydantic Validation",
        "prompt": "Explain why returning structured JSON from LLMs is critical for downstream backend application stability compared to unstructured plain text."
    },
    {
        "id": "T3",
        "topic": "Local LLM Deployments vs Cloud API Services",
        "prompt": "Compare local offline LLM deployments using GGUF quantization with cloud API services like OpenAI or Gemini in terms of privacy, operational cost, and latency."
    }
]

def execute_benchmark_suite():
    """Runs all test cases across all local benchmark models and collects performance metrics."""
    print("=" * 70)
    print("STARTING LOCAL LLM BENCHMARK SUITE")
    print(f"Models: {', '.join(BENCHMARK_MODELS)}")
    print(f"Test Cases per Model: {len(TEST_DATASET)}")
    print("=" * 70)

    summary_metrics = []
    raw_results = []

    for model in BENCHMARK_MODELS:
        print(f"\n[*] Evaluating Model: {model}")
        model_passed = 0
        model_retries = 0
        total_latency = 0.0

        for task in TEST_DATASET:
            print(f"  -> Executing Task [{task['id']}]: {task['topic']}...")
            output_obj, latency, retries, error = run_structured_inference(
                model_name=model,
                prompt=task["prompt"],
                schema_cls=BenchmarkTaskOutput,
                max_retries=2
            )

            total_latency += latency
            model_retries += retries

            success = output_obj is not None
            if success:
                model_passed += 1

            status_str = "PASS" if success else f"FAIL ({error})"
            print(f"     Status: {status_str} | Latency: {latency}s | Retries: {retries}")

            raw_results.append({
                "model": model,
                "task_id": task["id"],
                "topic": task["topic"],
                "status": "PASS" if success else "FAIL",
                "latency_seconds": latency,
                "retries": retries,
                "error": error
            })

        pass_rate = (model_passed / len(TEST_DATASET)) * 100
        avg_latency = total_latency / len(TEST_DATASET)

        summary_metrics.append({
            "Model": model,
            "Pass Rate (%)": f"{pass_rate:.1f}%",
            "Avg Latency (s)": f"{avg_latency:.2f}s",
            "Total Retries": model_retries
        })

    # Display clean table in terminal
    print("\n" + "=" * 70)
    print("FINAL BENCHMARK SUMMARY")
    print("=" * 70)
    print(tabulate(summary_metrics, headers="keys", tablefmt="github"))

    # Save benchmark result artifact
    os.makedirs("results", exist_ok=True)
    results_file = "results/benchmark_run.json"
    with open(results_file, "w") as f:
        json.dump({
            "summary": summary_metrics,
            "detailed_runs": raw_results
        }, f, indent=2)

    print(f"\n[+] Full results written to '{results_file}'")

if __name__ == "__main__":
    execute_benchmark_suite()
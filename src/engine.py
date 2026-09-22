import time
import json
import ollama
from pydantic import BaseModel, ValidationError

def run_structured_inference(
    model_name: str,
    prompt: str,
    schema_cls: type[BaseModel],
    max_retries: int = 2
) -> tuple[BaseModel | None, float, int, str | None]:
    """
    Executes local LLM inference via Ollama, enforcing Pydantic schema validation.
    
    Returns:
        (validated_object, latency_seconds, retry_count, error_message)
    """
    json_schema = json.dumps(schema_cls.model_json_schema(), indent=2)
    system_instruction = (
        "You are an expert structured output engine. "
        "Respond ONLY with a valid JSON object matching the schema below. "
        "Do NOT include markdown block wrappers (like ```json), commentary, or extra text.\n\n"
        f"JSON SCHEMA:\n{json_schema}"
    )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt}
    ]

    retries = 0
    start_time = time.perf_counter()

    while retries <= max_retries:
        try:
            response = ollama.chat(
                model=model_name,
                messages=messages,
                format="json"
            )
            raw_content = response["message"]["content"]

            # Validate against Pydantic schema
            validated_obj = schema_cls.model_validate_json(raw_content)
            latency = time.perf_counter() - start_time
            return validated_obj, round(latency, 3), retries, None

        except ValidationError as val_err:
            retries += 1
            if retries > max_retries:
                latency = time.perf_counter() - start_time
                return None, round(latency, 3), retries - 1, f"Schema validation failed: {val_err}"

            # Feedback validation error into prompt for auto-retry loop
            messages.append({"role": "assistant", "content": raw_content})
            messages.append({
                "role": "user",
                "content": f"Your last response failed JSON schema validation:\n{val_err}\nFix the output and return valid JSON."
            })

        except Exception as general_err:
            latency = time.perf_counter() - start_time
            return None, round(latency, 3), retries, f"Runtime error: {general_err}"

    latency = time.perf_counter() - start_time
    return None, round(latency, 3), retries, "Max retries exceeded."
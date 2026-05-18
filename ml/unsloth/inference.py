#!/usr/bin/env python3
"""Run one security log through a fine-tuned Unsloth LoRA adapter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.unsloth.train_lora import (  # noqa: E402
    DEFAULT_CONFIG_PATH,
    TrainingConfigError,
    load_config,
    require_section,
    resolve_repo_path,
)
from scripts.model_adapters.prompt_contract import (  # noqa: E402
    TRIAGE_PROMPT_VERSION,
    TRIAGE_SYSTEM_PROMPT,
    build_triage_user_prompt,
)


DEFAULT_SCHEMA_PATH = ROOT / "data" / "schemas" / "triage-output.schema.json"

JsonObject = dict[str, Any]
ChatMessage = dict[str, str]


class InferenceError(RuntimeError):
    """Raised when model loading, generation, or output parsing fails."""


def resolve_adapter_path(config: JsonObject, cli_adapter_path: Path | None) -> Path:
    if cli_adapter_path is not None:
        path = cli_adapter_path
        if not path.is_absolute():
            path = ROOT / path
        return path.resolve()

    output = require_section(config, "output")
    return resolve_repo_path(output.get("output_dir"), field_name="output.output_dir")


def load_schema(path: Path) -> JsonObject:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InferenceError(f"{path}: invalid JSON schema: {exc}") from exc
    if not isinstance(schema, dict):
        raise InferenceError(f"{path}: schema must be a JSON object")
    return schema


def build_inference_messages(log_line: str) -> list[ChatMessage]:
    if not log_line:
        raise InferenceError("log line must be a non-empty string")
    return [
        {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
        {"role": "user", "content": build_triage_user_prompt(log_line)},
    ]


def build_model_inputs(tokenizer: Any, messages: list[ChatMessage]) -> Any:
    try:
        return tokenizer.apply_chat_template(
            messages,
            add_generation_prompt=True,
            return_tensors="pt",
            tokenize=True,
            return_dict=True,
        )
    except Exception as exc:
        raise InferenceError(f"failed to apply tokenizer chat template: {type(exc).__name__}: {exc}") from exc


def torch_dtype(dtype_name: Any) -> Any:
    if dtype_name in (None, "", "auto"):
        return None
    try:
        import torch
    except ModuleNotFoundError as exc:
        raise InferenceError("torch is required for non-default dtype handling") from exc

    dtype_map = {
        "bfloat16": torch.bfloat16,
        "float16": torch.float16,
        "float32": torch.float32,
    }
    try:
        return dtype_map[str(dtype_name)]
    except KeyError as exc:
        raise InferenceError(f"unsupported dtype in config: {dtype_name}") from exc


def load_model_and_tokenizer(config: JsonObject, adapter_path: Path) -> tuple[Any, Any]:
    model_config = require_section(config, "model")
    base_model = model_config.get("base_model")
    if not isinstance(base_model, str) or not base_model:
        raise InferenceError("model.base_model must be a non-empty string")
    if not adapter_path.exists():
        raise InferenceError(f"LoRA adapter path does not exist: {adapter_path}")

    try:
        # Unsloth should load before PEFT/Transformers-backed helpers so the
        # runtime matches the repo's Unsloth-first training stack.
        from unsloth import FastLanguageModel
        from peft import PeftModel
    except ModuleNotFoundError as exc:
        raise InferenceError(
            "Unsloth inference dependencies are missing. Install the GPU training environment first."
        ) from exc

    try:
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=base_model,
            max_seq_length=int(model_config.get("max_seq_length", 2048)),
            dtype=torch_dtype(model_config.get("dtype")),
            load_in_4bit=bool(model_config.get("load_in_4bit", True)),
        )
        model = PeftModel.from_pretrained(model, str(adapter_path))
        FastLanguageModel.for_inference(model)
    except Exception as exc:
        raise InferenceError(f"failed to load base model and LoRA adapter: {type(exc).__name__}: {exc}") from exc

    return model, tokenizer


def model_device(model: Any) -> Any:
    try:
        return next(model.parameters()).device
    except Exception:
        return getattr(model, "device", "cpu")


def move_inputs_to_device(inputs: Any, device: Any) -> Any:
    if hasattr(inputs, "to"):
        return inputs.to(device)
    if isinstance(inputs, dict):
        return {key: value.to(device) if hasattr(value, "to") else value for key, value in inputs.items()}
    raise InferenceError(f"tokenizer returned unsupported input type: {type(inputs).__name__}")


def generate_completion(
    model: Any,
    tokenizer: Any,
    *,
    messages: list[ChatMessage],
    max_new_tokens: int,
) -> str:
    try:
        import torch
    except ModuleNotFoundError as exc:
        raise InferenceError("torch is required for model generation") from exc

    try:
        inputs = build_model_inputs(tokenizer, messages)
        device = model_device(model)
        inputs = move_inputs_to_device(inputs, device)
        prompt_length = inputs["input_ids"].shape[-1]
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                use_cache=True,
            )
        generated_ids = outputs[0][prompt_length:]
        return tokenizer.decode(generated_ids, skip_special_tokens=True).strip()
    except Exception as exc:
        raise InferenceError(f"model generation failed: {type(exc).__name__}: {exc}") from exc


def extract_json_object(text: str) -> JsonObject:
    stripped = text.strip()
    if not stripped:
        raise InferenceError("model returned an empty response")

    decoder = json.JSONDecoder()
    for index, char in enumerate(stripped):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(stripped[index:])
        except json.JSONDecodeError:
            continue
        if not isinstance(parsed, dict):
            raise InferenceError("parsed JSON is not an object")
        return parsed

    raise InferenceError("model response does not contain a valid JSON object")


def validate_output(output: JsonObject, schema: JsonObject) -> list[str]:
    errors: list[str] = []
    required = set(schema.get("required", []))
    properties = schema.get("properties", {})

    missing = sorted(required - set(output))
    if missing:
        errors.append(f"missing required fields: {', '.join(missing)}")

    if schema.get("additionalProperties") is False:
        extra = sorted(set(output) - set(properties))
        if extra:
            errors.append(f"unexpected fields: {', '.join(extra)}")

    label = output.get("label")
    label_enum = properties.get("label", {}).get("enum", [])
    if not isinstance(label, str):
        errors.append("label must be a string")
    elif label not in label_enum:
        errors.append(f"label must be one of: {', '.join(label_enum)}")

    severity = output.get("severity")
    severity_enum = properties.get("severity", {}).get("enum", [])
    if not isinstance(severity, str):
        errors.append("severity must be a string")
    elif severity not in severity_enum:
        errors.append(f"severity must be one of: {', '.join(severity_enum)}")

    if not isinstance(output.get("is_suspicious"), bool):
        errors.append("is_suspicious must be a boolean")

    evidence = output.get("evidence")
    if not isinstance(evidence, list):
        errors.append("evidence must be an array")
    else:
        for index, item in enumerate(evidence):
            if not isinstance(item, str) or not item:
                errors.append(f"evidence[{index}] must be a non-empty string")

    for field in ("reason", "recommended_action"):
        value = output.get(field)
        if not isinstance(value, str) or not value:
            errors.append(f"{field} must be a non-empty string")

    return errors


def print_raw_output(text: str) -> None:
    print("--- raw model output ---", file=sys.stderr)
    if text:
        print(text, file=sys.stderr)
    else:
        print("(empty)", file=sys.stderr)
    print("--- end raw model output ---", file=sys.stderr)


def read_log_line(args: argparse.Namespace) -> str:
    sources = [bool(args.log_line), bool(args.log_file), bool(args.stdin)]
    if sum(sources) != 1:
        raise InferenceError("provide exactly one of --log-line, --log-file, or --stdin")
    if args.log_line:
        return args.log_line.strip()
    if args.log_file:
        return args.log_file.read_text(encoding="utf-8").strip()
    return sys.stdin.read().strip()


def build_preflight_report(
    *,
    config_path: Path,
    config: JsonObject,
    schema_path: Path,
    adapter_path: Path,
    log_line: str,
) -> JsonObject:
    model_config = require_section(config, "model")
    output = require_section(config, "output")
    messages = build_inference_messages(log_line)
    return {
        "status": "inference_preflight_ok",
        "config_path": str(config_path.relative_to(ROOT)),
        "schema_path": str(schema_path.relative_to(ROOT)),
        "prompt_version": TRIAGE_PROMPT_VERSION,
        "base_model": model_config.get("base_model"),
        "max_seq_length": model_config.get("max_seq_length"),
        "load_in_4bit": model_config.get("load_in_4bit"),
        "default_output_dir": output.get("output_dir"),
        "adapter_path": str(adapter_path.relative_to(ROOT)) if adapter_path.is_relative_to(ROOT) else str(adapter_path),
        "adapter_exists": adapter_path.exists(),
        "message_roles": [message["role"] for message in messages],
        "test_split_policy": "evaluate post-training with scripts/evaluate.py --adapter openai-finetune --split data/splits/test.jsonl",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run one log line through a fine-tuned Unsloth LoRA adapter and return schema JSON.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Training/inference config path. Default: {DEFAULT_CONFIG_PATH}",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help=f"Triage output JSON schema. Default: {DEFAULT_SCHEMA_PATH}",
    )
    parser.add_argument(
        "--adapter-path",
        type=Path,
        help="LoRA adapter directory. Defaults to output.output_dir in the config.",
    )
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument("--log-line", help="Single security log line to analyze.")
    input_group.add_argument("--log-file", type=Path, help="File containing one security log line.")
    input_group.add_argument("--stdin", action="store_true", help="Read one security log line from stdin.")
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument(
        "--show-raw-output",
        action="store_true",
        help="Print the raw model completion to stderr for debugging before JSON parsing/validation.",
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate config, schema, adapter path, and prompt wiring without loading the model.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = args.config.resolve()
    schema_path = args.schema.resolve()
    raw_completion = ""
    raw_output_printed = False
    try:
        config = load_config(config_path)
        adapter_path = resolve_adapter_path(config, args.adapter_path)
        schema = load_schema(schema_path)
        log_line = read_log_line(args)
        messages = build_inference_messages(log_line)

        if args.preflight_only:
            report = build_preflight_report(
                config_path=config_path,
                config=config,
                schema_path=schema_path,
                adapter_path=adapter_path,
                log_line=log_line,
            )
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0

        model, tokenizer = load_model_and_tokenizer(config, adapter_path)
        raw_completion = generate_completion(
            model,
            tokenizer,
            messages=messages,
            max_new_tokens=args.max_new_tokens,
        )
        if args.show_raw_output:
            print_raw_output(raw_completion)
            raw_output_printed = True
        output = extract_json_object(raw_completion)
        errors = validate_output(output, schema)
        if errors:
            raise InferenceError(f"model output failed schema validation: {'; '.join(errors)}")
    except (OSError, TrainingConfigError, InferenceError, ValueError) as exc:
        if args.show_raw_output and raw_completion and not raw_output_printed:
            print_raw_output(raw_completion)
        print(f"inference failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

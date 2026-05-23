#!/usr/bin/env python3
"""Preflight entrypoint for the Unsloth LoRA training path.

This file intentionally starts with config and split validation before GPU-only
training code. The first guardrail is that training can read only the train and
validation splits; the fixed test split is reserved for post-training evaluation.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.unsloth.training_format import (  # noqa: E402
    TRIAGE_PROMPT_VERSION,
    apply_tokenizer_chat_template,
    format_split,
    load_jsonl,
)


DEFAULT_CONFIG_PATH = ROOT / "ml" / "unsloth" / "config.example.yaml"
EXPECTED_TRAIN_PATH = ROOT / "data" / "splits" / "train.jsonl"
EXPECTED_VALIDATION_PATH = ROOT / "data" / "splits" / "validation.jsonl"
V3_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-hard-contrast.jsonl"
V3_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-hard-contrast.jsonl"
V3_1_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-1-hard-contrast.jsonl"
V3_1_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-1-hard-contrast.jsonl"
V3_3_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-3-targeted-hard-contrast.jsonl"
V3_3_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-3-targeted-hard-contrast.jsonl"
V3_4_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-4-boundary-repair.jsonl"
V3_4_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-4-boundary-repair.jsonl"
V3_5_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-5-boundary-repair.jsonl"
V3_5_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-5-boundary-repair.jsonl"
V4_TRAIN_PATH = ROOT / "data" / "splits" / "train-v4-sqli-boundary-repair.jsonl"
V4_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v4-sqli-boundary-repair.jsonl"
V4_1_TRAIN_PATH = ROOT / "data" / "splits" / "train-v4-1-sqli-boundary-repair.jsonl"
V4_1_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v4-1-sqli-boundary-repair.jsonl"
V4_6_TRAIN_PATH = ROOT / "data" / "splits" / "train-v4-6-qwen35-normal-severity-calibration.jsonl"
V4_6_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v4-6-qwen35-normal-severity-calibration.jsonl"
RESERVED_TEST_PATH = ROOT / "data" / "splits" / "test.jsonl"
SPLITS_DIR = ROOT / "data" / "splits"
FAST_LANGUAGE_MODEL_LOADER = "fast_language_model"
FAST_VISION_MODEL_LOADER = "fast_vision_model"
SUPPORTED_MODEL_LOADERS = (FAST_LANGUAGE_MODEL_LOADER, FAST_VISION_MODEL_LOADER)

JsonObject = dict[str, Any]


class TrainingConfigError(ValueError):
    """Raised when the training config violates the POC split contract."""


def load_config(path: Path) -> JsonObject:
    try:
        import yaml  # type: ignore[import-not-found]
    except ModuleNotFoundError:
        return load_simple_yaml(path)

    config = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise TrainingConfigError(f"{path}: config must be a YAML object")
    return config


def load_simple_yaml(path: Path) -> JsonObject:
    """Parse the small config.example.yaml shape without requiring PyYAML."""
    config: JsonObject = {}
    current_section: dict[str, Any] | None = None
    current_list_key: str | None = None

    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        if indent == 0 and line.endswith(":"):
            section_name = line[:-1]
            current_section = {}
            config[section_name] = current_section
            current_list_key = None
            continue

        if current_section is None:
            raise TrainingConfigError(f"{path}:{line_number}: value appears before a section")

        if indent == 2 and ":" in line:
            key, raw_value = line.split(":", 1)
            value = raw_value.strip()
            if value:
                current_section[key] = parse_scalar(value)
                current_list_key = None
            else:
                current_section[key] = []
                current_list_key = key
            continue

        if indent == 4 and line.startswith("- ") and current_list_key:
            current_section[current_list_key].append(parse_scalar(line[2:].strip()))
            continue

        raise TrainingConfigError(f"{path}:{line_number}: unsupported YAML shape for built-in parser")

    return config


def parse_scalar(value: str) -> Any:
    normalized = value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    if normalized in {"null", "none"}:
        return None

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        return value


def resolve_repo_path(value: Any, *, field_name: str) -> Path:
    if not isinstance(value, str) or not value:
        raise TrainingConfigError(f"{field_name} must be a non-empty string path")
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def require_section(config: JsonObject, name: str) -> JsonObject:
    section = config.get(name)
    if not isinstance(section, dict):
        raise TrainingConfigError(f"config section `{name}` is required")
    return section


def validate_split_path(path: Path, *, expected_path: Path, field_name: str) -> None:
    if path == RESERVED_TEST_PATH.resolve():
        raise TrainingConfigError(f"{field_name} must not point to reserved test split: {path}")
    allowed_paths = {
        "data.train_path": {
            EXPECTED_TRAIN_PATH.resolve(),
            V3_TRAIN_PATH.resolve(),
            V3_1_TRAIN_PATH.resolve(),
            V3_3_TRAIN_PATH.resolve(),
            V3_4_TRAIN_PATH.resolve(),
            V3_5_TRAIN_PATH.resolve(),
            V4_TRAIN_PATH.resolve(),
            V4_1_TRAIN_PATH.resolve(),
            V4_6_TRAIN_PATH.resolve(),
        },
        "data.validation_path": {
            EXPECTED_VALIDATION_PATH.resolve(),
            V3_VALIDATION_PATH.resolve(),
            V3_1_VALIDATION_PATH.resolve(),
            V3_3_VALIDATION_PATH.resolve(),
            V3_4_VALIDATION_PATH.resolve(),
            V3_5_VALIDATION_PATH.resolve(),
            V4_VALIDATION_PATH.resolve(),
            V4_1_VALIDATION_PATH.resolve(),
            V4_6_VALIDATION_PATH.resolve(),
        },
    }.get(field_name, {expected_path.resolve()})
    if path not in allowed_paths:
        allowed_display = ", ".join(report_path(allowed_path) for allowed_path in sorted(allowed_paths))
        raise TrainingConfigError(f"{field_name} must point to one of: {allowed_display}")
    if not path.is_relative_to(SPLITS_DIR.resolve()):
        raise TrainingConfigError(f"{field_name} must stay under {SPLITS_DIR.relative_to(ROOT)}")
    if not path.exists():
        raise TrainingConfigError(f"{field_name} does not exist: {path}")
    if not path.is_file():
        raise TrainingConfigError(f"{field_name} must be a file: {path}")


def validate_training_splits(config: JsonObject) -> tuple[Path, Path]:
    data = require_section(config, "data")
    train_path = resolve_repo_path(data.get("train_path"), field_name="data.train_path")
    validation_path = resolve_repo_path(data.get("validation_path"), field_name="data.validation_path")

    if train_path == validation_path:
        raise TrainingConfigError("data.train_path and data.validation_path must be different files")

    validate_split_path(train_path, expected_path=EXPECTED_TRAIN_PATH, field_name="data.train_path")
    validate_split_path(
        validation_path,
        expected_path=EXPECTED_VALIDATION_PATH,
        field_name="data.validation_path",
    )
    return train_path, validation_path


def apply_path_overrides(config: JsonObject, *, train_path: str | None, validation_path: str | None) -> None:
    if not train_path and not validation_path:
        return
    data = require_section(config, "data")
    if train_path:
        data["train_path"] = train_path
    if validation_path:
        data["validation_path"] = validation_path


def count_labels(records: list[JsonObject]) -> dict[str, int]:
    labels = Counter(str(record.get("output", {}).get("label", "<missing>")) for record in records)
    return dict(sorted(labels.items()))


def report_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def coerce_bool(value: Any, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        if value in (0, 1):
            return bool(value)
        raise TrainingConfigError(f"{field_name} must be a boolean-like value")

    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise TrainingConfigError(f"{field_name} must be a boolean-like value")


def resolve_gradient_checkpointing(value: Any) -> bool | str:
    if isinstance(value, str) and value.strip().lower() == "unsloth":
        return "unsloth"
    return coerce_bool(value, field_name="model.use_gradient_checkpointing")


def resolve_model_loader(model_config: JsonObject) -> str:
    loader = model_config.get("loader", FAST_LANGUAGE_MODEL_LOADER)
    if not isinstance(loader, str):
        raise TrainingConfigError("model.loader must be a string")
    normalized = loader.strip().lower()
    if normalized not in SUPPORTED_MODEL_LOADERS:
        raise TrainingConfigError(
            f"unsupported model.loader: {loader}; expected one of: {', '.join(SUPPORTED_MODEL_LOADERS)}"
        )
    return normalized


def resolve_torch_dtype(dtype_name: Any, *, torch_module: Any) -> Any:
    if dtype_name in (None, "", "auto"):
        return None

    dtype_map = {
        "bfloat16": torch_module.bfloat16,
        "float16": torch_module.float16,
        "float32": torch_module.float32,
    }
    key = str(dtype_name).strip().lower()
    try:
        return dtype_map[key]
    except KeyError as exc:
        raise TrainingConfigError(f"unsupported model.dtype in config: {dtype_name}") from exc


def normalize_string_list(value: Any, *, field_name: str) -> list[str]:
    raw_items = [value] if isinstance(value, str) else value
    if not isinstance(raw_items, list) or not raw_items:
        raise TrainingConfigError(f"{field_name} must be a non-empty string list")

    normalized: list[str] = []
    for index, item in enumerate(raw_items):
        if not isinstance(item, str) or not item.strip():
            raise TrainingConfigError(f"{field_name}[{index}] must be a non-empty string")
        normalized.append(item.strip())
    return normalized


def optional_step_value(value: Any) -> int | float | None:
    if value in (None, ""):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    text = str(value).strip()
    try:
        number = float(text)
    except ValueError as exc:
        raise TrainingConfigError(f"step value must be numeric: {value}") from exc
    return int(number) if number.is_integer() else number


def build_sft_dataset(records: list[JsonObject], tokenizer: Any) -> Any:
    from datasets import Dataset

    return Dataset.from_list([{"text": apply_tokenizer_chat_template(tokenizer, record)} for record in records])


def load_base_model_for_training(
    *,
    model_config: JsonObject,
    lora_config: JsonObject,
    training_config: JsonObject,
    torch_module: Any,
) -> tuple[Any, Any, str, Any]:
    base_model = model_config.get("base_model")
    if not isinstance(base_model, str) or not base_model:
        raise TrainingConfigError("model.base_model must be a non-empty string")

    loader = resolve_model_loader(model_config)
    load_in_4bit = coerce_bool(model_config.get("load_in_4bit", True), field_name="model.load_in_4bit")

    if loader == FAST_LANGUAGE_MODEL_LOADER:
        from unsloth import FastLanguageModel

        max_seq_length = int(model_config.get("max_seq_length", 2048))
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=base_model,
            max_seq_length=max_seq_length,
            dtype=resolve_torch_dtype(model_config.get("dtype"), torch_module=torch_module),
            load_in_4bit=load_in_4bit,
        )
        model = FastLanguageModel.get_peft_model(
            model,
            r=int(lora_config.get("r", 16)),
            target_modules=normalize_string_list(
                lora_config.get("target_modules", ["all-linear"]),
                field_name="lora.target_modules",
            ),
            lora_alpha=int(lora_config.get("lora_alpha", 16)),
            lora_dropout=float(lora_config.get("lora_dropout", 0.0)),
            use_gradient_checkpointing=resolve_gradient_checkpointing(
                model_config.get("use_gradient_checkpointing", False)
            ),
            bias=str(lora_config.get("bias", "none")).lower(),
            random_state=int(lora_config.get("random_state", training_config.get("seed", 3407))),
            use_rslora=coerce_bool(lora_config.get("use_rslora", False), field_name="lora.use_rslora"),
            loftq_config=lora_config.get("loftq_config"),
        )
        return model, tokenizer, loader, FastLanguageModel

    from unsloth import FastVisionModel

    model, tokenizer = FastVisionModel.from_pretrained(
        model_name=base_model,
        load_in_4bit=load_in_4bit,
        use_gradient_checkpointing=resolve_gradient_checkpointing(
            model_config.get("use_gradient_checkpointing", False)
        ),
    )
    peft_kwargs = {
        "finetune_vision_layers": coerce_bool(
            lora_config.get("finetune_vision_layers", False),
            field_name="lora.finetune_vision_layers",
        ),
        "finetune_language_layers": coerce_bool(
            lora_config.get("finetune_language_layers", True),
            field_name="lora.finetune_language_layers",
        ),
        "finetune_attention_modules": coerce_bool(
            lora_config.get("finetune_attention_modules", True),
            field_name="lora.finetune_attention_modules",
        ),
        "finetune_mlp_modules": coerce_bool(
            lora_config.get("finetune_mlp_modules", True),
            field_name="lora.finetune_mlp_modules",
        ),
        "r": int(lora_config.get("r", 16)),
        "lora_alpha": int(lora_config.get("lora_alpha", 16)),
        "lora_dropout": float(lora_config.get("lora_dropout", 0.0)),
        "bias": str(lora_config.get("bias", "none")).lower(),
        "random_state": int(lora_config.get("random_state", training_config.get("seed", 3407))),
        "use_rslora": coerce_bool(lora_config.get("use_rslora", False), field_name="lora.use_rslora"),
        "loftq_config": lora_config.get("loftq_config"),
    }
    if "target_modules" in lora_config:
        peft_kwargs["target_modules"] = normalize_string_list(
            lora_config["target_modules"],
            field_name="lora.target_modules",
        )
    model = FastVisionModel.get_peft_model(model, **peft_kwargs)
    return model, tokenizer, loader, FastVisionModel


def validate_prompt_version(config: JsonObject) -> str:
    format_config = require_section(config, "format")
    config_prompt_version = format_config.get("prompt_version")
    if config_prompt_version != TRIAGE_PROMPT_VERSION:
        raise TrainingConfigError(
            f"format.prompt_version ({config_prompt_version}) does not match runtime prompt contract ({TRIAGE_PROMPT_VERSION})"
        )
    return str(config_prompt_version)


def build_preflight_report(config_path: Path, config: JsonObject) -> JsonObject:
    config_prompt_version = validate_prompt_version(config)

    train_path, validation_path = validate_training_splits(config)
    train_records = load_jsonl(train_path)
    validation_records = load_jsonl(validation_path)

    # Reuse the Day 5 formatter so split preflight also validates assistant JSON.
    format_split(train_records)
    format_split(validation_records)

    model = require_section(config, "model")
    output = require_section(config, "output")
    return {
        "status": "preflight_ok",
        "config_path": report_path(config_path),
        "model": {
            "base_model": model.get("base_model"),
            "loader": resolve_model_loader(model),
            "max_seq_length": model.get("max_seq_length"),
            "load_in_4bit": model.get("load_in_4bit"),
        },
        "splits": {
            "train_path": report_path(train_path),
            "train_records": len(train_records),
            "train_labels": count_labels(train_records),
            "validation_path": report_path(validation_path),
            "validation_records": len(validation_records),
            "validation_labels": count_labels(validation_records),
            "reserved_test_path": report_path(RESERVED_TEST_PATH),
            "test_split_policy": "never read during training; use only after training via scripts/evaluate.py",
        },
        "prompt": {
            "config_prompt_version": config_prompt_version,
            "formatter_prompt_version": TRIAGE_PROMPT_VERSION,
        },
        "output_dir": output.get("output_dir"),
    }


def run_gpu_training(config_path: Path, config: JsonObject) -> JsonObject:
    validate_prompt_version(config)
    train_path, validation_path = validate_training_splits(config)

    model_config = require_section(config, "model")
    training_config = require_section(config, "training")
    output_config = require_section(config, "output")
    lora_config = require_section(config, "lora")

    output_dir = resolve_repo_path(output_config.get("output_dir"), field_name="output.output_dir")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        import torch
        # Unsloth must load before TRL so its SFTTrainer compatibility patch
        # accepts notebook-style tokenizer kwargs on this training path.
        from unsloth import is_bfloat16_supported
        from trl import SFTConfig, SFTTrainer
    except ModuleNotFoundError as exc:
        raise TrainingConfigError(
            "GPU training dependencies are missing: install unsloth, trl, torch, transformers, datasets, and peft"
        ) from exc

    if not torch.cuda.is_available():
        raise TrainingConfigError("GPU training requires CUDA, but torch.cuda.is_available() is false")

    max_seq_length = int(model_config.get("max_seq_length", 2048))
    model, tokenizer, loader, model_backend = load_base_model_for_training(
        model_config=model_config,
        lora_config=lora_config,
        training_config=training_config,
        torch_module=torch,
    )

    train_records = load_jsonl(train_path)
    validation_records = load_jsonl(validation_path)

    train_dataset = build_sft_dataset(train_records, tokenizer)
    validation_dataset = build_sft_dataset(validation_records, tokenizer)
    bf16_supported = bool(is_bfloat16_supported())
    if loader == FAST_VISION_MODEL_LOADER:
        model_backend.for_training(model)

    args = SFTConfig(
        output_dir=str(output_dir),
        per_device_train_batch_size=int(training_config.get("per_device_train_batch_size", 2)),
        per_device_eval_batch_size=int(
            training_config.get(
                "per_device_eval_batch_size",
                training_config.get("per_device_train_batch_size", 2),
            )
        ),
        gradient_accumulation_steps=int(training_config.get("gradient_accumulation_steps", 8)),
        warmup_steps=int(training_config.get("warmup_steps", 5)),
        max_steps=int(training_config.get("max_steps", 30)),
        learning_rate=float(training_config.get("learning_rate", 2e-4)),
        num_train_epochs=float(training_config.get("num_train_epochs", 1)),
        optim=str(training_config.get("optim", "adamw_8bit")),
        weight_decay=float(training_config.get("weight_decay", 0.001)),
        lr_scheduler_type=str(training_config.get("lr_scheduler_type", "linear")),
        logging_steps=int(training_config.get("logging_steps", 1)),
        eval_strategy=str(training_config.get("eval_strategy", "epoch")),
        eval_steps=optional_step_value(training_config.get("eval_steps")),
        save_strategy=str(training_config.get("save_strategy", "epoch")),
        save_steps=optional_step_value(training_config.get("save_steps")),
        seed=int(training_config.get("seed", 3407)),
        report_to=str(training_config.get("report_to", "none")),
        remove_unused_columns=False,
        dataset_num_proc=1,
        dataset_text_field="text",
        max_length=max_seq_length,
        packing=False,
        bf16=bf16_supported,
        fp16=not bf16_supported,
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        args=args,
        max_seq_length=max_seq_length,
    )

    train_result = trainer.train()
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))

    return {
        "status": "training_complete",
        "config_path": report_path(config_path),
        "output_dir": report_path(output_dir),
        "train_records": len(train_records),
        "validation_records": len(validation_records),
        "metrics": dict(sorted(getattr(train_result, "metrics", {}).items())),
    }

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate config and run the Day 6 Unsloth LoRA training path.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Training config path. Default: {DEFAULT_CONFIG_PATH}",
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate config and dataset splits without starting GPU training.",
    )
    parser.add_argument(
        "--train-path",
        help="Override data.train_path for validation/testing of split guards.",
    )
    parser.add_argument(
        "--validation-path",
        help="Override data.validation_path for validation/testing of split guards.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = args.config.resolve()
    try:
        config = load_config(config_path)
        apply_path_overrides(
            config,
            train_path=args.train_path,
            validation_path=args.validation_path,
        )
        report = build_preflight_report(config_path, config)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.preflight_only:
            return 0

        training_result = run_gpu_training(config_path, config)
        print(json.dumps(training_result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, TrainingConfigError, ValueError) as exc:
        print(f"training failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

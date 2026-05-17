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

from ml.unsloth.training_format import format_split, load_jsonl  # noqa: E402


DEFAULT_CONFIG_PATH = ROOT / "ml" / "unsloth" / "config.example.yaml"
EXPECTED_TRAIN_PATH = ROOT / "data" / "splits" / "train.jsonl"
EXPECTED_VALIDATION_PATH = ROOT / "data" / "splits" / "validation.jsonl"
RESERVED_TEST_PATH = ROOT / "data" / "splits" / "test.jsonl"
SPLITS_DIR = ROOT / "data" / "splits"

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
    if value == "true":
        return True
    if value == "false":
        return False
    if value == "null":
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
    if path != expected_path.resolve():
        raise TrainingConfigError(f"{field_name} must point to {expected_path.relative_to(ROOT)}")
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


def build_preflight_report(config_path: Path, config: JsonObject) -> JsonObject:
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
        "config_path": str(config_path.relative_to(ROOT)),
        "model": {
            "base_model": model.get("base_model"),
            "max_seq_length": model.get("max_seq_length"),
            "load_in_4bit": model.get("load_in_4bit"),
        },
        "splits": {
            "train_path": str(train_path.relative_to(ROOT)),
            "train_records": len(train_records),
            "train_labels": count_labels(train_records),
            "validation_path": str(validation_path.relative_to(ROOT)),
            "validation_records": len(validation_records),
            "validation_labels": count_labels(validation_records),
            "reserved_test_path": str(RESERVED_TEST_PATH.relative_to(ROOT)),
            "test_split_policy": "never read during training; use only after training via scripts/evaluate.py",
        },
        "output_dir": output.get("output_dir"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate config and split policy for the Day 5 Unsloth LoRA path.",
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
    except (OSError, TrainingConfigError, ValueError) as exc:
        print(f"training preflight failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not args.preflight_only:
        print(
            "training preflight only for now; GPU training implementation is the next Day 5 step",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

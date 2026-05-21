#!/usr/bin/env python3
"""Format triage JSONL records for supervised fine-tuning."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.model_adapters.prompt_contract import (  # noqa: E402
    TRIAGE_LABELS,
    TRIAGE_OUTPUT_KEYS,
    TRIAGE_PROMPT_VERSION,
    TRIAGE_SEVERITIES,
    TRIAGE_SYSTEM_PROMPT,
    build_triage_user_prompt,
)


DEFAULT_SPLIT_PATH = ROOT / "data" / "splits" / "train.jsonl"

JsonObject = dict[str, Any]
ChatMessage = dict[str, str]


class TrainingFormatError(ValueError):
    """Raised when a dataset record cannot be used for SFT formatting."""


def load_jsonl(path: Path) -> list[JsonObject]:
    records: list[JsonObject] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TrainingFormatError(f"{path}:{line_number}: invalid JSONL record: {exc}") from exc
        if not isinstance(item, dict):
            raise TrainingFormatError(f"{path}:{line_number}: JSONL record must be an object")
        records.append(item)
    return records


def canonical_output(output: Any, *, record_id: str) -> JsonObject:
    if not isinstance(output, dict):
        raise TrainingFormatError(f"{record_id}: output must be an object")

    expected_keys = set(TRIAGE_OUTPUT_KEYS)
    actual_keys = set(output)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        raise TrainingFormatError(f"{record_id}: output missing fields: {', '.join(missing)}")
    if extra:
        raise TrainingFormatError(f"{record_id}: output has unexpected fields: {', '.join(extra)}")

    label = output["label"]
    if not isinstance(label, str) or label not in TRIAGE_LABELS:
        raise TrainingFormatError(f"{record_id}: output.label must be one of: {', '.join(TRIAGE_LABELS)}")

    severity = output["severity"]
    if not isinstance(severity, str) or severity not in TRIAGE_SEVERITIES:
        raise TrainingFormatError(
            f"{record_id}: output.severity must be one of: {', '.join(TRIAGE_SEVERITIES)}"
        )

    is_suspicious = output["is_suspicious"]
    if not isinstance(is_suspicious, bool):
        raise TrainingFormatError(f"{record_id}: output.is_suspicious must be a boolean")
    if label == "normal" and is_suspicious:
        raise TrainingFormatError(f"{record_id}: normal label must set is_suspicious=false")
    if label != "normal" and not is_suspicious:
        raise TrainingFormatError(f"{record_id}: suspicious label must set is_suspicious=true")

    evidence = output["evidence"]
    if not isinstance(evidence, list):
        raise TrainingFormatError(f"{record_id}: output.evidence must be an array")
    if not 1 <= len(evidence) <= 3:
        raise TrainingFormatError(f"{record_id}: output.evidence must contain one to three items")
    for index, item in enumerate(evidence):
        if not isinstance(item, str) or not item:
            raise TrainingFormatError(f"{record_id}: output.evidence[{index}] must be a non-empty string")
        if len(item) > 160:
            raise TrainingFormatError(f"{record_id}: output.evidence[{index}] must be 160 characters or fewer")

    for field in ("reason", "recommended_action"):
        value = output[field]
        if not isinstance(value, str) or not value:
            raise TrainingFormatError(f"{record_id}: output.{field} must be a non-empty string")

    return {key: output[key] for key in TRIAGE_OUTPUT_KEYS}


def assistant_json(output: JsonObject) -> str:
    return json.dumps(output, ensure_ascii=False, separators=(",", ":"))


def build_training_messages(record: JsonObject) -> list[ChatMessage]:
    record_id = str(record.get("id", "<missing-id>"))
    log_line = record.get("input")
    if not isinstance(log_line, str) or not log_line:
        raise TrainingFormatError(f"{record_id}: input must be a non-empty string")

    output = canonical_output(record.get("output"), record_id=record_id)
    return [
        {"role": "system", "content": TRIAGE_SYSTEM_PROMPT},
        {"role": "user", "content": build_triage_user_prompt(log_line)},
        {"role": "assistant", "content": assistant_json(output)},
    ]


def format_record_for_sft(record: JsonObject) -> JsonObject:
    record_id = str(record.get("id", "<missing-id>"))
    return {
        "id": record_id,
        "prompt_version": TRIAGE_PROMPT_VERSION,
        "format": "chat_messages",
        "messages": build_training_messages(record),
    }


def apply_tokenizer_chat_template(tokenizer: Any, record: JsonObject) -> str:
    """Render one record with the target model tokenizer chat template."""
    messages = build_training_messages(record)
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=False,
    )


def format_split(records: list[JsonObject]) -> list[JsonObject]:
    return [format_record_for_sft(record) for record in records]


def summarize_formatted_records(path: Path, formatted: list[JsonObject]) -> JsonObject:
    return {
        "split": str(path),
        "records": len(formatted),
        "prompt_version": TRIAGE_PROMPT_VERSION,
        "format": "chat_messages",
        "assistant_output_keys": list(TRIAGE_OUTPUT_KEYS),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and preview the Day 5 SFT chat-message format.",
    )
    parser.add_argument(
        "--split",
        type=Path,
        default=DEFAULT_SPLIT_PATH,
        help=f"JSONL split to format. Default: {DEFAULT_SPLIT_PATH}",
    )
    parser.add_argument(
        "--preview",
        type=int,
        default=0,
        help="Print the first N formatted records as JSONL instead of only a summary.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = load_jsonl(args.split)
    formatted = format_split(records)

    if args.preview > 0:
        for item in formatted[: args.preview]:
            print(json.dumps(item, ensure_ascii=False, sort_keys=True))
        return 0

    print(json.dumps(summarize_formatted_records(args.split, formatted), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

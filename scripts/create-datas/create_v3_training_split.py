#!/usr/bin/env python3
"""Create Phase 6 v3 training split files without touching fixed holdouts."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.generate_dataset import LABELS, validate_record, write_jsonl  # noqa: E402
from ml.unsloth.training_format import format_split  # noqa: E402


CANONICAL_TRAIN_PATH = ROOT / "data" / "splits" / "train.jsonl"
CANONICAL_VALIDATION_PATH = ROOT / "data" / "splits" / "validation.jsonl"
HARD_CONTRAST_PATH = ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"
TRAIN_PLUS_PATH = ROOT / "data" / "generated" / "train-plus-v3-hard-contrast.jsonl"

V3_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-hard-contrast.jsonl"
V3_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-hard-contrast.jsonl"

JsonObject = dict[str, Any]


def load_jsonl(path: Path) -> list[JsonObject]:
    records: list[JsonObject] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSONL record: {exc}") from exc
        if not isinstance(item, dict):
            raise ValueError(f"{path}:{line_number}: JSONL record must be an object")
        records.append(item)
    return records


def label_counts(records: list[JsonObject]) -> Counter[str]:
    return Counter(str(item.get("output", {}).get("label", "<missing>")) for item in records)


def validate_records(records: list[JsonObject], *, expected_count: int, expected_per_label: int, name: str) -> None:
    if len(records) != expected_count:
        raise ValueError(f"{name}: expected {expected_count} records, got {len(records)}")

    ids = [str(item.get("id", "")) for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name}: record ids must be unique")

    for item in records:
        validate_record(item)

    counts = label_counts(records)
    for label in LABELS:
        if counts[label] != expected_per_label:
            raise ValueError(f"{name}/{label}: expected {expected_per_label}, got {counts[label]}")

    format_split(records)


def ensure_train_plus_matches(train_records: list[JsonObject], hard_records: list[JsonObject]) -> list[JsonObject]:
    expected_records = [*train_records, *hard_records]
    expected_ids = [str(item["id"]) for item in expected_records]

    if not TRAIN_PLUS_PATH.exists():
        write_jsonl(TRAIN_PLUS_PATH, expected_records)
        return expected_records

    existing_records = load_jsonl(TRAIN_PLUS_PATH)
    existing_ids = [str(item["id"]) for item in existing_records]
    if existing_ids != expected_ids:
        raise ValueError(
            f"{TRAIN_PLUS_PATH.relative_to(ROOT)} exists but does not match canonical train + v3 hard contrast"
        )
    return existing_records


def main() -> int:
    train_records = load_jsonl(CANONICAL_TRAIN_PATH)
    validation_records = load_jsonl(CANONICAL_VALIDATION_PATH)
    hard_records = load_jsonl(HARD_CONTRAST_PATH)
    train_plus_records = ensure_train_plus_matches(train_records, hard_records)

    validate_records(train_records, expected_count=350, expected_per_label=70, name="canonical train")
    validate_records(hard_records, expected_count=50, expected_per_label=10, name="v3 hard contrast")
    validate_records(train_plus_records, expected_count=400, expected_per_label=80, name="v3 train")
    validate_records(validation_records, expected_count=75, expected_per_label=15, name="v3 validation")

    train_ids = {str(item["id"]) for item in train_plus_records}
    validation_ids = {str(item["id"]) for item in validation_records}
    if train_ids & validation_ids:
        raise ValueError("v3 train and validation records overlap")

    write_jsonl(V3_TRAIN_PATH, train_plus_records)
    write_jsonl(V3_VALIDATION_PATH, validation_records)

    print(f"Wrote {len(train_plus_records)} records to {V3_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(validation_records)} records to {V3_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Train labels: {dict(sorted(label_counts(train_plus_records).items()))}")
    print(f"Validation labels: {dict(sorted(label_counts(validation_records).items()))}")
    print("Fixed test split was not read or modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

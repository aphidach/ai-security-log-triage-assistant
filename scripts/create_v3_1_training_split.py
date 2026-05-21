#!/usr/bin/env python3
"""Create Phase 6 v3.1 training split files without touching fixed holdouts."""

from __future__ import annotations

import copy
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
TRAIN_PLUS_PATH = ROOT / "data" / "generated" / "train-plus-v3-1-hard-contrast.jsonl"
V3_1_TRAIN_PATH = ROOT / "data" / "splits" / "train-v3-1-hard-contrast.jsonl"
V3_1_VALIDATION_PATH = ROOT / "data" / "splits" / "validation-v3-1-hard-contrast.jsonl"


JsonObject = dict[str, Any]

HARD_WEIGHT = 3
HARD_WEIGHTED_PREFIX = "v3-1-hard-weighted-"
TRAIN_PER_LABEL = 100
VALIDATION_PER_LABEL = 15


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
    return Counter(str(item["output"]["label"]) for item in records)


def validate_records(records: list[JsonObject], *, expected_count: int, expected_per_label: int, name: str) -> None:
    if len(records) != expected_count:
        raise ValueError(f"{name}: expected {expected_count} records, got {len(records)}")

    ids = [str(item["id"]) for item in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"{name}: record ids must be unique")

    for item in records:
        validate_record(item)

    counts = label_counts(records)
    for label in LABELS:
        if counts[label] != expected_per_label:
            raise ValueError(f"{name}/{label}: expected {expected_per_label}, got {counts[label]}")

    format_split(records)


def build_weighted_hard_records(hard_records: list[JsonObject]) -> list[JsonObject]:
    weighted: list[JsonObject] = []
    for index, hard_record in enumerate(hard_records, start=1):
        for repeat in range(HARD_WEIGHT):
            copy_record = copy.deepcopy(hard_record)
            copy_record["id"] = f"{HARD_WEIGHTED_PREFIX}{index:03d}-{repeat + 1:02d}"
            weighted.append(copy_record)
    return weighted


def build_v3_1_split_records() -> tuple[list[JsonObject], list[JsonObject]]:
    canonical_train = load_jsonl(CANONICAL_TRAIN_PATH)
    canonical_validation = load_jsonl(CANONICAL_VALIDATION_PATH)
    hard_records = load_jsonl(HARD_CONTRAST_PATH)

    weighted_hard_records = build_weighted_hard_records(hard_records)
    train_plus_records = [*canonical_train, *weighted_hard_records]

    validate_records(canonical_train, expected_count=350, expected_per_label=70, name="canonical train")
    validate_records(hard_records, expected_count=50, expected_per_label=10, name="v3 hard contrast")
    validate_records(weighted_hard_records, expected_count=150, expected_per_label=30, name="v3 hard weighted")
    validate_records(train_plus_records, expected_count=500, expected_per_label=TRAIN_PER_LABEL, name="v3.1 train")
    validate_records(canonical_validation, expected_count=75, expected_per_label=VALIDATION_PER_LABEL, name="v3.1 validation")

    canonical_ids = {str(item["id"]) for item in canonical_train}
    validation_ids = {str(item["id"]) for item in canonical_validation}
    weighted_ids = {str(item["id"]) for item in weighted_hard_records}
    if weighted_ids & canonical_ids:
        raise ValueError("v3 hard weighted ids overlap canonical train ids")
    if weighted_ids & validation_ids:
        raise ValueError("v3 hard weighted ids overlap validation ids")

    train_ids = {str(item["id"]) for item in train_plus_records}
    if train_ids & validation_ids:
        raise ValueError("v3.1 train and validation records overlap")

    return train_plus_records, canonical_validation


def main() -> int:
    train_plus_records, validation_records = build_v3_1_split_records()

    write_jsonl(TRAIN_PLUS_PATH, train_plus_records)
    write_jsonl(V3_1_TRAIN_PATH, train_plus_records)
    write_jsonl(V3_1_VALIDATION_PATH, validation_records)

    print(f"Wrote {len(train_plus_records)} records to {TRAIN_PLUS_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(train_plus_records)} records to {V3_1_TRAIN_PATH.relative_to(ROOT)}")
    print(f"Wrote {len(validation_records)} records to {V3_1_VALIDATION_PATH.relative_to(ROOT)}")
    print(f"Train labels: {dict(sorted(label_counts(train_plus_records).items()))}")
    print(f"Validation labels: {dict(sorted(label_counts(validation_records).items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

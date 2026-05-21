#!/usr/bin/env python3
"""Regression checks for the Phase 6 v3.1 recovery workflow."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

from ml.unsloth.train_lora import (  # noqa: E402
    TrainingConfigError,
    build_preflight_report,
    load_config,
    run_gpu_training,
)
from ml.unsloth.training_format import format_split  # noqa: E402
from scripts.generate_dataset import LABELS  # noqa: E402
from scripts.model_adapters.prompt_contract import TRIAGE_PROMPT_VERSION  # noqa: E402


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def label_counts(records: list[dict]) -> dict[str, int]:
    counts = {label: 0 for label in LABELS}
    for record in records:
        counts[record["output"]["label"]] += 1
    return counts


class V31RecoveryWorkflowTest(unittest.TestCase):
    def test_config_prompt_version_matches_runtime_contract(self) -> None:
        config_path = ROOT / "ml" / "unsloth" / "config.example.yaml"
        config = load_config(config_path)

        self.assertEqual(config["format"]["prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(config["data"]["train_path"], "data/splits/train-v3-1-hard-contrast.jsonl")
        self.assertEqual(
            config["data"]["validation_path"],
            "data/splits/validation-v3-1-hard-contrast.jsonl",
        )

        report = build_preflight_report(config_path, config)
        self.assertEqual(report["prompt"]["config_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(report["prompt"]["formatter_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertIn("v3-1-hard-contrast", config["output"]["output_dir"])
        self.assertIn("v3-1-hard-contrast", config["output"]["adapter_name"])

    def test_stale_prompt_version_is_rejected_before_training(self) -> None:
        config_path = ROOT / "ml" / "unsloth" / "config.example.yaml"
        config = load_config(config_path)
        config["format"]["prompt_version"] = "triage-json-v2"

        with self.assertRaises(TrainingConfigError):
            build_preflight_report(config_path, config)
        with self.assertRaises(TrainingConfigError):
            run_gpu_training(config_path, config)

    def test_v3_1_weighted_split_contract(self) -> None:
        from scripts.create_v3_1_training_split import (
            TRAIN_PLUS_PATH,
            V3_1_TRAIN_PATH,
            V3_1_VALIDATION_PATH,
            build_v3_1_split_records,
            main as create_v3_1_training_split,
        )

        expected_train_records, expected_validation_records = build_v3_1_split_records()
        checked_train_records = load_jsonl(V3_1_TRAIN_PATH)
        checked_validation_records = load_jsonl(V3_1_VALIDATION_PATH)
        checked_train_plus_records = load_jsonl(TRAIN_PLUS_PATH)

        self.assertEqual(checked_train_records, expected_train_records)
        self.assertEqual(checked_train_plus_records, expected_train_records)
        self.assertEqual(checked_validation_records, expected_validation_records)

        test_path = ROOT / "data" / "splits" / "test.jsonl"
        before_test_hash = file_sha256(test_path)
        before_artifact_hashes = {
            TRAIN_PLUS_PATH: file_sha256(TRAIN_PLUS_PATH),
            V3_1_TRAIN_PATH: file_sha256(V3_1_TRAIN_PATH),
            V3_1_VALIDATION_PATH: file_sha256(V3_1_VALIDATION_PATH),
        }

        self.assertEqual(create_v3_1_training_split(), 0)

        self.assertEqual(file_sha256(test_path), before_test_hash)
        self.assertEqual(
            {path: file_sha256(path) for path in before_artifact_hashes},
            before_artifact_hashes,
        )

        train_records = load_jsonl(V3_1_TRAIN_PATH)
        validation_records = load_jsonl(V3_1_VALIDATION_PATH)

        self.assertEqual(len(train_records), 500)
        self.assertEqual(label_counts(train_records), {label: 100 for label in LABELS})
        self.assertEqual(len(validation_records), 75)
        self.assertEqual(label_counts(validation_records), {label: 15 for label in LABELS})

        train_ids = {record["id"] for record in train_records}
        validation_ids = {record["id"] for record in validation_records}
        self.assertEqual(len(train_ids), len(train_records))
        self.assertEqual(train_ids & validation_ids, set())
        self.assertGreaterEqual(
            sum(1 for record in train_records if record["id"].startswith("v3-1-hard-weighted-")),
            150,
        )

        # The SFT formatter is the contract that training actually consumes.
        format_split(train_records)
        format_split(validation_records)


if __name__ == "__main__":
    unittest.main()

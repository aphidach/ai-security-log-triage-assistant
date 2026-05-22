#!/usr/bin/env python3
"""Regression checks for the Phase 6 v3.4 boundary repair workflow."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

from ml.unsloth.train_lora import build_preflight_report, load_config  # noqa: E402
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


class V34BoundaryRepairWorkflowTest(unittest.TestCase):
    def test_config_v3_4_preflight_contract(self) -> None:
        config_path = ROOT / "ml" / "unsloth" / "config.v3-4.yaml"
        config = load_config(config_path)

        self.assertEqual(config["format"]["prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(config["data"]["train_path"], "data/splits/train-v3-4-boundary-repair.jsonl")
        self.assertEqual(
            config["data"]["validation_path"],
            "data/splits/validation-v3-4-boundary-repair.jsonl",
        )

        report = build_preflight_report(config_path, config)
        self.assertEqual(report["prompt"]["config_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(report["prompt"]["formatter_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(report["splits"]["train_records"], 710)
        self.assertEqual(report["splits"]["validation_records"], 75)
        self.assertIn("v3-4-boundary-repair", config["output"]["output_dir"])
        self.assertIn("v3-4-boundary-repair", config["output"]["adapter_name"])

    def test_v3_4_boundary_repair_split_contract(self) -> None:
        from scripts.create_v3_4_boundary_repair_dataset import (
            SUPPLEMENT_PATH,
            TRAIN_PLUS_PATH,
            V3_4_TRAIN_PATH,
            V3_4_VALIDATION_PATH,
            build_v3_4_split_records,
            main as create_v3_4_boundary_repair_dataset,
        )

        expected_train_records, expected_validation_records, expected_supplement_records = (
            build_v3_4_split_records()
        )
        checked_train_records = load_jsonl(V3_4_TRAIN_PATH)
        checked_train_plus_records = load_jsonl(TRAIN_PLUS_PATH)
        checked_validation_records = load_jsonl(V3_4_VALIDATION_PATH)
        checked_supplement_records = load_jsonl(SUPPLEMENT_PATH)

        expected_clean_supplement = [
            {key: value for key, value in record.items() if key != "metadata"}
            for record in expected_supplement_records
        ]

        self.assertEqual(checked_train_records, expected_train_records)
        self.assertEqual(checked_train_plus_records, expected_train_records)
        self.assertEqual(checked_validation_records, expected_validation_records)
        self.assertEqual(checked_supplement_records, expected_clean_supplement)
        self.assertTrue(all("metadata" not in record for record in checked_supplement_records))

        test_path = ROOT / "data" / "splits" / "test.jsonl"
        before_test_hash = file_sha256(test_path)
        before_artifact_hashes = {
            SUPPLEMENT_PATH: file_sha256(SUPPLEMENT_PATH),
            TRAIN_PLUS_PATH: file_sha256(TRAIN_PLUS_PATH),
            V3_4_TRAIN_PATH: file_sha256(V3_4_TRAIN_PATH),
            V3_4_VALIDATION_PATH: file_sha256(V3_4_VALIDATION_PATH),
        }

        self.assertEqual(create_v3_4_boundary_repair_dataset(), 0)

        self.assertEqual(file_sha256(test_path), before_test_hash)
        self.assertEqual(
            {path: file_sha256(path) for path in before_artifact_hashes},
            before_artifact_hashes,
        )

        train_records = load_jsonl(V3_4_TRAIN_PATH)
        validation_records = load_jsonl(V3_4_VALIDATION_PATH)
        supplement_records = load_jsonl(SUPPLEMENT_PATH)

        self.assertEqual(len(supplement_records), 160)
        self.assertEqual(
            label_counts(supplement_records),
            {
                "normal": 60,
                "failed_login_bruteforce": 20,
                "sql_injection_attempt": 40,
                "directory_traversal_attempt": 0,
                "port_scan_or_recon": 40,
            },
        )
        self.assertEqual(len(train_records), 710)
        self.assertEqual(
            label_counts(train_records),
            {
                "normal": 170,
                "failed_login_bruteforce": 120,
                "sql_injection_attempt": 160,
                "directory_traversal_attempt": 100,
                "port_scan_or_recon": 160,
            },
        )
        self.assertEqual(len(validation_records), 75)
        self.assertEqual(label_counts(validation_records), {label: 15 for label in LABELS})

        train_ids = {record["id"] for record in train_records}
        validation_ids = {record["id"] for record in validation_records}
        self.assertEqual(len(train_ids), len(train_records))
        self.assertEqual(train_ids & validation_ids, set())
        self.assertGreaterEqual(
            sum(1 for record in train_records if record["id"].startswith("v3-4-boundary-")),
            160,
        )

        format_split(train_records)
        format_split(validation_records)


if __name__ == "__main__":
    unittest.main()

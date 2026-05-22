#!/usr/bin/env python3
"""Regression checks for the Phase 8 v4 SQLi boundary repair workflow."""

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


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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


def assert_evidence_in_input(test_case: unittest.TestCase, records: list[dict]) -> None:
    for record in records:
        log_line = record["input"]
        for evidence in record["output"]["evidence"]:
            test_case.assertIn(evidence, log_line, record["id"])


class V4SqliBoundaryRepairWorkflowTest(unittest.TestCase):
    def test_v4_failure_slice_contract(self) -> None:
        from scripts.create_v4_sqli_failure_slice import (
            OUTPUT_JSON_PATH,
            OUTPUT_MD_PATH,
            build_report,
            main as create_v4_sqli_failure_slice,
        )

        expected_report = build_report()
        checked_report = load_json(OUTPUT_JSON_PATH)

        self.assertEqual(checked_report, expected_report)
        self.assertTrue(OUTPUT_MD_PATH.exists())
        self.assertEqual(checked_report["fixed_test_split_used"], False)
        self.assertEqual(checked_report["label_failure_count"], 8)

        bucket_counts = {
            bucket["bucket"]: bucket["count"] for bucket in checked_report["bucket_summary"]
        }
        self.assertEqual(
            bucket_counts,
            {
                "normal_to_bruteforce": 2,
                "sqli_to_invalid": 1,
                "sqli_to_normal": 1,
                "sqli_to_traversal": 4,
            },
        )

        test_path = ROOT / "data" / "splits" / "test.jsonl"
        before_test_hash = file_sha256(test_path)
        before_report_hashes = {
            OUTPUT_JSON_PATH: file_sha256(OUTPUT_JSON_PATH),
            OUTPUT_MD_PATH: file_sha256(OUTPUT_MD_PATH),
        }

        self.assertEqual(create_v4_sqli_failure_slice(), 0)

        self.assertEqual(file_sha256(test_path), before_test_hash)
        self.assertEqual(
            {path: file_sha256(path) for path in before_report_hashes},
            before_report_hashes,
        )

    def test_config_v4_preflight_contract(self) -> None:
        config_path = ROOT / "ml" / "unsloth" / "config.v4.yaml"
        config = load_config(config_path)

        self.assertEqual(config["model"]["base_model"], "unsloth/LFM2-350M")
        self.assertEqual(config["model"]["max_seq_length"], 2048)
        self.assertEqual(config["format"]["prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(
            config["data"]["train_path"],
            "data/splits/train-v4-sqli-boundary-repair.jsonl",
        )
        self.assertEqual(
            config["data"]["validation_path"],
            "data/splits/validation-v4-sqli-boundary-repair.jsonl",
        )
        self.assertEqual(config["training"]["max_steps"], 540)

        report = build_preflight_report(config_path, config)
        self.assertEqual(report["prompt"]["config_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(report["prompt"]["formatter_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(report["splits"]["train_records"], 1070)
        self.assertEqual(report["splits"]["validation_records"], 75)
        self.assertIn("v4-2048-sqli-boundary-repair", config["output"]["output_dir"])
        self.assertIn("v4-2048-sqli-boundary-repair", config["output"]["adapter_name"])

    def test_v4_sqli_boundary_repair_split_contract(self) -> None:
        from scripts.create_v4_sqli_boundary_repair_dataset import (
            SUPPLEMENT_PATH,
            TRAIN_PLUS_PATH,
            V4_TRAIN_PATH,
            V4_VALIDATION_PATH,
            build_v4_split_records,
            main as create_v4_sqli_boundary_repair_dataset,
        )

        expected_train_records, expected_validation_records, expected_supplement_records = (
            build_v4_split_records()
        )
        checked_train_records = load_jsonl(V4_TRAIN_PATH)
        checked_train_plus_records = load_jsonl(TRAIN_PLUS_PATH)
        checked_validation_records = load_jsonl(V4_VALIDATION_PATH)
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
            V4_TRAIN_PATH: file_sha256(V4_TRAIN_PATH),
            V4_VALIDATION_PATH: file_sha256(V4_VALIDATION_PATH),
        }

        self.assertEqual(create_v4_sqli_boundary_repair_dataset(), 0)

        self.assertEqual(file_sha256(test_path), before_test_hash)
        self.assertEqual(
            {path: file_sha256(path) for path in before_artifact_hashes},
            before_artifact_hashes,
        )

        train_records = load_jsonl(V4_TRAIN_PATH)
        validation_records = load_jsonl(V4_VALIDATION_PATH)
        supplement_records = load_jsonl(SUPPLEMENT_PATH)

        self.assertEqual(len(supplement_records), 160)
        self.assertEqual(
            label_counts(supplement_records),
            {
                "normal": 40,
                "failed_login_bruteforce": 10,
                "sql_injection_attempt": 80,
                "directory_traversal_attempt": 20,
                "port_scan_or_recon": 10,
            },
        )
        self.assertEqual(len(train_records), 1070)
        self.assertEqual(
            label_counts(train_records),
            {
                "normal": 255,
                "failed_login_bruteforce": 130,
                "sql_injection_attempt": 315,
                "directory_traversal_attempt": 175,
                "port_scan_or_recon": 195,
            },
        )
        self.assertEqual(len(validation_records), 75)
        self.assertEqual(label_counts(validation_records), {label: 15 for label in LABELS})

        train_ids = {record["id"] for record in train_records}
        validation_ids = {record["id"] for record in validation_records}
        self.assertEqual(len(train_ids), len(train_records))
        self.assertEqual(train_ids & validation_ids, set())
        self.assertGreaterEqual(
            sum(1 for record in train_records if record["id"].startswith("v4-sqli-")),
            160,
        )

        assert_evidence_in_input(self, supplement_records)
        format_split(train_records)
        format_split(validation_records)


if __name__ == "__main__":
    unittest.main()

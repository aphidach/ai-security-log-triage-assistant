#!/usr/bin/env python3
"""Regression checks for the Phase 8 v4.7 Qwen3.5 calibration workflow."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

from ml.unsloth.train_lora import FAST_VISION_MODEL_LOADER, load_config, resolve_model_loader  # noqa: E402
from ml.unsloth.train_lora_vision_qwen import (  # noqa: E402
    build_preflight_report as build_vision_preflight_report,
)
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


class V47Qwen35AuthSqliSeverityCalibrationWorkflowTest(unittest.TestCase):
    def test_v4_7_failure_slice_contract(self) -> None:
        from scripts.create_v4_7_qwen35_auth_sqli_severity_calibration_slice import (
            OUTPUT_JSON_PATH,
            OUTPUT_MD_PATH,
            build_report,
            main as create_v4_7_slice,
        )

        expected_report = build_report()
        checked_report = load_json(OUTPUT_JSON_PATH)

        self.assertEqual(checked_report, expected_report)
        self.assertTrue(OUTPUT_MD_PATH.exists())
        self.assertEqual(checked_report["fixed_test_split_used"], False)
        self.assertEqual(checked_report["case_count"], 18)
        self.assertEqual(
            checked_report["bucket_counts"],
            {
                "normal_to_bruteforce": 7,
                "sqli_to_bruteforce": 2,
                "bruteforce_medium_to_high": 7,
                "port_recon_medium_to_high": 1,
                "traversal_evidence_miss": 1,
            },
        )
        self.assertEqual(
            [case["id"] for case in checked_report["cases"]],
            [
                "v3-hard-000001",
                "v3-hard-000002",
                "v3-hard-000003",
                "v3-hard-000015",
                "v3-hard-000016",
                "v3-hard-000018",
                "v3-hard-000021",
                "v3-hard-000025",
                "v3-hard-000035",
                "v3-hard-000050",
                "v4-6-qwen35-cal-000121",
                "v4-6-qwen35-cal-000122",
                "v4-6-qwen35-cal-000123",
                "v4-6-qwen35-cal-000124",
                "v4-6-qwen35-cal-000136",
                "v4-6-qwen35-cal-000137",
                "v4-6-qwen35-cal-000138",
                "v4-6-qwen35-cal-000139",
            ],
        )

        test_path = ROOT / "data" / "splits" / "test.jsonl"
        before_test_hash = file_sha256(test_path)
        before_report_hashes = {
            OUTPUT_JSON_PATH: file_sha256(OUTPUT_JSON_PATH),
            OUTPUT_MD_PATH: file_sha256(OUTPUT_MD_PATH),
        }

        self.assertEqual(create_v4_7_slice(), 0)

        self.assertEqual(file_sha256(test_path), before_test_hash)
        self.assertEqual(
            {path: file_sha256(path) for path in before_report_hashes},
            before_report_hashes,
        )

    def test_v4_7_dataset_contract(self) -> None:
        from scripts.create_v4_7_qwen35_auth_sqli_severity_calibration_dataset import (
            SUPPLEMENT_PATH,
            TRAIN_PLUS_PATH,
            V4_7_PROBE_PATH,
            V4_7_TRAIN_PATH,
            V4_7_VALIDATION_PATH,
            build_v4_7_split_records,
            main as create_v4_7_dataset,
        )

        expected_train_records, expected_validation_records, expected_supplement_records, expected_probe_records = (
            build_v4_7_split_records()
        )
        checked_train_records = load_jsonl(V4_7_TRAIN_PATH)
        checked_train_plus_records = load_jsonl(TRAIN_PLUS_PATH)
        checked_validation_records = load_jsonl(V4_7_VALIDATION_PATH)
        checked_supplement_records = load_jsonl(SUPPLEMENT_PATH)
        checked_probe_records = load_jsonl(V4_7_PROBE_PATH)

        expected_clean_supplement = [
            {key: value for key, value in record.items() if key != "metadata"}
            for record in expected_supplement_records
        ]

        self.assertEqual(checked_train_records, expected_train_records)
        self.assertEqual(checked_train_plus_records, expected_train_records)
        self.assertEqual(checked_validation_records, expected_validation_records)
        self.assertEqual(checked_supplement_records, expected_clean_supplement)
        self.assertEqual(checked_probe_records, expected_probe_records)
        self.assertTrue(all("metadata" not in record for record in checked_supplement_records))

        test_path = ROOT / "data" / "splits" / "test.jsonl"
        before_test_hash = file_sha256(test_path)
        before_artifact_hashes = {
            SUPPLEMENT_PATH: file_sha256(SUPPLEMENT_PATH),
            TRAIN_PLUS_PATH: file_sha256(TRAIN_PLUS_PATH),
            V4_7_TRAIN_PATH: file_sha256(V4_7_TRAIN_PATH),
            V4_7_VALIDATION_PATH: file_sha256(V4_7_VALIDATION_PATH),
            V4_7_PROBE_PATH: file_sha256(V4_7_PROBE_PATH),
        }

        self.assertEqual(create_v4_7_dataset(), 0)

        self.assertEqual(file_sha256(test_path), before_test_hash)
        self.assertEqual(
            {path: file_sha256(path) for path in before_artifact_hashes},
            before_artifact_hashes,
        )

        self.assertEqual(len(checked_supplement_records), 150)
        self.assertEqual(
            label_counts(checked_supplement_records),
            {
                "normal": 69,
                "failed_login_bruteforce": 39,
                "sql_injection_attempt": 23,
                "directory_traversal_attempt": 9,
                "port_scan_or_recon": 10,
            },
        )
        self.assertEqual(len(checked_probe_records), 30)
        self.assertEqual(
            label_counts(checked_probe_records),
            {
                "normal": 15,
                "failed_login_bruteforce": 7,
                "sql_injection_attempt": 5,
                "directory_traversal_attempt": 1,
                "port_scan_or_recon": 2,
            },
        )
        self.assertEqual(len(checked_train_records), 1460)
        self.assertEqual(
            label_counts(checked_train_records),
            {
                "normal": 405,
                "failed_login_bruteforce": 186,
                "sql_injection_attempt": 439,
                "directory_traversal_attempt": 205,
                "port_scan_or_recon": 225,
            },
        )
        self.assertEqual(len(checked_validation_records), 130)
        self.assertEqual(
            label_counts(checked_validation_records),
            {
                "normal": 45,
                "failed_login_bruteforce": 26,
                "sql_injection_attempt": 21,
                "directory_traversal_attempt": 17,
                "port_scan_or_recon": 21,
            },
        )

        train_ids = {record["id"] for record in checked_train_records}
        validation_ids = {record["id"] for record in checked_validation_records}
        probe_ids = {record["id"] for record in checked_probe_records}
        self.assertEqual(len(train_ids), len(checked_train_records))
        self.assertEqual(len(validation_ids), len(checked_validation_records))
        self.assertEqual(train_ids & validation_ids, set())
        self.assertTrue(probe_ids <= validation_ids)
        self.assertEqual(train_ids & probe_ids, set())
        self.assertEqual(
            sum(1 for record in checked_train_records if record["id"].startswith("v4-7-qwen35-cal-")),
            120,
        )

        hard_contrast_records = load_jsonl(
            ROOT / "data" / "generated" / "v3-hard-contrast-security-triage.jsonl"
        )
        hard_contrast_inputs = {record["input"] for record in hard_contrast_records}
        supplement_inputs = {record["input"] for record in checked_supplement_records}
        self.assertEqual(supplement_inputs & hard_contrast_inputs, set())

        assert_evidence_in_input(self, checked_supplement_records)
        format_split(checked_train_records)
        format_split(checked_validation_records)
        format_split(checked_probe_records)

    def test_v4_7_qwen35_config_preflight_contract(self) -> None:
        config_path = ROOT / "ml" / "unsloth" / "qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml"
        config = load_config(config_path)

        self.assertEqual(config["model"]["base_model"], "unsloth/Qwen3.5-0.8B")
        self.assertEqual(resolve_model_loader(config["model"]), FAST_VISION_MODEL_LOADER)
        self.assertEqual(config["model"]["max_seq_length"], 1024)
        self.assertEqual(config["format"]["prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(
            config["data"]["train_path"],
            "data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl",
        )
        self.assertEqual(
            config["data"]["validation_path"],
            "data/splits/validation-v4-7-qwen35-auth-sqli-severity-calibration.jsonl",
        )
        self.assertEqual(config["training"]["max_steps"], 275)
        self.assertEqual(config["training"]["learning_rate"], 0.00008)
        self.assertIn("v4-7-auth-sqli-severity-calibration", config["output"]["output_dir"])

        report = build_vision_preflight_report(config_path, config)
        self.assertEqual(report["model"]["loader"], FAST_VISION_MODEL_LOADER)
        self.assertEqual(report["prompt"]["config_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(report["prompt"]["formatter_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(report["splits"]["train_records"], 1460)
        self.assertEqual(report["splits"]["validation_records"], 130)
        self.assertEqual(
            report["splits"]["train_labels"],
            {
                "directory_traversal_attempt": 205,
                "failed_login_bruteforce": 186,
                "normal": 405,
                "port_scan_or_recon": 225,
                "sql_injection_attempt": 439,
            },
        )


if __name__ == "__main__":
    unittest.main()

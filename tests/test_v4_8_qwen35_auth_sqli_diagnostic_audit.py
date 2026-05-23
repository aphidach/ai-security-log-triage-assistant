#!/usr/bin/env python3
"""Regression checks for the Phase 8 v4.8 Qwen3.5 diagnostic audit."""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

V48_REPORT_JSON = ROOT / "reports" / "phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json"
V48_REPORT_MD = ROOT / "reports" / "phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.md"
V48_REPORT_HTML = ROOT / "reports" / "phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html"


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class V48Qwen35AuthSqliDiagnosticAuditTest(unittest.TestCase):
    def test_v4_8_audit_contract(self) -> None:
        from scripts.create_v4_8_qwen35_auth_sqli_diagnostic_audit import build_report

        report = load_json(V48_REPORT_JSON)
        self.assertEqual(report, build_report())
        self.assertEqual(report["diagnostic_type"], "v4_8_auth_sqli_severity_diagnostic_audit")
        self.assertFalse(report["fixed_test_split_used"])
        self.assertFalse(report["training_artifacts_created"])
        self.assertEqual(report["decision"]["status"], "prepare_v4_8_diagnostic_first")
        self.assertEqual(report["decision"]["fixed_split"], "closed")

        comparator = report["comparator_status"]["v4_6_on_v4_7_probe"]
        self.assertEqual(comparator["status"], "blocked_not_served")
        self.assertEqual(comparator["requested_alias"], "qwen3.6-8B-triage-v2")
        self.assertEqual(
            comparator["observed_served_model_ids"],
            ["unsloth/Qwen3.5-0.8B", "qwen3.6-8B-triage-v3"],
        )

        self.assertEqual(report["headline_metrics"]["v4_7_model"]["label_accuracy"], 0.366667)
        self.assertEqual(report["headline_metrics"]["heuristic"]["label_accuracy"], 0.666667)
        self.assertEqual(report["headline_metrics"]["base_qwen35"]["invalid_output_count"], 1)
        self.assertEqual(
            report["metric_deltas"]["v4_7_model_minus_heuristic"]["label_accuracy"],
            -0.3,
        )

    def test_v4_8_bucket_summary_records_next_failure_focus(self) -> None:
        report = load_json(V48_REPORT_JSON)
        buckets = {bucket["bucket"]: bucket for bucket in report["bucket_summary"]}

        self.assertEqual(buckets["normal_auth_negative"]["sample_count"], 15)
        self.assertEqual(buckets["normal_auth_negative"]["reports"]["v4_7_model"]["label_correct"], 0)
        self.assertEqual(buckets["normal_auth_negative"]["reports"]["heuristic"]["label_correct"], 13)

        self.assertEqual(buckets["sqli_auth_context"]["sample_count"], 5)
        self.assertEqual(buckets["sqli_auth_context"]["reports"]["v4_7_model"]["label_correct"], 1)
        self.assertEqual(buckets["sqli_auth_context"]["reports"]["heuristic"]["label_correct"], 3)

        self.assertEqual(buckets["bruteforce_medium_severity"]["sample_count"], 7)
        self.assertEqual(buckets["bruteforce_medium_severity"]["reports"]["v4_7_model"]["label_correct"], 7)
        self.assertEqual(buckets["bruteforce_medium_severity"]["reports"]["v4_7_model"]["severity_correct"], 0)

    def test_v4_8_reports_are_traceable(self) -> None:
        markdown = V48_REPORT_MD.read_text(encoding="utf-8")
        html = V48_REPORT_HTML.read_text(encoding="utf-8")

        self.assertIn("Phase 8 V4.8 Qwen3.5 Auth/SQLi Diagnostic Audit", markdown)
        self.assertIn("v4.6 on v4.7 probe: `blocked_not_served`", markdown)
        self.assertIn("`normal_auth_negative`", markdown)
        self.assertIn("`bruteforce_medium_severity`", markdown)

        self.assertIn("<title>Phase 8 v4.8 Qwen3.5 Diagnostic Audit</title>", html)
        self.assertIn("fixed split remains closed", html)
        self.assertIn("Case Matrix", html)

    def test_v4_8_audit_script_is_deterministic_and_does_not_create_training_artifacts(self) -> None:
        from scripts.create_v4_8_qwen35_auth_sqli_diagnostic_audit import main as create_v4_8_audit

        test_path = ROOT / "data" / "splits" / "test.jsonl"
        before_test_hash = file_sha256(test_path)
        before_report_hashes = {
            V48_REPORT_JSON: file_sha256(V48_REPORT_JSON),
            V48_REPORT_MD: file_sha256(V48_REPORT_MD),
            V48_REPORT_HTML: file_sha256(V48_REPORT_HTML),
        }

        self.assertEqual(create_v4_8_audit(), 0)

        self.assertEqual(file_sha256(test_path), before_test_hash)
        self.assertEqual(
            {path: file_sha256(path) for path in before_report_hashes},
            before_report_hashes,
        )
        self.assertEqual(list((ROOT / "data" / "splits").glob("*v4-8*")), [])
        self.assertEqual(list((ROOT / "data" / "generated").glob("*v4-8*")), [])
        self.assertEqual(list((ROOT / "ml" / "unsloth").glob("*v4-8*")), [])


if __name__ == "__main__":
    unittest.main()

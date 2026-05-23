#!/usr/bin/env python3
"""Regression checks for the Phase 8 v4.4 hard-contrast boundary audit."""

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

V44_DOC = ROOT / "docs" / "output-structure-fix" / "phase-8-v4-4-hard-contrast-boundary-audit-plan.md"
V44_REPORT_JSON = ROOT / "reports" / "phase-8-v4-4-hard-contrast-boundary-audit.json"
V44_REPORT_MD = ROOT / "reports" / "phase-8-v4-4-hard-contrast-boundary-audit.md"


class V44HardContrastBoundaryAuditTest(unittest.TestCase):
    def test_v4_4_doc_records_boundary_audit_decision(self) -> None:
        content = V44_DOC.read_text(encoding="utf-8")

        self.assertIn("Status", content)
        self.assertIn("Audit complete", content)
        self.assertIn("union label failures มี `26`", content)
        self.assertIn("persistent failures มี `25`", content)
        self.assertIn("SQLi/traversal/recon -> normal มี `20/50`", content)
        self.assertIn("`22/50`", content)
        self.assertIn("base model ตรงจาก Hub", content)
        self.assertIn("ไม่ใช่ model ที่ train/LoRA แล้ว", content)
        self.assertIn("Hold the base Qwen3.5-0.8B candidate after v4.4 boundary audit", content)
        self.assertIn("No `data/splits/test.jsonl` run was opened", content)
        self.assertIn("No `ml/unsloth/config.v4-4.yaml`", content)

    def test_v4_4_report_contract(self) -> None:
        report = json.loads(V44_REPORT_JSON.read_text(encoding="utf-8"))

        self.assertEqual(report["diagnostic_type"], "hard_contrast_boundary_audit")
        self.assertFalse(report["fixed_test_split_used"])
        self.assertFalse(report["training_artifacts_created"])
        self.assertEqual(report["union_label_failure_count"], 26)
        self.assertEqual(report["persistent_label_failure_count"], 25)
        self.assertEqual(
            report["probe_summaries"]["temp_0"]["key_case_counts"][
                "sqli_traversal_recon_to_normal_count"
            ],
            20,
        )
        self.assertEqual(
            report["probe_summaries"]["temp_0_3"]["key_case_counts"][
                "sqli_traversal_recon_to_normal_count"
            ],
            22,
        )

    def test_v4_4_markdown_report_is_traceable(self) -> None:
        content = V44_REPORT_MD.read_text(encoding="utf-8")

        self.assertIn("Phase 8 V4.4 Hard-Contrast Boundary Audit", content)
        self.assertIn("Union label failures: `26` IDs", content)
        self.assertIn("Persistent failures across both probes: `25` IDs", content)
        self.assertIn("`v3-hard-000024`", content)
        self.assertIn("No Training Artifacts", content)

    def test_v4_4_does_not_create_training_artifacts(self) -> None:
        self.assertEqual(list((ROOT / "data" / "splits").glob("*v4-4*")), [])
        self.assertEqual(list((ROOT / "data" / "generated").glob("*v4-4*")), [])
        self.assertFalse((ROOT / "ml" / "unsloth" / "config.v4-4.yaml").exists())


if __name__ == "__main__":
    unittest.main()

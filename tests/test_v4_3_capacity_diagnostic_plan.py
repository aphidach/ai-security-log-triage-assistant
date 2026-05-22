#!/usr/bin/env python3
"""Regression checks for the Phase 8 v4.3 capacity diagnostic plan."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]

from scripts.model_adapters.openai_compatible import (  # noqa: E402
    OPENAI_COMPATIBLE_ENV,
    _build_config,
)
from scripts.model_adapters.prompt_contract import TRIAGE_PROMPT_VERSION  # noqa: E402


V42_DOC = ROOT / "docs" / "output-structure-fix" / "phase-8-v4-2-sqli-priority-diagnostic-plan.md"
V43_DOC = ROOT / "docs" / "output-structure-fix" / "phase-8-v4-3-capacity-architecture-diagnostic-plan.md"


class V43CapacityDiagnosticPlanTest(unittest.TestCase):
    def test_default_prompt_profile_remains_v2_1(self) -> None:
        config_path = self.write_config(
            """
openai-compatible:
  base_url: http://yaml.example/v1
  api_key: yaml-key
  model: lfm2-security-triage-v4-1
  max_tokens: 2048
  response_format: structured_outputs
  schema_path: data/schemas/triage-output.schema.json
"""
        )

        with patch.dict(os.environ, {}, clear=True):
            config, error = _build_config(
                "openai-compatible",
                OPENAI_COMPATIBLE_ENV,
                base_url=None,
                api_key=None,
                model=None,
                timeout_seconds=None,
                max_retries=None,
                max_tokens=None,
                response_format=None,
                schema_path=None,
                config_path=config_path,
            )

        self.assertIsNone(error)
        assert config is not None
        self.assertEqual(config.prompt_version, TRIAGE_PROMPT_VERSION)

    def test_v4_2_posthoc_fixed_split_sanity_is_documented_as_non_gate(self) -> None:
        content = V42_DOC.read_text(encoding="utf-8")

        self.assertIn("Post-Hoc Fixed Split Sanity Check", content)
        self.assertIn("0.893333", content)
        self.assertIn("not a Phase 8 gate", content)
        self.assertIn("not tuning feedback", content)

    def test_v4_3_plan_contract(self) -> None:
        content = V43_DOC.read_text(encoding="utf-8")

        self.assertIn("Status", content)
        self.assertIn("Planned", content)
        self.assertIn("No new synthetic data", content)
        self.assertIn("Do not run `data/splits/test.jsonl`", content)
        self.assertIn("data/generated/v3-hard-contrast-security-triage.jsonl", content)
        self.assertIn("OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.1", content)
        self.assertIn("capacity/architecture diagnostic", content)

    def test_v4_3_plan_does_not_include_fixed_split_eval_command(self) -> None:
        content = V43_DOC.read_text(encoding="utf-8")

        self.assertNotIn("--split data/splits/test.jsonl", content)
        self.assertNotIn("OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.2-sqli-priority", content)

    def test_v4_3_does_not_create_training_artifacts(self) -> None:
        self.assertEqual(list((ROOT / "data" / "splits").glob("*v4-3*")), [])
        self.assertEqual(list((ROOT / "data" / "generated").glob("*v4-3*")), [])
        self.assertFalse((ROOT / "ml" / "unsloth" / "config.v4-3.yaml").exists())

    def write_config(self, body: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "config-adapter.yml"
        path.write_text(body.strip() + "\n", encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()

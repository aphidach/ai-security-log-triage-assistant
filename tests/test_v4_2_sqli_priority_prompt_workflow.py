#!/usr/bin/env python3
"""Regression checks for the Phase 8 v4.2 SQLi priority prompt diagnostic."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]

from scripts.model_adapters.openai_compatible import (  # noqa: E402
    OPENAI_COMPATIBLE_ENV,
    REQUEST_MODE_STRUCTURED_OUTPUTS,
    OpenAICompatibleAdapter,
    _build_config,
    _chat_completion_kwargs,
)
from scripts.model_adapters.prompt_contract import (  # noqa: E402
    PROMPT_VERSIONS,
    SQLI_PRIORITY_PROMPT_VERSION,
    TRIAGE_PROMPT_VERSION,
    TRIAGE_SYSTEM_PROMPT,
    get_triage_system_prompt,
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class V42SqliPriorityPromptWorkflowTest(unittest.TestCase):
    def test_v4_2_failure_slice_contract(self) -> None:
        from scripts.create_v4_2_sqli_priority_diagnostic_slice import (
            OUTPUT_JSON_PATH,
            OUTPUT_MD_PATH,
            build_report,
            main as create_v4_2_sqli_priority_diagnostic_slice,
        )

        expected_report = build_report()
        checked_report = load_json(OUTPUT_JSON_PATH)

        self.assertEqual(checked_report, expected_report)
        self.assertTrue(OUTPUT_MD_PATH.exists())
        self.assertEqual(checked_report["fixed_test_split_used"], False)
        self.assertEqual(checked_report["union_label_failure_count"], 6)
        self.assertEqual(checked_report["diagnostic_type"], "prompt_priority")
        self.assertEqual(checked_report["training_artifacts_created"], False)

        temp0_bucket_counts = {
            bucket["bucket"]: bucket["count"]
            for bucket in checked_report["probe_summaries"]["temp_0"]["bucket_summary"]
        }
        self.assertEqual(
            temp0_bucket_counts,
            {
                "normal_to_bruteforce": 2,
                "sqli_to_normal": 1,
                "sqli_to_port": 1,
                "sqli_to_traversal": 2,
            },
        )

        temp03_bucket_counts = {
            bucket["bucket"]: bucket["count"]
            for bucket in checked_report["probe_summaries"]["temp_0_3"]["bucket_summary"]
        }
        self.assertEqual(
            temp03_bucket_counts,
            {
                "normal_to_bruteforce": 2,
                "sqli_to_normal": 1,
                "sqli_to_port": 1,
                "sqli_to_traversal": 1,
            },
        )

        self.assertEqual(
            checked_report["union_failure_ids"],
            [
                "v3-hard-000001",
                "v3-hard-000003",
                "v3-hard-000024",
                "v3-hard-000025",
                "v3-hard-000026",
                "v3-hard-000029",
            ],
        )

        test_path = ROOT / "data" / "splits" / "test.jsonl"
        before_test_hash = file_sha256(test_path)
        before_report_hashes = {
            OUTPUT_JSON_PATH: file_sha256(OUTPUT_JSON_PATH),
            OUTPUT_MD_PATH: file_sha256(OUTPUT_MD_PATH),
        }

        self.assertEqual(create_v4_2_sqli_priority_diagnostic_slice(), 0)

        self.assertEqual(file_sha256(test_path), before_test_hash)
        self.assertEqual(
            {path: file_sha256(path) for path in before_report_hashes},
            before_report_hashes,
        )

    def test_prompt_profiles_keep_default_and_add_sqli_priority(self) -> None:
        self.assertIn(TRIAGE_PROMPT_VERSION, PROMPT_VERSIONS)
        self.assertIn(SQLI_PRIORITY_PROMPT_VERSION, PROMPT_VERSIONS)
        self.assertEqual(get_triage_system_prompt(TRIAGE_PROMPT_VERSION), TRIAGE_SYSTEM_PROMPT)

        sqli_priority_prompt = get_triage_system_prompt(SQLI_PRIORITY_PROMPT_VERSION)
        self.assertIn("SQLi priority rules", sqli_priority_prompt)
        self.assertIn("OR 1=1", sqli_priority_prompt)
        self.assertIn("information_schema", sqli_priority_prompt)
        self.assertIn("Traversal requires file or path access evidence", sqli_priority_prompt)
        self.assertNotEqual(sqli_priority_prompt, TRIAGE_SYSTEM_PROMPT)

    def test_openai_compatible_env_selects_sqli_priority_prompt(self) -> None:
        config_path = self.write_config(
            """
openai-compatible:
  base_url: http://yaml.example/v1
  api_key: yaml-key
  model: yaml-model
  max_tokens: 123
  response_format: structured_outputs
  prompt_version: triage-json-v2.1
  schema_path: data/schemas/triage-output.schema.json
"""
        )
        env = {
            "OPENAI_COMPATIBLE_PROMPT_VERSION": SQLI_PRIORITY_PROMPT_VERSION,
        }

        with patch.dict(os.environ, env, clear=True):
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
        self.assertEqual(config.prompt_version, SQLI_PRIORITY_PROMPT_VERSION)

    def test_chat_completion_kwargs_send_selected_prompt_profile(self) -> None:
        kwargs = _chat_completion_kwargs(
            request_mode=REQUEST_MODE_STRUCTURED_OUTPUTS,
            model="lfm2-security-triage-v4-1",
            log_line="GET /search?q=information_schema.tables HTTP/1.1",
            max_tokens=2048,
            provider_schema={"type": "object"},
            request_options={"temperature": 0},
            extra_body=None,
            prompt_version=SQLI_PRIORITY_PROMPT_VERSION,
        )

        self.assertEqual(kwargs["messages"][0]["content"], get_triage_system_prompt(SQLI_PRIORITY_PROMPT_VERSION))
        self.assertEqual(kwargs["messages"][1]["role"], "user")

    def test_adapter_metadata_reports_selected_prompt_version(self) -> None:
        config_path = self.write_config(
            """
openai-compatible:
  base_url: http://yaml.example/v1
  api_key: yaml-key
  model: lfm2-security-triage-v4-1
  max_tokens: 2048
  response_format: structured_outputs
  prompt_version: triage-json-v2.2-sqli-priority
  schema_path: data/schemas/triage-output.schema.json
"""
        )

        with patch.dict(os.environ, {}, clear=True):
            adapter = OpenAICompatibleAdapter(config_path=config_path)

        metadata = adapter._metadata()
        self.assertEqual(metadata["prompt_version"], SQLI_PRIORITY_PROMPT_VERSION)
        self.assertEqual(metadata["env"]["prompt_version"], "OPENAI_COMPATIBLE_PROMPT_VERSION")

    def test_v4_2_does_not_create_training_artifacts(self) -> None:
        self.assertEqual(list((ROOT / "data" / "splits").glob("*v4-2*")), [])
        self.assertFalse((ROOT / "ml" / "unsloth" / "config.v4-2.yaml").exists())
        self.assertFalse(
            (ROOT / "data" / "generated" / "v4-2-sqli-boundary-repair-security-triage.jsonl").exists()
        )

    def write_config(self, body: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "config-adapter.yml"
        path.write_text(body.strip() + "\n", encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()

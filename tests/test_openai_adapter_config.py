"""Regression checks for OpenAI-compatible adapter runtime config."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.model_adapters.openai_compatible import (
    OPENAI_COMPATIBLE_ENV,
    REQUEST_MODE_STRUCTURED_OUTPUTS,
    _build_config,
    _chat_completion_kwargs,
)


ROOT = Path(__file__).resolve().parents[1]


class OpenAIAdapterConfigTest(unittest.TestCase):
    def test_yaml_config_supplies_runtime_and_request_options(self) -> None:
        config_path = self.write_config(
            """
defaults:
  timeout_seconds: 99
  request:
    temperature: 0.3
    top_p: 0.9
    extra_body:
      min_p: 0.15
openai-compatible:
  base_url: http://example.test/v1
  api_key: local
  model: model-from-yaml
  max_retries: 0
  max_tokens: 123
  response_format: structured_outputs
  schema_path: data/schemas/triage-output.schema.json
  request:
    temperature: 0.4
    frequency_penalty: 0.1
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
        self.assertEqual(config.base_url, "http://example.test/v1")
        self.assertEqual(config.model, "model-from-yaml")
        self.assertEqual(config.max_tokens, 123)
        self.assertEqual(config.response_format, "structured_outputs")
        self.assertEqual(config.request_options["temperature"], 0.4)
        self.assertEqual(config.request_options["top_p"], 0.9)
        self.assertEqual(config.request_options["frequency_penalty"], 0.1)
        self.assertEqual(config.extra_body, {"min_p": 0.15})

    def test_environment_values_override_yaml_config(self) -> None:
        config_path = self.write_config(
            """
openai-compatible:
  base_url: http://yaml.example/v1
  api_key: yaml-key
  model: yaml-model
  max_tokens: 123
  response_format: structured_outputs
"""
        )
        env = {
            "OPENAI_COMPATIBLE_MODEL": "env-model",
            "OPENAI_COMPATIBLE_MAX_TOKENS": "456",
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
        self.assertEqual(config.model, "env-model")
        self.assertEqual(config.max_tokens, 456)

    def test_chat_completion_kwargs_include_request_options_and_extra_body(self) -> None:
        kwargs = _chat_completion_kwargs(
            request_mode=REQUEST_MODE_STRUCTURED_OUTPUTS,
            model="model-a",
            log_line="2026-05-21 test log",
            max_tokens=256,
            provider_schema={"type": "object"},
            request_options={"temperature": 0.3, "top_p": 0.9},
            extra_body={"min_p": 0.15, "repetition_penalty": 1.05},
        )

        self.assertEqual(kwargs["temperature"], 0.3)
        self.assertEqual(kwargs["top_p"], 0.9)
        self.assertEqual(kwargs["max_tokens"], 256)
        self.assertEqual(kwargs["extra_body"]["min_p"], 0.15)
        self.assertEqual(kwargs["extra_body"]["repetition_penalty"], 1.05)
        self.assertEqual(
            kwargs["extra_body"]["structured_outputs"],
            {"json": {"type": "object"}},
        )

    def write_config(self, body: str) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "config-adapter.yml"
        path.write_text(body.strip() + "\n", encoding="utf-8")
        return path


if __name__ == "__main__":
    unittest.main()

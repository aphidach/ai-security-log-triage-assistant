#!/usr/bin/env python3
"""Regression checks for the Qwen3.5 exploratory Unsloth training pilot."""

from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

from ml.unsloth.train_lora import (  # noqa: E402
    FAST_LANGUAGE_MODEL_LOADER,
    FAST_VISION_MODEL_LOADER,
    build_preflight_report,
    load_config,
    resolve_model_loader,
)
from ml.unsloth.train_lora_vision_qwen import (  # noqa: E402
    build_preflight_report as build_vision_preflight_report,
    build_vision_training_messages,
)
from scripts.model_adapters.prompt_contract import TRIAGE_PROMPT_VERSION  # noqa: E402


class Qwen35TrainingPilotConfigTest(unittest.TestCase):
    def test_existing_lfm2_configs_default_to_fast_language_model(self) -> None:
        config_path = ROOT / "ml" / "unsloth" / "config.v4.yaml"
        config = load_config(config_path)

        self.assertNotIn("loader", config["model"])
        self.assertEqual(resolve_model_loader(config["model"]), FAST_LANGUAGE_MODEL_LOADER)

        report = build_preflight_report(config_path, config)
        self.assertEqual(report["model"]["loader"], FAST_LANGUAGE_MODEL_LOADER)
        self.assertEqual(report["splits"]["train_records"], 1070)
        self.assertEqual(report["splits"]["validation_records"], 75)

    def test_qwen35_pilot_uses_fast_vision_model_text_only_lora(self) -> None:
        config_path = ROOT / "ml" / "unsloth" / "qwen3-5-0-8b-security-triage-pilot.yaml"
        config = load_config(config_path)

        self.assertEqual(config["model"]["base_model"], "unsloth/Qwen3.5-0.8B")
        self.assertEqual(resolve_model_loader(config["model"]), FAST_VISION_MODEL_LOADER)
        self.assertNotIn("dtype", config["model"])
        self.assertEqual(
            config["lora"]["target_modules"],
            ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        )
        self.assertFalse(config["lora"]["finetune_vision_layers"])
        self.assertTrue(config["lora"]["finetune_language_layers"])
        self.assertTrue(config["lora"]["finetune_attention_modules"])
        self.assertTrue(config["lora"]["finetune_mlp_modules"])

        report = build_vision_preflight_report(config_path, config)
        self.assertEqual(report["model"]["loader"], FAST_VISION_MODEL_LOADER)
        self.assertEqual(report["prompt"]["config_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(report["splits"]["train_records"], 1220)
        self.assertEqual(report["splits"]["validation_records"], 75)

    def test_qwen35_vision_runner_formats_text_only_messages(self) -> None:
        record = {
            "id": "sample-test",
            "instruction": "Analyze this security log and classify whether it is suspicious.",
            "input": "192.168.1.20 - - [10/May/2026] \"GET /login?user=admin' OR '1'='1 HTTP/1.1\" 200",
            "output": {
                "label": "sql_injection_attempt",
                "severity": "high",
                "is_suspicious": True,
                "evidence": ["admin' OR '1'='1"],
                "reason": "The request contains a common SQL injection pattern.",
                "recommended_action": "Review web application logs and block or rate-limit the source IP.",
            },
        }

        messages = build_vision_training_messages(record)

        self.assertEqual([message["role"] for message in messages], ["system", "user", "assistant"])
        for message in messages:
            self.assertEqual(len(message["content"]), 1)
            self.assertEqual(message["content"][0]["type"], "text")
            self.assertIn("text", message["content"][0])
            self.assertNotIn("image", message["content"][0])


if __name__ == "__main__":
    unittest.main()

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
        self.assertNotIn("target_modules", config["lora"])
        self.assertFalse(config["lora"]["finetune_vision_layers"])
        self.assertTrue(config["lora"]["finetune_language_layers"])
        self.assertTrue(config["lora"]["finetune_attention_modules"])
        self.assertTrue(config["lora"]["finetune_mlp_modules"])

        report = build_preflight_report(config_path, config)
        self.assertEqual(report["model"]["loader"], FAST_VISION_MODEL_LOADER)
        self.assertEqual(report["prompt"]["config_prompt_version"], TRIAGE_PROMPT_VERSION)
        self.assertEqual(report["splits"]["train_records"], 1220)
        self.assertEqual(report["splits"]["validation_records"], 75)


if __name__ == "__main__":
    unittest.main()

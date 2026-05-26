#!/usr/bin/env python3
"""Minimal Unsloth save script for a trained LoRA adapter.

This intentionally avoids the extra project merge/export wrapper logic so it is
easy to check how Unsloth's own save methods behave for one checkpoint.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.unsloth.train_lora import (  # noqa: E402
    FAST_LANGUAGE_MODEL_LOADER,
    FAST_VISION_MODEL_LOADER,
    coerce_bool,
    load_config,
    require_section,
    resolve_model_loader,
    resolve_repo_path,
    resolve_torch_dtype,
)


DEFAULT_CONFIG = ROOT / "ml" / "unsloth" / "qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml"
DEFAULT_OUTPUT_DIR = ROOT / "ml" / "unsloth" / "outputs" / "simple-unsloth-save"


def repo_path(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def resolve_adapter_path(config: dict[str, Any], adapter_path: Path | None) -> Path:
    if adapter_path is not None:
        return repo_path(adapter_path).resolve()
    output_config = require_section(config, "output")
    return resolve_repo_path(output_config.get("output_dir"), field_name="output.output_dir")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Save a LoRA adapter using Unsloth's own save helpers.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Training YAML config path.")
    parser.add_argument("--adapter-path", type=Path, help="LoRA adapter directory. Defaults to output.output_dir.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory.")
    parser.add_argument(
        "--mode",
        choices=("merged", "gguf"),
        default="merged",
        help="Use save_pretrained_merged or save_pretrained_gguf.",
    )
    parser.add_argument(
        "--load-in-4bit",
        choices=("true", "false"),
        default="false",
        help="Load base model in 4-bit before saving. Use false for clean GGUF experiments.",
    )
    parser.add_argument(
        "--save-method",
        default="merged_16bit",
        choices=("merged_16bit", "merged_4bit"),
        help="Method passed to save_pretrained_merged.",
    )
    parser.add_argument(
        "--gguf-quantization",
        default="f16",
        help="Quantization method passed to save_pretrained_gguf, for example f16, q8_0, q4_k_m.",
    )
    parser.add_argument("--force", action="store_true", help="Delete output dir before saving.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = repo_path(args.config).resolve()
    output_dir = repo_path(args.output_dir).resolve()

    config = load_config(config_path)
    model_config = require_section(config, "model")
    base_model = model_config.get("base_model")
    if not isinstance(base_model, str) or not base_model:
        raise ValueError("model.base_model must be a non-empty string")

    adapter_path = resolve_adapter_path(config, args.adapter_path)
    if not adapter_path.exists():
        raise FileNotFoundError(f"adapter path does not exist: {adapter_path}")

    if output_dir.exists() and args.force:
        shutil.rmtree(output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"output directory is not empty; pass --force: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    import torch

    loader = resolve_model_loader(model_config)
    load_in_4bit = coerce_bool(args.load_in_4bit, field_name="--load-in-4bit")

    # Import Unsloth before PEFT so the patched model classes are installed.
    if loader == FAST_LANGUAGE_MODEL_LOADER:
        from unsloth import FastLanguageModel
        from peft import PeftModel

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=base_model,
            max_seq_length=int(model_config.get("max_seq_length", 2048)),
            dtype=resolve_torch_dtype(model_config.get("dtype"), torch_module=torch),
            load_in_4bit=load_in_4bit,
        )
    elif loader == FAST_VISION_MODEL_LOADER:
        from unsloth import FastVisionModel
        from peft import PeftModel

        model, tokenizer = FastVisionModel.from_pretrained(
            model_name=base_model,
            load_in_4bit=load_in_4bit,
        )
    else:
        raise ValueError(f"unsupported model.loader: {loader}")

    model = PeftModel.from_pretrained(model, str(adapter_path))

    if args.mode == "merged":
        if not hasattr(model, "save_pretrained_merged"):
            raise RuntimeError("loaded model does not expose save_pretrained_merged")
        model.save_pretrained_merged(str(output_dir), tokenizer, save_method=args.save_method)
    else:
        if not hasattr(model, "save_pretrained_gguf"):
            raise RuntimeError("loaded model does not expose save_pretrained_gguf")
        model.save_pretrained_gguf(
            str(output_dir),
            tokenizer,
            quantization_method=args.gguf_quantization,
        )

    report = {
        "status": "ok",
        "mode": args.mode,
        "config": str(config_path),
        "base_model": base_model,
        "loader": loader,
        "adapter_path": str(adapter_path),
        "output_dir": str(output_dir),
        "load_in_4bit": load_in_4bit,
        "save_method": args.save_method if args.mode == "merged" else None,
        "gguf_quantization": args.gguf_quantization if args.mode == "gguf" else None,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Merge or export a trained LoRA adapter with the configured base model.

This script is intentionally separate from training and inference. The default
project workflow keeps LoRA adapters as the first output, then merges only when
the adapter is ready to serve or export as a standalone checkpoint or GGUF.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ml.unsloth.train_lora import (  # noqa: E402
    DEFAULT_CONFIG_PATH,
    FAST_LANGUAGE_MODEL_LOADER,
    FAST_VISION_MODEL_LOADER,
    TrainingConfigError,
    coerce_bool,
    load_config,
    report_path,
    require_section,
    resolve_model_loader,
    resolve_repo_path,
    resolve_torch_dtype,
)


DEFAULT_MERGED_DIR = ROOT / "ml" / "unsloth" / "outputs" / "lfm2-350m-security-triage-merged"
DEFAULT_GGUF_DIR = ROOT / "ml" / "unsloth" / "outputs" / "lfm2-350m-security-triage-gguf"
GGUF_QUANTIZATIONS = ("q8_0", "f16", "q4_k_m")

JsonObject = dict[str, Any]


class MergeAdapterError(RuntimeError):
    """Raised when adapter merge setup or export fails."""


def resolve_optional_repo_path(value: Path | None, *, default: Path) -> Path:
    path = value if value is not None else default
    if not path.is_absolute():
        path = ROOT / path
    return path.resolve()


def resolve_adapter_path(config: JsonObject, cli_adapter_path: Path | None) -> Path:
    if cli_adapter_path is not None:
        return resolve_optional_repo_path(cli_adapter_path, default=cli_adapter_path)

    output = require_section(config, "output")
    return resolve_repo_path(output.get("output_dir"), field_name="output.output_dir")


def build_preflight_report(
    *,
    config_path: Path,
    config: JsonObject,
    adapter_path: Path,
    output_dir: Path,
    export_format: str,
    save_method: str,
    gguf_quantizations: list[str],
    hub_repo: str | None,
) -> JsonObject:
    model_config = require_section(config, "model")
    return {
        "status": "merge_preflight_ok",
        "config_path": report_path(config_path),
        "base_model": model_config.get("base_model"),
        "loader": resolve_model_loader(model_config),
        "adapter_path": report_path(adapter_path),
        "adapter_exists": adapter_path.exists(),
        "output_dir": report_path(output_dir),
        "output_exists": output_dir.exists(),
        "export_format": export_format,
        "save_method": save_method,
        "gguf_quantizations": gguf_quantizations,
        "hub_repo": hub_repo,
    }


def load_model_tokenizer_and_adapter(config: JsonObject, adapter_path: Path) -> tuple[Any, Any, str]:
    model_config = require_section(config, "model")
    base_model = model_config.get("base_model")
    if not isinstance(base_model, str) or not base_model:
        raise MergeAdapterError("model.base_model must be a non-empty string")
    if not adapter_path.exists():
        raise MergeAdapterError(f"LoRA adapter path does not exist: {adapter_path}")

    try:
        import torch

        # Keep Unsloth first so the runtime patching matches train_lora.py and
        # inference.py in the same GPU environment.
        from peft import PeftModel
    except ModuleNotFoundError as exc:
        raise MergeAdapterError(
            "merge dependencies are missing. Activate the GPU environment and run scripts/setup_gpu_env.sh first."
        ) from exc

    try:
        loader = resolve_model_loader(model_config)
        load_in_4bit = coerce_bool(model_config.get("load_in_4bit", True), field_name="model.load_in_4bit")
        if loader == FAST_LANGUAGE_MODEL_LOADER:
            from unsloth import FastLanguageModel

            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name=base_model,
                max_seq_length=int(model_config.get("max_seq_length", 2048)),
                dtype=resolve_torch_dtype(model_config.get("dtype"), torch_module=torch),
                load_in_4bit=load_in_4bit,
            )
        elif loader == FAST_VISION_MODEL_LOADER:
            from unsloth import FastVisionModel

            model, tokenizer = FastVisionModel.from_pretrained(
                model_name=base_model,
                load_in_4bit=load_in_4bit,
            )
        else:
            raise MergeAdapterError(f"unsupported model.loader: {loader}")
        model = PeftModel.from_pretrained(model, str(adapter_path))
    except Exception as exc:
        raise MergeAdapterError(f"failed to load base model and LoRA adapter: {type(exc).__name__}: {exc}") from exc

    return model, tokenizer, base_model


def export_merged_checkpoint(
    *,
    config_path: Path,
    base_model: str,
    model: Any,
    tokenizer: Any,
    adapter_path: Path,
    output_dir: Path,
    save_method: str,
    force: bool,
) -> JsonObject:
    if output_dir.exists() and any(output_dir.iterdir()) and not force:
        raise MergeAdapterError(f"output directory is not empty; pass --force to overwrite: {output_dir}")

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        if hasattr(model, "save_pretrained_merged"):
            model.save_pretrained_merged(str(output_dir), tokenizer, save_method=save_method)
        else:
            merged_model = model.merge_and_unload()
            merged_model.save_pretrained(str(output_dir), safe_serialization=True)
            tokenizer.save_pretrained(str(output_dir))
    except Exception as exc:
        raise MergeAdapterError(f"failed to merge adapter: {type(exc).__name__}: {exc}") from exc

    return {
        "status": "merge_complete",
        "config_path": report_path(config_path),
        "base_model": base_model,
        "adapter_path": report_path(adapter_path),
        "output_dir": report_path(output_dir),
        "export_format": "merged",
        "save_method": save_method,
    }


def export_gguf(
    *,
    config_path: Path,
    base_model: str,
    model: Any,
    tokenizer: Any,
    adapter_path: Path,
    output_dir: Path,
    quantizations: list[str],
    hub_repo: str | None,
    hub_token: str | None,
    force: bool,
) -> JsonObject:
    if output_dir.exists() and any(output_dir.iterdir()) and not force:
        raise MergeAdapterError(f"output directory is not empty; pass --force to overwrite: {output_dir}")
    if not hasattr(model, "save_pretrained_gguf"):
        raise MergeAdapterError(
            "loaded model does not expose save_pretrained_gguf; verify the Unsloth version and import order"
        )
    if hub_repo and not hasattr(model, "push_to_hub_gguf"):
        raise MergeAdapterError(
            "loaded model does not expose push_to_hub_gguf; verify the Unsloth version and import order"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[JsonObject] = []
    try:
        for quantization in quantizations:
            quantized_dir = output_dir / quantization
            quantized_dir.mkdir(parents=True, exist_ok=True)
            model.save_pretrained_gguf(
                str(quantized_dir),
                tokenizer,
                quantization_method=quantization,
            )
            saved.append(
                {
                    "quantization_method": quantization,
                    "output_dir": report_path(quantized_dir),
                }
            )

        if hub_repo:
            for quantization in quantizations:
                model.push_to_hub_gguf(
                    hub_repo,
                    tokenizer,
                    quantization_method=quantization,
                    token=hub_token,
                )
    except Exception as exc:
        raise MergeAdapterError(f"failed to export GGUF: {type(exc).__name__}: {exc}") from exc

    return {
        "status": "gguf_export_complete",
        "config_path": report_path(config_path),
        "base_model": base_model,
        "adapter_path": report_path(adapter_path),
        "output_dir": report_path(output_dir),
        "export_format": "gguf",
        "gguf_quantizations": saved,
        "hub_repo": hub_repo,
    }


def normalize_gguf_quantizations(values: list[str] | None) -> list[str]:
    quantizations = values or ["q4_k_m"]
    invalid = [value for value in quantizations if value not in GGUF_QUANTIZATIONS]
    if invalid:
        raise MergeAdapterError(
            f"unsupported GGUF quantization(s): {', '.join(invalid)}; allowed: {', '.join(GGUF_QUANTIZATIONS)}"
        )
    return list(dict.fromkeys(quantizations))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge the configured Unsloth LoRA adapter or export it to GGUF.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"Training config path. Default: {DEFAULT_CONFIG_PATH}",
    )
    parser.add_argument(
        "--adapter-path",
        type=Path,
        help="LoRA adapter directory. Defaults to output.output_dir in the config.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help=(
            "Output directory. Defaults to the merged checkpoint dir for --export-format merged "
            f"and the GGUF dir for --export-format gguf."
        ),
    )
    parser.add_argument(
        "--export-format",
        default="merged",
        choices=("merged", "gguf"),
        help="Export format. Use merged for Hugging Face checkpoint, gguf for llama.cpp/Ollama/LM Studio.",
    )
    parser.add_argument(
        "--save-method",
        default="merged_16bit",
        choices=("merged_16bit", "merged_4bit"),
        help="Unsloth save method when save_pretrained_merged is available.",
    )
    parser.add_argument(
        "--gguf-quantization",
        action="append",
        choices=GGUF_QUANTIZATIONS,
        help=(
            "GGUF quantization method. Repeat for multiple exports. "
            "Defaults to q4_k_m when --export-format gguf is used."
        ),
    )
    parser.add_argument(
        "--hub-repo",
        help="Optional Hugging Face repo id for push_to_hub_gguf, for example username/model-name.",
    )
    parser.add_argument(
        "--hub-token",
        help="Optional Hugging Face token for --hub-repo. Prefer HF_TOKEN/HUGGING_FACE_HUB_TOKEN instead.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow writing into a non-empty output directory.",
    )
    parser.add_argument(
        "--preflight-only",
        action="store_true",
        help="Validate paths and config without loading the model or adapter.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config_path = args.config.resolve()
    try:
        config = load_config(config_path)
        adapter_path = resolve_adapter_path(config, args.adapter_path)
        default_output_dir = DEFAULT_GGUF_DIR if args.export_format == "gguf" else DEFAULT_MERGED_DIR
        output_dir = resolve_optional_repo_path(args.output_dir, default=default_output_dir)
        gguf_quantizations = (
            normalize_gguf_quantizations(args.gguf_quantization) if args.export_format == "gguf" else []
        )
        report = build_preflight_report(
            config_path=config_path,
            config=config,
            adapter_path=adapter_path,
            output_dir=output_dir,
            export_format=args.export_format,
            save_method=args.save_method,
            gguf_quantizations=gguf_quantizations,
            hub_repo=args.hub_repo,
        )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if args.preflight_only:
            return 0

        model, tokenizer, base_model = load_model_tokenizer_and_adapter(config, adapter_path)
        if args.export_format == "gguf":
            import os

            hub_token = args.hub_token or os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
            merge_report = export_gguf(
                config_path=config_path,
                base_model=base_model,
                model=model,
                tokenizer=tokenizer,
                adapter_path=adapter_path,
                output_dir=output_dir,
                quantizations=gguf_quantizations,
                hub_repo=args.hub_repo,
                hub_token=hub_token,
                force=args.force,
            )
        else:
            merge_report = export_merged_checkpoint(
                config_path=config_path,
                base_model=base_model,
                model=model,
                tokenizer=tokenizer,
                adapter_path=adapter_path,
                output_dir=output_dir,
                save_method=args.save_method,
                force=args.force,
            )
    except (OSError, TrainingConfigError, MergeAdapterError, ValueError) as exc:
        print(f"merge failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(merge_report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Structured Output Backend Inventory

Phase 1 inventory report for structured-output runtime work.

## Status

Updated 2026-05-20.

This report has enough current-endpoint metadata from Phase 0 to establish the baseline. The vLLM candidate has now served the Unsloth Studio LoRA adapter and passed the smoke output-contract gate through `structured_outputs`.

## Current Endpoint

| Field | Value |
| --- | --- |
| Adapter | `openai-compatible` |
| Runtime label | `unsloth-studio` |
| Exact backend | Unknown |
| Backend version | Unknown |
| Base URL | `http://192.168.8.141:8888/v1` |
| Requested model | `lfm2-security-triage` |
| Response model | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` |
| Prompt version | `triage-json-v2` |
| Response format requested | `json_schema` |
| Response format mode | `json_schema_strict` |
| Schema path | `data/schemas/triage-output.schema.json` |
| Preserved smoke JSON | `reports/openai-compatible-unsloth-studio-json-schema-smoke.json` |
| Preserved smoke Markdown | `reports/openai-compatible-unsloth-studio-json-schema-smoke.md` |
| JSON/schema success | `0.2` |
| Invalid outputs | `4/5` |

## vLLM Candidate

| Field | Value |
| --- | --- |
| Candidate backend | `vLLM` |
| Backend version | `0.21.0+cu129` CLI, `0.21.0` Python package |
| Base URL | `http://192.168.8.141:8080/v1` for the successful smoke run |
| Adapter path | `/mnt/c/Users/dargy/.unsloth/studio/outputs/unsloth_LFM2-350M_1779162226` |
| Adapter type | LoRA adapter |
| Base model | `unsloth/LFM2-350M` |
| LoRA rank | `16` |
| Served alias | `lfm2-security-triage` |
| Launch command | `vllm serve "$BASE_MODEL" --host 0.0.0.0 --port 8080 --enable-lora --lora-modules lfm2-security-triage="$ADAPTER_DIR" --max-lora-rank "$LORA_RANK"` |
| `/v1/models` output | Base model `unsloth/LFM2-350M`; LoRA alias `lfm2-security-triage` with parent `unsloth/LFM2-350M` |
| Primary structured mode to test | `structured_outputs` |
| Fallback mode to compare | `json_schema` |
| Successful smoke report | `reports/openai-compatible-vllm-structured-outputs-smoke.json` |
| Successful response model | `lfm2-security-triage` |

## Command Output To Paste Here

### Adapter Config

```json
{
  "base_model_name_or_path": "unsloth/LFM2-350M",
  "peft_type": "LORA",
  "task_type": "CAUSAL_LM",
  "r": 16,
  "lora_alpha": 16,
  "target_modules": [
    "v_proj",
    "gate_proj",
    "k_proj",
    "up_proj",
    "down_proj",
    "o_proj",
    "q_proj"
  ],
  "modules_to_save": null
}
```

### vLLM Version

```text
0.21.0+cu129
0.21.0
```

### GPU

```text
name, memory.total [MiB], driver_version
NVIDIA GeForce RTX 3060 Laptop GPU, 6144 MiB, 596.36
```

### Launch Command

```bash
ADAPTER_DIR=/mnt/c/Users/dargy/.unsloth/studio/outputs/unsloth_LFM2-350M_1779162226
BASE_MODEL="$(jq -r '.base_model_name_or_path // "LiquidAI/LFM2-350M"' "$ADAPTER_DIR/adapter_config.json")"
LORA_RANK="$(jq -r '.r // 64' "$ADAPTER_DIR/adapter_config.json")"

vllm serve "$BASE_MODEL" \
  --host 0.0.0.0 \
  --port 8080 \
  --enable-lora \
  --lora-modules lfm2-security-triage="$ADAPTER_DIR" \
  --max-lora-rank "$LORA_RANK"
```

### Models Endpoint

```json
{
  "object": "list",
  "data": [
    {
      "id": "unsloth/LFM2-350M",
      "object": "model",
      "owned_by": "vllm",
      "root": "unsloth/LFM2-350M",
      "parent": null,
      "max_model_len": 32768
    },
    {
      "id": "lfm2-security-triage",
      "object": "model",
      "owned_by": "vllm",
      "root": "/mnt/c/Users/dargy/.unsloth/studio/outputs/unsloth_LFM2-350M_1779162226",
      "parent": "unsloth/LFM2-350M",
      "max_model_len": null
    }
  ]
}
```

## Successful Smoke Run

Command summary:

```bash
OPENAI_COMPATIBLE_BASE_URL=http://192.168.8.141:8080/v1 \
OPENAI_COMPATIBLE_API_KEY=local \
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-smoke.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-smoke.md
```

| Metric | Value |
| --- | ---: |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `invalid_output_count` | `0` |
| `label_accuracy` | `0.2` |
| `severity_accuracy` | `0.6` |
| `is_suspicious_accuracy` | `0.8` |
| `evidence_partial_match` | `0.6` |
| `average_latency_ms` | `1204.060858` |

Interpretation:

- vLLM `structured_outputs` is the first observed runtime/mode that satisfies the output contract on `data/splits/smoke-output-contract.jsonl`.
- The contract gate is separate from semantic quality. Label accuracy remains low on the 5-sample smoke set, so the next work should be mini semantic evaluation and error analysis, not fixed-split comparison yet.
- The response metadata reports `requested_model=lfm2-security-triage` and `response_model=lfm2-security-triage`, so the successful vLLM run does not show the alias drift seen on the current endpoint.

## Phase 1 Decision

For the vLLM path, Phase 1 is complete enough to proceed: the backend, version, base model, LoRA adapter, served alias, response model, request mode, and smoke report are recorded.

The older current endpoint remains useful only as a preserved baseline unless its exact backend and launch settings are later needed. The next active phase is Phase 5 mini semantic evaluation because vLLM `structured_outputs` has already passed the Phase 4 output-contract gate.

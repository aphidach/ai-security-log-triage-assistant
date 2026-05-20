# Structured Output Backend Inventory

Phase 1 inventory report for structured-output runtime work.

## Status

In progress.

This report has enough current-endpoint metadata from Phase 0 to establish the baseline. vLLM fields are pending command output from the WSL/Windows machine that has the Unsloth Studio adapter directory.

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
| Backend version | Pending `vllm --version` |
| Base URL | Pending, expected `http://127.0.0.1:8000/v1` or LAN equivalent |
| Adapter path | `/mnt/c/Users/dargy/.unsloth/studio/outputs/unsloth_LFM2-350M_1779162226` |
| Adapter type | Likely LoRA adapter, pending `adapter_config.json` confirmation |
| Base model | Pending `adapter_config.json.base_model_name_or_path`; expected LFM2-350M family |
| Served alias | `lfm2-security-triage` |
| Launch command | Pending |
| `/v1/models` output | Pending |
| Primary structured mode to test | `structured_outputs` |
| Fallback mode to compare | `json_schema` |

## Command Output To Paste Here

### Adapter Config

```json
TODO: paste jq output from adapter_config.json
```

### vLLM Version

```text
TODO: paste vllm --version and python import output
```

### GPU

```text
TODO: paste nvidia-smi query output
```

### Launch Command

```bash
TODO: paste exact vLLM serve command
```

### Models Endpoint

```json
TODO: paste curl http://127.0.0.1:8000/v1/models output
```

## Phase 1 Decision

Pending.

Phase 1 can move to Phase 2 when exact backend version, launch command, served model alias, and `/v1/models` output are recorded.

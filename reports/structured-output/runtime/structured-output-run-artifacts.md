# Structured Output Run Artifacts

Phase 0 evidence register for output-contract experiments.

## Frozen Splits

| Split | SHA-256 | Use |
| --- | --- | --- |
| `data/splits/test.jsonl` | `b838f07b902890a8dc9159cd1d2a413e9d7c7ae4eeff5754d9c947a35e4cdb3b` | Fixed holdout; do not use during prompt/runtime tuning |
| `data/splits/smoke-output-contract.jsonl` | `631f013874b89402f59fbe6b9c724db5ef87c3a533a97bfefce1aea5efa6d589` | Five-sample output-contract gate |

## Preserved Smoke Artifact

| Field | Value |
| --- | --- |
| Canonical JSON | `reports/structured-output/smoke/openai-compatible-unsloth-studio-json-schema-smoke.json` |
| Canonical Markdown | `reports/structured-output/smoke/openai-compatible-unsloth-studio-json-schema-smoke.md` |
| Source artifact | `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json` / `.md` |
| Adapter | `openai-compatible` |
| Runtime | `unsloth-studio` |
| Runtime note | inferred from `response_model=C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` in sample metadata |
| Mode | `json-schema` |
| Request mode | `json_schema_strict` |
| Requested model | `lfm2-security-triage` |
| Response model | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` |
| Split | `data/splits/smoke-output-contract.jsonl` |
| Samples | `5` |
| JSON parse success | `0.2` |
| Schema success | `0.2` |
| Invalid outputs | `4` |
| JSON SHA-256 | `f9fd8e2e69027745ce8a2373eae73edfd14411e455d0004828adfe3c9e39808d` |
| Markdown SHA-256 | `51e22e4687092fd64dbaeab38c67329bc7aa4ea0c68399adebde16fcf74d94ab` |

Raw model outputs are preserved in `reports/structured-output/smoke/openai-compatible-unsloth-studio-json-schema-smoke.json` under `samples[].raw_prediction`. Per-sample runtime metadata is preserved under `samples[].adapter_metadata`.

## Sample Evidence Summary

| Sample | Expected | Predicted | JSON parse | Schema | Raw output evidence |
| --- | --- | --- | --- | --- | --- |
| `sample-000035` | `normal` | `<invalid>` | `false` | `false` | Markdown-fenced JSON predicts `port_scan_or_recon` |
| `sample-000137` | `failed_login_bruteforce` | `failed_login_bruteforce` | `true` | `true` | Valid JSON, but severity/evidence still fail expected checks |
| `sample-000248` | `sql_injection_attempt` | `<invalid>` | `false` | `false` | Markdown-fenced JSON invents label `ssh_attempt_failed` |
| `sample-000331` | `directory_traversal_attempt` | `<invalid>` | `false` | `false` | Markdown-fenced JSON predicts `failed_login_bruteforce` |
| `sample-000474` | `port_scan_or_recon` | `<invalid>` | `false` | `false` | Markdown-fenced JSON invents label `ssh_bruteforce_attempt` |

## Next Artifact Names

Future smoke runs must use:

```text
reports/{adapter}-{runtime}-{mode}-smoke.json
reports/{adapter}-{runtime}-{mode}-smoke.md
```

Do not write new smoke experiments to generic paths such as `reports/openai-compatible-eval.json`.

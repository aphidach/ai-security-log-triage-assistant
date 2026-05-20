# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/splits/smoke-output-contract.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `5`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.2` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `severity_accuracy` | `0.6` |
| `is_suspicious_accuracy` | `0.8` |
| `evidence_partial_match` | `0.6` |
| `average_latency_ms` | `1204.060858` |
| `invalid_output_count` | `0` |

## Failure Summary

- Failure cases: `5`
- Invalid outputs: `0`

## Failure Cases

- `sample-000035` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000137` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `sample-000248` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `sample-000331` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `sample-000474` expected `port_scan_or_recon`, predicted `sql_injection_attempt`

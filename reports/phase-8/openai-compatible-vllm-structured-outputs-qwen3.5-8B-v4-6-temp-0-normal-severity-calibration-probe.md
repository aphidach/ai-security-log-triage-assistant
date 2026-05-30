# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/splits/v4-6-normal-severity-calibration-probe.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `25`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.84` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `severity_accuracy` | `0.8` |
| `is_suspicious_accuracy` | `0.84` |
| `evidence_partial_match` | `1.0` |
| `average_latency_ms` | `6040.52215` |
| `invalid_output_count` | `0` |

## Failure Summary

- Failure cases: `8`
- Invalid outputs: `0`

## Failure Cases

- `v4-6-qwen35-cal-000121` expected `normal`, predicted `failed_login_bruteforce`
- `v4-6-qwen35-cal-000122` expected `normal`, predicted `failed_login_bruteforce`
- `v4-6-qwen35-cal-000123` expected `normal`, predicted `failed_login_bruteforce`
- `v4-6-qwen35-cal-000124` expected `normal`, predicted `failed_login_bruteforce`
- `v4-6-qwen35-cal-000136` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v4-6-qwen35-cal-000137` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v4-6-qwen35-cal-000138` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v4-6-qwen35-cal-000139` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`

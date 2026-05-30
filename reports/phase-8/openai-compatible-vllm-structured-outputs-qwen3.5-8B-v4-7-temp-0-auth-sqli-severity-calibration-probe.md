# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `30`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.366667` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `severity_accuracy` | `0.6` |
| `is_suspicious_accuracy` | `0.666667` |
| `evidence_partial_match` | `1.0` |
| `average_latency_ms` | `6592.079815` |
| `invalid_output_count` | `0` |

## Failure Summary

- Failure cases: `27`
- Invalid outputs: `0`

## Failure Cases

- `v4-7-qwen35-cal-000121` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000122` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000123` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000124` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000125` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000126` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000127` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000128` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000129` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000130` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000131` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000132` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000133` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000134` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000135` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000136` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000137` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000138` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000139` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000140` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`

# Triage Adapter Evaluation Report

- Adapter: `heuristic`
- Split: `data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `30`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.666667` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `severity_accuracy` | `0.666667` |
| `is_suspicious_accuracy` | `0.666667` |
| `evidence_partial_match` | `1.0` |
| `average_latency_ms` | `0.058292` |
| `invalid_output_count` | `0` |

## Failure Summary

- Failure cases: `10`
- Invalid outputs: `0`

## Failure Cases

- `v4-7-qwen35-cal-000122` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000123` expected `normal`, predicted `failed_login_bruteforce`
- `v4-7-qwen35-cal-000137` expected `failed_login_bruteforce`, predicted `normal`
- `v4-7-qwen35-cal-000138` expected `failed_login_bruteforce`, predicted `normal`
- `v4-7-qwen35-cal-000139` expected `failed_login_bruteforce`, predicted `normal`
- `v4-7-qwen35-cal-000140` expected `failed_login_bruteforce`, predicted `normal`
- `v4-7-qwen35-cal-000141` expected `failed_login_bruteforce`, predicted `normal`
- `v4-7-qwen35-cal-000144` expected `sql_injection_attempt`, predicted `normal`
- `v4-7-qwen35-cal-000145` expected `sql_injection_attempt`, predicted `normal`
- `v4-7-qwen35-cal-000148` expected `port_scan_or_recon`, predicted `normal`

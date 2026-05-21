# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/splits/mini-semantic-eval.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `25`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.36` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `severity_accuracy` | `0.68` |
| `is_suspicious_accuracy` | `0.8` |
| `evidence_partial_match` | `0.6` |
| `average_latency_ms` | `586.249022` |
| `invalid_output_count` | `0` |

## Failure Summary

- Failure cases: `23`
- Invalid outputs: `0`

## Failure Cases

- `sample-000063` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000329` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `sample-000158` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `sample-000056` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000023` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000423` expected `port_scan_or_recon`, predicted `failed_login_bruteforce`
- `sample-000382` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `sample-000014` expected `normal`, predicted `sql_injection_attempt`
- `sample-000437` expected `port_scan_or_recon`, predicted `port_scan_or_recon`
- `sample-000495` expected `port_scan_or_recon`, predicted `failed_login_bruteforce`
- `sample-000385` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `sample-000458` expected `port_scan_or_recon`, predicted `port_scan_or_recon`
- `sample-000485` expected `port_scan_or_recon`, predicted `port_scan_or_recon`
- `sample-000338` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `sample-000003` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000204` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `sample-000163` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `sample-000202` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `sample-000298` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `sample-000155` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`

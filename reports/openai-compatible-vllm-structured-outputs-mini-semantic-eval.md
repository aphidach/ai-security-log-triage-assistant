# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/splits/mini-semantic-eval.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `25`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.24` |
| `json_parse_success_rate` | `0.88` |
| `schema_success_rate` | `0.88` |
| `severity_accuracy` | `0.68` |
| `is_suspicious_accuracy` | `0.68` |
| `evidence_partial_match` | `0.8` |
| `average_latency_ms` | `8337.805605` |
| `invalid_output_count` | `3` |

## Failure Summary

- Failure cases: `20`
- Invalid outputs: `3`

## Failure Cases

- `sample-000063` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000329` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `sample-000056` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000023` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000423` expected `port_scan_or_recon`, predicted `failed_login_bruteforce`
- `sample-000382` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `sample-000014` expected `normal`, predicted `sql_injection_attempt`
- `sample-000437` expected `port_scan_or_recon`, predicted `<invalid>`
- `sample-000495` expected `port_scan_or_recon`, predicted `failed_login_bruteforce`
- `sample-000385` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `sample-000458` expected `port_scan_or_recon`, predicted `<invalid>`
- `sample-000485` expected `port_scan_or_recon`, predicted `<invalid>`
- `sample-000338` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `sample-000003` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000204` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `sample-000169` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `sample-000202` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `sample-000298` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `sample-000220` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `sample-000293` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`

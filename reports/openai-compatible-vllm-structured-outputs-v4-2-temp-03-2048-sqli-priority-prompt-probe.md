# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/generated/v3-hard-contrast-security-triage.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `50`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.62` |
| `json_parse_success_rate` | `0.98` |
| `schema_success_rate` | `0.98` |
| `severity_accuracy` | `0.48` |
| `is_suspicious_accuracy` | `0.86` |
| `evidence_partial_match` | `0.92` |
| `average_latency_ms` | `896.53257` |
| `invalid_output_count` | `1` |

## Failure Summary

- Failure cases: `30`
- Invalid outputs: `1`

## Failure Cases

- `v3-hard-000001` expected `normal`, predicted `failed_login_bruteforce`
- `v3-hard-000002` expected `normal`, predicted `failed_login_bruteforce`
- `v3-hard-000003` expected `normal`, predicted `failed_login_bruteforce`
- `v3-hard-000010` expected `normal`, predicted `<invalid>`
- `v3-hard-000012` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000013` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000015` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000016` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000018` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000020` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000021` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `v3-hard-000023` expected `sql_injection_attempt`, predicted `port_scan_or_recon`
- `v3-hard-000024` expected `sql_injection_attempt`, predicted `port_scan_or_recon`
- `v3-hard-000025` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000026` expected `sql_injection_attempt`, predicted `port_scan_or_recon`
- `v3-hard-000027` expected `sql_injection_attempt`, predicted `port_scan_or_recon`
- `v3-hard-000030` expected `sql_injection_attempt`, predicted `sql_injection_attempt`
- `v3-hard-000031` expected `directory_traversal_attempt`, predicted `port_scan_or_recon`
- `v3-hard-000032` expected `directory_traversal_attempt`, predicted `normal`
- `v3-hard-000033` expected `directory_traversal_attempt`, predicted `port_scan_or_recon`

# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/generated/v3-hard-contrast-security-triage.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `50`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.84` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `severity_accuracy` | `0.82` |
| `is_suspicious_accuracy` | `0.94` |
| `evidence_partial_match` | `0.96` |
| `average_latency_ms` | `460.607813` |
| `invalid_output_count` | `0` |

## Failure Summary

- Failure cases: `16`
- Invalid outputs: `0`

## Failure Cases

- `v3-hard-000001` expected `normal`, predicted `failed_login_bruteforce`
- `v3-hard-000003` expected `normal`, predicted `failed_login_bruteforce`
- `v3-hard-000012` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000013` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000014` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000018` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000021` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000023` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000024` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000025` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000026` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000029` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000033` expected `directory_traversal_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000035` expected `directory_traversal_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000042` expected `port_scan_or_recon`, predicted `port_scan_or_recon`
- `v3-hard-000043` expected `port_scan_or_recon`, predicted `port_scan_or_recon`

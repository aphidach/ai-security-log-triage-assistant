# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/generated/v3-hard-contrast-security-triage.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `50`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.56` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `severity_accuracy` | `0.78` |
| `is_suspicious_accuracy` | `0.9` |
| `evidence_partial_match` | `0.92` |
| `average_latency_ms` | `487.630723` |
| `invalid_output_count` | `0` |

## Failure Summary

- Failure cases: `26`
- Invalid outputs: `0`

## Failure Cases

- `v3-hard-000001` expected `normal`, predicted `failed_login_bruteforce`
- `v3-hard-000003` expected `normal`, predicted `failed_login_bruteforce`
- `v3-hard-000015` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000016` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000018` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000021` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `v3-hard-000023` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `v3-hard-000024` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000025` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000026` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000027` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000028` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000029` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `v3-hard-000030` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000034` expected `directory_traversal_attempt`, predicted `sql_injection_attempt`
- `v3-hard-000037` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `v3-hard-000039` expected `directory_traversal_attempt`, predicted `directory_traversal_attempt`
- `v3-hard-000040` expected `directory_traversal_attempt`, predicted `failed_login_bruteforce`
- `v3-hard-000041` expected `port_scan_or_recon`, predicted `failed_login_bruteforce`
- `v3-hard-000042` expected `port_scan_or_recon`, predicted `failed_login_bruteforce`

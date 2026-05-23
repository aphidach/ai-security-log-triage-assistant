# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/generated/v3-hard-contrast-security-triage.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `50`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.48` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `severity_accuracy` | `0.36` |
| `is_suspicious_accuracy` | `0.58` |
| `evidence_partial_match` | `0.86` |
| `average_latency_ms` | `5569.326359` |
| `invalid_output_count` | `0` |

## Failure Summary

- Failure cases: `34`
- Invalid outputs: `0`

## Failure Cases

- `v3-hard-000001` expected `normal`, predicted `failed_login_bruteforce`
- `v3-hard-000002` expected `normal`, predicted `failed_login_bruteforce`
- `v3-hard-000004` expected `normal`, predicted `normal`
- `v3-hard-000009` expected `normal`, predicted `normal`
- `v3-hard-000013` expected `failed_login_bruteforce`, predicted `normal`
- `v3-hard-000015` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000016` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000018` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `v3-hard-000021` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000023` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000024` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000025` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000026` expected `sql_injection_attempt`, predicted `failed_login_bruteforce`
- `v3-hard-000027` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000028` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000030` expected `sql_injection_attempt`, predicted `normal`
- `v3-hard-000031` expected `directory_traversal_attempt`, predicted `normal`
- `v3-hard-000032` expected `directory_traversal_attempt`, predicted `normal`
- `v3-hard-000033` expected `directory_traversal_attempt`, predicted `normal`
- `v3-hard-000034` expected `directory_traversal_attempt`, predicted `normal`

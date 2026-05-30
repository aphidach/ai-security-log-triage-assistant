# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/splits/test.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `75`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.84` |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `severity_accuracy` | `0.76` |
| `is_suspicious_accuracy` | `0.933333` |
| `evidence_partial_match` | `0.973333` |
| `average_latency_ms` | `445.131397` |
| `invalid_output_count` | `0` |

## Failure Summary

- Failure cases: `26`
- Invalid outputs: `0`

## Failure Cases

- `sample-000474` expected `port_scan_or_recon`, predicted `port_scan_or_recon`
- `sample-000331` expected `directory_traversal_attempt`, predicted `directory_traversal_attempt`
- `sample-000137` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `sample-000248` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `sample-000013` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000240` expected `sql_injection_attempt`, predicted `sql_injection_attempt`
- `sample-000136` expected `failed_login_bruteforce`, predicted `normal`
- `sample-000078` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000218` expected `sql_injection_attempt`, predicted `port_scan_or_recon`
- `sample-000444` expected `port_scan_or_recon`, predicted `port_scan_or_recon`
- `sample-000119` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `sample-000053` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000462` expected `port_scan_or_recon`, predicted `port_scan_or_recon`
- `sample-000450` expected `port_scan_or_recon`, predicted `port_scan_or_recon`
- `sample-000116` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`
- `sample-000480` expected `port_scan_or_recon`, predicted `port_scan_or_recon`
- `sample-000346` expected `directory_traversal_attempt`, predicted `sql_injection_attempt`
- `sample-000028` expected `normal`, predicted `failed_login_bruteforce`
- `sample-000253` expected `sql_injection_attempt`, predicted `directory_traversal_attempt`
- `sample-000177` expected `failed_login_bruteforce`, predicted `failed_login_bruteforce`

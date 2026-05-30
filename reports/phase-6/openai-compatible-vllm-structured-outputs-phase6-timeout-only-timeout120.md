# Triage Adapter Evaluation Report

- Adapter: `openai-compatible`
- Split: `data/splits/phase6-timeout-only.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `3`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.0` |
| `json_parse_success_rate` | `0.0` |
| `schema_success_rate` | `0.0` |
| `severity_accuracy` | `0.0` |
| `is_suspicious_accuracy` | `0.0` |
| `evidence_partial_match` | `0.0` |
| `average_latency_ms` | `5320.462083` |
| `invalid_output_count` | `3` |

## Failure Summary

- Failure cases: `3`
- Invalid outputs: `3`

## Failure Cases

- `sample-000437` expected `port_scan_or_recon`, predicted `<invalid>`
- `sample-000458` expected `port_scan_or_recon`, predicted `<invalid>`
- `sample-000485` expected `port_scan_or_recon`, predicted `<invalid>`

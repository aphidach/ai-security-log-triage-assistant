# Triage Adapter Evaluation Report

- Adapter: `openai-finetune`
- Split: `data/raw/test.jsonl`
- Schema: `data/schemas/triage-output.schema.json`
- Samples: `5`

## Metrics

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.0` |
| `json_parse_success_rate` | `0.0` |
| `schema_success_rate` | `0.0` |
| `severity_accuracy` | `0.0` |
| `evidence_partial_match` | `0.0` |
| `average_latency_ms` | `6449.376058` |
| `invalid_output_count` | `5` |

## Failure Summary

- Failure cases: `5`
- Invalid outputs: `5`

## Failure Cases

- `sample-000474` expected `port_scan_or_recon`, predicted `<invalid>`
- `sample-000335` expected `directory_traversal_attempt`, predicted `<invalid>`
- `sample-000331` expected `directory_traversal_attempt`, predicted `<invalid>`
- `sample-000137` expected `failed_login_bruteforce`, predicted `<invalid>`
- `sample-000388` expected `directory_traversal_attempt`, predicted `<invalid>`

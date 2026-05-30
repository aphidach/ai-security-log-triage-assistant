# Phase 8 V4.8 Qwen3.5 Auth/SQLi Diagnostic Audit

- Created: `2026-05-23`
- Source probe: `data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl`
- Fixed split used: `false`
- Training artifacts created: `false`
- Decision: `prepare_v4_8_diagnostic_first`; fixed split remains closed.

## Comparator Status

- v4.6 on v4.7 probe: `completed` with alias `qwen3.6-8B-triage-v2`.
- Source report: `reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.json`

## Headline Metrics

| Comparator | Label | Severity | Suspicious | Evidence | JSON/schema | Invalid | Avg latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `v4.6 trained adapter` | `0.433333` | `0.4` | `0.533333` | `1.0` | `1.0 / 1.0` | `0` | `5957.112975` |
| `v4.7 trained adapter` | `0.366667` | `0.6` | `0.666667` | `1.0` | `1.0 / 1.0` | `0` | `6592.079815` |
| `heuristic baseline` | `0.666667` | `0.666667` | `0.666667` | `1.0` | `1.0 / 1.0` | `0` | `0.058292` |
| `base Qwen3.5` | `0.366667` | `0.2` | `0.433333` | `0.7` | `0.966667 / 0.966667` | `1` | `8768.592156` |

## Bucket Summary

| Bucket | Samples | v4.6 label/severity | v4.7 label/severity | Heuristic label/severity | Base label/severity | Diagnostic read |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `normal_auth_negative` | `15` | `2/15 / 9/15` | `0/15 / 15/15` | `13/15 / 13/15` | `3/15 / 3/15` | v4.7 treats benign auth/login vocabulary as enough evidence for brute force. |
| `sqli_auth_context` | `5` | `1/5 / 1/5` | `1/5 / 1/5` | `3/5 / 3/5` | `0/5 / 2/5` | v4.7 underweights SQL payload syntax when the route looks like login or account activity. |
| `bruteforce_medium_severity` | `7` | `7/7 / 0/7` | `7/7 / 0/7` | `2/7 / 2/7` | `7/7 / 0/7` | v4.7 keeps brute-force label recall, but escalates all medium examples to high. |
| `port_recon_severity` | `2` | `2/2 / 1/2` | `2/2 / 1/2` | `1/2 / 1/2` | `1/2 / 1/2` | v4.7 mostly keeps the recon label, but one medium/high boundary remains unstable. |
| `directory_traversal_guard` | `1` | `1/1 / 1/1` | `1/1 / 1/1` | `1/1 / 1/1` | `0/1 / 0/1` | v4.7 passes the single traversal guard in this probe. |

## Recommended V4.8 Gate

- `calibration_label_accuracy`: `>= 0.85`
- `normal_auth_label_correct`: `>= 13/15`
- `sqli_auth_context_label_correct`: `>= 4/5`
- `bruteforce_medium_severity_correct`: `>= 5/7`
- `hard_contrast_label_accuracy`: `>= 0.92`
- `json_schema`: `1.0 / 1.0`
- `invalid_output_count`: `0`

## Source Reports

- `v4_6_model`: `reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.json`
- `v4_7_model`: `reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json`
- `heuristic`: `reports/phase-8/heuristic-v4-7-auth-sqli-severity-calibration-probe.json`
- `base_qwen35`: `reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.json`

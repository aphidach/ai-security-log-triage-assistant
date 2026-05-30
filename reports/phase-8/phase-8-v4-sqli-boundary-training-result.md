# Phase 8 V4 SQLi Boundary Training Result

v4 trained from `unsloth/LFM2-350M` with `ml/unsloth/config.v4.yaml`, `1070` train records, `75` validation records, and final `train_loss=0.5690714741470637`.

## Training

| Field | Value |
| --- | ---: |
| Epoch | `4.029906542056075` |
| Runtime seconds | `401.7052` |
| Train samples/sec | `10.754` |
| Train steps/sec | `1.344` |
| Total FLOPs | `4612151839601664.0` |

## Hard-Contrast Gates

Both probes used `data/generated/v3-hard-contrast-security-triage.jsonl`; `data/splits/test.jsonl` was not used.

| Probe | Label accuracy | JSON/schema | Invalid | SQLi | Normal | Traversal | Port/recon | Predicted brute-force | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| temp 0 | `0.84` | `1.0 / 1.0` | `0` | `4/10` | `8/10` | `10/10` | `10/10` | `12/50` | Held |
| temp 0.3 | `0.84` | `1.0 / 1.0` | `0` | `4/10` | `8/10` | `10/10` | `10/10` | `12/50` | Held |

v4 fixed the invalid-output problem on this hard-contrast probe and kept normal/traversal/port/brute-force guards stable, but it did not improve the SQLi boundary over v3.5. Mini semantic eval remains blocked because both probes miss `label_accuracy >= 0.90` and `sql_injection_attempt >= 8/10`.

## Sources

- `ml/unsloth/config.v4.yaml`
- `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json`
- `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-temp-03-2048-hard-contrast-memorization-probe.json`
- User-provided training completion metrics on 2026-05-22

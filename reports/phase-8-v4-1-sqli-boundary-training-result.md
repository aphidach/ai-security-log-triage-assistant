# Phase 8 V4.1 SQLi Boundary Training Result

v4.1 trained from `unsloth/LFM2-350M` with `ml/unsloth/config.v4-1.yaml`, `1220` train records, `75` validation records, and final `train_loss=0.5194365828985074`.

## Training

| Field | Value |
| --- | ---: |
| Epoch | `3.9901639344262296` |
| Runtime seconds | `459.4452` |
| Train samples/sec | `10.622` |
| Train steps/sec | `1.328` |
| Total FLOPs | `5212426293030912.0` |

## Hard-Contrast Gates

Both probes used `data/generated/v3-hard-contrast-security-triage.jsonl`; `data/splits/test.jsonl` was not used.

| Probe | Label accuracy | JSON/schema | Invalid | SQLi | SQLi -> traversal | Normal | Traversal | Port/recon | Predicted brute-force | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| temp 0 | `0.88` | `1.0 / 1.0` | `0` | `6/10` | `2/10` | `8/10` | `10/10` | `10/10` | `12/50` | Held |
| temp 0.3 | `0.90` | `1.0 / 1.0` | `0` | `7/10` | `1/10` | `8/10` | `10/10` | `10/10` | `12/50` | Held |

v4.1 improves the SQLi boundary over v4 (`4/10`) and keeps JSON/schema reliability at `1.0`, but it still misses the required SQLi `>=8/10` gate. Mini semantic eval remains blocked.

Remaining temp 0 failures: `normal_to_failed_login_bruteforce=2`, `sqli_to_traversal=2`, `sqli_to_normal=1`, `sqli_to_port=1`.

Remaining temp 0.3 failures: `normal_to_failed_login_bruteforce=2`, `sqli_to_traversal=1`, `sqli_to_normal=1`, `sqli_to_port=1`.

## Decision

Hold v4.1 before mini semantic eval. Per the v4.1 plan, if SQLi remains `<=6/10` on canonical temp 0, stop data-only repair and plan a capacity/architecture diagnostic before any v4.2.

## Sources

- `ml/unsloth/config.v4-1.yaml`
- `reports/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json`
- `reports/openai-compatible-vllm-structured-outputs-v4-1-temp-03-2048-hard-contrast-memorization-probe.json`
- User-provided training completion metrics on 2026-05-22

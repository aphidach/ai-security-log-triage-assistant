# Phase 6 V3.5 Boundary Training Result

**Summary**

The v3.5 boundary repair fine-tune completed with `train_records=910`, `validation_records=75`, and final `train_loss=0.6392523148461529` from the user-provided training output. The run was later aligned to 2048-token train/runtime context. The best 2048 hard-contrast runtime probe reached `label_accuracy=0.88`, JSON/schema `1.0`, and invalid output `0`, but strict gate status is still held because canonical temp 0 remains at JSON/schema `0.98` and SQLi is still below the `7/10` target.

**Sources**

- User-provided training output in the Codex session on 2026-05-22.
- `ml/unsloth/config.v3-5.yaml` for the v3.5 training config and output directory.
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json` for the canonical post-training hard-contrast probe.
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json` for the temp 0.3 runtime probe.
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-2048-hard-contrast-memorization-probe.json` for the 2048-token canonical temp 0 probe.
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-2048-hard-contrast-memorization-probe.json` for the 2048-token temp 0.3 runtime probe.
- `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md` for the required post-training eval order.

**Status**

`training_complete_probed`

## Training Run

| Field | Value |
| --- | --- |
| Config | `ml/unsloth/config.v3-5.yaml` |
| Output dir | `ml/unsloth/outputs/lfm2-350m-v3-5-2048-boundary-repair-security-triage-lora` |
| Served alias | `lfm2-security-triage-v3-5` |
| Train max sequence length | `2048` |
| Runtime context length | `2048` |
| Train records | `910` |
| Validation records | `75` |
| Final train loss | `0.6392523148461529` |
| Epoch | `4.035164835164835` |
| Runtime | `347.5661s` |
| Train samples/sec | `10.588` |
| Train steps/sec | `1.323` |
| Fixed test split used | `false` |

## Hard-Contrast Results

| Run | Label accuracy | JSON/schema | Invalid | SQLi | Traversal | Port/recon | Normal | Brute predictions | Status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Temp 0 | `0.84` | `0.98 / 0.98` | `1` | `4/10` | `10/10` | `10/10` | `8/10` | `12/50` | Held |
| Temp 0.3 | `0.84` | `0.98 / 0.98` | `1` | `4/10` | `10/10` | `10/10` | `8/10` | `12/50` | Held |
| Temp 0, 2048 | `0.84` | `0.98 / 0.98` | `1` | `4/10` | `10/10` | `10/10` | `8/10` | `12/50` | Held |
| Temp 0.3, 2048 | `0.88` | `1.0 / 1.0` | `0` | `6/10` | `10/10` | `10/10` | `8/10` | `12/50` | Strong runtime probe |

v3.5 repaired the broad prediction collapse: traversal, brute force, and port/recon now hit `10/10`, while brute-force predictions fell from v3.4 temp 0 `19/50` to `12/50`. The 2048 temp 0.3 probe also fixes the quote-heavy invalid output and raises SQLi to `6/10`. The remaining blocker is now narrower: canonical temp 0 does not reproduce the output-contract fix, and SQLi still misses the strict `7/10` target.

## Report Artifacts

```text
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.md
reports/phase-6-v3-5-temp-0-hard-contrast-memorization-probe-infographic.html
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.md
reports/phase-6-v3-5-temp-03-hard-contrast-memorization-probe-infographic.html
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-2048-hard-contrast-memorization-probe.json
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-2048-hard-contrast-memorization-probe.md
reports/phase-6-v3-5-temp-0-2048-hard-contrast-memorization-probe-infographic.html
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-2048-hard-contrast-memorization-probe.json
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-2048-hard-contrast-memorization-probe.md
reports/phase-6-v3-5-temp-03-2048-hard-contrast-memorization-probe-infographic.html
```

## Decision

Do not advance to Phase 7 fixed split yet. The 2048 temp 0.3 probe is strong enough to justify one more decision point: either run mini semantic eval as a runtime-only exploratory check, clearly marked non-canonical, or do a narrow v3.5.1 SQLi repair to reach `>=7/10` under canonical temp 0. This remains a triage-pattern evaluation, not a claim that any single log proves compromise.

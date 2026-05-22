# Phase 6 V3.5 Boundary Training Result

**Summary**

The v3.5 boundary repair fine-tune completed with `train_records=910`, `validation_records=75`, and final `train_loss=0.6392523148461529` from the user-provided training output. Post-training hard-contrast probes improved label accuracy to `0.84`, but v3.5 still does not pass the full exit gate because JSON/schema remains `0.98`, invalid output remains `1`, and SQLi is still only `4/10`.

**Sources**

- User-provided training output in the Codex session on 2026-05-22.
- `ml/unsloth/config.v3-5.yaml` for the v3.5 training config and output directory.
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json` for the canonical post-training hard-contrast probe.
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json` for the temp 0.3 runtime probe.
- `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md` for the required post-training eval order.

**Status**

`training_complete_probed`

## Training Run

| Field | Value |
| --- | --- |
| Config | `ml/unsloth/config.v3-5.yaml` |
| Output dir | `ml/unsloth/outputs/lfm2-350m-v3-5-boundary-repair-security-triage-lora` |
| Served alias | `lfm2-security-triage-v3-5` |
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

v3.5 repaired the broad prediction collapse: traversal, brute force, and port/recon now hit `10/10`, while brute-force predictions fell from v3.4 temp 0 `19/50` to `12/50`. The remaining blocker is narrower: SQLi still reaches only `4/10`, and quote-heavy SQLi `v3-hard-000030` still produces invalid JSON/schema output.

## Report Artifacts

```text
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.md
reports/phase-6-v3-5-temp-0-hard-contrast-memorization-probe-infographic.html
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json
reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.md
reports/phase-6-v3-5-temp-03-hard-contrast-memorization-probe-infographic.html
```

## Decision

Do not advance to mini semantic eval or Phase 7 fixed split yet. The next repair should be a narrow v3.5.1 slice for SQLi-vs-traversal confusion and quote-heavy structured-output validity. This remains a triage-pattern evaluation, not a claim that any single log proves compromise.

# Phase 6 V3.4 Boundary Training Result

**Summary**

The v3.4 boundary repair fine-tune completed with `train_records=710`, `validation_records=75`, and final `train_loss=0.7541013557049964` from the user-provided training output. This is a training artifact record only: v3.4 has not yet passed the hard-contrast canary, and `data/splits/test.jsonl` remains held.

**Sources**

- User-provided training output in the Codex session on 2026-05-22.
- `ml/unsloth/config.v3-4.yaml` for the v3.4 training config and output directory.
- `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md` for the required post-training eval order.

**Status**

`training_complete_unprobed`

## Training Run

| Field | Value |
| --- | --- |
| Config | `ml/unsloth/config.v3-4.yaml` |
| Output dir | `ml/unsloth/outputs/lfm2-350m-v3-4-boundary-repair-security-triage-lora` |
| Planned serve alias | `lfm2-security-triage-v3-4` |
| Train records | `710` |
| Validation records | `75` |
| Final train loss | `0.7541013557049964` |
| Epoch | `4.045070422535211` |
| Runtime | `298.2706s` |
| Train samples/sec | `9.656` |
| Train steps/sec | `1.207` |
| Fixed test split used | `false` |

## Workspace Check

`ml/unsloth/inference.py --preflight-only --config ml/unsloth/config.v3-4.yaml` passed prompt/config wiring, but the adapter directory is not present in this workspace checkout yet. The endpoint health check against `http://192.168.8.141:8080/v1/models` failed from this machine with connection reset, so no v3.4 probe report was generated.

## Next Reports

Run these only after the v3.4 adapter is available to the serving host and exposed as `lfm2-security-triage-v3-4`:

```text
reports/openai-compatible-vllm-structured-outputs-v3-4-hard-contrast-memorization-probe.json
reports/openai-compatible-vllm-structured-outputs-v3-4-hard-contrast-memorization-probe.md
reports/openai-compatible-vllm-structured-outputs-v3-4-temp-03-hard-contrast-memorization-probe.json
reports/openai-compatible-vllm-structured-outputs-v3-4-temp-03-hard-contrast-memorization-probe.md
reports/openai-compatible-vllm-structured-outputs-v3-4-mini-semantic-eval.json
reports/openai-compatible-vllm-structured-outputs-v3-4-mini-semantic-eval.md
```

## Decision

Do not advance to Phase 7 yet. The next gate is the canonical `temperature=0` hard-contrast probe on `data/generated/v3-hard-contrast-security-triage.jsonl`, followed by the runtime probe and mini semantic eval only if the canary improves.

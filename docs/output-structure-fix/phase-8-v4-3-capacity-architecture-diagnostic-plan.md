# Phase 8 V4.3 Capacity Architecture Diagnostic Plan

**Summary**

v4.3 เป็น capacity/architecture diagnostic ต่อจาก v4.2 held decision เป้าหมายคือแยกว่า SQLi boundary failure ที่เหลือเป็นเพดานของ `LFM2-350M`, ผลจาก adapter/training mixture, หรือความกำกวมของ prompt/eval boundary รอบนี้ไม่เพิ่ม dataset, ไม่ train LoRA ใหม่, ไม่เปลี่ยน schema/taxonomy/evaluator/UI API, และไม่ใช้ `data/splits/test.jsonl` เป็น tuning หรือ gate

**Sources**

- v4.1 hard-contrast reports สำหรับ LFM2 control behavior (source: reports/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json, source: reports/openai-compatible-vllm-structured-outputs-v4-1-temp-03-2048-hard-contrast-memorization-probe.json)
- v4.2 prompt diagnostic result สำหรับเหตุผลที่ต้องไป capacity/architecture แทน prompt wording เพิ่ม (source: docs/output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan.md, source: reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json, source: reports/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.json)
- hard-contrast probe split สำหรับ diagnostic input เท่านั้น (source: data/generated/v3-hard-contrast-security-triage.jsonl)
- downloaded Hugging Face model card สำหรับ first candidate `unsloth/Qwen3.5-0.8B` (source: docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md, source: https://huggingface.co/unsloth/Qwen3.5-0.8B)
- runtime prompt/config support ที่คง default prompt เป็น `triage-json-v2.1` (source: scripts/model_adapters/prompt_contract.py, source: scripts/model_adapters/openai_compatible.py)

**Last updated**

2026-05-23

## Status

Planned. First candidate intake selected `unsloth/Qwen3.5-0.8B` and downloaded its model card to `docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md`. No new synthetic data, train split, validation split, LoRA config, or train allowlist entry should be created for v4.3. This diagnostic compares served model behavior under the default prompt profile `triage-json-v2.1` on the existing hard-contrast probe only.

## Why This Exists

v4.1 improved SQLi but still missed the hard-contrast SQLi gate: temp 0 reached `6/10` and temp 0.3 reached `7/10`. v4.2 prompt priority removed SQLi-to-traversal drift, but SQLi stayed `4/10` and other labels regressed. That pattern suggests the next useful question is not "which synthetic SQLi examples should be added?" but "does a stronger model/runtime separate these boundaries with the same schema and prompt?"

The manual fixed split sanity run after v4.2 showed v4.1 can score `0.893333` on `data/splits/test.jsonl` with default prompt v2.1, but that result is historical context only. It is not a Phase 8 gate because the fixed split has already been exposed during earlier comparison work.

## Diagnostic Scope

Use the same five labels and the same output schema:

```text
normal
failed_login_bruteforce
sql_injection_attempt
directory_traversal_attempt
port_scan_or_recon
```

Do not add labels, schema fields, evaluator metrics, frontend API changes, or a new prompt default. Use `OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.1` explicitly in v4.3 command examples so the diagnostic is not confused with v4.2.

## Candidate Lanes

| Lane | Purpose | Requirement | Interpretation |
| --- | --- | --- | --- |
| LFM2 control | Preserve the v4.1 reference behavior | Use existing v4.1 hard-contrast reports, or rerun only if serving/runtime changed | If candidate improves while control remains held, suspect LFM2-350M capacity or adapter ceiling |
| Larger instruction model, no fine-tune | Test semantic boundary capacity with the same prompt/schema | Serve one stronger OpenAI-compatible model alias and run hard-contrast only | If it passes, run a small pilot fine-tune or adapter strategy next |
| Alternative architecture pilot | Test whether another small/medium architecture separates SQLi/traversal/recon better | Use the same runtime adapter and report naming, no fixed split | If it also fails, inspect label definitions, hard-contrast ambiguity, or evaluator assumptions |

## Candidate Intake

`unsloth/Qwen3.5-0.8B` is the first v4.3 candidate. The local source snapshot is:

```text
docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md
```

Why it fits this diagnostic:

- It is still a sub-1B model, so it tests whether a newer small architecture can beat the current `LFM2-350M` adapter without jumping directly to a 4B/7B model.
- The model card describes it as intended for prototyping, task-specific fine-tuning, and research/development purposes, which matches a diagnostic POC rather than production detection.
- Hugging Face metadata reports `qwen3_5`, `apache-2.0`, `image-text-to-text`, base model `Qwen/Qwen3.5-0.8B`, and about `873M` safetensors parameters, so the run should be documented as a Qwen3.5 capacity/architecture candidate, not as an LFM2 repair run.

Caveat: the model card identifies the model as a causal language model with a vision encoder and an `image-text-to-text` pipeline. The v4.3 probe must use text-only security log prompts through the same OpenAI-compatible adapter and structured-output schema before treating it as useful for this project.

Suggested local naming:

```text
CANDIDATE_MODEL_ALIAS=qwen3-5-0-8b-security-triage
CANDIDATE_MODEL_SLUG=qwen3-5-0-8b
```

## Commands

Preflight:

```bash
rtk .venv/bin/python -m unittest tests/test_openai_adapter_config.py tests/test_v4_2_sqli_priority_prompt_workflow.py tests/test_v4_3_capacity_diagnostic_plan.py
rtk .venv/bin/python -m py_compile scripts/model_adapters/prompt_contract.py scripts/model_adapters/openai_compatible.py
```

Candidate hard-contrast temp 0:

```bash
OPENAI_COMPATIBLE_MODEL="$CANDIDATE_MODEL_ALIAS" \
OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.1 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TEMPERATURE=0 \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-0-2048-capacity-diagnostic-hard-contrast.json" \
  --comparison-out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-0-2048-capacity-diagnostic-hard-contrast.md"
```

Candidate hard-contrast temp 0.3:

```bash
OPENAI_COMPATIBLE_MODEL="$CANDIDATE_MODEL_ALIAS" \
OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.1 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TEMPERATURE=0.3 \
OPENAI_COMPATIBLE_TOP_P=0.9 \
OPENAI_COMPATIBLE_EXTRA_BODY='{"min_p":0.15,"repetition_penalty":1.05}' \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-03-2048-capacity-diagnostic-hard-contrast.json" \
  --comparison-out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-03-2048-capacity-diagnostic-hard-contrast.md"
```

Do not run `data/splits/test.jsonl` in v4.3. If a final comparison is needed later, freeze a genuinely new holdout first.

## Gates

For a candidate to justify a follow-up pilot, both hard-contrast probes should hit JSON parse `1.0`, schema `1.0`, invalid outputs `0`, label accuracy `>=0.90`, SQLi `>=8/10`, SQLi predicted as traversal `<=2/10`, normal `>=8/10`, traversal `>=9/10`, port/recon `>=9/10`, and predicted brute-force `<=14/50`.

If a stronger candidate passes while v4.1 remains held, plan a capacity pilot. If every candidate fails similarly, stop model swapping and audit the hard-contrast examples, label boundary text, and evaluator expectations before training again.

## Non-Goals

- No new synthetic SQLi/traversal/bruteforce records by default
- No `ml/unsloth/config.v4-3.yaml`
- No v4.3 train or validation split
- No prompt v2.2 promotion
- No fixed test run as a Phase 8 decision gate

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-22 | Codex | Added v4.3 capacity/architecture diagnostic plan after v4.2 held | `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md`, `tests/test_v4_3_capacity_diagnostic_plan.py` | Planned |
| 2026-05-23 | Codex | Added `unsloth/Qwen3.5-0.8B` as the first v4.3 candidate intake and downloaded the model card | `docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md` | Candidate selected; probe not run |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-22 | Make v4.3 a capacity/architecture diagnostic | v4.1 data repair and v4.2 prompt priority both failed hard-contrast SQLi gates in different ways | Next evidence should compare model/runtime capacity with the same prompt/schema, not add more synthetic data by default |
| 2026-05-22 | Keep default prompt at `triage-json-v2.1` | v2.2 damaged broad label boundaries and temp 0.3 output contract | v4.3 command examples set v2.1 explicitly and leave v2.2 as historical diagnostic only |
| 2026-05-22 | Keep fixed split out of Phase 8 gates | The user-run fixed split sanity result is useful context but historically exposed | v4.3 uses hard-contrast probes or a future newly frozen holdout, not `data/splits/test.jsonl` |
| 2026-05-23 | Use `unsloth/Qwen3.5-0.8B` as the first candidate intake | The user selected it as the next small-model architecture to test, and the Hugging Face card positions it for prototyping and task-specific fine-tuning | v4.3 can proceed to serving and hard-contrast probes under prompt `triage-json-v2.1`; no v4.3 training artifacts are created |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan]]
- [[openai-adapter-runtime-config]]
- [[fine-tuning-notes]]
- [[structured-output-reliability-research-2026]]
- [[model-candidates/unsloth-qwen3.5-0.8b/model-card]]

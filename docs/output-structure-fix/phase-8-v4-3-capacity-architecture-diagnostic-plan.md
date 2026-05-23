# Phase 8 V4.3 Capacity Architecture Diagnostic Plan

**Summary**

v4.3 เป็น capacity/architecture diagnostic ต่อจาก v4.2 held decision รอบนี้ serve `unsloth/Qwen3.5-0.8B` เป็น base model ตรงจาก Hub ไม่ใช่ model ที่ fine-tune/LoRA แล้ว และทดสอบครบ 3 แบบ: smoke, hard-contrast temp 0, และ hard-contrast temp 0.3 ผลคือ output contract ผ่านทุก run แต่ semantic boundary ยังไม่ผ่าน gate โดย hard-contrast ได้ label accuracy `0.50` และ `0.48`, SQLi เหลือ `3/10` และ `2/10` ตามลำดับ ดังนั้น base candidate นี้ถูก hold และยังไม่ควรเปิด fixed split หรือถือเป็นเหตุผลให้สร้าง v4.3 training artifact

**Sources**

- v4.1 hard-contrast reports สำหรับ LFM2 control behavior (source: reports/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json, source: reports/openai-compatible-vllm-structured-outputs-v4-1-temp-03-2048-hard-contrast-memorization-probe.json)
- v4.2 prompt diagnostic result สำหรับเหตุผลที่ต้องไป capacity/architecture แทน prompt wording เพิ่ม (source: docs/output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan.md, source: reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json, source: reports/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.json)
- hard-contrast probe split สำหรับ diagnostic input เท่านั้น (source: data/generated/v3-hard-contrast-security-triage.jsonl)
- downloaded Hugging Face model card สำหรับ first candidate `unsloth/Qwen3.5-0.8B` (source: docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md, source: https://huggingface.co/unsloth/Qwen3.5-0.8B)
- runtime prompt/config support ที่คง default prompt เป็น `triage-json-v2.1` (source: scripts/model_adapters/prompt_contract.py, source: scripts/model_adapters/openai_compatible.py)
- v4.3 Qwen3.5 base-model smoke report (source: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-smoke.json, source: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-smoke.md)
- v4.3 Qwen3.5 base-model hard-contrast temp 0 report (source: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json, source: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.md)
- v4.3 Qwen3.5 base-model hard-contrast temp 0.3 report (source: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json, source: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.md)

**Last updated**

2026-05-23

## Status

Probed; held. First candidate `unsloth/Qwen3.5-0.8B` was served as the Hub base model, with no project fine-tune and no LoRA adapter, through the OpenAI-compatible vLLM structured-output path on port `8080`. It was tested with smoke plus both hard-contrast probes. No new synthetic data, train split, validation split, LoRA config, or train allowlist entry should be created for v4.3. This result compares served base-model behavior under default prompt profile `triage-json-v2.1` on the existing smoke and hard-contrast probe only.

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
- In v4.3 this is served as the base model as-is. It is not the output of `ml/unsloth/train_lora.py`, not a Qwen LoRA adapter, and not a project-trained checkpoint.

Caveat: the model card identifies the model as a causal language model with a vision encoder and an `image-text-to-text` pipeline. The v4.3 probe must use text-only security log prompts through the same OpenAI-compatible adapter and structured-output schema before treating it as useful for this project.

Suggested local naming:

```text
CANDIDATE_MODEL_ALIAS=qwen3-5-0-8b-security-triage
CANDIDATE_MODEL_SLUG=qwen3-5-0-8b
```

## Qwen3.5-0.8B Result Summary

The user-run v4.3 base-model probe now has 3 completed report pairs under `reports/`. All three runs preserve JSON/schema reliability, so the immediate blocker is not output parsing. The blocker is semantic triage quality on hard-contrast labels.

| Run | Split | Runtime setting | Label accuracy | JSON/schema | Invalid | Severity | Suspicious | Evidence | Avg latency |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Smoke | `data/splits/smoke-output-contract.jsonl` | temp `0` | `0.60` | `1.0 / 1.0` | `0` | `0.40` | `0.60` | `1.00` | `6422.59 ms` |
| Hard-contrast | `data/generated/v3-hard-contrast-security-triage.jsonl` | temp `0` | `0.50` | `1.0 / 1.0` | `0` | `0.42` | `0.54` | `0.82` | `5845.25 ms` |
| Hard-contrast | `data/generated/v3-hard-contrast-security-triage.jsonl` | temp `0.3`, top_p `0.9`, min_p `0.15`, repetition penalty `1.05` | `0.48` | `1.0 / 1.0` | `0` | `0.36` | `0.58` | `0.86` | `5569.33 ms` |

Hard-contrast label view:

| Slice | Gate | Temp 0 result | Temp 0.3 result | Read |
| --- | ---: | ---: | ---: | --- |
| Overall label accuracy | `>=0.90` | `0.50` | `0.48` | fails both |
| `normal` | `>=8/10` | `8/10` | `8/10` | passes, but suspicious classes collapse into normal |
| `failed_login_bruteforce` | diagnostic | `9/10` | `9/10` | stable |
| `sql_injection_attempt` | `>=8/10` | `3/10` | `2/10` | fails; mostly predicted `normal`, then some `failed_login_bruteforce` |
| `directory_traversal_attempt` | `>=9/10` | `2/10` | `2/10` | fails; `8/10` predicted `normal` in both runs |
| `port_scan_or_recon` | `>=9/10` | `3/10` | `3/10` | fails; `7/10` predicted `normal` in both runs |
| Predicted `failed_login_bruteforce` total | `<=14/50` | `13/50` | `12/50` | passes the overprediction guard |

Prediction distribution confirms the main failure mode:

| Run | `normal` | `failed_login_bruteforce` | `sql_injection_attempt` | `directory_traversal_attempt` | `port_scan_or_recon` |
| --- | ---: | ---: | ---: | ---: | ---: |
| Temp 0 | `29/50` | `13/50` | `3/50` | `2/50` | `3/50` |
| Temp 0.3 | `31/50` | `12/50` | `2/50` | `2/50` | `3/50` |

Interpretation: the untrained project base-model run of Qwen3.5-0.8B handles the structured-output contract, but under the current `triage-json-v2.1` prompt and hard-contrast split it under-detects suspicious security patterns. The failure is not the same as v4.2 SQLi-to-traversal drift; here many SQLi, traversal, and recon cases become `normal`. Temp `0.3` does not rescue the base candidate: evidence match rises slightly, but label accuracy and SQLi recall fall.

Decision: hold this base-model `unsloth/Qwen3.5-0.8B` candidate for v4.3. Do not run `data/splits/test.jsonl`, do not promote it as a replacement for the v4.1/v4 path, and do not treat a future Qwen LoRA smoke train as the v4.3 gate. A Qwen LoRA pilot can still be a separate exploratory training run if explicitly opened later, but the current base-model capacity diagnostic does not justify it as the next gate by itself.

## Command Runbook

Use these commands from the repo root. The v4.3 gate is a base-model serving diagnostic only; the training commands at the end are a separate post-gate pilot path and must not be used to decide the v4.3 hard-contrast gate.

### 1. Local Variables

```bash
export CANDIDATE_REPO="unsloth/Qwen3.5-0.8B"
export CANDIDATE_MODEL_ALIAS="qwen3-5-0-8b-security-triage"
export CANDIDATE_MODEL_SLUG="qwen3-5-0-8b"
export CANDIDATE_BASE_URL="http://localhost:8080/v1"
export CANDIDATE_API_KEY="EMPTY"
export V43_SPLIT="data/generated/v3-hard-contrast-security-triage.jsonl"
export TRIAGE_SCHEMA="data/schemas/triage-output.schema.json"
```

### 2. Repo And Model-Card Preflight

```bash
rtk .venv/bin/python -m unittest tests/test_openai_adapter_config.py tests/test_v4_2_sqli_priority_prompt_workflow.py tests/test_v4_3_capacity_diagnostic_plan.py
rtk .venv/bin/python -m py_compile scripts/model_adapters/prompt_contract.py scripts/model_adapters/openai_compatible.py
rtk hf models info "$CANDIDATE_REPO" --format json
rtk wc -l docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md
rtk rg -n "Qwen3.5-0.8B|license: apache-2.0|pipeline_tag: image-text-to-text" docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md
```

Refresh the local model card only if the Hub card changed:

```bash
rtk hf download "$CANDIDATE_REPO" README.md \
  --local-dir /tmp/qwen3-5-0-8b-card \
  --force-download
rtk cp /tmp/qwen3-5-0-8b-card/README.md docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md
```

### 3. Serve Candidate, Preferred vLLM Text-Only Path

The model card says Qwen3.5 can use vLLM and recommends reducing context length if OOM occurs. This project is text-only, so use `--language-model-only` and a smaller diagnostic context first.

```bash
rtk vllm serve "$CANDIDATE_REPO" \
  --host 0.0.0.0 \
  --port 8080 \
  --served-model-name "$CANDIDATE_MODEL_ALIAS" \
  --tensor-parallel-size 1 \
  --max-model-len 8192 \
  --language-model-only
```

If the machine can safely support the model-card default context, use the official-style long-context shape only as a later throughput/runtime check:

```bash
rtk vllm serve "$CANDIDATE_REPO" \
  --host 0.0.0.0 \
  --port 8080 \
  --served-model-name "$CANDIDATE_MODEL_ALIAS" \
  --tensor-parallel-size 1 \
  --max-model-len 262144 \
  --language-model-only
```

### 4. Alternative Server Smoke With Transformers

Use this only if the vLLM nightly path is unavailable. It is a moderate-load smoke path, not the preferred v4.3 runtime.

```bash
rtk transformers serve \
  --force-model "$CANDIDATE_REPO" \
  --port 8080 \
  --continuous-batching
```

### 5. Endpoint Smoke

```bash
rtk curl -s "$CANDIDATE_BASE_URL/models"
```

```bash
rtk curl -s "$CANDIDATE_BASE_URL/chat/completions" \
  -H "Authorization: Bearer $CANDIDATE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "'"$CANDIDATE_MODEL_ALIAS"'",
    "messages": [
      {"role": "user", "content": "Return exactly: ok"}
    ],
    "max_tokens": 16,
    "temperature": 0
  }'
```

### 6. Output-Contract Smoke

Run the existing smoke split before hard-contrast. This is not the fixed split.

```bash
OPENAI_COMPATIBLE_BASE_URL="$CANDIDATE_BASE_URL" \
OPENAI_COMPATIBLE_API_KEY="$CANDIDATE_API_KEY" \
OPENAI_COMPATIBLE_MODEL="$CANDIDATE_MODEL_ALIAS" \
OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.1 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH="$TRIAGE_SCHEMA" \
OPENAI_COMPATIBLE_MAX_TOKENS=512 \
OPENAI_COMPATIBLE_TIMEOUT_SECONDS=120 \
OPENAI_COMPATIBLE_TEMPERATURE=0 \
rtk .venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-0-smoke.json" \
  --comparison-out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-0-smoke.md"
```

```text
adapter: openai-compatible
split: data/splits/smoke-output-contract.jsonl
samples: 5
label_accuracy: 0.6
json_parse_success_rate: 1.0
schema_success_rate: 1.0
severity_accuracy: 0.4
is_suspicious_accuracy: 0.6
evidence_partial_match: 1.0
average_latency_ms: 6422.592034
invalid_output_count: 0
json_report: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-smoke.json
markdown_report: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-smoke.md

```
### 7. Candidate Hard-Contrast Temp 0

This is the first v4.3 gate run. Keep thinking mode off; `Qwen3.5-0.8B` defaults to non-thinking mode and the model card warns that thinking mode can loop.

```bash
OPENAI_COMPATIBLE_BASE_URL="$CANDIDATE_BASE_URL" \
OPENAI_COMPATIBLE_API_KEY="$CANDIDATE_API_KEY" \
OPENAI_COMPATIBLE_MODEL="$CANDIDATE_MODEL_ALIAS" \
OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.1 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH="$TRIAGE_SCHEMA" \
OPENAI_COMPATIBLE_MAX_TOKENS=512 \
OPENAI_COMPATIBLE_TIMEOUT_SECONDS=120 \
OPENAI_COMPATIBLE_TEMPERATURE=0 \
rtk .venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split "$V43_SPLIT" \
  --out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-0-2048-capacity-diagnostic-hard-contrast.json" \
  --comparison-out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-0-2048-capacity-diagnostic-hard-contrast.md"
```

```text
adapter: openai-compatible
split: data/generated/v3-hard-contrast-security-triage.jsonl
samples: 50
label_accuracy: 0.5
json_parse_success_rate: 1.0
schema_success_rate: 1.0
severity_accuracy: 0.42
is_suspicious_accuracy: 0.54
evidence_partial_match: 0.82
average_latency_ms: 5845.253222
invalid_output_count: 0
json_report: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json
markdown_report: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.md

```
### 8. Candidate Hard-Contrast Temp 0.3

This mirrors the runtime probe style used for v4.1. If the backend rejects `min_p` or `repetition_penalty`, rerun without the unsupported field and record the rejection in the report notes.

```bash
OPENAI_COMPATIBLE_BASE_URL="$CANDIDATE_BASE_URL" \
OPENAI_COMPATIBLE_API_KEY="$CANDIDATE_API_KEY" \
OPENAI_COMPATIBLE_MODEL="$CANDIDATE_MODEL_ALIAS" \
OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.1 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH="$TRIAGE_SCHEMA" \
OPENAI_COMPATIBLE_MAX_TOKENS=512 \
OPENAI_COMPATIBLE_TIMEOUT_SECONDS=120 \
OPENAI_COMPATIBLE_TEMPERATURE=0.3 \
OPENAI_COMPATIBLE_TOP_P=0.9 \
OPENAI_COMPATIBLE_EXTRA_BODY='{"min_p":0.15,"repetition_penalty":1.05}' \
rtk .venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split "$V43_SPLIT" \
  --out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-03-2048-capacity-diagnostic-hard-contrast.json" \
  --comparison-out "reports/openai-compatible-vllm-structured-outputs-v4-3-${CANDIDATE_MODEL_SLUG}-temp-03-2048-capacity-diagnostic-hard-contrast.md"
```

```text
adapter: openai-compatible
split: data/generated/v3-hard-contrast-security-triage.jsonl
samples: 50
label_accuracy: 0.48
json_parse_success_rate: 1.0
schema_success_rate: 1.0
severity_accuracy: 0.36
is_suspicious_accuracy: 0.58
evidence_partial_match: 0.86
average_latency_ms: 5569.326359
invalid_output_count: 0
json_report: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json
markdown_report: reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.md
```
### 9. Metric Extraction

```bash
rtk .venv/bin/python - <<'PY'
import json
from collections import Counter, defaultdict
from pathlib import Path

for path in sorted(Path("reports").glob("openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-*-capacity-diagnostic-hard-contrast.json")):
    report = json.loads(path.read_text())
    metrics = report["metrics"]
    predictions = report.get("predicted_label_distribution", {})
    confusion = defaultdict(Counter)
    for sample in report.get("samples", []):
        confusion[sample.get("expected_label")][sample.get("predicted_label")] += 1
    print(path)
    print("  label_accuracy:", metrics.get("label_accuracy"))
    print("  json/schema:", metrics.get("json_parse_success_rate"), metrics.get("schema_success_rate"))
    print("  invalid_output_count:", metrics.get("invalid_output_count"))
    print("  sql_injection_attempt:", dict(confusion.get("sql_injection_attempt", {})))
    print("  normal:", dict(confusion.get("normal", {})))
    print("  directory_traversal_attempt:", dict(confusion.get("directory_traversal_attempt", {})))
    print("  port_scan_or_recon:", dict(confusion.get("port_scan_or_recon", {})))
    print("  predicted failed_login_bruteforce:", predictions.get("failed_login_bruteforce"))
PY
```

Do not run `data/splits/test.jsonl` in v4.3. If a final comparison is needed later, freeze a genuinely new holdout first.

### 10. Train Pilot Commands, Not A V4.3 Gate

Run this only after the candidate passes the v4.3 hard-contrast gate or after a separate decision opens a Qwen3.5 training pilot. This command intentionally uses the existing v4.1 train/validation splits through the checked-in exploratory pilot config, not a v4.3 train split or `ml/unsloth/config.v4-3.yaml`.

Preflight only:

```bash
rtk .venv/bin/python ml/unsloth/train_lora_vision_qwen.py \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml \
  --preflight-only
```

GPU smoke train:

```bash
rtk .venv/bin/python ml/unsloth/train_lora_vision_qwen.py \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml
```

The checked-in pilot config uses `model.loader: fast_vision_model` to follow the Unsloth Qwen3.5 notebook, keeps `finetune_vision_layers: false` for the text-only security-log task, and leaves the fixed split closed. The dedicated `ml/unsloth/train_lora_vision_qwen.py` runner keeps this vision-collator path separate from the LFM2 `train_lora.py` path. If this smoke train succeeds, document it as a separate pilot result before scaling `max_steps`.

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
| 2026-05-23 | Codex | Expanded v4.3 into a copyable command runbook for preflight, server launch, endpoint smoke, hard-contrast probes, metric extraction, and post-gate train pilot smoke | `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md` | Runbook prepared |
| 2026-05-23 | Codex | Changed v4.3 Qwen3.5 server and adapter commands to local port `8080` | `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md` | Runbook updated |
| 2026-05-23 | User/Codex | Recorded all 3 v4.3 Qwen3.5 probe results and summarized the candidate decision | `reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-smoke.json`, `reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json`, `reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json` | Probed; held |
| 2026-05-23 | Codex | Branched the held Qwen3.5 result into a v4.4 hard-contrast boundary audit | `docs/output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan.md`, `reports/phase-8-v4-4-hard-contrast-boundary-audit.json` | Follow-up audit complete |
| 2026-05-23 | User/Codex | Clarified that v4.3 Qwen3.5 probes used the Hub base model, not a trained Qwen model | `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md` | Clarified |
| 2026-05-23 | Codex | Updated Qwen3.5 train pilot command notes to use the checked-in `FastVisionModel` pilot config | `ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml`, `ml/unsloth/train_lora.py` | Pilot wiring prepared |
| 2026-05-23 | Codex | Split the Qwen3.5 train pilot runbook to the dedicated vision trainer | `ml/unsloth/train_lora_vision_qwen.py`, `ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml` | Pilot runner separated |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-22 | Make v4.3 a capacity/architecture diagnostic | v4.1 data repair and v4.2 prompt priority both failed hard-contrast SQLi gates in different ways | Next evidence should compare model/runtime capacity with the same prompt/schema, not add more synthetic data by default |
| 2026-05-22 | Keep default prompt at `triage-json-v2.1` | v2.2 damaged broad label boundaries and temp 0.3 output contract | v4.3 command examples set v2.1 explicitly and leave v2.2 as historical diagnostic only |
| 2026-05-22 | Keep fixed split out of Phase 8 gates | The user-run fixed split sanity result is useful context but historically exposed | v4.3 uses hard-contrast probes or a future newly frozen holdout, not `data/splits/test.jsonl` |
| 2026-05-23 | Use `unsloth/Qwen3.5-0.8B` as the first base-model candidate intake | The user selected it as the next small-model architecture to test, and the Hugging Face card positions it for prototyping and task-specific fine-tuning | v4.3 can proceed to base-model serving and hard-contrast probes under prompt `triage-json-v2.1`; no v4.3 training artifacts are created |
| 2026-05-23 | Hold the Qwen3.5-0.8B v4.3 base candidate after smoke and hard-contrast probes | The base model preserves JSON/schema reliability but hard-contrast label accuracy is only `0.50` at temp 0 and `0.48` at temp 0.3, with SQLi at `3/10` and `2/10` | Do not open fixed split or promote a future Qwen LoRA pilot as the v4.3 gate; next evidence should be another capacity candidate or a hard-contrast boundary audit |
| 2026-05-23 | Keep checked-in Qwen3.5 LoRA config exploratory | The pilot exists to validate Unsloth `FastVisionModel` training mechanics, not to reverse the held base-model decision | Use existing v4.1 train/validation splits, keep `data/splits/test.jsonl` closed, and do not create `ml/unsloth/config.v4-3.yaml` |
| 2026-05-23 | Keep the exploratory Qwen pilot on a dedicated runner | The Qwen path needs vision-native collation while LFM2 should keep the existing language SFTTrainer path | Run `ml/unsloth/train_lora_vision_qwen.py` for Qwen smoke training and leave `ml/unsloth/train_lora.py` for language configs |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan]]
- [[output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan]]
- [[openai-adapter-runtime-config]]
- [[fine-tuning-notes]]
- [[structured-output-reliability-research-2026]]
- [[model-candidates/unsloth-qwen3.5-0.8b/model-card]]

# V1 LFM2-350M Security Triage

**Summary**

version 1 ของ fine-tuned path นี้พิสูจน์แล้วว่า training, adapter save, local inference และ vLLM base+LoRA serving เดินได้ แต่ยังไม่ผ่านเกณฑ์ model output สำหรับ POC เพราะ API endpoint ยังตอบเป็น prose หรือ prose+JSON แทน JSON object ล้วน และ local inference แม้ parse JSON ได้ในบางเคสก็ยังมี hallucination ใน `reason`

**Sources**

- `ml/unsloth/config.example.yaml` สำหรับ config ของ LFM2-350M + LoRA v1 (source: ml/unsloth/config.example.yaml)
- `ml/unsloth/train_lora.py` สำหรับ training implementation, split guard และ Unsloth-first training path (source: ml/unsloth/train_lora.py)
- `ml/unsloth/inference.py` สำหรับ local adapter inference และ raw output debug flag (source: ml/unsloth/inference.py)
- `ml/unsloth/merge_adapter.py` สำหรับ merge/GGUF export path หลัง train (source: ml/unsloth/merge_adapter.py)
- `reports/openai-finetune-eval.json` สำหรับ smoke evaluation ของ OpenAI-compatible endpoint (source: reports/openai-finetune-eval.json)
- `reports/openai-finetune-eval.md` สำหรับ metric summary ของ smoke evaluation (source: reports/openai-finetune-eval.md)
- `docs/Day6.md` สำหรับสถานะ Day 6 และ decision ว่า smoke/debug eval ยังไม่ใช่ final comparison (source: docs/Day6.md)

**Last updated**

2026-05-18

## Version Metadata

| Field | Value |
| --- | --- |
| Model version | `v1` |
| Model name | `lfm2-350m-security-triage-lora` |
| Base model | `unsloth/LFM2-350M` |
| Model family | `LFM2` |
| Adapter path | `ml/unsloth/outputs/lfm2-350m-security-triage-lora` |
| Merged output path | `ml/unsloth/outputs/lfm2-350m-security-triage-mearged` in manual run; intended default is `ml/unsloth/outputs/lfm2-350m-security-triage-merged` |
| vLLM served LoRA name | `lfm2-security-triage` |
| Prompt version | `triage-json-v1` |
| Training splits | `data/splits/train.jsonl`, `data/splits/validation.jsonl` |
| Smoke API split | `data/raw/test.jsonl` |
| Fixed evaluation split | `data/splits/test.jsonl` not completed yet |
| Status | `trained-smoke-tested-rejected-for-output-contract` |

## Config Snapshot

```yaml
model:
  base_model: unsloth/LFM2-350M
  model_family: LFM2
  max_seq_length: 2048
  load_in_4bit: true
  use_gradient_checkpointing: unsloth
  dtype: bfloat16

data:
  train_path: data/splits/train.jsonl
  validation_path: data/splits/validation.jsonl
  input_field: input
  output_field: output

format:
  prompt_version: triage-json-v1
  training_record_format: chat_messages
  use_tokenizer_chat_template: true
  strict_output_schema: true
  assistant_output_keys:
    - label
    - severity
    - is_suspicious
    - evidence
    - reason
    - recommended_action

lora:
  r: 16
  lora_alpha: 16
  lora_dropout: 0.0
  bias: none
  task_type: CAUSAL_LM
  random_state: 3407
  use_rslora: false
  loftq_config: null
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
    - gate_proj
    - up_proj
    - down_proj

training:
  per_device_train_batch_size: 2
  per_device_eval_batch_size: 2
  gradient_accumulation_steps: 4
  warmup_steps: 5
  max_steps: 90
  learning_rate: 0.0001
  num_train_epochs: 1
  optim: adamw_8bit
  weight_decay: 0.001
  lr_scheduler_type: linear
  logging_steps: 1
  eval_strategy: epoch
  save_strategy: epoch
  seed: 3407
  report_to: none

output:
  output_dir: ml/unsloth/outputs/lfm2-350m-security-triage-lora
  adapter_name: lfm2-350m-security-triage-lora
```

## What Happened

1. Training path was completed enough to run GPU short trial and save a LoRA adapter. The implementation keeps train and validation paths in config and intentionally excludes `data/splits/test.jsonl` from training (source: ml/unsloth/config.example.yaml, ml/unsloth/train_lora.py).
2. Local Unsloth inference can load the base model plus adapter and emit parseable JSON for at least one hand-run SQLi-like log, but the generated `reason` may mention unrelated SQL patterns such as `UNION` when the input only contains `SLEEP(5)`. That means JSON shape can pass while semantic grounding still fails (source: ml/unsloth/inference.py).
3. Merge/export tooling exists, including GGUF export, but merge/GGUF is only a packaging step. It does not fix schema adherence, hallucinated reasons, or taxonomy drift (source: ml/unsloth/merge_adapter.py, docs/Day6.md).
4. vLLM base+LoRA serving reached a usable endpoint with `unsloth/LFM2-350M` as base and `lfm2-security-triage` as LoRA model name. The safer serving path for now is adapter-first, not the merged checkpoint path.
5. API smoke evaluation through the OpenAI-compatible adapter produced a report, but the report is a failure artifact: 5/5 outputs were invalid under strict JSON parsing (source: reports/openai-finetune-eval.json, reports/openai-finetune-eval.md).

## API Smoke Evaluation

| Metric | Value |
| --- | ---: |
| Samples | `5` |
| JSON parse success rate | `0.0` |
| Schema success rate | `0.0` |
| Label accuracy | `0.0` |
| Severity accuracy | `0.0` |
| Evidence partial match | `0.0` |
| Invalid output count | `5` |
| Average latency ms | `6449.376058` |

Important context: this smoke run used `data/raw/test.jsonl` with 5 samples, not the final fixed split `data/splits/test.jsonl` with 75 samples. It is useful for debugging output contract failure, not for final model comparison (source: reports/openai-finetune-eval.md, docs/Day6.md).

## Observed Failure Modes

| Area | What failed | Example or evidence | Impact |
| --- | --- | --- | --- |
| JSON contract | API output often starts with explanation text before JSON or contains no JSON object | `raw_prediction` contains prose such as "The log contains several suspicious activities" before any schema-like block (source: reports/openai-finetune-eval.json) | strict evaluator marks output invalid |
| Required fields | Some outputs omit `recommended_action` | model output examples in manual test and smoke failures | schema contract breaks |
| Label taxonomy | Output may invent labels outside the five-label taxonomy | `botnet_command_and_control` appears in a raw smoke prediction (source: reports/openai-finetune-eval.json) | evaluator and UI cannot trust labels |
| Label casing | Output may use wrong casing such as `SQL_injection_attempt` | manual API test screenshot/run note | schema enum mismatch |
| Evidence quality | Evidence can be generic instead of a concrete substring from the log | `["SQL injection attempt"]` rather than payload or path fragment | weak investigation value |
| Reason grounding | Reason may describe attacks not present in the log | local SLEEP example mentions unrelated `UNION` style reasoning | model looks confident but misleading |
| Split discipline | Smoke run used `data/raw/test.jsonl` | report path records `split: data/raw/test.jsonl` (source: reports/openai-finetune-eval.json) | cannot use this as final comparison |

## Working Pieces

- GPU training script exists and can save an adapter artifact (source: ml/unsloth/train_lora.py).
- Config keeps training values outside Python code, so runs are reproducible and auditable (source: ml/unsloth/config.example.yaml).
- Local inference script can show raw model output for debugging with `--show-raw-output` (source: ml/unsloth/inference.py).
- vLLM can serve the base model plus LoRA adapter as an OpenAI-compatible endpoint when model name, LoRA path, memory, CUDA stack, and tokenizer are handled correctly.
- Evaluator catches the bad behavior instead of hiding it, because it requires strict JSON via `json.loads` (source: reports/openai-finetune-eval.json).

## Decision

| Decision | Rationale |
| --- | --- |
| Do not promote v1 as a usable fine-tuned model | It proves the pipeline but fails the output contract in API evaluation |
| Keep v1 artifacts as debug baseline | The failures are useful for prompt, dataset, tokenizer, and serve-path fixes |
| Keep evaluator strict | Loosening evaluation to accept prose+JSON would hide production-facing failure |
| Do not treat merge/GGUF as quality fix | Export format changes packaging, not model behavior |

## Next Experiment

1. Tighten the prompt contract so the model sees "return exactly one JSON object" and no longer sees wording that encourages prose plus `Output schema`.
2. Add structured-output or guided-JSON support in the vLLM/OpenAI-compatible adapter if available in the runtime path.
3. Add training examples that punish prose wrappers and require JSON-only assistant messages.
4. Add hard negative and near-miss examples for `SLEEP(5)`, directory traversal, and port scan cases so `reason` stays grounded in the actual log.
5. Re-run smoke evaluation on the same 5 examples first, then run fixed split evaluation with `data/splits/test.jsonl` only after JSON parse success is high.

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-18 | Codex | Documented v1 model behavior, config, smoke-eval failure modes, and next experiment plan | `docs/model-output/v1-lfm2-350m-security-triage.md` | Done |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-18 | Mark v1 as rejected for output contract | API smoke evaluation has 0 JSON parse success and 5 invalid outputs | Next iteration must optimize JSON/schema adherence before final fixed-split comparison |
| 2026-05-18 | Keep adapter-first serve path as current runtime baseline | vLLM base+LoRA serving works while merged checkpoint path is not the stable evaluation path | Evaluation should target the `lfm2-security-triage` LoRA model name first |

## Related pages

- [[model-output/README]]
- [[model-output/template]]
- [[Day6]]
- [[fine-tuning-notes]]
- [[triage-output-schema]]
- [[evaluation-metrics-rationale]]

# V1 LFM2-350M Security Triage

**Summary**

หน้าเดิมนี้เริ่มจาก v1 ของ fine-tuned path แต่ตอนนี้ใช้เก็บผลรันล่าสุดของ artifact ใหม่ด้วย: `unsloth_LFM2-350M_1779162226` หรือเรียกสั้น ๆ ว่า `v2` ได้ โดยยังอยู่บน base model `unsloth/LFM2-350M` เดิม ไม่ใช่การเปลี่ยน base model รอบ prompt v2 smoke ล่าสุด load LoRA แบบ 16-bit ผ่าน OpenAI-compatible endpoint แล้ว แต่ยังไม่ผ่านเกณฑ์ model output สำหรับ POC เพราะ output ยังมี markdown-fenced JSON, JSON ที่ไม่ตรง schema, label นอก taxonomy และ field ขาด

**Sources**

- `ml/unsloth/config.example.yaml` สำหรับ config ของ LFM2-350M + LoRA v1 (source: ml/unsloth/config.example.yaml)
- `ml/unsloth/train_lora.py` สำหรับ training implementation, split guard และ Unsloth-first training path (source: ml/unsloth/train_lora.py)
- `ml/unsloth/inference.py` สำหรับ local adapter inference และ raw output debug flag (source: ml/unsloth/inference.py)
- `ml/unsloth/merge_adapter.py` สำหรับ merge/GGUF export path หลัง train (source: ml/unsloth/merge_adapter.py)
- `reports/openai-finetune-eval.json` สำหรับ smoke evaluation ของ OpenAI-compatible endpoint (source: reports/openai-finetune-eval.json)
- `reports/openai-finetune-eval.md` สำหรับ metric summary ของ smoke evaluation (source: reports/openai-finetune-eval.md)
- `reports/openai-compatible-eval.json` สำหรับ prompt v2 structured-output smoke evaluation ล่าสุดบน deterministic smoke split (source: reports/openai-compatible-eval.json)
- `reports/openai-compatible-eval.md` สำหรับ metric summary ของ prompt v2 smoke evaluation ล่าสุด (source: reports/openai-compatible-eval.md)
- `docs/Day6.md` สำหรับสถานะ Day 6 และ decision ว่า smoke/debug eval ยังไม่ใช่ final comparison (source: docs/Day6.md)
- Unsloth Studio run note และ screenshot วันที่ 2026-05-19 สำหรับ artifact `unsloth_LFM2-350M_1779162226`, training files, hyperparameters และ LoRA 16-bit load profile (source: user-provided Codex thread note, 2026-05-19)

**Last updated**

2026-05-19

## Version Metadata

| Field | Value |
| --- | --- |
| Model version | `v1`; latest prompt v2 smoke artifact is `v2` |
| Model name | `lfm2-350m-security-triage-lora` for v1; `unsloth_LFM2-350M_1779162226` for latest v2 run |
| Base model | `unsloth/LFM2-350M` unchanged |
| Model family | `LFM2` |
| Adapter path | `ml/unsloth/outputs/lfm2-350m-security-triage-lora` |
| Merged output path | `ml/unsloth/outputs/lfm2-350m-security-triage-mearged` in manual run; intended default is `ml/unsloth/outputs/lfm2-350m-security-triage-merged` |
| Latest trained artifact | `unsloth_LFM2-350M_1779162226` |
| Runtime model alias in report | `lfm2-security-triage` |
| LoRA load profile | 16-bit LoRA load for latest v2 smoke run |
| Training prompt version | `triage-json-v1` |
| Latest runtime prompt version tested | `triage-json-v2` |
| Repo training splits | `data/splits/train.jsonl`, `data/splits/validation.jsonl` |
| Latest Unsloth Studio train files | `train.jsonl`, `validation.jsonl` |
| Latest training record format | instruction tuning: `instruction`, `input`, `output` |
| Smoke API split | `data/raw/test.jsonl` |
| Output-contract smoke split | `data/splits/smoke-output-contract.jsonl` |
| Fixed evaluation split | `data/splits/test.jsonl` not completed yet |
| Status | `v2-smoke-tested-rejected-for-output-contract` |

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

## Latest Unsloth Studio V2 Snapshot

รอบล่าสุดเป็นการ train model ใหม่ใน Unsloth Studio ด้วยไฟล์ `train.jsonl` และ `validation.jsonl` ในรูปแบบ instruction tuning ตรง ๆ คือ source record มี `instruction`, `input`, และ `output` โดย `output` เป็น triage schema เดิมของโปรเจกต์ รอบนี้ควรนับเป็น artifact ใหม่ชื่อ `unsloth_LFM2-350M_1779162226` หรือ alias `v2` แต่ base model ยังเป็น `unsloth/LFM2-350M` เดิม

```yaml
model:
  base_model: unsloth/LFM2-350M
  trained_artifact: unsloth_LFM2-350M_1779162226
  artifact_alias: v2
  max_seq_length: 2048
  lora_load_profile: 16-bit

data:
  train_path: train.jsonl
  validation_path: validation.jsonl
  training_record_format: instruction_tuning
  fields:
    - instruction
    - input
    - output
  output_contract: data/schemas/triage-output.schema.json

lora:
  enabled: true
  r: 16
  lora_alpha: 16
  lora_dropout: 0.0
  target_modules:
    - q_proj
    - k_proj
    - v_proj
    - o_proj
    - gate_proj
    - up_proj
    - down_proj

training:
  max_steps: 55
  learning_rate: 0.0002
  per_device_train_batch_size: 2
  gradient_accumulation_steps: 4
  warmup_steps: 8
  save_steps: 30
  eval_steps: 0.1
  seed: 3407
  optim: adamw_8bit
  lr_scheduler_type: linear
```

## What Happened

1. Training path was completed enough to run GPU short trial and save a LoRA adapter. The implementation keeps train and validation paths in config and intentionally excludes `data/splits/test.jsonl` from training (source: ml/unsloth/config.example.yaml, ml/unsloth/train_lora.py).
2. Local Unsloth inference can load the base model plus adapter and emit parseable JSON for at least one hand-run SQLi-like log, but the generated `reason` may mention unrelated SQL patterns such as `UNION` when the input only contains `SLEEP(5)`. That means JSON shape can pass while semantic grounding still fails (source: ml/unsloth/inference.py).
3. Merge/export tooling exists, including GGUF export, but merge/GGUF is only a packaging step. It does not fix schema adherence, hallucinated reasons, or taxonomy drift (source: ml/unsloth/merge_adapter.py, docs/Day6.md).
4. vLLM base+LoRA serving reached a usable endpoint with `unsloth/LFM2-350M` as base and `lfm2-security-triage` as LoRA model name. The safer serving path for now is adapter-first, not the merged checkpoint path.
5. API smoke evaluation through the OpenAI-compatible adapter produced a report, but the report is a failure artifact: 5/5 outputs were invalid under strict JSON parsing (source: reports/openai-finetune-eval.json, reports/openai-finetune-eval.md).
6. A later prompt v2 smoke run used a newly trained Unsloth Studio artifact, `unsloth_LFM2-350M_1779162226` (`v2`), loaded as 16-bit LoRA on the same `unsloth/LFM2-350M` base. The evaluator report still records the served model alias as `lfm2-security-triage`, so the artifact-to-alias mapping comes from the operator run note rather than the report metadata itself. The run used `data/splits/smoke-output-contract.jsonl`, requested `json_schema_strict`, and did not fall back to `json_object`, but output contract quality was still poor: 4/5 outputs were invalid under strict JSON parsing and only 1/5 passed schema validation (source: reports/openai-compatible-eval.json; user-provided Codex thread note, 2026-05-19).

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

## Prompt V2 Structured-Output Smoke Evaluation

รอบล่าสุดใช้ deterministic smoke split ที่ `data/splits/smoke-output-contract.jsonl` จำนวน 5 samples กับ model ใหม่จาก Unsloth Studio คือ `unsloth_LFM2-350M_1779162226` (`v2`) แต่ base ยังเป็น `unsloth/LFM2-350M` เดิม รอบ serve ใช้ LoRA load แบบ 16-bit และ adapter `openai-compatible` ชี้ไป runtime alias `lfm2-security-triage` ตาม report metadata โดย request ใช้ `response_format_requested=json_schema`, `response_format_mode=json_schema_strict` และ `response_format_attempted_modes=["json_schema_strict"]` ไม่มี fallback ไป `json_object` (source: reports/openai-compatible-eval.json; user-provided Codex thread note, 2026-05-19)

| Run field | Value |
| --- | --- |
| Runtime artifact | `unsloth_LFM2-350M_1779162226` |
| Working alias | `v2` |
| Base model | `unsloth/LFM2-350M` unchanged |
| Report model alias | `lfm2-security-triage` |
| LoRA load profile | 16-bit |
| Training files | `train.jsonl`, `validation.jsonl` |
| Training format | instruction tuning with `instruction`, `input`, `output` |
| Runtime prompt | `triage-json-v2` |
| Response format requested | `json_schema` / `json_schema_strict` |

| Metric | Value |
| --- | ---: |
| Samples | `5` |
| JSON parse success rate | `0.2` |
| Schema success rate | `0.2` |
| Label accuracy | `0.2` |
| Severity accuracy | `0.0` |
| Evidence partial match | `0.0` |
| Invalid output count | `4` |
| Average latency ms | `4490.161525` |

ผลนี้ยืนยันว่า artifact ใหม่ train และ serve ได้แล้ว แต่ยังไม่ผ่าน output contract เพราะ 4/5 samples parse ไม่ผ่านจากมุมมอง evaluator strict และทุก sample ยังมี failure อย่างน้อยหนึ่งข้อ จึงยังไม่ควรใช้ run นี้เป็น final comparison กับ baseline หรือรัน fixed split 75 samples ต่อทันที

### Prompt V2 Failure Notes

| Sample | Expected | Observed | Main issue |
| --- | --- | --- | --- |
| `sample-000035` | `normal` | markdown-fenced JSON with `port_scan_or_recon` | normal connection ถูกมองเป็น scan และ parse ไม่ผ่านเพราะมี code fence |
| `sample-000137` | `failed_login_bruteforce` | schema-valid `failed_login_bruteforce` with `high` severity | label ถูก แต่ severity ผิด และ evidence hallucinate เช่น `sshd.log`, `ssh2.log` |
| `sample-000248` | `sql_injection_attempt` | markdown-fenced JSON with `ssh_attempt_failed` | label นอก taxonomy, ขาด `recommended_action`, และเหตุผล drift ไป SSH brute force |
| `sample-000331` | `directory_traversal_attempt` | markdown-fenced JSON with `failed_login_bruteforce` | directory traversal ถูกอธิบายเป็น failed login |
| `sample-000474` | `port_scan_or_recon` | markdown-fenced JSON with `ssh_bruteforce_attempt` | label นอก taxonomy, ขาด `recommended_action`, และเหตุผล drift ไป brute force |

ข้อสรุปของรอบนี้คือ prompt v2 และ model artifact ใหม่ช่วยยืนยันว่า training pipeline รอบใหม่เดินถึง smoke evaluation แล้ว แต่ runtime path ยังไม่ได้ enforce structured output จริงในเชิงผลลัพธ์ เพราะยังเห็น markdown fence, label นอก enum และ field ขาด ทั้งที่ metadata ฝั่ง adapter ระบุว่าใช้ `json_schema_strict` แล้ว (source: reports/openai-compatible-eval.json)

## Observed Failure Modes

| Area | What failed | Example or evidence | Impact |
| --- | --- | --- | --- |
| JSON contract | API output often starts with explanation text before JSON or contains no JSON object | `raw_prediction` contains prose such as "The log contains several suspicious activities" before any schema-like block (source: reports/openai-finetune-eval.json) | strict evaluator marks output invalid |
| Structured output enforcement | Prompt v2 run requested `json_schema_strict`, but raw output still contained markdown-fenced JSON | `raw_prediction` for multiple prompt v2 samples starts with a markdown JSON code fence (source: reports/openai-compatible-eval.json) | endpoint/runtime appears not to enforce schema-constrained output despite request metadata |
| Required fields | Some outputs omit `recommended_action` | model output examples in manual test and smoke failures | schema contract breaks |
| Label taxonomy | Output may invent labels outside the five-label taxonomy | `botnet_command_and_control` appears in the earlier smoke run; `ssh_attempt_failed` and `ssh_bruteforce_attempt` appear in the prompt v2 smoke run (source: reports/openai-finetune-eval.json, reports/openai-compatible-eval.json) | evaluator and UI cannot trust labels |
| Label casing | Output may use wrong casing such as `SQL_injection_attempt` | manual API test screenshot/run note | schema enum mismatch |
| Evidence quality | Evidence can be generic instead of a concrete substring from the log | `["SQL injection attempt"]` rather than payload or path fragment | weak investigation value |
| Reason grounding | Reason may describe attacks not present in the log | local SLEEP example mentions unrelated `UNION` style reasoning | model looks confident but misleading |
| Split discipline | Smoke run used `data/raw/test.jsonl` | report path records `split: data/raw/test.jsonl` (source: reports/openai-finetune-eval.json) | cannot use this as final comparison |

## Working Pieces

- GPU training script exists and can save an adapter artifact (source: ml/unsloth/train_lora.py).
- Unsloth Studio training can produce a newer LoRA artifact, `unsloth_LFM2-350M_1779162226`, from instruction tuning records and load it as 16-bit LoRA for endpoint smoke testing (source: user-provided Codex thread note, 2026-05-19).
- Config keeps training values outside Python code, so runs are reproducible and auditable (source: ml/unsloth/config.example.yaml).
- Local inference script can show raw model output for debugging with `--show-raw-output` (source: ml/unsloth/inference.py).
- vLLM can serve the base model plus LoRA adapter as an OpenAI-compatible endpoint when model name, LoRA path, memory, CUDA stack, and tokenizer are handled correctly.
- Evaluator catches the bad behavior instead of hiding it, because it requires strict JSON via `json.loads` (source: reports/openai-finetune-eval.json).

## Decision

| Decision | Rationale | Impact |
| --- | --- | --- |
| Do not promote v1 as a usable fine-tuned model | It proves the pipeline but fails the output contract in API evaluation | v1 remains a reference/debug baseline only |
| Keep v1 artifacts as debug baseline | The failures are useful for prompt, dataset, tokenizer, and serve-path fixes | Later runs can compare whether output-contract fixes improve over v1 |
| Treat `unsloth_LFM2-350M_1779162226` as v2, not a new base model | The latest artifact is a new LoRA/fine-tuned run on the same `unsloth/LFM2-350M` base | Reports and docs should separate base model identity from trained artifact identity |
| Keep evaluator strict | Loosening evaluation to accept prose+JSON would hide production-facing failure | Smoke reports should continue to fail loudly when output is not exact JSON |
| Do not treat merge/GGUF as quality fix | Export format changes packaging, not model behavior | Quality work should focus on runtime schema enforcement and data/prompt behavior |
| Do not run fixed split comparison from the latest smoke state | Prompt v2 smoke has only 0.2 JSON/schema success and 4 invalid outputs out of 5 | Fix or verify structured-output enforcement before spending a 75-sample endpoint run |

## Next Experiment

1. Test a direct request to the endpoint with `response_format=json_schema` outside LangChain to confirm whether the server enforces schema-constrained decoding.
2. If the standard request is not enforced, test the vLLM-style `extra_body={"structured_outputs":{"json": schema}}` path directly.
3. Keep evaluator parsing strict with `json.loads(raw_prediction)` and avoid treating markdown-fenced JSON as valid in the main path.
4. Fix adapter/reporting so the smoke report distinguishes "schema requested" from "schema actually enforced" as clearly as possible.
5. Only after JSON parse and schema success are close to 1.0 on `data/splits/smoke-output-contract.jsonl`, run the fixed split evaluation with `data/splits/test.jsonl`.
6. Do not start another retrain immediately. Since `v2` has already been trained with instruction tuning data, first fix or verify runtime structured-output enforcement. If schema validity improves but semantic drift remains, prepare a `v3` dataset pass with hard examples for `SLEEP(5)`, directory traversal, and port scan cases.

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-18 | Codex | Documented v1 model behavior, config, smoke-eval failure modes, and next experiment plan | `docs/model-output/v1-lfm2-350m-security-triage.md` | Done |
| 2026-05-19 | Codex | Added prompt v2 structured-output smoke result and failure analysis | `reports/openai-compatible-eval.json`, `docs/model-output/v1-lfm2-350m-security-triage.md` | Done |
| 2026-05-19 | Codex | Corrected latest prompt v2 smoke identity to the new Unsloth Studio artifact `unsloth_LFM2-350M_1779162226` and documented its LoRA 16-bit load/training profile | `docs/model-output/v1-lfm2-350m-security-triage.md` | Done |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-18 | Mark v1 as rejected for output contract | API smoke evaluation has 0 JSON parse success and 5 invalid outputs | Next iteration must optimize JSON/schema adherence before final fixed-split comparison |
| 2026-05-18 | Keep adapter-first serve path as current runtime baseline | vLLM base+LoRA serving works while merged checkpoint path is not the stable evaluation path | Evaluation should target the `lfm2-security-triage` LoRA model name first |
| 2026-05-19 | Keep v1 rejected after prompt v2 structured-output smoke | The latest smoke run still has only 0.2 JSON/schema success, 0.0 severity/evidence match, and 4 invalid outputs out of 5 | Do not proceed to fixed split comparison until structured output enforcement is verified and smoke validity recovers |
| 2026-05-19 | Reclassify the latest prompt v2 smoke as the v2 Unsloth Studio artifact run | Operator clarified that the run came from `unsloth_LFM2-350M_1779162226`, loaded as 16-bit LoRA on the existing LFM2-350M base | v1 remains the historical debug baseline; v2 is the latest artifact but is still rejected for output contract until smoke validity recovers |

## Related pages

- [[model-output/README]]
- [[model-output/template]]
- [[Day6]]
- [[fine-tuning-notes]]
- [[triage-output-schema]]
- [[evaluation-metrics-rationale]]

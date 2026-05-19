# Model Output Template

**Summary**

ใช้หน้านี้เป็น template สำหรับบันทึก model version ใหม่ ให้ copy ไปเป็น `docs/model-output/vN-name.md` แล้วกรอกเฉพาะสิ่งที่เกิดขึ้นจริง ห้ามทำ metric ให้ดูดีเกินจริง และต้องแยก smoke/debug result ออกจาก fixed-split evaluation เสมอ

**Sources**

- `AGENTS.md` สำหรับ output schema, label scope และ evaluation rules (source: AGENTS.md)
- `docs/triage-output-schema.md` สำหรับ schema contract กลาง (source: docs/triage-output-schema.md)
- `docs/evaluation-metrics-rationale.md` สำหรับ metric ที่ต้องเก็บ (source: docs/evaluation-metrics-rationale.md)
- `ml/unsloth/config.example.yaml` หรือ config ของ run นั้นสำหรับ training/runtime parameters (source: ml/unsloth/config.example.yaml)

**Last updated**

YYYY-MM-DD

## Version Metadata

| Field | Value |
| --- | --- |
| Model version | `vN` |
| Model name | `...` |
| Base model | `...` |
| Adapter path | `...` |
| Output path | `...` |
| Prompt version | `triage-json-v2` |
| Dataset train split | `data/splits/train.jsonl` |
| Dataset validation split | `data/splits/validation.jsonl` |
| Output-contract smoke split | `data/splits/smoke-output-contract.jsonl` |
| Evaluation split | `data/splits/test.jsonl` |
| Created date | `YYYY-MM-DD` |
| Status | `draft / trained / served / evaluated / rejected / promoted` |

## Config Snapshot

```yaml
model:
  base_model:
  model_family:
  max_seq_length:
  load_in_4bit:
  dtype:

format:
  prompt_version:
  training_record_format:
  strict_output_schema:

lora:
  r:
  lora_alpha:
  lora_dropout:
  target_modules:

training:
  per_device_train_batch_size:
  gradient_accumulation_steps:
  max_steps:
  learning_rate:
  seed:

output:
  output_dir:
  adapter_name:
```

## Training Notes

- Environment:
- Command:
- Duration:
- GPU/VRAM:
- Train/validation behavior:
- Artifacts produced:
- Known caveats:

## Serve Notes

- Runtime:
- Command:
- Model name exposed to API:
- Tokenizer path:
- LoRA mode:
- Memory/latency notes:
- Warnings:

## Local Inference Checks

| Date | Input | Raw output shape | Parse result | Quality note |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | `...` | JSON-only / prose+JSON / prose-only | pass/fail | ... |

## API Evaluation

| Report | Split | Samples | JSON parse | Schema success | Label accuracy | Notes |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `reports/...json` | `...` | 0 | 0.0 | 0.0 | 0.0 | ... |

## Failure Modes

- JSON contract:
- Schema fields:
- Label taxonomy:
- Evidence quality:
- Reason hallucination:
- Runtime/deployment:

## Decision

| Decision | Rationale |
| --- | --- |
| Keep / retrain / reject / promote | ... |

## Next Experiment

- Prompt:
- Dataset:
- Training:
- Evaluation:
- Runtime:

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | ... | ... | ... | ... |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| YYYY-MM-DD | ... | ... | ... |

## Related pages

- [[model-output/README]]
- [[Day6]]
- [[fine-tuning-notes]]
- [[triage-output-schema]]

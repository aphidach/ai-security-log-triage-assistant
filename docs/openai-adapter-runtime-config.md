# OpenAI Adapter Runtime Config

**Summary**

หน้านี้อธิบายไฟล์ `config-adapter.yml` สำหรับปรับค่า runtime ของ `openai-compatible` และ `openai-finetune` adapters โดยไม่ต้อง export env ยาว ๆ ทุกครั้ง ใช้กับค่า endpoint, model, structured-output mode และ request parameters เช่น `temperature`, `top_p`, `frequency_penalty`, `presence_penalty`, `seed`, `stop` รวมถึง `extra_body` สำหรับ backend ที่เป็น OpenAI-compatible แต่มี parameter เพิ่ม เช่น vLLM (source: scripts/model_adapters/openai_compatible.py, config-adapter.example.yml)

**Sources**

- `scripts/model_adapters/openai_compatible.py` สำหรับ loader, precedence, request options และ metadata ที่บันทึกใน report (source: scripts/model_adapters/openai_compatible.py)
- `config-adapter.example.yml` สำหรับตัวอย่างไฟล์ local config (source: config-adapter.example.yml)
- `.env.example` สำหรับ env fallback และ config path env variables (source: .env.example)
- `scripts/evaluate.py` สำหรับ workflow ที่เรียก adapters ระหว่าง evaluation (source: scripts/evaluate.py)

**Last updated**

2026-05-21

## Local File

สร้างไฟล์ local จากตัวอย่าง:

```bash
cp config-adapter.example.yml config-adapter.yml
```

`config-adapter.yml` ถูก ignore โดย git เพราะอาจมี endpoint URL หรือ API key จริง ถ้าต้องการใช้ชื่ออื่น ให้ชี้ path ผ่าน env:

```bash
OPENAI_ADAPTER_CONFIG_PATH=config-adapter.yml
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml
OPENAI_FINETUNE_CONFIG_PATH=config-adapter.yml
```

adapter จะหาไฟล์ตามลำดับนี้:

1. `OPENAI_COMPATIBLE_CONFIG_PATH` หรือ `OPENAI_FINETUNE_CONFIG_PATH`
2. `OPENAI_ADAPTER_CONFIG_PATH`
3. `config-adapter.yml` หรือ `config-adapter.yaml` ที่ repo root ถ้ามี
4. ถ้าไม่เจอไฟล์ จะ fallback ไป env/default เดิม

## Precedence

สำหรับ field พื้นฐาน เช่น `model`, `max_tokens`, `response_format` และ `schema_path` ใช้ลำดับนี้:

1. explicit adapter constructor argument
2. env เช่น `OPENAI_COMPATIBLE_MODEL`
3. YAML section ของ adapter
4. adapter default

ดังนั้น command เดิมที่ export `OPENAI_COMPATIBLE_MODEL=...` ยัง override ค่าใน YAML ได้อยู่

## Example

```yaml
defaults:
  request:
    temperature: 0

openai-compatible:
  base_url: http://192.168.8.141:8080/v1
  api_key: local
  model: lfm2-security-triage-v3-3
  timeout_seconds: 120
  max_retries: 0
  max_tokens: 512
  response_format: structured_outputs
  schema_path: data/schemas/triage-output.schema.json
  request:
    temperature: 0.3
    top_p: 0.9
    extra_body:
      min_p: 0.15
      repetition_penalty: 1.05
```

`request.temperature`, `top_p`, `frequency_penalty`, `presence_penalty`, `seed`, และ `stop` จะถูกส่งเป็น OpenAI chat-completions kwargs ส่วน `extra_body` จะ merge กับ structured-output payload เช่น `structured_outputs` หรือ `guided_json`

สำหรับ `responses_parse` adapter จะส่งเฉพาะ request option ที่ path นั้นรองรับตอนนี้คือ `temperature` และ `top_p`

## Evaluation Guidance

ให้เก็บ deterministic path เป็น baseline ก่อน เช่น `temperature: 0`

ถ้าจะลองค่าจาก model card เช่น `temperature: 0.3`, `min_p: 0.15`, หรือ `repetition_penalty: 1.05` ให้ใช้ report path แยก เพื่อไม่ปนกับ canonical eval:

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-runtime-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-runtime-probe.md \
  --no-progress
```

report metadata จะบันทึก `config_path`, `request_options` และ `extra_body` เพื่อให้ย้อนดูได้ว่ารอบนั้นใช้ runtime setting อะไร

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Created adapter runtime config doc for YAML-based OpenAI-compatible request settings | `config-adapter.example.yml`, `scripts/model_adapters/openai_compatible.py` | Created |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Keep `config-adapter.yml` local and ignored | Adapter config may contain runtime URLs or API keys | Commit only `config-adapter.example.yml`; local config can vary per machine |
| 2026-05-21 | Keep env override above YAML | Existing eval commands already rely on env overrides for model aliases and report-specific runs | Old workflow remains compatible while YAML reduces repeated boilerplate |

## Related pages

- [[scripts]]
- [[output-contract-hardening]]
- [[model-repetition-loop-diagnostics]]
- [[lfm2-350m-model-card-notes]]

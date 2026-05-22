# OpenAI Adapter Runtime Config

**Summary**

หน้านี้อธิบายไฟล์ `config-adapter.yml` สำหรับปรับค่า runtime ของ `openai-compatible` และ `openai-finetune` adapters โดยไม่ต้อง export env ยาว ๆ ทุกครั้ง ใช้กับค่า endpoint, model, structured-output mode, prompt profile และ request parameters เช่น `temperature`, `top_p`, `frequency_penalty`, `presence_penalty`, `seed`, `stop` รวมถึง `extra_body` สำหรับ backend ที่เป็น OpenAI-compatible แต่มี parameter เพิ่ม เช่น vLLM โดย report-specific runs ยัง override request options ผ่าน env ได้เพื่อกัน stale config ชี้ผิด model, prompt หรือ temperature (source: scripts/model_adapters/openai_compatible.py, config-adapter.example.yml)

**Sources**

- `scripts/model_adapters/openai_compatible.py` สำหรับ loader, precedence, request options และ metadata ที่บันทึกใน report (source: scripts/model_adapters/openai_compatible.py)
- `config-adapter.example.yml` สำหรับตัวอย่างไฟล์ local config (source: config-adapter.example.yml)
- `.env.example` สำหรับ env fallback และ config path env variables (source: .env.example)
- `scripts/evaluate.py` สำหรับ workflow ที่เรียก adapters ระหว่าง evaluation (source: scripts/evaluate.py)

**Last updated**

2026-05-22

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

สำหรับ field พื้นฐาน เช่น `model`, `max_tokens`, `response_format`, `prompt_version` และ `schema_path` ใช้ลำดับนี้:

1. explicit adapter constructor argument
2. env เช่น `OPENAI_COMPATIBLE_MODEL`
3. YAML section ของ adapter
4. adapter default

ดังนั้น command เดิมที่ export `OPENAI_COMPATIBLE_MODEL=...` ยัง override ค่าใน YAML ได้อยู่

สำหรับ request options ใน `request:` ตอนนี้ override ผ่าน env ได้เช่นกัน:

| YAML key | Env override |
| --- | --- |
| `prompt_version` | `OPENAI_COMPATIBLE_PROMPT_VERSION` |
| `temperature` | `OPENAI_COMPATIBLE_TEMPERATURE` |
| `top_p` | `OPENAI_COMPATIBLE_TOP_P` |
| `frequency_penalty` | `OPENAI_COMPATIBLE_FREQUENCY_PENALTY` |
| `presence_penalty` | `OPENAI_COMPATIBLE_PRESENCE_PENALTY` |
| `seed` | `OPENAI_COMPATIBLE_SEED` |
| `stop` | `OPENAI_COMPATIBLE_STOP` |
| `extra_body` | `OPENAI_COMPATIBLE_EXTRA_BODY` เป็น JSON object string |

`openai-finetune` ใช้ prefix เดียวกันตาม adapter เช่น `OPENAI_FINETUNE_PROMPT_VERSION`, `OPENAI_FINETUNE_TEMPERATURE` และ `OPENAI_FINETUNE_EXTRA_BODY`

prompt profile default คือ `triage-json-v2.1` ซึ่งเป็น prompt ที่ใช้กับ training และ runtime เดิมทั้งหมด ส่วน `triage-json-v2.2-sqli-priority` เป็น profile สำหรับ Phase 8/v4.2 hard-contrast diagnostic เท่านั้น ยังไม่ใช่ default UI หรือ training prompt

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
  prompt_version: triage-json-v2.1
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
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v3-3 \
OPENAI_COMPATIBLE_TEMPERATURE=0.3 \
OPENAI_COMPATIBLE_TOP_P=0.9 \
OPENAI_COMPATIBLE_EXTRA_BODY='{"min_p":0.15,"repetition_penalty":1.05}' \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-runtime-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-runtime-probe.md \
  --no-progress
```

report metadata จะบันทึก `config_path`, `request_options` และ `extra_body` เพื่อให้ย้อนดูได้ว่ารอบนั้นใช้ runtime setting อะไร

สำหรับ Phase 8/v4.2 SQLi-priority prompt diagnostic ให้ override prompt ใน command เดียวกับ report path:

```bash
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v4-1 \
OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.2-sqli-priority \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TEMPERATURE=0 \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.md
```

report metadata จะบันทึก `prompt_version` เพื่อแยก v4.2 prompt-probe ออกจาก v4.1 checkpoint run เดิม

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Created adapter runtime config doc for YAML-based OpenAI-compatible request settings | `config-adapter.example.yml`, `scripts/model_adapters/openai_compatible.py` | Created |
| 2026-05-22 | Codex | Documented request-option env overrides for report-specific runtime probes | `scripts/model_adapters/openai_compatible.py`, `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md` | Updated |
| 2026-05-22 | Codex | Documented runtime-selectable prompt profiles for v4.2 SQLi-priority probes | `scripts/model_adapters/prompt_contract.py`, `scripts/model_adapters/openai_compatible.py` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Keep `config-adapter.yml` local and ignored | Adapter config may contain runtime URLs or API keys | Commit only `config-adapter.example.yml`; local config can vary per machine |
| 2026-05-21 | Keep env override above YAML | Existing eval commands already rely on env overrides for model aliases and report-specific runs | Old workflow remains compatible while YAML reduces repeated boilerplate |
| 2026-05-22 | Allow request options to be overridden per command | Runtime probe report names include model/temp settings, so stale YAML must not silently change what got measured | Eval commands can force `temperature`, `top_p`, and `extra_body` in the same shell block as the report path |
| 2026-05-22 | Keep `triage-json-v2.1` as the default prompt profile | Existing training configs and UI runtime should remain comparable after adding the v4.2 prompt diagnostic | v4.2 must opt in with `OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.2-sqli-priority` |

## Related pages

- [[scripts]]
- [[output-contract-hardening]]
- [[model-repetition-loop-diagnostics]]
- [[lfm2-350m-model-card-notes]]

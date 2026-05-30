# Output Contract Hardening

**Summary**

หน้านี้สรุปรอบแก้ปัญหา output contract ของ fine-tuned/OpenAI-compatible path ว่าทำอะไรไปแล้ว ตัดสินใจอะไรไป และตั้งใจแยกปัญหา `output shape` ออกจาก `model quality` อย่างไร ก่อนตัดสินใจ retrain รอบถัดไป

**Sources**

- `AGENTS.md` สำหรับ output schema กลาง, implementation priority และหลักการไม่ overclaim (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ POC scope และเกณฑ์ evaluation ที่ต้องแยก JSON/schema validity ออกจาก accuracy (source: docs/poc-plan.md)
- `docs/Day4.md` สำหรับ adapter/prompt contract path และ env contract ของ OpenAI-compatible runtime (source: docs/Day4.md)
- `docs/Day6.md` สำหรับสถานะ fine-tuned smoke evaluation และ decision ว่ายังไม่ retrain ทันที (source: docs/Day6.md)
- `scripts/evaluate.py` สำหรับ strict JSON parsing และ schema validation ที่ยังคงเป็น evaluator contract หลัก (source: scripts/evaluate.py)
- `scripts/probe_openai_structured_output.py` สำหรับ OpenAI Python client structured-output probe โดยไม่ผ่าน LangChain รวมถึง `responses_parse`, `json_schema`, `structured_outputs`, และ `guided_json` (source: scripts/probe_openai_structured_output.py)
- `scripts/model_adapters/prompt_contract.py` สำหรับ prompt `triage-json-v2` ฝั่ง Python (source: scripts/model_adapters/prompt_contract.py)
- `scripts/model_adapters/openai_compatible.py` สำหรับ OpenAI SDK runtime path, `responses_parse` mode, Pydantic validation, structured output modes, schema sanitizer และ fallback logic (source: scripts/model_adapters/openai_compatible.py)
- `frontend/lib/prompts.ts` สำหรับ prompt mirror ฝั่ง frontend (source: frontend/lib/prompts.ts)
- `data/schemas/triage-output.schema.json` สำหรับ canonical triage output schema ของ repo (source: data/schemas/triage-output.schema.json)
- `data/splits/smoke-output-contract.jsonl` สำหรับ deterministic 5-sample smoke split ใหม่ (source: data/splits/smoke-output-contract.jsonl)
- `.env.example` สำหรับ env flags ใหม่ของ adapter (source: .env.example)
- `ml/unsloth/config.example.yaml` สำหรับ prompt version ที่ training path อ้างอิง (source: ml/unsloth/config.example.yaml)
- `docs/model-output/v1-lfm2-350m-security-triage.md` สำหรับ historical artifact ของ failure state ก่อนรอบ hardening นี้ (source: docs/model-output/v1-lfm2-350m-security-triage.md)
- `reports/openai-finetune-eval.md` สำหรับ historical failure state ของ smoke evaluation รอบก่อนแก้ contract (source: reports/openai-finetune-eval.md)
- Operator probe results วันที่ 2026-05-19 สำหรับ `responses_parse` และ `json_schema` บน `sample-000137` / `sample-000474` (source: user-provided terminal output, 2026-05-19)

**Last updated**

2026-05-19

## Problem Statement

fine-tuned endpoint รอบก่อนหน้านี้แพ้ตั้งแต่ชั้น output contract คือคืน prose หรือ prose+JSON แทน JSON object ล้วน ทำให้ strict evaluator parse ไม่ผ่านตั้งแต่ต้น และยังแยกไม่ออกว่าปัญหาหลักมาจาก prompt, runtime serve path, หรือ semantic quality ของ model เอง (source: reports/openai-finetune-eval.md, source: docs/Day6.md)

จุดที่ต้องแก้ก่อน retrain จึงไม่ใช่ accuracy แต่เป็นการบังคับให้ runtime ตอบกลับในรูปที่ parse และ validate ได้ก่อน แล้วค่อยวัดว่าหลังจากนั้น label, severity และ evidence ยัง drift แค่ไหน (source: docs/Day6.md, source: scripts/evaluate.py)

## What Changed

### Prompt Contract

- ยก prompt version จาก `triage-json-v1` เป็น `triage-json-v2` ทั้งฝั่ง Python และ frontend mirror (source: scripts/model_adapters/prompt_contract.py, source: frontend/lib/prompts.ts)
- ตัด `Output schema example:` ออกจาก system prompt เพื่อหยุดการกระตุ้นให้ model leak หัวข้อ schema หรือ prose wrapper ก่อน JSON (source: scripts/model_adapters/prompt_contract.py)
- เพิ่มข้อบังคับว่า response ต้องเริ่มด้วย `{` และจบด้วย `}` พร้อมย้ำว่าห้ามมีข้อความนอก JSON และต้องมี `recommended_action` เสมอ (source: scripts/model_adapters/prompt_contract.py)
- เพิ่ม `Respond with the JSON object only.` ใน user prompt เพื่อกดพฤติกรรมการอธิบายก่อนตอบ (source: scripts/model_adapters/prompt_contract.py)

### Structured Output Adapter

- เพิ่ม response-format config ให้ OpenAI-compatible adapters ผ่าน `OPENAI_COMPATIBLE_RESPONSE_FORMAT` และ `OPENAI_FINETUNE_RESPONSE_FORMAT` (source: scripts/model_adapters/openai_compatible.py, source: .env.example)
- adapter runtime หลักย้ายจาก LangChain `ChatOpenAI` มาเป็น OpenAI Python SDK โดยตรง เพื่อลด wrapper layer ระหว่าง evaluator กับ endpoint (source: scripts/model_adapters/openai_compatible.py)
- เพิ่ม `responses_parse` เป็น adapter mode จริง ไม่ใช่แค่ probe mode โดยเรียก `client.responses.parse(..., text_format=...)` และคืน parsed Pydantic object เป็น `dict` ให้ evaluator ใช้ต่อได้ทันที (source: scripts/model_adapters/openai_compatible.py)
- ตั้ง default response format ใหม่เป็น `responses_parse` เพื่อให้ smoke รอบถัดไปเริ่มจาก Pydantic validation path ก่อน ส่วน `json_schema`, `structured_outputs`, `guided_json`, `json_object` และ `off` ยังใช้ได้ผ่าน OpenAI SDK สำหรับ debug/fallback (source: scripts/model_adapters/openai_compatible.py, source: .env.example)
- เมื่อใช้ `json_schema` mode adapter จะพยายาม request mode ตามลำดับ `json_schema_strict` -> `structured_outputs_json` -> `json_object` และ fallback เฉพาะ error ที่มีลักษณะว่า runtime หรือ schema feature ไม่รองรับ (source: scripts/model_adapters/openai_compatible.py)
- adapter metadata จะบันทึกทั้ง `requested_model` และ `response_model` เพื่อไม่ให้สับสนระหว่าง alias ที่ยิง request กับ model จริงที่ runtime รายงานกลับมา (source: scripts/model_adapters/openai_compatible.py)
- ไม่ใช้ LangChain `PydanticOutputParser` หรือ `StructuredOutputParser` เป็น path หลัก เพราะสองอย่างนั้นเป็น parser/client-side formatting layer หลัง model ตอบแล้ว ไม่ใช่ runtime path ที่พิสูจน์กับ endpoint ผ่าน `data/raw/test.py` (source: scripts/model_adapters/openai_compatible.py, source: data/raw/test.py)

### Provider Schema Sanitizer

- canonical schema ของ repo ยังอยู่ที่ `data/schemas/triage-output.schema.json` และยังใช้เป็น source of truth สำหรับ evaluator (source: data/schemas/triage-output.schema.json, source: scripts/evaluate.py)
- เพิ่ม adapter layer ที่โหลด schema เดิมแล้ว sanitize ให้เหลือ provider-compatible subset ก่อนส่งเข้า runtime แทนการแก้ canonical schema ตรง ๆ (source: scripts/model_adapters/openai_compatible.py)
- sanitizer เก็บเฉพาะ keyword ที่ใช้บังคับ shape จริง เช่น `type`, `properties`, `required`, `additionalProperties`, `items`, `enum`, `description` และตัด metadata/constraints อื่นออกจาก request schema (source: scripts/model_adapters/openai_compatible.py)

### Direct Structured-Output Probe

- เพิ่ม `scripts/probe_openai_structured_output.py` เพื่อยิง endpoint ผ่าน OpenAI Python client โดยไม่ผ่าน LangChain และเทียบ mode ได้ทีละแบบ: `responses_parse`, `json_schema`, `structured_outputs`, `guided_json`, `json_object`, หรือ `plain` (source: scripts/probe_openai_structured_output.py)
- probe ใช้ prompt contract และ schema sanitizer เดียวกับ adapter เพื่อให้ผลเทียบกับ evaluator path ได้ตรงขึ้น แต่แยกปัญหา LangChain wrapper ออกจากปัญหา backend/runtime enforcement (source: scripts/probe_openai_structured_output.py, scripts/model_adapters/openai_compatible.py)
- mode `responses_parse` ใช้ `client.responses.parse(..., text_format=...)` ตาม pattern ใน `data/raw/test.py`, default model เป็น `current` และให้ OpenAI SDK/Pydantic validate output เป็น triage model โดยตรง (source: scripts/probe_openai_structured_output.py, data/raw/test.py)
- สำหรับ vLLM-style structured output, probe ใช้ `extra_body={"structured_outputs": {"json": schema}}` ตาม OpenAI client pattern เพื่อส่ง field เพิ่มไปยัง OpenAI-compatible backend (source: scripts/probe_openai_structured_output.py)
- เพิ่ม `guided_json` เป็น compatibility probe สำหรับ runtime ที่ยังใช้ guided decoding API รุ่นเก่าหรือไม่ได้ implement `structured_outputs` แบบใหม่ (source: scripts/probe_openai_structured_output.py, scripts/model_adapters/openai_compatible.py)

### Evaluator Metric Coverage

- เพิ่ม `is_suspicious_accuracy` ใน evaluator เพื่อวัดว่า boolean triage decision ตรง expected output หรือไม่ แยกจาก schema validation ที่เช็กแค่ว่า field นี้เป็น boolean (source: scripts/evaluate.py)

## Latest Probe Learning

ผล probe ล่าสุดแยกปัญหาได้ละเอียดขึ้นกว่าเดิม: endpoint alias ที่ request กับ model จริงที่ตอบอาจไม่ใช่ชื่อเดียวกัน ต้องดูทั้ง `requested_model` และ `response_model` ใน probe output เช่น request ไปที่ `lfm2-security-triage` หรือ `current` แต่ response ระบุ model จริงเป็น `unsloth/Qwen3.5-0.8B` (source: user-provided terminal output, 2026-05-19)

| Sample | Probe mode | Response model | Result | Learning |
| --- | --- | --- | --- | --- |
| `sample-000474` | `json_schema` | `unsloth/Qwen3.5-0.8B` | JSON parse ผ่าน แต่ schema fail เพราะขาด `recommended_action`; label ยังตอบ `normal` ทั้งที่ expected เป็น `port_scan_or_recon` | `chat.completions` + `json_schema` ช่วยให้ JSON ล้วนขึ้นได้กับ Qwen แต่ยังไม่บังคับ field ครบและยังมี semantic drift |
| `sample-000474` | `responses_parse` | not completed as valid parsed object | Pydantic validation fail ที่ field `recommended_action` missing | Responses parse path ทำงานถึงชั้น validation แล้ว failure นี้เป็น schema/model-output issue ไม่ใช่ markdown fence issue |
| `sample-000137` | `responses_parse` | `unsloth/Qwen3.5-0.8B` | `json_parse_success=true`, `schema_success=true`, มี `openai_parsed` เป็น triage object ครบทุก field | Responses parse เป็น runtime path ที่มีแนวโน้มดีที่สุดสำหรับ output contract เพราะ validate เป็น Pydantic object ได้จริงเมื่อ model ตอบครบ |

ข้อสรุปใหม่คือ path ที่ควรดันต่อไม่ใช่ `guided_json` หรือ `structured_outputs` บน chat completions เป็นหลัก แต่คือ `client.responses.parse(..., text_format=...)` เพราะ path นี้ทำให้เห็นชัดว่า output ผ่านหรือไม่ผ่าน Pydantic schema ตรงไหน ตอนนี้ path ดังกล่าวถูกย้ายเข้า adapter แล้วผ่าน `OPENAI_COMPATIBLE_RESPONSE_FORMAT=responses_parse` หรือ `OPENAI_FINETUNE_RESPONSE_FORMAT=responses_parse` ส่วนปัญหาที่เหลือหลังจาก parse สำเร็จต้องแยกเป็น model quality เช่น label drift, severity drift, evidence grounding และ field completeness (source: scripts/model_adapters/openai_compatible.py, scripts/probe_openai_structured_output.py, user-provided terminal output, 2026-05-19)

## Latest Responses Parse Smoke Run

หลังเพิ่ม `responses_parse` เข้า adapter แล้ว ผู้ใช้รัน smoke split ด้วย `OPENAI_COMPATIBLE_RESPONSE_FORMAT=responses_parse` และ `OPENAI_COMPATIBLE_MODEL=current` ผลยังอยู่ที่ `json_parse_success_rate=0.2`, `schema_success_rate=0.2`, `invalid_output_count=4` จาก 5 samples ซึ่งเท่ากับยังไม่ผ่าน output-contract gate (source: user-provided terminal output, 2026-05-19)

ความหมายของรอบนี้คือ adapter path ใหม่ทำหน้าที่ validate แบบ strict ได้แล้ว แต่ backend/model ยัง generate markdown-fenced JSON ใน 4/5 samples ทำให้ Pydantic เห็นเป็น invalid JSON ตั้งแต่ line 1 column 1 ไม่ใช่ parsed object ที่ validate fields ต่อได้ ดังนั้น `responses_parse` ใน endpoint นี้ยังเป็น validation path มากกว่า constrained decoding path (source: user-provided terminal output, 2026-05-19)

บันทึกแยกของ v2 run นี้อยู่ที่ [[model-output/v2-lfm2-350m-security-triage-responses-parse]] เพื่อไม่ให้ปนกับหน้า v1 historical baseline และเพื่อเตือนว่ารอบถัดไปควรใช้ `--out` / `--comparison-out` แยกตาม mode เช่น `reports/structured-output/smoke/openai-compatible-responses-parse-eval.json` (source: docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md)

### Smoke Split

- เพิ่ม smoke split ใหม่ที่ `data/splits/smoke-output-contract.jsonl` เพื่อใช้ debug output contract แบบ deterministic แทน path เดิมที่ไม่ชัดใน repo (source: data/splits/smoke-output-contract.jsonl)
- smoke split นี้มี 5 records และครอบคลุมทั้ง 5 labels ของ POC เพื่อให้เช็กได้ครบว่าทั้ง normal และ suspicious classes ยังอยู่ใน contract เดียวกัน (source: data/splits/smoke-output-contract.jsonl)

### Training And UI Alignment

- training config ขยับ prompt version เป็น `triage-json-v2` เพื่อไม่ให้ train path อ้าง prompt version เก่า (source: ml/unsloth/config.example.yaml)
- frontend prompt mirror ถูกแก้ตาม prompt ฝั่ง Python เพื่อไม่ให้ UI path กับ evaluator/training path drift จากกัน (source: frontend/lib/prompts.ts)

## Decisions

| Decision | Rationale | Impact |
| --- | --- | --- |
| แก้ runtime contract ก่อน retrain | ถ้า output ยัง parse/schema-valid ไม่ได้ การ retrain จะทำให้แยก semantic error ออกจาก contract error ยาก | phase นี้เน้น prompt, adapter, schema path, smoke split ก่อน |
| ใช้ `json_schema` ก่อน `json_object` | ต้องพยายามบังคับ shape และ required fields ให้ใกล้ schema หลักที่สุด ไม่ใช่แค่ให้เป็น valid JSON | adapter default ไปที่ strict structured output path ก่อน |
| เก็บ canonical schema ไว้สำหรับ evaluator | schema ของ repo เป็น contract กลางร่วมกันของ dataset, evaluator, API และ UI | ห้ามลดความเข้มของ evaluator เพื่อเอาใจ runtime provider |
| sanitize schema ใน adapter layer | provider/runtime อาจรับ JSON schema ได้ไม่เท่ากับ canonical schema ของ repo | ลดความเสี่ยงที่ strict mode จะพังเพราะ keyword subset ต่างกัน |
| fallback แบบจำกัด ไม่ fallback ทุก error | ถ้า fallback กว้างเกินไป จะซ่อน bug จริงใน adapter หรือ endpoint | adapter จะ fallback เฉพาะ error แนว unsupported feature/schema/runtime |
| สร้าง deterministic smoke split แยกจาก fixed test split | ต้องมีชุด debug เล็กที่รันไวและ reproducible ก่อนวิ่ง fixed comparison 75 samples | smoke path ชัดเจนขึ้นและไม่ปนกับ comparison artifact หลัก |
| ยังไม่ผ่อน evaluator strictness | evaluator เป็นตัวที่จับปัญหา production-facing ได้จริง | prose+JSON ยังถือว่า fail ใน report หลักต่อไป |
| ใช้ Responses parse เป็น runtime path หลักของ adapter รอบถัดไป | `sample-000137` ผ่านทั้ง JSON parse และ schema ด้วย `openai_parsed` ส่วน `sample-000474` fail แบบ schema validation ที่ชี้ field ขาดชัดเจน | smoke รอบถัดไปควรรัน evaluator ผ่าน `OPENAI_COMPATIBLE_RESPONSE_FORMAT=responses_parse` เพื่อแยก schema validation failure ออกจาก markdown-fence parse failure |

## What We Did Not Change

- ยังไม่ retrain model ในรอบนี้ เพราะเป้าหมายคือดูให้ชัดก่อนว่า output contract problem จบได้ที่ runtime layer แค่ไหน (source: docs/Day6.md)
- ยังไม่เปลี่ยน canonical output schema ของ repo เพราะ schema หลักยังใช้ได้กับ evaluator และ dataset เดิม (source: data/schemas/triage-output.schema.json)
- ยังไม่แก้ evaluator ให้ parse prose+JSON แบบหลวม เพราะจะทำให้ report มองโลกดีกว่าความจริง (source: scripts/evaluate.py, source: docs/Day6.md)
- ยังไม่อัปเดตรายงาน model-output `v1` ให้ดูเหมือน run ใหม่ เพราะหน้านั้นเป็น historical artifact ของ failure state เดิม ไม่ใช่ผลหลัง hardening รอบนี้ (source: docs/model-output/v1-lfm2-350m-security-triage.md)

## Validation Done

- ตรวจ syntax ของไฟล์ Python ที่แก้ด้วย `python3 -m py_compile` สำหรับ prompt contract, adapter, evaluator, direct probe และ training formatter
- ตรวจว่า `ml/unsloth/training_format.py` render smoke split ใหม่ได้ภายใต้ prompt `triage-json-v2`
- ตรวจว่า provider schema หลัง sanitize ไม่มี keyword อย่าง `minLength` หลุดไปใน request schema
- ตรวจ `git diff --check` เพื่อกัน whitespace/syntax issue ใน patch ชุดนี้
- ตรวจ adapter path ใหม่ด้วย `.venv` แล้ว: `responses_parse` normalize base URL จาก `/v1/chat/completions` กลับเป็น `/v1`, fallback model เป็น `current` เมื่อไม่ได้ส่ง model และ Pydantic validation จับ field ขาดเป็น `ValidationError` ได้ (source: scripts/model_adapters/openai_compatible.py)
- รัน heuristic smoke split แล้วยังได้ `json_parse_success_rate=1.0`, `schema_success_rate=1.0`, `invalid_output_count=0` จึงไม่กระทบ baseline/evaluator path (source: scripts/evaluate.py, data/splits/smoke-output-contract.jsonl)

หมายเหตุ: มีการลอง live endpoint smoke ด้วย `OPENAI_COMPATIBLE_RESPONSE_FORMAT=responses_parse` และ `OPENAI_COMPATIBLE_MODEL=current` แบบ `--no-write` แล้ว แต่ server ตอบ `No model loaded. Call POST /inference/load first.` ทุก sample ดังนั้นตัวเลข 0/5 จากรอบนั้นเป็น runtime serve-state issue ไม่ใช่ผลวัด model quality หรือ schema path ใหม่ (source: scripts/model_adapters/openai_compatible.py, user-run validation, 2026-05-19)

## Next Step

1. รัน smoke evaluation ใหม่กับ `data/splits/smoke-output-contract.jsonl` โดยใช้ `OPENAI_COMPATIBLE_RESPONSE_FORMAT=responses_parse` และ `OPENAI_COMPATIBLE_MODEL=current`
2. ดู 3 ค่าแรกก่อน: `json_parse_success_rate`, `schema_success_rate`, `invalid_output_count`
3. ถ้า output ที่ fail กลายเป็น Pydantic validation error ที่ field ชัดเจน แปลว่า runtime path ดีขึ้นแล้ว เหลือ field completeness/model quality
4. ถ้า `json_parse_success_rate` และ `schema_success_rate` ฟื้นเป็น `1.0` ค่อยแยกดู semantic drift ต่อ เช่น `sample-000474` ที่ model มอง port scan เป็น normal
5. ถ้า contract ผ่านแต่ label/evidence/reason ยัง drift ค่อย re-render training text ด้วย prompt `v2` แล้วค่อย retrain หรือเปลี่ยน model candidate หลัก

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-19 | Codex | Created a dedicated output-contract hardening note for prompt v2, structured adapter modes, schema sanitization, and smoke split flow | `docs/output-contract-hardening.md` | Done |
| 2026-05-19 | Codex | Added direct structured-output probe and evaluator `is_suspicious_accuracy` coverage to the hardening workflow | `scripts/probe_openai_structured_output.py`, `scripts/evaluate.py`, `docs/output-contract-hardening.md` | Done |
| 2026-05-19 | Codex | Added `guided_json` as a forced adapter/probe mode after `json_schema` and `structured_outputs` were observed to be ignored by the endpoint | `scripts/model_adapters/openai_compatible.py`, `scripts/probe_openai_structured_output.py`, `.env.example`, `docs/output-contract-hardening.md` | Done |
| 2026-05-19 | Codex | Switched the direct structured-output probe from raw HTTP to the OpenAI Python client pattern used in `data/raw/test.py` | `scripts/probe_openai_structured_output.py`, `requirements.txt`, `docs/output-contract-hardening.md` | Done |
| 2026-05-19 | Codex | Added `responses_parse` probe mode using the same `client.responses.parse(..., text_format=...)` path as `data/raw/test.py` | `scripts/probe_openai_structured_output.py`, `requirements.txt`, `docs/output-contract-hardening.md` | Done |
| 2026-05-19 | Codex | Changed `responses_parse` probe default model to `current` and renamed printed model field to `requested_model` to separate request alias from response model | `scripts/probe_openai_structured_output.py`, `docs/output-contract-hardening.md` | Done |
| 2026-05-19 | Codex | Recorded latest probe learning: `responses_parse` passes schema on `sample-000137`, while `sample-000474` still fails field completeness/semantic classification | `docs/output-contract-hardening.md` | Done |
| 2026-05-19 | Codex | Promoted OpenAI Responses parse from probe-only path into the OpenAI-compatible adapter with lazy Pydantic validation and OpenAI SDK chat fallback modes | `scripts/model_adapters/openai_compatible.py`, `.env.example`, `requirements.txt`, `docs/output-contract-hardening.md` | Done |
| 2026-05-19 | Codex | Recorded the latest `responses_parse` smoke run and linked it to a new v2 model-output page | `docs/output-contract-hardening.md`, `docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md` | Done |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-19 | แยก output-contract hardening เป็นหน้าของตัวเอง | เรื่องนี้กระทบ prompt, adapter, schema, smoke split และ retrain decision พร้อมกัน จึงไม่ควรฝังเป็นแค่ note สั้นใน Day4/Day6 | ทีมสามารถย้อนดูเหตุผลของ phase นี้ได้จากหน้าเดียว |
| 2026-05-19 | ใช้หน้านี้เป็น handoff note ก่อน live smoke rerun | โค้ดแก้แล้ว แต่ยังไม่ได้ยิง endpoint รอบใหม่ใน turn เดียวกัน | คนที่มารัน smoke/eval ต่อจะเห็นทันทีว่าต้องดูอะไรและอะไรยังไม่ควรถูกตีความเกินจริง |
| 2026-05-19 | ดัน Responses parse เป็น runtime candidate ถัดไป | probe แสดงว่า `responses_parse` validate เป็น Pydantic object ได้จริงใน `sample-000137` และให้ error ชัดเมื่อ `recommended_action` ขาดใน `sample-000474` | งานถัดไปควรทำ adapter/evaluator path สำหรับ Responses parse ก่อนรัน fixed split |
| 2026-05-19 | ใช้ OpenAI SDK + Pydantic เป็น adapter runtime หลักแทน LangChain parser | endpoint ทดลองผ่าน `client.responses.parse(..., text_format=...)` ได้จริง และ failure ที่ได้เป็น schema validation ตรงกว่า markdown/prose parsing failure | evaluator จะรับ dict ที่ผ่าน Pydantic แล้วใน path สำเร็จ และจะเห็น adapter error ชัดเมื่อ model ยังตอบ field ไม่ครบ |
| 2026-05-19 | ยังไม่เลื่อน v2 ไป fixed split หลัง `responses_parse` smoke | smoke ยังผ่าน JSON/schema เพียง 1/5 และ invalid output ยังเป็น 4/5 | งานถัดไปต้องแก้ generation/output habit หรือหา runtime constrained decoding ก่อน |

## Related pages

- [[Day4]]
- [[Day6]]
- [[fine-tuning-notes]]
- [[model-output/v1-lfm2-350m-security-triage]]
- [[triage-output-schema]]

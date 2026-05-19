# Output Contract Hardening

**Summary**

หน้านี้สรุปรอบแก้ปัญหา output contract ของ fine-tuned/OpenAI-compatible path ว่าทำอะไรไปแล้ว ตัดสินใจอะไรไป และตั้งใจแยกปัญหา `output shape` ออกจาก `model quality` อย่างไร ก่อนตัดสินใจ retrain รอบถัดไป

**Sources**

- `AGENTS.md` สำหรับ output schema กลาง, implementation priority และหลักการไม่ overclaim (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ POC scope และเกณฑ์ evaluation ที่ต้องแยก JSON/schema validity ออกจาก accuracy (source: docs/poc-plan.md)
- `docs/Day4.md` สำหรับ adapter/prompt contract path และ env contract ของ OpenAI-compatible runtime (source: docs/Day4.md)
- `docs/Day6.md` สำหรับสถานะ fine-tuned smoke evaluation และ decision ว่ายังไม่ retrain ทันที (source: docs/Day6.md)
- `scripts/evaluate.py` สำหรับ strict JSON parsing และ schema validation ที่ยังคงเป็น evaluator contract หลัก (source: scripts/evaluate.py)
- `scripts/model_adapters/prompt_contract.py` สำหรับ prompt `triage-json-v2` ฝั่ง Python (source: scripts/model_adapters/prompt_contract.py)
- `scripts/model_adapters/openai_compatible.py` สำหรับ structured output modes, schema sanitizer และ fallback logic (source: scripts/model_adapters/openai_compatible.py)
- `frontend/lib/prompts.ts` สำหรับ prompt mirror ฝั่ง frontend (source: frontend/lib/prompts.ts)
- `data/schemas/triage-output.schema.json` สำหรับ canonical triage output schema ของ repo (source: data/schemas/triage-output.schema.json)
- `data/splits/smoke-output-contract.jsonl` สำหรับ deterministic 5-sample smoke split ใหม่ (source: data/splits/smoke-output-contract.jsonl)
- `.env.example` สำหรับ env flags ใหม่ของ adapter (source: .env.example)
- `ml/unsloth/config.example.yaml` สำหรับ prompt version ที่ training path อ้างอิง (source: ml/unsloth/config.example.yaml)
- `docs/model-output/v1-lfm2-350m-security-triage.md` สำหรับ historical artifact ของ failure state ก่อนรอบ hardening นี้ (source: docs/model-output/v1-lfm2-350m-security-triage.md)
- `reports/openai-finetune-eval.md` สำหรับ historical failure state ของ smoke evaluation รอบก่อนแก้ contract (source: reports/openai-finetune-eval.md)

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
- ตั้ง default path ใหม่เป็น `json_schema` ไม่ใช่ plain chat completion เพื่อพยายามบังคับ output shape ตั้งแต่ชั้น provider/runtime (source: scripts/model_adapters/openai_compatible.py)
- adapter จะพยายาม request mode ตามลำดับ `json_schema_strict` -> `structured_outputs_json` -> `json_object` เมื่อเปิด `json_schema` mode และ fallback เฉพาะ error ที่มีลักษณะว่า runtime หรือ schema feature ไม่รองรับ (source: scripts/model_adapters/openai_compatible.py)
- adapter metadata จะบันทึกทั้ง mode ที่ request และ mode ที่ใช้จริง เพื่อให้อ่าน report ย้อนหลังได้ว่า run นั้นใช้ path ไหน (source: scripts/model_adapters/openai_compatible.py)

### Provider Schema Sanitizer

- canonical schema ของ repo ยังอยู่ที่ `data/schemas/triage-output.schema.json` และยังใช้เป็น source of truth สำหรับ evaluator (source: data/schemas/triage-output.schema.json, source: scripts/evaluate.py)
- เพิ่ม adapter layer ที่โหลด schema เดิมแล้ว sanitize ให้เหลือ provider-compatible subset ก่อนส่งเข้า runtime แทนการแก้ canonical schema ตรง ๆ (source: scripts/model_adapters/openai_compatible.py)
- sanitizer เก็บเฉพาะ keyword ที่ใช้บังคับ shape จริง เช่น `type`, `properties`, `required`, `additionalProperties`, `items`, `enum`, `description` และตัด metadata/constraints อื่นออกจาก request schema (source: scripts/model_adapters/openai_compatible.py)

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

## What We Did Not Change

- ยังไม่ retrain model ในรอบนี้ เพราะเป้าหมายคือดูให้ชัดก่อนว่า output contract problem จบได้ที่ runtime layer แค่ไหน (source: docs/Day6.md)
- ยังไม่เปลี่ยน canonical output schema ของ repo เพราะ schema หลักยังใช้ได้กับ evaluator และ dataset เดิม (source: data/schemas/triage-output.schema.json)
- ยังไม่แก้ evaluator ให้ parse prose+JSON แบบหลวม เพราะจะทำให้ report มองโลกดีกว่าความจริง (source: scripts/evaluate.py, source: docs/Day6.md)
- ยังไม่อัปเดตรายงาน model-output `v1` ให้ดูเหมือน run ใหม่ เพราะหน้านั้นเป็น historical artifact ของ failure state เดิม ไม่ใช่ผลหลัง hardening รอบนี้ (source: docs/model-output/v1-lfm2-350m-security-triage.md)

## Validation Done

- ตรวจ syntax ของไฟล์ Python ที่แก้ด้วย `python3 -m py_compile` สำหรับ prompt contract, adapter, และ training formatter
- ตรวจว่า `ml/unsloth/training_format.py` render smoke split ใหม่ได้ภายใต้ prompt `triage-json-v2`
- ตรวจว่า provider schema หลัง sanitize ไม่มี keyword อย่าง `minLength` หลุดไปใน request schema
- ตรวจ `git diff --check` เพื่อกัน whitespace/syntax issue ใน patch ชุดนี้

หมายเหตุ: รอบนี้ยังไม่ได้รัน live endpoint evaluation ใหม่ เพราะ environment ที่ใช้แก้โค้ดยังไม่มี `langchain_openai` และ endpoint พร้อมให้ยิง smoke run จริงใน turn เดียวกัน

## Next Step

1. รัน smoke evaluation ใหม่กับ `data/splits/smoke-output-contract.jsonl`
2. ตรวจจาก report ว่า mode ที่ใช้จริงคือ `json_schema_strict`, `structured_outputs_json`, หรือ `json_object`
3. ถ้า `json_parse_success_rate` และ `schema_success_rate` ฟื้นเป็น `1.0` ค่อยแยกดู semantic drift ต่อ
4. ถ้า contract ผ่านแต่ label/evidence/reason ยัง drift ค่อย re-render training text ด้วย prompt `v2` แล้วค่อย retrain

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-19 | Codex | Created a dedicated output-contract hardening note for prompt v2, structured adapter modes, schema sanitization, and smoke split flow | `docs/output-contract-hardening.md` | Done |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-19 | แยก output-contract hardening เป็นหน้าของตัวเอง | เรื่องนี้กระทบ prompt, adapter, schema, smoke split และ retrain decision พร้อมกัน จึงไม่ควรฝังเป็นแค่ note สั้นใน Day4/Day6 | ทีมสามารถย้อนดูเหตุผลของ phase นี้ได้จากหน้าเดียว |
| 2026-05-19 | ใช้หน้านี้เป็น handoff note ก่อน live smoke rerun | โค้ดแก้แล้ว แต่ยังไม่ได้ยิง endpoint รอบใหม่ใน turn เดียวกัน | คนที่มารัน smoke/eval ต่อจะเห็นทันทีว่าต้องดูอะไรและอะไรยังไม่ควรถูกตีความเกินจริง |

## Related pages

- [[Day4]]
- [[Day6]]
- [[fine-tuning-notes]]
- [[model-output/v1-lfm2-350m-security-triage]]
- [[triage-output-schema]]

# Day 4: Model Adapters And Prompt Contract

**Summary**

วันที่สี่เพิ่ม adapter สำหรับ base model ที่ยังไม่ fine-tune เช่น OpenAI-compatible endpoint, Ollama หรือ LM Studio พร้อม prompt contract ที่บังคับให้ตอบ JSON ตาม schema เดิม เป้าหมายคือเทียบ heuristic baseline กับ model baseline ได้จริง

**Sources**

- `docs/poc-plan.md` สำหรับ model baseline adapter และ prompt/schema requirement (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ expected output schema และ implementation priority (source: AGENTS.md)
- `docs/References.md` สำหรับแนวคิด adapter separation จาก lm-evaluation-harness และ dataset formatting จาก TRL (source: docs/References.md)
- `scripts/model_adapters/prompt_contract.py` สำหรับ Python prompt contract และ CLI สำหรับพิมพ์ system/user prompt (source: scripts/model_adapters/prompt_contract.py)
- LangChain `ChatOpenAI` documentation สำหรับการเรียก OpenAI-compatible chat model ผ่าน `langchain-openai` (source: https://docs.langchain.com/oss/python/integrations/chat/openai/)
- `llm-wiki/SKILL.md` สำหรับ page shape และ decision log (source: SKILL.md)

**Last updated**

2026-05-19

## Goal

มี adapter interface เดียวที่เรียก model ได้หลายแบบ และ evaluator ใช้งานได้โดยไม่ต้องรู้ว่าเบื้องหลังคือ service ไหน

## Scope

- เขียน `frontend/lib/prompts.ts`
- เขียน Python adapter interface กลาง
- เขียน Python model adapter สำหรับ OpenAI-compatible endpoint
- เขียน Python model adapter สำหรับ fine-tuned model ที่ expose ผ่าน OpenAI-compatible endpoint
- เขียน Python model adapter สำหรับ Ollama หรือ LM Studio
- ให้ frontend เรียกผลผ่าน API/endpoint หรือ wrapper ภายหลัง แทนการเป็น evaluation path หลัก
- เพิ่ม JSON parse และ schema validation path
- เพิ่ม `.env.example` เฉพาะค่าที่ไม่ใช่ secret จริง
- รัน model baseline evaluation เมื่อมี endpoint พร้อม

## Checklist

- [x] define `TriageModelAdapter`
- [x] เพิ่ม system prompt สำหรับตอบ JSON เท่านั้น
- [x] เพิ่ม OpenAI-compatible adapter
- [x] เพิ่ม FineTuneAdapter สำหรับ fine-tuned OpenAI-compatible endpoint
- [x] เพิ่ม timeout และ latency measurement
- [x] เพิ่ม JSON parsing guard
- [x] เพิ่ม schema validation guard
- [x] เพิ่ม error reporting ที่ evaluator อ่านได้
- [x] เพิ่ม progress 0-100% ระหว่างรัน evaluator
- [x] เขียน notes ว่าต้องตั้งค่า endpoint อย่างไร

## Acceptance Criteria

- evaluator สลับ adapter ได้จาก command option หรือ config
- adapter ทุกตัวคืน structured result หรือ structured error
- ไม่มี API key ถูก hard-code
- ถ้า model ตอบ malformed JSON ต้องถูกนับเป็น failure
- report แยก heuristic baseline กับ model baseline ได้

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 4 plan page | `docs/Day4.md` | Planned |
| 2026-05-16 | Codex | Aligned model adapter plan with Python-first evaluation workflow | `scripts/`, `frontend/lib/prompts.ts` | Planned |
| 2026-05-17 | Codex | Added shared triage prompt contract for JSON-only model output | `frontend/lib/prompts.ts` | Done |
| 2026-05-17 | Codex | Added Python adapter interface for future model adapters | `scripts/model_adapters/base.py`, `scripts/model_adapters/__init__.py` | Done |
| 2026-05-17 | Codex | Added LangChain OpenAI-compatible and fine-tuned model adapters | `scripts/model_adapters/openai_compatible.py`, `.env.example`, `requirements.txt` | Done |
| 2026-05-17 | Codex | Connected evaluator to adapter interface and adapter-specific report defaults | `scripts/evaluate.py` | Done |
| 2026-05-17 | Codex | Added 0-100% progress output while evaluator runs each sample | `scripts/evaluate.py` | Done |
| 2026-05-18 | Codex | Added a CLI path to print the Python prompt contract for inspection and reuse | `scripts/model_adapters/prompt_contract.py` | Done |
| 2026-05-19 | Codex | Hardened the prompt contract and OpenAI-compatible adapters for structured JSON output | `scripts/model_adapters/prompt_contract.py`, `scripts/model_adapters/openai_compatible.py`, `frontend/lib/prompts.ts`, `.env.example` | Done |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ adapter interface เดียว | evaluator และ UI ไม่ควรผูกกับ provider | เปลี่ยน model ได้โดยไม่แก้ evaluation logic |
| 2026-05-16 | วัด JSON validity แยกจาก accuracy | model อาจทายถูกแต่ output ใช้งานต่อไม่ได้ | report จะเห็นคุณภาพด้าน format ชัดขึ้น |
| 2026-05-16 | ให้ Python adapter เป็น path หลักของ model baseline | evaluator หลักอยู่ฝั่ง Python จึงควรเรียก provider จาก workflow เดียวกัน | frontend adapter เป็น presentation/integration layer หลัง evaluation path นิ่งแล้ว |
| 2026-05-17 | prompt contract ต้องบังคับ JSON-only และห้าม overclaim | model baseline ต้องถูก parse และ validate ได้เหมือน heuristic baseline | adapter รอบถัดไปจะใช้ prompt เดียวกันก่อนส่ง log เข้า model |
| 2026-05-17 | adapter interface คืน `AdapterResult` กลาง | evaluator ต้องเห็น raw output, latency และ error ในรูปแบบเดียวกันทุก provider | adapter จริงรอบถัดไปจะ implement `TriageModelAdapter.analyze()` |
| 2026-05-17 | แยก `OpenAICompatibleAdapter` กับ `FineTuneAdapter` | base model และ fine-tuned model อาจใช้ OpenAI-compatible API เหมือนกัน แต่ต้องมี env, report identity และ run path แยกกัน | config แยกเป็น `OPENAI_COMPATIBLE_*` และ `OPENAI_FINETUNE_*` โดยใช้ implementation LangChain เดียวกัน |
| 2026-05-17 | evaluator สร้าง adapter instance ก่อนเริ่ม run | heuristic, base model และ fine-tuned model ต้องผ่าน evaluation path เดียวกัน | `scripts/evaluate.py --adapter` รองรับ `heuristic`, `openai-compatible` และ `openai-finetune` |
| 2026-05-17 | progress ของ evaluator แสดงทาง `stderr` | ต้องให้ผู้ใช้เห็นสถานะระหว่างรัน model endpoint ที่ช้า โดยไม่ปนกับ summary หลักใน `stdout` | เพิ่ม progress bar 0-100% และมี `--no-progress` สำหรับรันแบบเงียบ |
| 2026-05-18 | พิมพ์ prompt contract จาก source เดียวกับ adapter | ลดโอกาสที่ prompt ในเอกสารหรือ notebook จะ drift จาก `TRIAGE_SYSTEM_PROMPT` จริง | ใช้ `scripts/model_adapters/prompt_contract.py` เป็น CLI สำหรับ inspect system prompt, prompt version และ user prompt |
| 2026-05-19 | ใช้ structured-output adapter layer ก่อน retrain | ปัญหาหลักล่าสุดคือ model หลุด output contract ตั้งแต่ก่อนวัด accuracy ถ้าไม่แก้ runtime contract ก่อนจะวิเคราะห์คุณภาพ model ได้ไม่ชัด | adapter ใช้ `response_format=json_schema` แบบ strict ก่อน แล้ว fallback แบบจำกัดไป `structured_outputs` หรือ `json_object` เมื่อ endpoint ไม่รองรับ |

## Notes

วันที่สี่ต้องระวังอย่าให้ prompt กลายเป็น logic หลักทั้งหมด Logic ที่ควรอยู่ใน code เช่น schema validation, retry limit และ error reporting ควรอยู่ใน adapter หรือ evaluator เพื่อให้ผลวัดซ้ำได้

### Endpoint Environment

ใช้ `.env.example` เป็น template เท่านั้น ห้ามใส่ secret จริงลง git

`OpenAICompatibleAdapter` ใช้ env ชุดนี้:

```text
OPENAI_COMPATIBLE_BASE_URL
OPENAI_COMPATIBLE_API_KEY
OPENAI_COMPATIBLE_MODEL
OPENAI_COMPATIBLE_TIMEOUT_SECONDS
OPENAI_COMPATIBLE_MAX_RETRIES
OPENAI_COMPATIBLE_RESPONSE_FORMAT
OPENAI_COMPATIBLE_SCHEMA_PATH
```

`FineTuneAdapter` ใช้ env ชุดนี้:

```text
OPENAI_FINETUNE_BASE_URL
OPENAI_FINETUNE_API_KEY
OPENAI_FINETUNE_MODEL
OPENAI_FINETUNE_TIMEOUT_SECONDS
OPENAI_FINETUNE_MAX_RETRIES
OPENAI_FINETUNE_RESPONSE_FORMAT
OPENAI_FINETUNE_SCHEMA_PATH
```

ทั้งสอง adapter ใช้ `langchain-openai` และ prompt contract เดียวกัน ต่างกันที่ env prefix และชื่อ adapter เพื่อให้ report แยก base model กับ fine-tuned model ได้ชัด

`*_RESPONSE_FORMAT` รองรับ `json_schema`, `json_object`, หรือ `off` โดย default path ใหม่คือ `json_schema` เพื่อบังคับ output shape ให้ใกล้ schema หลักที่สุด ส่วน `*_SCHEMA_PATH` ชี้ไป schema canonical ของ repo ที่ `data/schemas/triage-output.schema.json` แล้ว adapter จะ sanitize ให้เป็น provider-compatible subset ก่อนส่งเข้า runtime (source: scripts/model_adapters/openai_compatible.py, data/schemas/triage-output.schema.json)

### Evaluation Progress

`scripts/evaluate.py` จะแสดง progress 0-100% ตามจำนวน record ใน split ที่กำลัง evaluate อยู่ โดยพิมพ์ออก `stderr` เพื่อให้ summary และ report path ใน `stdout` ยังอ่านง่าย ถ้าต้องการรันเงียบใน automation ให้เพิ่ม `--no-progress`

### Prompt Contract CLI

ใช้ `scripts/model_adapters/prompt_contract.py` เป็น source เดียวสำหรับ prompt ที่ Python adapters, Unsloth training format และ inference path ใช้ร่วมกัน เมื่ออยาก inspect หรือ copy prompt ไปเทียบกับ notebook/endpoint ให้พิมพ์จาก script นี้แทนการคัดลอกจากเอกสาร (source: scripts/model_adapters/prompt_contract.py, ml/unsloth/training_format.py, ml/unsloth/inference.py)

Prompt version ปัจจุบันคือ `triage-json-v2` ซึ่งตัด schema example ออกจาก prompt, ย้ำว่าคำตอบต้องเริ่มด้วย `{` และจบด้วย `}`, และเพิ่ม `Respond with the JSON object only.` ใน user prompt เพื่อกด prose wrapper ก่อน JSON (source: scripts/model_adapters/prompt_contract.py, frontend/lib/prompts.ts)

พิมพ์ system prompt:

```bash
python3 scripts/model_adapters/prompt_contract.py
```

พิมพ์ prompt version:

```bash
python3 scripts/model_adapters/prompt_contract.py --kind version
```

พิมพ์ user prompt สำหรับ log หนึ่งบรรทัด:

```bash
python3 scripts/model_adapters/prompt_contract.py --kind user --log-line '127.0.0.1 - - [10/May/2026] "GET /login HTTP/1.1" 200'
```

## Related pages

- [[Day3]]
- [[Day5]]
- [[poc-plan]]
- [[References]]

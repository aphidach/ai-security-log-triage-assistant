# Day 4: Model Adapters And Prompt Contract

**Summary**

วันที่สี่เพิ่ม adapter สำหรับ base model ที่ยังไม่ fine-tune เช่น OpenAI-compatible endpoint, Ollama หรือ LM Studio พร้อม prompt contract ที่บังคับให้ตอบ JSON ตาม schema เดิม เป้าหมายคือเทียบ heuristic baseline กับ model baseline ได้จริง

**Sources**

- `docs/poc-plan.md` สำหรับ model baseline adapter และ prompt/schema requirement (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ expected output schema และ implementation priority (source: AGENTS.md)
- `docs/References.md` สำหรับแนวคิด adapter separation จาก lm-evaluation-harness และ dataset formatting จาก TRL (source: docs/References.md)
- LangChain `ChatOpenAI` documentation สำหรับการเรียก OpenAI-compatible chat model ผ่าน `langchain-openai` (source: https://docs.langchain.com/oss/python/integrations/chat/openai/)
- `llm-wiki/SKILL.md` สำหรับ page shape และ decision log (source: SKILL.md)

**Last updated**

2026-05-17

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
```

`FineTuneAdapter` ใช้ env ชุดนี้:

```text
OPENAI_FINETUNE_BASE_URL
OPENAI_FINETUNE_API_KEY
OPENAI_FINETUNE_MODEL
OPENAI_FINETUNE_TIMEOUT_SECONDS
OPENAI_FINETUNE_MAX_RETRIES
```

ทั้งสอง adapter ใช้ `langchain-openai` และ prompt contract เดียวกัน ต่างกันที่ env prefix และชื่อ adapter เพื่อให้ report แยก base model กับ fine-tuned model ได้ชัด

### Evaluation Progress

`scripts/evaluate.py` จะแสดง progress 0-100% ตามจำนวน record ใน split ที่กำลัง evaluate อยู่ โดยพิมพ์ออก `stderr` เพื่อให้ summary และ report path ใน `stdout` ยังอ่านง่าย ถ้าต้องการรันเงียบใน automation ให้เพิ่ม `--no-progress`

## Related pages

- [[Day3]]
- [[Day5]]
- [[poc-plan]]
- [[References]]

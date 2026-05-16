# Day 4: Model Adapters And Prompt Contract

**Summary**

วันที่สี่เพิ่ม adapter สำหรับ base model ที่ยังไม่ fine-tune เช่น OpenAI-compatible endpoint, Ollama หรือ LM Studio พร้อม prompt contract ที่บังคับให้ตอบ JSON ตาม schema เดิม เป้าหมายคือเทียบ heuristic baseline กับ model baseline ได้จริง

**Sources**

- `docs/poc-plan.md` สำหรับ model baseline adapter และ prompt/schema requirement (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ expected output schema และ implementation priority (source: AGENTS.md)
- `References.md` สำหรับแนวคิด adapter separation จาก lm-evaluation-harness และ dataset formatting จาก TRL (source: References.md)
- `llm-wiki/SKILL.md` สำหรับ page shape และ decision log (source: SKILL.md)

**Last updated**

2026-05-16

## Goal

มี adapter interface เดียวที่เรียก model ได้หลายแบบ และ evaluator ใช้งานได้โดยไม่ต้องรู้ว่าเบื้องหลังคือ service ไหน

## Scope

- เขียน `src/lib/prompts.ts`
- เขียน adapter interface กลาง
- เขียน `src/lib/model-adapters/openai-compatible.ts`
- เขียน `src/lib/model-adapters/local-ollama.ts`
- เพิ่ม JSON parse และ schema validation path
- เพิ่ม `.env.example` เฉพาะค่าที่ไม่ใช่ secret จริง
- รัน model baseline evaluation เมื่อมี endpoint พร้อม

## Checklist

- [ ] define `TriageModelAdapter`
- [ ] เพิ่ม system prompt สำหรับตอบ JSON เท่านั้น
- [ ] เพิ่ม OpenAI-compatible adapter
- [ ] เพิ่ม Ollama หรือ LM Studio adapter
- [ ] เพิ่ม timeout และ latency measurement
- [ ] เพิ่ม JSON parsing guard
- [ ] เพิ่ม schema validation guard
- [ ] เพิ่ม error reporting ที่ evaluator อ่านได้
- [ ] เขียน notes ว่าต้องตั้งค่า endpoint อย่างไร

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

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ adapter interface เดียว | evaluator และ UI ไม่ควรผูกกับ provider | เปลี่ยน model ได้โดยไม่แก้ evaluation logic |
| 2026-05-16 | วัด JSON validity แยกจาก accuracy | model อาจทายถูกแต่ output ใช้งานต่อไม่ได้ | report จะเห็นคุณภาพด้าน format ชัดขึ้น |

## Notes

วันที่สี่ต้องระวังอย่าให้ prompt กลายเป็น logic หลักทั้งหมด Logic ที่ควรอยู่ใน code เช่น schema validation, retry limit และ error reporting ควรอยู่ใน adapter หรือ evaluator เพื่อให้ผลวัดซ้ำได้

## Related pages

- [[Day3]]
- [[Day5]]
- [[poc-plan]]
- [[References]]


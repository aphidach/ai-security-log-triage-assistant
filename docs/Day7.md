# Day 7: Demo UI, README, And Handoff

**Summary**

วันที่เจ็ดทำ demo ให้คนอื่นลองได้และจัดเอกสารส่งมอบให้ครบ เป้าหมายคือมี UI หรือ CLI ที่เล่า POC ได้ภายในไม่กี่นาที พร้อม README, report และ demo script ที่ไม่พูดเกินกว่าผล evaluation

**Sources**

- `docs/poc-plan.md` สำหรับ demo plan, definition of done และ timeline (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ UI guidance และ security/privacy rules (source: AGENTS.md)
- `References.md` สำหรับ reference mapping ที่ใช้เล่า rationale ของ repo (source: References.md)
- `llm-wiki/SKILL.md` สำหรับ page shape, related pages และ append-only log (source: SKILL.md)

**Last updated**

2026-05-16

## Goal

ทำให้ POC พร้อม demo: paste log, analyze, เห็น evidence, เห็น structured result และดู comparison baseline vs fine-tuned ได้

## Scope

- ทำหน้า UI หลักสำหรับ paste log
- เพิ่ม sample log picker
- เพิ่ม analyzer selector
- แสดง structured result
- highlight evidence ใน log
- แสดง comparison metric
- update README ให้ครบ setup, dataset, evaluate, train, demo
- เขียน demo script สั้นสำหรับอัดวิดีโอ 2-3 นาที

## Checklist

- [ ] สร้างหน้า analyze log
- [ ] เพิ่ม sample logs ครบ 5 labels
- [ ] เพิ่ม selector สำหรับ heuristic, base model, fine-tuned model
- [ ] แสดง label, severity, evidence, reason, recommended action
- [ ] แสดง raw JSON output
- [ ] เพิ่ม comparison panel
- [ ] update README
- [ ] เพิ่ม demo script
- [ ] run lint/typecheck/build
- [ ] ตรวจว่า UI ไม่ fake fine-tuned result ถ้ายังไม่ได้ configure model

## Acceptance Criteria

- dev server รันได้
- sample log วิเคราะห์ได้อย่างน้อยด้วย heuristic baseline
- UI แสดงสถานะชัดเจนถ้า model adapter ยังไม่ได้ configure
- README อธิบาย workflow ทั้งหมดตั้งแต่ dataset ถึง evaluation
- demo script เล่าได้ว่า POC นี้วัดผลอย่างไร ไม่ใช่แค่โชว์ AI ตอบ log

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 7 plan page | `docs/Day7.md` | Planned |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | demo เป็น tool ไม่ใช่ landing page | stakeholder ต้องเห็น workflow วิเคราะห์ log จริง | UI โฟกัสที่ paste log, result และ comparison |
| 2026-05-16 | ไม่ fake fine-tuned result | ความน่าเชื่อถือของ POC อยู่ที่การวัดผลจริง | UI ต้องแสดง unconfigured state เมื่อยังไม่มี model |

## Notes

วันสุดท้ายต้องทำให้เรื่องเล่าง่าย: เราสร้าง dataset, วัด baseline, fine-tune small model, evaluate ด้วย test split เดียวกัน แล้วโชว์ผลผ่าน demo ที่ตรวจ evidence ได้

## Related pages

- [[Day6]]
- [[poc-plan]]
- [[References]]


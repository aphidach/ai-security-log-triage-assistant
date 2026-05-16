# Day 6: Fine-Tuned Evaluation And Comparison Report

**Summary**

วันที่หกเอา fine-tuned model หรือ adapter ที่ได้มาวัดกับ fixed test split เดียวกับ baseline แล้วเขียน comparison report แบบตรงไปตรงมา เป้าหมายคืออธิบายให้ได้ว่า fine-tune ช่วยตรงไหน ยังพลาดตรงไหน และควรปรับ dataset หรือ prompt อย่างไรต่อ

**Sources**

- `docs/poc-plan.md` สำหรับ evaluation plan และ report format (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ evaluation rules และคำเตือนเรื่อง overclaim (source: AGENTS.md)
- `docs/References.md` สำหรับ lm-evaluation-harness, SigmaHQ และ Unsloth mapping (source: docs/References.md)
- `llm-wiki/SKILL.md` สำหรับ log append-only และ related pages (source: SKILL.md)

**Last updated**

2026-05-16

## Goal

สร้างผลเทียบ baseline vs fine-tuned model ที่มีตัวเลข, error analysis และข้อสรุปที่เอาไปคุยกับ stakeholder ได้

## Scope

- รัน evaluator กับ fine-tuned adapter
- เขียน `reports/finetuned-eval.json`
- update `reports/comparison.md`
- วิเคราะห์ false positive และ false negative
- ตรวจ evidence quality
- บันทึก limitation และ next experiment

## Checklist

- [ ] รัน evaluation ด้วย fixed test split
- [ ] เก็บ raw outputs เท่าที่จำเป็นสำหรับ debug
- [ ] เขียน `reports/finetuned-eval.json`
- [ ] update `reports/comparison.md`
- [ ] เพิ่มตาราง metric เทียบ heuristic, base model และ fine-tuned model
- [ ] เพิ่ม error analysis ราย label
- [ ] เพิ่ม note ว่า dataset เป็น synthetic
- [ ] ระบุ next dataset improvements

## Acceptance Criteria

- baseline และ fine-tuned ใช้ test split เดียวกัน
- report บอก metric ครบ
- ถ้า fine-tuned แพ้บาง metric ต้องเขียนไว้ตรง ๆ
- มีตัวอย่าง error อย่างน้อย 3-5 เคส
- ไม่มีการ claim ว่า model ยืนยันการถูก hack ได้จาก log เส้นเดียว

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 6 plan page | `docs/Day6.md` | Planned |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ fixed test split เท่านั้น | comparison ต้องแฟร์และรันซ้ำได้ | ห้ามแตะ test split ระหว่าง train |
| 2026-05-16 | report ต้องบอกข้อจำกัดชัดเจน | synthetic dataset อาจทำให้ผลดูดีเกินจริง | stakeholder จะเข้าใจว่า POC ยังไม่ใช่ production detector |

## Notes

วันที่หกเป็นวันที่ POC เริ่มมีน้ำหนัก เพราะมีตัวเลขให้คุย ถ้าผลยังไม่สวย ให้เก็บเป็น insight ว่า dataset หรือ schema ยังต้องปรับ ไม่ต้องกลบจุดอ่อน

## Related pages

- [[Day5]]
- [[Day7]]
- [[poc-plan]]
- [[References]]


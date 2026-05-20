# Phase 5 Mini Semantic Eval

**Summary**

Phase 5 วัด semantic quality เฉพาะหลัง output contract ผ่านแล้ว จุดประสงค์คือดู error profile ก่อนแตะ fixed test split

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ mini semantic eval checklist (source: docs/structured-output-fix-plan.md)
- `docs/evaluation-metrics-rationale.md` สำหรับ metric rationale (source: docs/evaluation-metrics-rationale.md)
- `data/splits/test.jsonl` สำหรับ fixed split ที่ยังห้ามใช้ใน phase นี้ (source: data/splits/test.jsonl)

**Last updated**

2026-05-20

## Status

Draft. เริ่มหลัง Phase 4 ผ่านเท่านั้น

## Required Work

- สร้าง mini eval split 20-25 samples ที่ไม่ใช่ `data/splits/test.jsonl`
- รัน evaluator ด้วย runtime/mode ที่ผ่าน contract gate
- ตรวจ confusion ราย label
- ตรวจ severity drift
- ตรวจ evidence ว่าเป็น substring จาก log
- บันทึก latency และ retry count ถ้ามี retry loop

## Pass Condition

- output contract ยังผ่าน `1.0`
- semantic errors ถูกจัดกลุ่มได้พอจะตัดสินใจว่าแก้ dataset, schema wording, training format, runtime หรือ model capacity

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 5 detail stub | `docs/output-structure-fix/phase-5-mini-semantic-eval.md` | Drafted |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-4-contract-gate]]
- [[structured-output-fix-plan]]

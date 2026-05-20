# Phase 6 V3 Or Runtime Decision

**Summary**

Phase 6 เป็น decision point หลังรู้แล้วว่า output contract fail เพราะ runtime หรือ semantics fail เพราะ model/data/training format

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ Phase 6 decision rules (source: docs/structured-output-fix-plan.md)
- `docs/fine-tuning-notes.md` สำหรับ Unsloth training/export context (source: docs/fine-tuning-notes.md)
- `docs/data-formats-for-llm-training.md` สำหรับ training render format rationale (source: docs/data-formats-for-llm-training.md)

**Last updated**

2026-05-20

## Status

Draft. เริ่มหลัง Phase 5 มี error profile แล้ว

## Decision Rules

ถ้า contract fail เพราะ runtime:

- เปลี่ยน serving runtime หรือ config ก่อน
- ห้ามให้ retrain v3 เป็นคำตอบหลัก

ถ้า contract ผ่านแต่ semantics fail:

- เตรียม v3 training data
- assistant output ต้องเป็น raw JSON object เท่านั้น
- เพิ่ม hard cases ที่ v2 สับ label
- เพิ่ม examples ที่บังคับ field completeness
- ปรับ schema descriptions/key wording ถ้าช่วย semantics ได้
- retrain ด้วย prompt/render format เดียวกับ evaluator

ถ้า LFM2-350M ยังอ่อนแม้ runtime ดี:

- เก็บ LFM2-350M เป็น resource-constrained baseline
- รัน diagnostic กับ model ใหญ่กว่า 7B/8B
- ใช้ smoke gate เดียวกันกับทุก candidate

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 6 detail stub | `docs/output-structure-fix/phase-6-v3-or-runtime-decision.md` | Drafted |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-5-mini-semantic-eval]]
- [[structured-output-fix-plan]]

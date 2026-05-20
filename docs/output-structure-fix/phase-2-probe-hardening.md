# Phase 2 Probe Hardening

**Summary**

Phase 2 จะเพิ่ม probe ให้แยกได้ว่า backend บังคับ JSON/schema ตอน decode จริงหรือแค่ปล่อย model generate แล้วค่อย validate ภายหลัง

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ Phase 2 checklist (source: docs/structured-output-fix-plan.md)
- `scripts/probe_openai_structured_output.py` สำหรับ probe path ปัจจุบัน (source: scripts/probe_openai_structured_output.py)
- `data/splits/smoke-output-contract.jsonl` สำหรับ 5-sample smoke gate (source: data/splits/smoke-output-contract.jsonl)
- `reports/README.md` สำหรับ report path convention (source: reports/README.md)

**Last updated**

2026-05-20

## Status

Draft. เริ่มหลัง Phase 1 ระบุ backend/version/launch settings ได้ครบ

## Required Changes

- เพิ่ม flag สำหรับ adversarial format instruction เช่นขอให้ตอบใน markdown fence
- เพิ่ม mode ที่รันหลาย sample จาก `data/splits/smoke-output-contract.jsonl` ในคำสั่งเดียว
- บันทึก raw output, latency, requested model, response model, provider schema mode และ validation result ต่อ sample
- เพิ่ม output path ที่บังคับไม่เขียนทับ report เก่า
- ถ้าต้องทำ JSON extraction ให้แยกเป็น debug-only field และห้ามนับเป็น metric หลัก

## Pass Condition

ถ้า prompt ขอ markdown fence แต่ backend เป็น constrained decoder จริง output ต้องยังเป็น JSON object เปล่า ๆ ที่เริ่มด้วย `{` และจบด้วย `}`

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 2 detail stub | `docs/output-structure-fix/phase-2-probe-hardening.md` | Drafted |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-1-backend-inventory]]
- [[structured-output-fix-plan]]

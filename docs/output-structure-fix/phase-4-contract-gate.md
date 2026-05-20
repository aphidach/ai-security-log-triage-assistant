# Phase 4 Contract Gate

**Summary**

Phase 4 เป็น gate ก่อนดู semantic quality ทุกครั้ง ต้องผ่าน output contract บน smoke split ก่อนถึงจะไป mini semantic eval หรือ fixed split

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ contract gate (source: docs/structured-output-fix-plan.md)
- `data/splits/smoke-output-contract.jsonl` สำหรับ smoke split (source: data/splits/smoke-output-contract.jsonl)
- `data/schemas/triage-output.schema.json` สำหรับ schema gate (source: data/schemas/triage-output.schema.json)

**Last updated**

2026-05-20

## Status

Draft. เริ่มหลัง Phase 3 พบ runtime/mode candidate ที่น่าจะ enforce schema ได้จริง

## Gate

- [ ] `json_parse_success_rate = 1.0`
- [ ] `schema_success_rate = 1.0`
- [ ] `invalid_output_count = 0`
- [ ] required fields ครบทุก sample
- [ ] label และ severity อยู่ใน enum ทั้งหมด
- [ ] raw output ไม่มี markdown fence หรือ prose wrapper

## Failure Handling

ถ้าไม่ผ่าน ให้หยุดก่อน fixed split และแยกว่า fail จาก:

- backend ไม่ enforce schema
- schema incompatibility
- missing required field
- invalid enum
- token truncation
- model hallucinating field/value แม้ schema ถูก enforce บางส่วน

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 4 detail stub | `docs/output-structure-fix/phase-4-contract-gate.md` | Drafted |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-3-runtime-capability-matrix]]
- [[structured-output-fix-plan]]

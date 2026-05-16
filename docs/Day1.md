# Day 1: Project Foundation

**Summary**

วันแรกวางฐาน repo ให้พร้อมทำ POC แบบวัดผลได้ เริ่มจาก project scaffold, schema, label taxonomy, directory structure และ README ขั้นต้น เป้าหมายคือให้คนเปิด repo แล้วเข้าใจทันทีว่าเรากำลังทำ security log triage ไม่ใช่ RAG เอกสารทั่วไป

**Sources**

- `AGENTS.md` สำหรับ mission, scope, schema และ working rules (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ milestone และ timeline หลัก (source: docs/poc-plan.md)
- `docs/References.md` สำหรับแนวทางจาก Unsloth, Axolotl, TRL, lm-evaluation-harness, Loghub, SigmaHQ และ OWASP (source: docs/References.md)
- `llm-wiki/SKILL.md` สำหรับแนวคิด page shape, source citation, related pages และ append-only log (source: SKILL.md)

**Last updated**

2026-05-16

## Goal

ทำให้ repo มีโครงเริ่มต้นที่ชัดพอสำหรับ dataset, evaluation, fine-tuning และ demo UI ในวันถัดไป

## Scope

- สร้าง Next.js และ TypeScript project
- วาง directory structure ตาม `docs/poc-plan.md`
- เพิ่ม output schema สำหรับ triage result
- เพิ่ม label taxonomy ชุดแรก
- เพิ่ม README ขั้นต้นสำหรับ setup และ workflow
- ยืนยันว่า dev command พื้นฐานรันได้

## Checklist

- [ ] scaffold Next.js/TypeScript project
- [x] เพิ่ม `data/`, `scripts/`, `frontend/`, `ml/`, `reports/`
- [ ] เพิ่ม `data/schemas/triage-output.schema.json`
- [ ] เพิ่ม `frontend/lib/labels.ts`
- [ ] เพิ่ม `frontend/lib/triage-schema.ts`
- [ ] เพิ่ม README quickstart
- [ ] run lint/typecheck หรือ command ตรวจพื้นฐานเท่าที่ project มี

## Acceptance Criteria

- เปิด repo แล้วเห็น project structure ชัดเจน
- schema ระบุ field หลักครบ: `label`, `severity`, `is_suspicious`, `evidence`, `reason`, `recommended_action`
- label รอบแรกยังจำกัดอยู่ที่ `normal`, `failed_login_bruteforce`, `sql_injection_attempt`, `directory_traversal_attempt`, `port_scan_or_recon`
- ยังไม่มี dependency training หนัก ๆ ปนกับ frontend

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 1 plan page | `docs/Day1.md` | Planned |
| 2026-05-16 | Codex | Created initial repo directory structure with git placeholders | `data/`, `scripts/`, `ml/`, `reports/`, `frontend/` | Done |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | เริ่มแบบ schema-first | evaluator, model adapter และ UI ต้องใช้ output shape เดียวกัน | ลดการแก้ซ้ำเมื่อเริ่มเขียน baseline และ fine-tune |
| 2026-05-16 | แยก training code ไว้ใน `ml/` | fine-tuning มี dependency และ environment คนละชุดกับ frontend | frontend demo ยังรันได้แม้ไม่มี GPU |

## Notes

วันแรกยังไม่ต้องทำ model ให้ฉลาด จุดสำคัญคือสร้างฐานที่ทุกอย่างต่อกันได้ดี พอ schema และ label คงที่แล้ว วันถัดไปจะ generate dataset และวัดผลได้ไม่สะดุด

## Related pages

- [[Day2]]
- [[poc-plan]]
- [[References]]

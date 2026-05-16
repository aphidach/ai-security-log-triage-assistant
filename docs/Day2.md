# Day 2: Dataset And Data Card

**Summary**

วันที่สองสร้าง synthetic dataset รอบแรกสำหรับ security log triage และเขียน data-card เพื่อบอกที่มา format ข้อจำกัด และวิธี split ข้อมูล เป้าหมายคือให้มีข้อมูล 500 records สำหรับ baseline, validation และ fine-tuning รอบแรก

**Sources**

- `docs/poc-plan.md` สำหรับ dataset plan และ label scope (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ JSONL record format และ privacy rules (source: AGENTS.md)
- `docs/References.md` สำหรับ Loghub, SigmaHQ และ OWASP ที่ใช้เป็นแนวทางด้าน dataset และ taxonomy (source: docs/References.md)
- `llm-wiki/SKILL.md` สำหรับแนวคิด source citation และ append-only change log (source: SKILL.md)

**Last updated**

2026-05-16

## Goal

สร้าง dataset ชุดแรกแบบ deterministic จำนวน 500 records เพื่อให้ baseline และ fine-tuning ใช้ข้อมูลเดียวกันและเทียบผลได้ตรงไปตรงมา

## Scope

- เขียน `scripts/generate-dataset.ts`
- generate examples สำหรับ 5 labels รอบแรก label ละ 100 records
- แบ่งข้อมูลเป็น `train`, `validation`, `test` ด้วย split `70/15/15`
- เพิ่ม `docs/data-card.md`
- ตรวจว่า JSONL ทุกบรรทัด parse ได้
- ตรวจว่า output ทุก record ตรง schema

## Checklist

- [ ] สร้าง generator พร้อม seed คงที่
- [ ] สร้างตัวอย่าง `normal`
- [ ] สร้างตัวอย่าง `failed_login_bruteforce`
- [ ] สร้างตัวอย่าง `sql_injection_attempt`
- [ ] สร้างตัวอย่าง `directory_traversal_attempt`
- [ ] สร้างตัวอย่าง `port_scan_or_recon`
- [ ] เขียน `data/splits/train.jsonl` จำนวน 350 records
- [ ] เขียน `data/splits/validation.jsonl` จำนวน 75 records
- [ ] เขียน `data/splits/test.jsonl` จำนวน 75 records
- [ ] เขียน `docs/data-card.md`
- [ ] เพิ่ม command ตรวจ dataset

## Acceptance Criteria

- มี dataset รอบแรก 500 records
- แต่ละ label มี 100 records
- split เป็น `70/15/15`
- ทุก record มี `id`, `instruction`, `input`, `output`
- `output` ตรง schema
- test split ไม่ซ้ำกับ train split
- data-card อธิบายชัดว่า dataset รอบแรกเป็น synthetic และยังไม่แทน log production จริง

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 2 plan page | `docs/Day2.md` | Planned |
| 2026-05-16 | Codex | Documented dataset input/output record contract | `docs/dataset-input-output-format.md` | Done |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ synthetic dataset ก่อน | คุม label, evidence และ edge case ได้ง่ายใน POC แรก | ต้องเขียน limitation ให้ชัดใน data-card |
| 2026-05-16 | ใช้ JSONL เป็น format หลัก | เหมาะกับ training/evaluation และอ่านทีละ record ได้ง่าย | scripts และ trainer ใช้ format เดียวกัน |
| 2026-05-16 | เริ่ม dataset รอบแรกที่ 500 records | ทรัพยากรจำกัดและต้องการเห็นสัญญาณจาก baseline/evaluator ก่อนขยายข้อมูล | label ละ 100 records และ split `350/75/75` |

## Notes

dataset รอบแรกควรมีทั้งเคสง่ายและเคสหลอก เช่น normal log ที่มีคำว่า `admin`, request ที่มี encoded payload หรือ failed login ที่ยังไม่ถึง brute force threshold ตรงนี้จะช่วยให้ evaluation ไม่ง่ายจนหลอกตัวเอง

## Related pages

- [[Day1]]
- [[Day3]]
- [[poc-plan]]
- [[dataset-input-output-format]]
- [[References]]

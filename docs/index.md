# Docs Index

**Summary**

สารบัญเอกสารของ `AI Security Log Triage Assistant` สำหรับนำทางแผน POC, day plan, rationale และ documentation log

**Sources**

- `AGENTS.md` สำหรับ mission และ repo scope (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ milestone และ repo structure (source: docs/poc-plan.md)
- `docs/project-structure-rationale.md` สำหรับเหตุผลของ directory structure (source: docs/project-structure-rationale.md)

**Last updated**

2026-05-16

## Core Pages

- [[poc-plan]]: แผน POC หลัก ตั้งแต่ scope, success criteria, dataset, baseline, fine-tuning และ evaluation
- [[project-structure-rationale]]: เหตุผลที่ต้องแยก `data/`, `scripts/`, `ml/`, `reports/` และ `frontend/`
- [[triage-output-schema]]: อธิบาย `data/schemas/triage-output.schema.json` ซึ่งเป็น output contract กลางของ dataset, evaluator, model adapter และ UI
- [[label-taxonomy]]: ความหมาย วิธีใช้ evidence และ caveat ของ label รอบแรกทั้ง 5 ตัว
- [[dataset-input-output-format]]: รูปแบบ JSONL ของ `instruction`, `input`, `output`, ขนาด dataset รอบแรก และ validation rules
- [[evaluation-metrics-rationale]]: เหตุผลที่ต้องวัด metric รอบแรก เช่น label accuracy, JSON/schema validity, evidence match และ latency
- [[dataset-source-strategy]]: กลยุทธ์เลือกและจัดลำดับแหล่ง dataset ภายนอก เช่น Loghub, OTRF/Mordor, BOTS, SigmaHQ, Splunk Attack Data และ Kaggle synthetic candidate
- [[slm-fine-tuning-model-choice]]: สรุป benchmark SLM และเหตุผลที่ POC รอบแรกเริ่มจาก LFM2-350M
- [[slm-rag-fine-tuning-hallucination]]: บทเรียนจาก industrial RAG fine-tuning เรื่อง cost-aware evaluation, factuality และ hallucination taxonomy
- [[tinylora-reasoning-13-parameters]]: สรุป TinyLoRA และบทเรียนเรื่อง RL-based ultra-low-parameter tuning สำหรับ future work

## Day Plans

- [[Day1]]: project foundation, schema, label taxonomy และ repo structure
- [[Day2]]: dataset และ data card
- [[Day3]]: heuristic baseline
- [[Day4]]: evaluation runner
- [[Day5]]: model adapters
- [[Day6]]: demo UI
- [[Day7]]: fine-tuning path และ evaluation comparison

## External References

- [[References]]: แหล่งอ้างอิงและเหตุผลการยืมแนวคิดจาก Unsloth, Axolotl, TRL, lm-evaluation-harness, Loghub, Splunk BOTS, OTRF, SigmaHQ และ OWASP

## Documentation Maintenance

- [[log]]: append-only documentation change log

## Work Log

Append-only log สำหรับบันทึกว่า index นี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created docs index and linked current planning pages | `docs/index.md` | Drafted |
| 2026-05-16 | Codex | Added SLM model-choice page to core docs | `docs/slm-fine-tuning-model-choice.md` | Updated |
| 2026-05-16 | Codex | Added industrial SLM RAG fine-tuning page to core docs | `docs/slm-rag-fine-tuning-hallucination.md` | Updated |
| 2026-05-16 | Codex | Added TinyLoRA page to core docs | `docs/tinylora-reasoning-13-parameters.md` | Updated |
| 2026-05-16 | Codex | Added evaluation metrics rationale page to core docs | `docs/evaluation-metrics-rationale.md` | Updated |
| 2026-05-16 | Codex | Added dataset source strategy page to core docs | `docs/dataset-source-strategy.md` | Updated |
| 2026-05-16 | Codex | Moved References into the docs wiki directory | `docs/References.md` | Updated |
| 2026-05-16 | Codex | Added triage output schema explanation page | `docs/triage-output-schema.md` | Updated |
| 2026-05-16 | Codex | Added first-pass label taxonomy page to core docs | `docs/label-taxonomy.md` | Updated |
| 2026-05-16 | Codex | Added dataset input/output format page to core docs | `docs/dataset-input-output-format.md` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | เพิ่ม docs index | docs มีหลายหน้าแล้วและต้องค้นหา rationale ได้ง่าย | เอกสารใหม่ถูกผูกเข้ากับ mini-wiki แทนที่จะเป็น markdown โดด ๆ |
| 2026-05-16 | ย้าย References เข้า `docs/` | ให้ reference อยู่ใน mini-wiki เดียวกับ day plan, rationale และ dataset strategy | path อ้างอิงหลักเปลี่ยนจาก `References.md` เป็น `docs/References.md` |

## Related pages

- [[poc-plan]]
- [[project-structure-rationale]]
- [[log]]

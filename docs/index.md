# Docs Index

**Summary**

สารบัญเอกสารของ `AI Security Log Triage Assistant` สำหรับนำทางแผน POC, day plan, rationale และ documentation log

**Sources**

- `AGENTS.md` สำหรับ mission และ repo scope (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ milestone และ repo structure (source: docs/poc-plan.md)
- `docs/project-structure-rationale.md` สำหรับเหตุผลของ directory structure (source: docs/project-structure-rationale.md)

**Last updated**

2026-05-19

## Core Pages

- [[poc-plan]]: แผน POC หลัก ตั้งแต่ scope, success criteria, dataset, baseline, fine-tuning และ evaluation
- [[project-structure-rationale]]: เหตุผลที่ต้องแยก `data/`, `scripts/`, `ml/`, `reports/` และ `frontend/`
- [[triage-output-schema]]: อธิบาย `data/schemas/triage-output.schema.json` ซึ่งเป็น output contract กลางของ dataset, evaluator, model adapter และ UI
- [[label-taxonomy]]: ความหมาย วิธีใช้ evidence และ caveat ของ label รอบแรกทั้ง 5 ตัว
- [[dataset-input-output-format]]: รูปแบบ JSONL ของ `instruction`, `input`, `output`, ขนาด dataset รอบแรก และ validation rules
- [[data-formats-for-llm-training]]: สรุปรูปแบบข้อมูลสำหรับ LLM training และเหตุผลที่โปรเจกต์นี้ควรใช้ `instruction/input/output` เป็น source format แล้ว render เป็น `messages`
- [[data-card]]: data card ของ synthetic dataset รอบแรก รวมที่มา วิธี generate split ข้อจำกัด และ privacy note
- [[log-type-examples]]: คำอธิบาย log format ที่ dataset จำลองไว้ เช่น web access, SSH auth, WAF, IDS และ netflow-style log พร้อมตัวอย่าง
- [[evaluation-metrics-rationale]]: เหตุผลที่ต้องวัด metric รอบแรก เช่น label accuracy, JSON/schema validity, evidence match และ latency
- [[fine-tuning-notes]]: notes สำหรับ Unsloth fine-tuning path, Colab/GPU setup, limitation และ Day 6 handoff
- [[model-output/README]]: บันทึก versioned model output notes, template และ behavior ของ model แต่ละรอบ
- [[model-output/v1-lfm2-350m-security-triage]]: สรุปว่า v1 train/serve ได้ แต่ออก API เป็น prose/prose+JSON จึงยังไม่ผ่าน output contract
- [[dataset-source-strategy]]: กลยุทธ์เลือกและจัดลำดับแหล่ง dataset ภายนอก เช่น Loghub, OTRF/Mordor, BOTS, SigmaHQ, Splunk Attack Data และ Kaggle synthetic candidate
- [[slm-fine-tuning-model-choice]]: สรุป benchmark SLM และเหตุผลที่ POC รอบแรกเริ่มจาก LFM2-350M
- [[slm-rag-fine-tuning-hallucination]]: บทเรียนจาก industrial RAG fine-tuning เรื่อง cost-aware evaluation, factuality และ hallucination taxonomy
- [[tinylora-reasoning-13-parameters]]: สรุป TinyLoRA และบทเรียนเรื่อง RL-based ultra-low-parameter tuning สำหรับ future work

## Day Plans

- [[Day1]]: project foundation, schema, label taxonomy และ repo structure
- [[Day2]]: dataset และ data card
- [[Day3]]: heuristic baseline
- [[Day4]]: model adapters และ evaluator integration
- [[Day5]]: fine-tuning path ด้วย Unsloth, config, training format และ inference wiring
- [[Day6]]: GPU training, fine-tuned evaluation และ comparison report
- [[Day7]]: demo UI และ integration รอบถัดไป

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
| 2026-05-17 | Codex | Added first synthetic dataset data card to core docs | `docs/data-card.md` | Updated |
| 2026-05-17 | Codex | Added log type examples page to core docs | `docs/log-type-examples.md` | Updated |
| 2026-05-17 | Codex | Added fine-tuning notes page and refreshed day plan labels | `docs/fine-tuning-notes.md`, `docs/index.md` | Updated |
| 2026-05-18 | Codex | Added model-output notes and linked v1 output-contract failure page | `docs/model-output/README.md`, `docs/model-output/v1-lfm2-350m-security-triage.md` | Updated |
| 2026-05-19 | Codex | Added LLM training data format guide to core docs | `docs/data-formats-for-llm-training.md` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | เพิ่ม docs index | docs มีหลายหน้าแล้วและต้องค้นหา rationale ได้ง่าย | เอกสารใหม่ถูกผูกเข้ากับ mini-wiki แทนที่จะเป็น markdown โดด ๆ |
| 2026-05-16 | ย้าย References เข้า `docs/` | ให้ reference อยู่ใน mini-wiki เดียวกับ day plan, rationale และ dataset strategy | path อ้างอิงหลักเปลี่ยนจาก `References.md` เป็น `docs/References.md` |
| 2026-05-18 | เพิ่มหมวด `docs/model-output/` | ต้องแยกพฤติกรรม model แต่ละ version ออกจาก day plan เพื่อเทียบ run ได้ตรงไปตรงมา | model version ถัดไปควรมีหน้า output note ตาม template เดียวกัน |
| 2026-05-19 | เพิ่ม data format guide สำหรับ LLM training | ต้องมีหน้าอธิบายความต่างระหว่าง source dataset format กับ training render format ก่อนแก้ output model รอบถัดไป | Day 6 output-fix discussion มี reference กลางสำหรับเลือก instruction tuning และ chat-message rendering |

## Related pages

- [[poc-plan]]
- [[project-structure-rationale]]
- [[log]]

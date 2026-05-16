# Evaluation Metrics Rationale

**Summary**

เอกสารนี้อธิบายว่าทำไม POC `AI Security Log Triage Assistant` ต้องวัด `label_accuracy`, `json_parse_success_rate`, `schema_success_rate`, `severity_accuracy`, `evidence_partial_match`, `average_latency_ms` และ `invalid_output_count` ตั้งแต่รอบแรก เป้าหมายไม่ใช่แค่วัดว่าโมเดลตอบถูกกี่ข้อ แต่ต้องพิสูจน์ว่า output เป็น structured triage result ที่ API, UI, report และมนุษย์ใช้สอบสวนต่อได้จริง

**Sources**

- `AGENTS.md` สำหรับ mission, output schema, evaluation rules และ guardrail ว่าโปรเจกต์นี้คือ fine-tuning/evaluation POC ไม่ใช่ระบบยืนยัน compromise (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับรายการ metric รอบแรก, fixed test split, report format และ baseline vs fine-tuned comparison (source: docs/poc-plan.md)
- `References.md` สำหรับแนวคิด evaluation harness, model adapter separation และการใช้หลาย metric เพื่อไม่สรุปจาก accuracy อย่างเดียว (source: References.md)

**Last updated**

2026-05-16

## ทำไมต้องมี metric หลายตัว

งานนี้เป็น structured security log triage ไม่ใช่ text generation ทั่วไป output ที่ดีต้องผ่านหลายเงื่อนไขพร้อมกัน: classify pattern ถูก, severity มีประโยชน์ต่อ priority, evidence อ้างอิงจาก log จริง, JSON ใช้ต่อในระบบได้ และ latency ไม่ทำให้ workflow ช้าเกินไป (source: AGENTS.md, docs/poc-plan.md)

ถ้าวัดแค่ accuracy เดียว เราอาจได้ภาพที่หลอกตัวเอง เช่น model เลือก label ถูกแต่ตอบเป็น prose ที่ parse ไม่ได้, label ถูกแต่ severity ผิด, หรือพูด evidence ที่ไม่มีอยู่ใน log แบบนี้ดูเหมือนเก่งใน spreadsheet แต่ใช้เป็น triage assistant จริงไม่ได้ (source: AGENTS.md)

metric ชุดนี้จึงแบ่งปัญหาออกเป็น 3 ชั้น:

- ความถูกต้องของ triage: `label_accuracy`, `severity_accuracy`, `evidence_partial_match`
- ความพร้อมใช้ของ output: `json_parse_success_rate`, `schema_success_rate`, `invalid_output_count`
- ความเหมาะสมเชิง workflow: `average_latency_ms`

## Metric Rationale

| Metric | วัดคำถามอะไร | ทำไมต้องวัด | ถ้าไม่วัดจะพลาดอะไร |
| --- | --- | --- | --- |
| `label_accuracy` | โมเดลเลือก label ตรง expected output หรือไม่ | label คือแกนหลักของ POC เพราะ taxonomy รอบแรกมี 5 class และ report ต้องเทียบ heuristic, base model และ fine-tuned model ด้วย test split เดียวกัน | อาจสรุปไม่ได้ว่า fine-tuning ช่วยแยก normal, brute force, SQL injection, directory traversal และ port scan ดีขึ้นจริงหรือไม่ |
| `json_parse_success_rate` | output parse เป็น JSON ได้หรือไม่ | evaluator, API และ UI ต้องอ่าน output แบบ machine-readable ถ้า parse ไม่ได้ แม้เนื้อหาจะดูดีในสายตามนุษย์ก็ใช้ต่อแบบอัตโนมัติไม่ได้ | โมเดลอาจดูเหมือนตอบดี แต่ pipeline แตกเพราะมี prose, markdown fence หรือ JSON syntax ผิด |
| `schema_success_rate` | JSON มี field ครบและ type ถูกหรือไม่ | schema ของโปรเจกต์ต้อง stable เพื่อให้ dataset generator, evaluator, API, UI และ report ใช้ contract เดียวกัน | JSON อาจ parse ได้แต่ขาด `evidence`, ใช้ `severity` ผิด type หรือคืน field ที่ UI ใช้ไม่ได้ |
| `severity_accuracy` | severity ตรง expected output หรือไม่ | severity เป็นสัญญาณ priority สำหรับการสอบสวน label ถูกแต่ severity ผิดอาจทำให้ผู้ใช้จัดลำดับงานผิด | โมเดลอาจจับ pattern ถูกแต่ลด/เพิ่มความสำคัญผิด เช่น suspicious event ถูกจัดเป็น low โดยไม่มีเหตุผล |
| `evidence_partial_match` | evidence ที่ตอบมี substring ตรงกับ expected evidence หรือไม่ | triage result ต้องมีหลักฐานที่เห็นได้ใน log ไม่ใช่แค่คำตอบสวย ๆ การใช้ partial match เหมาะกับรอบแรกเพราะ evidence อาจมี quoting หรือ substring ต่างกันเล็กน้อย | โมเดลอาจเดา label ถูกจาก pattern กว้าง ๆ แต่ hallucinate evidence หรืออธิบายโดยไม่ชี้หลักฐานจริง |
| `average_latency_ms` | ใช้เวลาเฉลี่ยต่อ sample เท่าไร | POC ต้องเทียบ heuristic baseline กับ model adapter หลายแบบ ความแม่นที่เพิ่มขึ้นต้องมองคู่กับเวลาที่เสียไป | fine-tuned model อาจชนะ accuracy แต่ช้าจนไม่เหมาะกับ demo หรือ workflow triage จริง |
| `invalid_output_count` | มี output กี่รายการที่ใช้ต่อไม่ได้ | count ทำให้เห็น operational failure แบบตรงไปตรงมา และช่วย debug sample ที่ parse/schema fail ได้ง่าย | percentage อาจดูไม่แย่ แต่จำนวนเคสเสียจริงอาจมากพอทำให้ report หรือ UI ไม่น่าเชื่อถือ |

## การตีความผล

ผล evaluation ควรอ่านแบบ tradeoff ไม่ใช่ดู metric เดียวแล้วประกาศชนะ ตัวอย่างเช่น fine-tuned model อาจมี `label_accuracy` สูงกว่า heuristic baseline แต่ `json_parse_success_rate` ต่ำกว่า แบบนี้ต้องรายงานตรง ๆ ว่าโมเดลแม่นขึ้นด้าน classification แต่ยังไม่นิ่งพอสำหรับ structured output (source: docs/poc-plan.md)

ถ้า `evidence_partial_match` ต่ำ แต่ `label_accuracy` สูง แปลว่าโมเดลอาจจำ pattern ได้แต่ยังอธิบายหลักฐานไม่ดีพอ ต้องกลับไปดู dataset format, evidence annotation หรือ prompt/output template ก่อนสรุปว่าโมเดลพร้อมใช้ (source: AGENTS.md, docs/poc-plan.md)

ถ้า `average_latency_ms` สูงมาก ควรแยกวิเคราะห์ว่าเกิดจาก model size, endpoint, local runtime, batching หรือ adapter overhead เพราะ POC นี้ต้องมี path ที่รันได้แม้ไม่มี GPU และควรเทียบกับ heuristic baseline ที่เร็วกว่าเสมอ (source: AGENTS.md, References.md)

## ทำไมยังไม่เริ่มจาก metric ที่ซับซ้อนกว่านี้

รอบแรกยังไม่จำเป็นต้องเริ่มจาก precision, recall, F1 ต่อ label, ROC, calibration หรือ cost-weighted score เพราะ scope ยังเล็กและ priority แรกคือทำ dataset, baseline, evaluator และ fixed test split ให้ reproducible ก่อน (source: AGENTS.md, docs/poc-plan.md)

metric เหล่านั้นควรเพิ่มภายหลังเมื่อมี test set ใหญ่พอและเริ่มเห็น error pattern จริง เช่น false positive ของ `normal`, false negative ของ suspicious label, หรือ severity ที่คลาดเคลื่อนบ่อยในบาง attack pattern

## ใช้เอกสารนี้กับ implementation อย่างไร

เมื่อเขียน evaluator ให้เก็บ raw prediction, parsed JSON, schema validation result, per-sample latency และ per-metric pass/fail ไว้ใน report JSON ก่อน แล้วค่อยสรุปเป็น markdown comparison เพื่อให้ตรวจย้อนหลังได้ว่า model แพ้หรือชนะเพราะอะไร (source: docs/poc-plan.md, References.md)

ถ้า schema หรือ label taxonomy เปลี่ยน ต้องอัปเดต evaluator, dataset generator, API, UI และเอกสารนี้พร้อมกัน เพราะ metric เหล่านี้ผูกกับ output contract โดยตรง (source: AGENTS.md)

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created evaluation metrics rationale page | `docs/evaluation-metrics-rationale.md` | Drafted |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | อธิบาย metric รอบแรกเป็น 3 กลุ่ม: triage correctness, output usability และ workflow fit | ช่วยให้ evaluator/report ไม่สรุปจาก label accuracy อย่างเดียว | implementation ของ evaluator ควรเก็บทั้ง correctness, validity และ latency |

## Related pages

- [[poc-plan]]
- [[Day4]]
- [[project-structure-rationale]]
- [[slm-rag-fine-tuning-hallucination]]
- [[tinylora-reasoning-13-parameters]]
- [[References]]

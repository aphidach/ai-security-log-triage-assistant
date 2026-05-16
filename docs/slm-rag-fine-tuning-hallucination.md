# SLM RAG Fine-Tuning And Hallucination

**Summary**

เอกสารนี้สรุป paper เรื่องการ fine-tune small language models สำหรับ industrial RAG โดยโฟกัสบทเรียนที่ใช้กับ `AI Security Log Triage Assistant`: fine-tuning ด้วยข้อมูลจำนวนน้อยอาจลด hallucination ได้, evaluation ต้องวัดหลายมิติ, และควรดูความคุ้มค่าต่อ compute ไม่ใช่ดู accuracy อย่างเดียว

**Sources**

- `docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md` สำหรับ methodology, datasets, metrics, results, cost-efficiency และ hallucination taxonomy (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)
- `docs/poc-plan.md` สำหรับ evaluation metrics, fixed test split, baseline comparison และ fine-tuning path ของโปรเจกต์นี้ (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ guardrail ว่าโปรเจกต์นี้เป็น security log triage ไม่ใช่ general document RAG และต้องไม่ overclaim detection (source: AGENTS.md)
- `docs/References.md` สำหรับแหล่งอ้างอิงด้าน fine-tuning และ evaluation ที่ repo ใช้เป็น design reference (source: docs/References.md)

**Last updated**

2026-05-16

## Paper นี้ศึกษาอะไร

paper นี้ศึกษา small language models ในระบบ industrial RAG โดยใช้ข้อมูลจริงจาก customer service logs และ internal regulation logs ขององค์กรในไต้หวัน แล้วเปรียบเทียบโมเดลที่ยังไม่ fine-tune กับโมเดลที่ fine-tune แล้วบนชุดทดสอบจริง (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)

โจทย์หลักไม่ใช่ train model จากศูนย์ แต่เป็น domain adaptation: ทำให้โมเดลเข้าใจศัพท์เฉพาะองค์กร, ใช้หลักฐานจาก retrieved documents ให้ดีขึ้น, และตอบในรูปแบบที่เหมาะกับงาน RAG เฉพาะโดเมน (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)

## Dataset และวิธีทดลอง

ข้อมูลจริงแบ่งเป็น 2 ชุด:

- customer service RAG logs: 383 records แบ่งเป็น 229 train และ 154 test
- internal regulation RAG logs: 179 records แบ่งเป็น 119 train และ 60 test

paper เพิ่ม synthetic RAG samples ด้วย GPT-4o และ few-shot generation แต่ให้ domain experts ตรวจและแก้ก่อนนำไปใช้ train ส่วน evaluation ใช้เฉพาะ real-world industrial logs ไม่ใช้ synthetic test samples (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)

แนวทางนี้สอดคล้องกับ POC ของเราในแง่การแยก train/test ให้ชัดและไม่เอาข้อมูล train ไปวัดผล แต่ต่างกันตรงที่โปรเจกต์เรารอบแรกยังเป็น security log triage แบบ structured JSON ไม่ใช่ RAG answer generation (source: docs/poc-plan.md, AGENTS.md)

## Metrics ที่ใช้

paper ใช้ RAGAS-style metrics และ GPT-4o เป็น evaluator สำหรับวัด generation quality:

- `faithfulness`: คำตอบยึดกับ retrieved context แค่ไหน
- `answer relevance`: คำตอบตรงกับ query แค่ไหน
- `factual correctness`: claim ในคำตอบตรงกับ reference แค่ไหน
- `F1`: overlap ระหว่างคำตอบกับ ground truth

นอกจากนี้ paper ยังเสนอ `delta(metric)/GPU-hour` เพื่อดูว่าการเพิ่ม training data หรือ compute ให้ improvement ต่อ GPU-hour คุ้มแค่ไหน (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)

สำหรับโปรเจกต์เรา ควรยืมหลักคิด cost-aware evaluation มาใช้กับ metric ที่ตรงงานกว่า เช่น `label_accuracy`, `evidence_partial_match`, `json_parse_success_rate`, `schema_success_rate`, `severity_accuracy`, `average_latency_ms` และอาจเพิ่ม training-time-normalized improvement ในรายงาน fine-tuning (source: docs/poc-plan.md)

## Findings ที่สำคัญ

### Fine-tuning ลด hallucination ได้แม้มี RAG แล้ว

paper ย้ำว่า retrieval ไม่ได้แก้ hallucination หมด แม้ retrieved documents จะเกี่ยวข้อง โมเดลยังอาจตีความหลักฐานผิด, สรุปเกิน evidence, หรือให้คำตอบที่ดูน่าเชื่อแต่ไม่ตรงกับ reference ได้ (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)

หลัง fine-tune ด้วย domain-specific RAG data, customer service corpus มีสัดส่วนคำตอบที่จัดเป็น `No major issue` เพิ่มจาก 58.4% เป็น 84.4% และ fabrication ลดลงชัดเจน (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)

### ข้อมูลน้อยก็เริ่มเห็น learning curve

paper ทดลอง training size หลายระดับ เช่น 50, 100, 150, 200 และช่วง 300-400 ตัวอย่าง ผลโดยรวมชี้ว่าช่วง 50-200 ตัวอย่างแรกให้ improvement สำคัญ โดยเฉพาะ factual correctness และ F1 ก่อนเริ่มมี diminishing returns (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)

บทเรียนสำหรับ POC นี้คือไม่ต้องรอ dataset ใหญ่มากก่อนเริ่มวัดสัญญาณ แต่ต้องมี validation/test split ที่สะอาดและรายงานข้อจำกัดของ synthetic data ให้ชัด (source: docs/poc-plan.md)

### ไม่มีโมเดลเดียวที่ชนะทุก metric

paper พบว่าแต่ละ architecture เด่นคนละด้าน เช่น บางโมเดลดีกว่าเรื่อง faithfulness, บางโมเดลดีกว่า answer relevance, บางโมเดลดีกว่า factual correctness และ F1 (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)

ดังนั้นการเลือกโมเดลสำหรับ POC ไม่ควรดู leaderboard เดียว ต้องนิยาม metric สำคัญของ security log triage ก่อน สำหรับรอบแรกของเรา metric ที่ควรสำคัญคือ schema validity, label correctness, evidence correctness และ recommended action ที่ไม่กล่าวเกินหลักฐาน (source: docs/poc-plan.md, AGENTS.md)

### Cost-efficiency สำคัญมากในงานทรัพยากรจำกัด

paper ใช้ `delta(metric)/GPU-hour` เพื่อดู marginal gain ต่อ compute และพบว่าโมเดลเล็กบางตัวอาจคุ้มกว่าโมเดลใหญ่ในบางโดเมน แม้คะแนน absolute จะไม่ดีที่สุด (source: docs/raw/Fine-tuning small language models for industrial retrieval-augmented generation Efficiency, factuality, and hallucination analysis.md)

แนวคิดนี้สนับสนุนทิศทางของ repo ที่เริ่มจาก LFM2-350M เพื่อพิสูจน์ workflow และวัด improvement ต่อทรัพยากรก่อนขยับไป model sweep ที่ใหญ่กว่า (source: AGENTS.md, docs/poc-plan.md)

## Hallucination Taxonomy

paper เสนอ heuristic taxonomy สำหรับจัดประเภท hallucination จากคะแนน `faithfulness`, `factual correctness` และ `answer relevance`:

- `FAB`: fabrication หรือ invented fact
- `UNSUP`: unsupported inference หรือ over-generalization
- `MIS`: misinterpretation หรือ low relevance
- `SUS`: suspected hallucination
- `LF`: low faithfulness

สำหรับ security log triage เราไม่ควรใช้ taxonomy นี้ตรง ๆ เพราะงานเราไม่ใช่ RAG answer generation แต่สามารถแปลงเป็น error taxonomy ของเราเองได้ เช่น:

- fabricated evidence: model อ้าง evidence ที่ไม่มีใน log
- unsupported label: label เป็น attack pattern แต่หลักฐานใน log ไม่พอ
- missed suspicious pattern: log มี pattern ชัดแต่ model ตอบ normal
- wrong severity: label ถูกแต่ severity ไม่สมเหตุสมผล
- unsafe recommendation: recommended action เกินหลักฐานหรือชี้นำผิดทาง

taxonomy แบบนี้จะช่วยให้รายงาน fine-tuning ไม่หยุดที่ accuracy แต่บอกได้ว่า model พลาดแบบไหนและควรแก้ dataset/prompt/evaluator ตรงไหน (source: docs/poc-plan.md, AGENTS.md)

## Implications For This POC

สิ่งที่ควรยืมมาใช้:

- เริ่มจาก dataset ขนาดเล็กแต่แยก train/validation/test ให้ชัด
- วัดหลาย metric พร้อมกัน ไม่ใช้ accuracy เดียวตัดสินคุณภาพ
- บันทึก training time และ latency เพื่อดูความคุ้มค่าต่อทรัพยากร
- ทำ error taxonomy สำหรับ triage output โดยเฉพาะ
- ใช้ synthetic data ได้ในรอบแรก แต่ต้องระบุข้อจำกัดและไม่ใช้ synthetic test เป็นหลักฐานเกินจริง

สิ่งที่ยังไม่ควรยืมตรง ๆ:

- ไม่ควรเปลี่ยนโปรเจกต์นี้เป็น general document RAG เพราะ scope ปัจจุบันคือ security log triage (source: AGENTS.md)
- ไม่ควรใช้ RAGAS metrics แทน evaluator หลักของเรา เพราะ output ของเราเป็น structured JSON ไม่ใช่ free-form answer
- ไม่ควรสรุปว่า model ใดใน paper จะชนะงาน security log triage โดยตรง เพราะ dataset, language, task และ evaluation ต่างกัน

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created curated wiki page from industrial SLM RAG fine-tuning paper | `docs/slm-rag-fine-tuning-hallucination.md` | Drafted |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ paper นี้เป็น reference ด้าน cost-aware evaluation และ error taxonomy | paper วัด fine-tuning ด้วยหลาย metric และเสนอ hallucination taxonomy ที่แปลงมาใช้กับ triage error analysis ได้ | evaluation report รอบ fine-tuning ควรมี error categories และบันทึก cost/latency |
| 2026-05-16 | ไม่ใช้ paper นี้เป็นเหตุผลให้เปลี่ยน scope ไปทำ RAG | AGENTS.md ระบุชัดว่าโปรเจกต์นี้ไม่ใช่ general document RAG | wiki page นี้ทำหน้าที่เป็น evaluation/fine-tuning reference เท่านั้น |

## Related pages

- [[poc-plan]]
- [[slm-fine-tuning-model-choice]]
- [[References]]
- [[log]]

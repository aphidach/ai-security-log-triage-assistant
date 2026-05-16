# SLM Fine-Tuning Model Choice

**Summary**

เอกสารนี้สรุปบทความ Distil Labs เรื่องการเลือก small language model สำหรับ fine-tuning และแปลผลให้เข้ากับ POC `AI Security Log Triage Assistant` ข้อสรุปสำหรับรอบแรกคือเริ่ม fine-tune ด้วย **LFM2-350M** เพราะทรัพยากรจำกัดและต้องการพิสูจน์ workflow ให้ครบก่อนขยายไปโมเดลใหญ่กว่า

**Sources**

- `docs/raw/What Small Language Model Is Best for Fine-Tuning.md` สำหรับผล benchmark, methodology, model ranking และ practical recommendations (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md)
- `docs/poc-plan.md` สำหรับ fine-tuning plan, fixed test split และ evaluation metrics ของโปรเจกต์นี้ (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ fine-tuning guidance ล่าสุดที่เลือก LFM2-350M เป็น candidate แรก (source: AGENTS.md)
- `docs/References.md` สำหรับ rationale ว่าบทความนี้เป็น reference ด้าน model choice ไม่ใช่หลักฐานผลลัพธ์บน security log โดยตรง (source: docs/References.md)

**Last updated**

2026-05-16

## บทความนี้ตอบคำถามอะไร

บทความของ Distil Labs benchmark small language model 15 ตัวกับงาน 9 ประเภท เช่น classification, information extraction, document understanding, QA และ tool calling แล้ววัดทั้ง base performance, fine-tuned performance และ tunability หรือ gain หลัง fine-tune (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md)

สิ่งที่น่าสนใจสำหรับโปรเจกต์นี้ไม่ใช่แค่ว่าโมเดลไหนคะแนนสูงสุด แต่คือ tradeoff ระหว่างขนาดโมเดลกับความคุ้มของการ fine-tune เพราะ POC นี้ต้องรันได้ภายใต้ทรัพยากรจำกัดและยังต้องมีทางที่ไม่พึ่ง GPU สำหรับ dataset, baseline และ evaluation (source: AGENTS.md, docs/poc-plan.md)

## Key Findings

### LFM2-350M เด่นที่สุดด้าน tunability

LFM2-350M ได้อันดับหนึ่งด้าน tunability ใน benchmark ของบทความ โดยมี average rank 2.11 และ 95% CI แคบที่สุดในกลุ่ม tunability ranking จุดนี้หมายความว่าโมเดลตัวเล็กมากตัวนี้รับสัญญาณจาก fine-tuning ได้ดีและ improve อย่างสม่ำเสมอในหลาย benchmark (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md)

สำหรับ POC นี้ ประเด็นนี้สำคัญกว่า raw accuracy สูงสุด เพราะเป้าหมายรอบแรกคือพิสูจน์ว่า dataset, LoRA/QLoRA training path, adapter และ evaluator ต่อกันได้จริง ไม่ใช่ใช้ compute ไปกับโมเดลใหญ่ตั้งแต่ต้น (source: docs/poc-plan.md)

### Qwen3-8B และ Qwen3-4B ยังเป็นตัวเทียบที่ดี

บทความชี้ว่า Qwen3-8B ได้ผล fine-tuned performance ดีที่สุดโดยรวม และ Qwen3-4B-Instruct-2507 สามารถ match หรือ exceed teacher model ขนาด 120B+ ได้ใน 8 จาก 9 benchmark (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md)

แต่สำหรับ repo นี้ Qwen 1.5B/3B/4B ยังไม่ควรเป็น default รอบแรก เพราะทรัพยากรเป็นข้อจำกัดหลัก ควรเก็บไว้เป็น candidate สำหรับรอบเปรียบเทียบภายหลัง เมื่อ workflow และ evaluator พร้อมแล้ว (source: AGENTS.md, docs/poc-plan.md)

### Fine-tuning สำคัญกว่าการพึ่ง prompt อย่างเดียว

บทความสรุปว่าโมเดลเล็กที่ fine-tune ดีอาจชนะโมเดลใหญ่ที่ใช้ prompting อย่างเดียวได้ จุดนี้เข้ากับโปรเจกต์ security log triage เพราะ output schema แคบ, label taxonomy จำกัด และ evidence ที่ต้องหาอยู่ใน log ทำให้งานเหมาะกับ supervised fine-tuning มากกว่างาน open-ended generation (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md, docs/poc-plan.md)

## Decision For This POC

เริ่ม fine-tuning path ด้วย **LFM2-350M** ก่อน

เหตุผล:

- โมเดลเล็กมาก เหมาะกับทรัพยากรจำกัด
- benchmark ภายนอกชี้ว่า LFM2-350M ได้ gain จาก fine-tuning สูง
- รอบแรกต้องพิสูจน์ workflow และ evaluation ให้จบก่อน ไม่ใช่ชนะ leaderboard
- ค่าใช้จ่ายและเวลาทดลองต่ำกว่าโมเดล 3B/4B/8B
- ถ้า LFM2-350M แพ้ heuristic baseline ในบาง metric ก็ยังเป็นข้อมูลที่มีค่า เพราะจะบอกว่าควรปรับ dataset, prompt format หรือขยับไปโมเดลใหญ่ขึ้นตรงไหน

Qwen 1.5B/3B/4B จะถูกเก็บเป็น candidate สำหรับรอบเปรียบเทียบภายหลัง ไม่ใช่ target หลักของรอบแรก (source: AGENTS.md, docs/poc-plan.md)

## How To Use This In The Project

ใน `ml/unsloth/config.example.yaml` ควรตั้งค่า `base_model` ให้ชี้ไปที่ LFM2-350M เป็น default รอบแรก และแยกค่า model name ออกจาก training script เพื่อให้เปลี่ยนไป Qwen หรือโมเดลอื่นภายหลังได้โดยไม่แก้ logic หลัก (source: docs/poc-plan.md, docs/References.md)

ใน evaluation report ต้องเทียบอย่างน้อย:

- heuristic baseline
- base model หรือ local model baseline ถ้ามี endpoint พร้อม
- fine-tuned LFM2-350M

ทุกตัวต้องใช้ fixed test split เดียวกัน และต้องรายงาน metric ด้าน JSON validity, schema validity, label accuracy, severity accuracy, evidence partial match และ latency (source: docs/poc-plan.md)

## Limitations

benchmark ต้นทางไม่ได้ทดสอบกับ security log triage โดยตรง จึงใช้เป็นเหตุผลในการเลือก candidate ไม่ใช่หลักฐานว่า LFM2-350M จะทำงานนี้ได้ดีที่สุดแน่นอน (source: docs/References.md)

ข้อมูล training ของบทความเป็น synthetic data จาก teacher model และใช้ benchmark หลายประเภท ส่วน POC นี้จะเริ่มจาก synthetic security logs เฉพาะ 5 label เท่านั้น ผลจึงต้องวัดใหม่ในบริบทของเราเอง (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md, docs/poc-plan.md)

ถ้า fine-tuned model ไม่ชนะ heuristic baseline ต้องรายงานตรง ๆ และวิเคราะห์ว่าแพ้ตรง label accuracy, evidence match, JSON/schema validity หรือ latency ไม่ควรสรุปแบบกว้าง ๆ ว่า fine-tuning ล้มเหลว (source: AGENTS.md, docs/poc-plan.md)

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created curated model-choice doc from raw Distil Labs clipping | `docs/slm-fine-tuning-model-choice.md` | Drafted |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | เลือก LFM2-350M เป็น fine-tuning candidate รอบแรก | ทรัพยากรจำกัดและบทความ benchmark ชี้ว่า LFM2-350M มี tunability สูง | training config, notes และ evaluation รอบแรกควรตั้งต้นจาก LFM2-350M |
| 2026-05-16 | เก็บ Qwen 1.5B/3B/4B ไว้เป็นรอบเปรียบเทียบภายหลัง | Qwen ได้ performance สูงกว่าใน benchmark แต่ใช้ทรัพยากรมากกว่า | POC รอบแรกโฟกัส workflow และ metric ก่อนขยาย model sweep |

## Related pages

- [[poc-plan]]
- [[Day5]]
- [[References]]
- [[log]]

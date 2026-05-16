# TinyLoRA Reasoning In 13 Parameters

**Summary**

เอกสารนี้สรุปบทความ MarkTechPost และ paper `Learning to Reason in 13 Parameters` ซึ่งเสนอ TinyLoRA วิธี fine-tuning แบบ ultra-low-parameter ที่ใช้ RL/GRPO กับ verifiable reward เพื่อเพิ่ม math reasoning ด้วย trainable parameters จำนวนน้อยมาก สำหรับ POC นี้ให้ใช้เป็น research reference ด้าน cost-aware tuning และ reward-based future work ไม่ใช่ path หลักของรอบแรก

**Sources**

- MarkTechPost summary สำหรับภาพรวม TinyLoRA, benchmark headline และ key takeaways (source: https://www.marktechpost.com/2026/03/24/this-ai-paper-introduces-tinylora-a-13-parameter-fine-tuning-method-that-reaches-91-8-percent-gsm8k-on-qwen2-5-7b/)
- `Learning to Reason in 13 Parameters` สำหรับ paper ต้นทาง, TinyLoRA formulation, SFT vs RL comparison และ math benchmark details (source: https://ar5iv.labs.arxiv.org/html/2602.04118)
- `docs/poc-plan.md` สำหรับ fine-tuning path, evaluation metrics และ fixed test split ของโปรเจกต์นี้ (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ guardrail ว่า POC รอบแรกต้องเน้น security log triage, evaluation และไม่ overclaim ผลโมเดล (source: AGENTS.md)

**Last updated**

2026-05-16

## Paper นี้เสนออะไร

TinyLoRA เป็น parameter-efficient fine-tuning method ที่พยายามลดขนาด adapter ให้เล็กกว่า LoRA และ LoRA-XS มาก โดย paper ตั้งคำถามว่าแม้แต่ rank-1 LoRA ยังใหญ่เกินจำเป็นหรือไม่สำหรับการสอนโมเดลให้ reason ในบางงาน (source: https://ar5iv.labs.arxiv.org/html/2602.04118)

ผล headline คือบน Qwen2.5-7B-Instruct งาน GSM8K โมเดล base ได้ 88.2%, TinyLoRA ที่ train เพียง 13 parameters ได้ 91.8%, TinyLoRA 196 parameters ได้ 92.2%, และ full fine-tuning ได้ 91.7% ตามสรุปของ MarkTechPost (source: https://www.marktechpost.com/2026/03/24/this-ai-paper-introduces-tinylora-a-13-parameter-fine-tuning-method-that-reaches-91-8-percent-gsm8k-on-qwen2-5-7b/)

paper ต้นทางยังรายงานว่าเมื่อใช้ TinyLoRA 196 parameters บน Qwen2.5-7B-Instruct สามารถเก็บ absolute performance improvement ได้ 87% ของ full fine-tuning โดยเฉลี่ยบน math reasoning benchmarks ที่ยากกว่า เช่น MATH500, AIME และ AMC (source: https://ar5iv.labs.arxiv.org/html/2602.04118)

## TinyLoRA ต่างจาก LoRA อย่างไร

LoRA ปกติใส่ low-rank update เข้าไปใน frozen linear layer แต่จำนวน parameter ยังขึ้นกับ model width และ rank แม้ rank ต่ำสุดก็ยังอาจมี trainable parameters ระดับหลักล้านในโมเดลขนาดหลายพันล้าน parameter (source: https://www.marktechpost.com/2026/03/24/this-ai-paper-introduces-tinylora-a-13-parameter-fine-tuning-method-that-reaches-91-8-percent-gsm8k-on-qwen2-5-7b/)

TinyLoRA ต่อยอดจาก LoRA-XS โดยใช้ truncated SVD ของ weight เดิม แล้วแทน trainable matrix ด้วย trainable vector ขนาดเล็กที่ถูก project ผ่าน fixed random tensor จากนั้นใช้ weight tying หรือ parameter sharing ข้าม modules/layers เพื่อให้จำนวน trainable parameters ลดลงได้ถึงระดับ single parameter ใน extreme setting (source: https://ar5iv.labs.arxiv.org/html/2602.04118)

## ทำไม RL สำคัญกว่า SFT ใน paper นี้

ข้อค้นพบสำคัญคือ TinyLoRA ให้ผลดีใน regime ที่ trainable parameters น้อยมากเมื่อใช้ reinforcement learning โดยเฉพาะ GRPO กับ reward ที่ตรวจได้ เช่น math answer ตรงหรือไม่ (source: https://ar5iv.labs.arxiv.org/html/2602.04118)

paper อธิบายว่า SFT ต้องให้โมเดลเรียนจาก token ทั้งหมดใน demonstration รวมทั้ง style, wording และ noise ที่ไม่เกี่ยวกับ task โดยตรง ส่วน RL ให้สัญญาณที่ sparse แต่สะอาดกว่า เพราะ reward-relevant features จะ correlate กับ reward ขณะที่รายละเอียดที่ไม่เกี่ยวข้องจะถูกเฉลี่ยออกเมื่อ sampling หลายครั้ง (source: https://ar5iv.labs.arxiv.org/html/2602.04118)

MarkTechPost สรุปว่า SFT ต้องใช้ update ใหญ่กว่า RL ประมาณ 100 ถึง 1,000 เท่าเพื่อไปถึง performance ใกล้กันใน low-capacity regime นี้ (source: https://www.marktechpost.com/2026/03/24/this-ai-paper-introduces-tinylora-a-13-parameter-fine-tuning-method-that-reaches-91-8-percent-gsm8k-on-qwen2-5-7b/)

## Optimization Notes

paper และบทความสรุประบุข้อสังเกตเชิง implementation หลายอย่าง:

- frozen SVD rank `r=2` ให้ผลดีใน setup ที่รายงาน
- parameter sharing แบบ tiling ตามความลึก/layer ใกล้กันดีกว่า structured sharing ตาม module type
- ใน regime ที่นับ bit เข้ม ๆ การเก็บ trainable parameters เป็น `fp32` อาจคุ้มกว่า bf16/fp16 แบบ bit-for-bit
- Qwen2.5 models ใน setup นี้ใช้ updated parameters น้อยกว่า LLaMA-3 ประมาณ 10 เท่าเพื่อไปถึง performance ใกล้กัน

ข้อสังเกตเหล่านี้ควรมองเป็นผลเฉพาะ setup ของ math reasoning และ TinyLoRA/GRPO ไม่ใช่ default สำหรับ security log triage ใน repo นี้ (source: https://www.marktechpost.com/2026/03/24/this-ai-paper-introduces-tinylora-a-13-parameter-fine-tuning-method-that-reaches-91-8-percent-gsm8k-on-qwen2-5-7b/, https://ar5iv.labs.arxiv.org/html/2602.04118)

## Implications For This POC

สิ่งที่ควรยืมมาใช้:

- เพิ่มมุมมอง cost-aware fine-tuning เช่น gain ต่อ trainable parameter, training time หรือ GPU-hour
- คิดล่วงหน้าว่า evaluator อาจกลายเป็น reward function ได้ ถ้าเราวัดได้ชัดว่า label ถูก, JSON valid, evidence อยู่ใน log จริง และ recommended action ไม่กล่าวเกินหลักฐาน
- ใช้ fixed test split และ metric หลายตัวเพื่อดูว่า update ขนาดเล็กช่วยตรงไหนจริง

สิ่งที่ยังไม่ควรทำใน POC รอบแรก:

- ไม่ควรเปลี่ยน path หลักจาก LoRA/QLoRA ไป TinyLoRA ทันที เพราะ TinyLoRA ยังเป็น research method และ paper ทดสอบกับ math reasoning ไม่ใช่ security log triage
- ไม่ควรเริ่มจาก RL/GRPO ก่อน dataset, heuristic baseline และ evaluator ของเรานิ่ง
- ไม่ควรสรุปว่า parameter น้อยมากจะพอสำหรับ security triage เพราะงานของเราต้องรักษา output schema, evidence extraction และ severity/action semantics พร้อมกัน

## Future Work Idea

เมื่อ evaluator ของโปรเจกต์พร้อมแล้ว อาจทดลอง reward-based tuning ในอนาคตโดยให้ reward จากองค์ประกอบที่ตรวจได้:

- JSON parse สำเร็จ
- schema ครบและ type ถูก
- label ตรง expected label
- evidence เป็น substring ที่มีอยู่จริงใน input log
- severity ตรงหรืออยู่ในระดับที่ยอมรับได้
- recommended action ไม่ claim เกินหลักฐาน

ถ้า reward function เหล่านี้เสถียรพอ แนวคิดแบบ TinyLoRA หรือ RL-based micro-update อาจกลายเป็น experiment รอบหลังสำหรับเปรียบเทียบกับ LoRA/QLoRA ปกติ (source: docs/poc-plan.md, AGENTS.md)

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created curated wiki page for TinyLoRA and 13-parameter reasoning | `docs/tinylora-reasoning-13-parameters.md` | Drafted |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ TinyLoRA เป็น future research reference | วิธีนี้พึ่ง RL/GRPO และ verifiable math reward ซึ่งยังไม่ใช่ path หลักของ POC รอบแรก | Fine-tuning รอบแรกยังเริ่มจาก LFM2-350M ด้วย LoRA/QLoRA |
| 2026-05-16 | จดแนวคิด reward-based tuning ไว้สำหรับหลัง evaluator พร้อม | security log triage มีบาง field ที่ตรวจ reward ได้ เช่น JSON validity, label, evidence substring และ severity | รอบหลังอาจทดลอง RL-based tuning ได้โดยไม่เปลี่ยน scope ปัจจุบัน |

## Related pages

- [[poc-plan]]
- [[slm-fine-tuning-model-choice]]
- [[slm-rag-fine-tuning-hallucination]]
- [[References]]
- [[log]]

# Project Structure Rationale

**Summary**

เอกสารนี้อธิบายว่าทำไม POC `AI Security Log Triage Assistant` ต้องแยก repo เป็น `data/`, `scripts/`, `ml/`, `reports/` และ `frontend/` แทนที่จะเริ่มจาก `frontend/` อย่างเดียว เหตุผลหลักคือโปรเจกต์นี้ต้องพิสูจน์ผลด้วย dataset, baseline, evaluator, fine-tuning และรายงานเปรียบเทียบ ไม่ใช่แค่ทำหน้า demo ให้ดูเหมือนระบบ AI (source: AGENTS.md, docs/poc-plan.md)

**Sources**

- `AGENTS.md` สำหรับ mission, output schema, implementation priorities, evaluation rules และ guardrails เรื่อง training/frontend separation (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ repo structure, success criteria, dataset plan, baseline plan, fine-tuning plan และ evaluation plan (source: docs/poc-plan.md)
- `docs/References.md` สำหรับ rationale จาก Loghub, lm-evaluation-harness, Unsloth, Axolotl, TRL, SigmaHQ และ OWASP (source: docs/References.md)
- `docs/Day1.md` สำหรับ scope ของวันแรกเรื่อง project foundation และ directory structure (source: docs/Day1.md)

**Last updated**

2026-05-16

## Context

งานนี้ไม่ได้เริ่มจากคำถามว่า "จะทำหน้าเว็บยังไง" แต่เริ่มจากคำถามว่า "เราจะพิสูจน์ได้ยังไงว่า fine-tuning ช่วยคัดกรอง security log ได้ดีขึ้นจริง" (source: AGENTS.md, docs/poc-plan.md)

เพราะแบบนี้ repo จึงต้องสะท้อน workflow ทั้งชุด ไม่ใช่มีแค่แอปหน้าเว็บ ถ้ามีแค่ `frontend/` เราอาจทำ demo ได้เร็ว แต่จะตอบคำถามสำคัญไม่ได้ เช่น data มาจากไหน train/test แยกกันจริงไหม baseline คะแนนเท่าไร fine-tuned model ดีขึ้นตรงไหน หรือ output ยังตรง schema เดิมหรือเปล่า

โครงที่เลือกไว้คือ:

```text
data/
  raw/
  generated/
  splits/
  schemas/
scripts/
ml/
reports/
frontend/
```

โครงนี้ตั้งใจบังคับให้โปรเจกต์เดินตามลำดับ `dataset -> baseline -> evaluation -> fine-tuning -> comparison -> demo` มากกว่าเริ่มจาก demo แล้วค่อยหา data และ metric มาประกอบทีหลัง (source: docs/poc-plan.md)

## Why This Shape

### `data/`

`data/` คือพื้นที่ของข้อมูลและ schema กลาง

งาน security log triage ต้องมี dataset ที่ตรวจสอบย้อนกลับได้ โดยเฉพาะเมื่อใช้ synthetic data รอบแรก เราต้องรู้ว่า record ไหนใช้ train, record ไหนใช้ validation, record ไหนเป็น fixed test split และ output ทุก record ตรง schema เดียวกันหรือไม่ (source: AGENTS.md, docs/poc-plan.md)

ถ้าเอาข้อมูลไปปนใน `frontend/` หรือ hard-code ใน component จะทำ demo ได้ แต่ evaluation จะเริ่มไม่สะอาด เพราะตัวอย่างที่โชว์ใน UI อาจปนกับตัวอย่างที่ใช้วัดผลหรือใช้ fine-tune ได้ง่ายเกินไป

### `scripts/`

`scripts/` คือพื้นที่ของ workflow ที่รันซ้ำได้

POC ที่วัดผลได้ต้องมี command สำหรับสร้าง dataset, split dataset, validate schema และ evaluate model หรือ baseline จากข้อมูลชุดเดิม (source: AGENTS.md, docs/poc-plan.md) ถ้า workflow อยู่ในมือคนหรือกระจายอยู่ใน notebook อย่างเดียว ผลลัพธ์จะอธิบายยากว่าได้มาอย่างไร

สำหรับ workflow หลักของ dataset, validation, baseline และ evaluator ให้ใช้ Python ก่อน เพราะต่อกับ ML tooling, JSONL processing, notebook และ fine-tuning path ได้ตรงกว่า ส่วน TypeScript ควรอยู่กับ `frontend/` เป็นหลัก เช่น UI, prompt display, runtime schema mirror หรือ integration wrapper

แนวคิดนี้สอดคล้องกับ reference ด้าน evaluation ที่แยก task, dataset, model adapter และ metric ออกจากกัน เพื่อให้ evaluator ไม่ผูกกับ model ตัวใดตัวหนึ่ง (source: docs/References.md)

### `ml/`

`ml/` คือพื้นที่ของ fine-tuning และ inference ฝั่งโมเดล

fine-tuning มี dependency และ environment คนละโลกกับ frontend เช่น PyTorch, Transformers, Unsloth, CUDA, notebook และ checkpoint (source: docs/References.md) ถ้าเอาส่วนนี้ไปปนกับ Next.js app จะทำให้ frontend หนักและเปราะโดยไม่จำเป็น

การแยก `ml/` ทำให้โปรเจกต์ยังมี path ที่รันได้โดยไม่ต้องมี GPU ตาม guardrail ของ POC ส่วนการ train ด้วย LoRA หรือ QLoRA เป็น optional path ที่เดินต่อได้เมื่อพร้อม (source: AGENTS.md, docs/poc-plan.md)

### `reports/`

`reports/` คือพื้นที่ของผลลัพธ์ที่ใช้คุยเรื่องคุณภาพ

เป้าของ POC ไม่ใช่แค่ให้ model ตอบได้ แต่ต้องเทียบได้ว่า heuristic baseline, model baseline และ fine-tuned model ต่างกันอย่างไรบน test split เดียวกัน (source: docs/poc-plan.md) รายงานจึงควรเก็บทั้ง machine-readable JSON และ human-readable summary เมื่อ evaluator พร้อม

ถ้าไม่มี `reports/` โปรเจกต์จะเหลือแค่ความรู้สึกว่า model ตอบดีขึ้น แต่ไม่มีหลักฐานให้ย้อนดูหรือคุยกับ stakeholder ได้

### `frontend/`

`frontend/` ยังจำเป็น เพราะ demo UI คือวิธีให้คนลองระบบจริง

แต่ frontend ไม่ควรเป็นที่เก็บทุกอย่าง หน้าที่หลักของ `frontend/` คือรับ log, แสดง structured result, highlight evidence, เปรียบเทียบ baseline กับ model และเรียก shared logic ที่เกี่ยวกับ triage (source: AGENTS.md, docs/poc-plan.md)

ส่วน data, training และ reports ควรอยู่ข้างนอก เพื่อไม่ให้ repo กลายเป็นเพียง "Next.js app ที่มี AI feature" แทนที่จะเป็น "fine-tuning and evaluation POC ที่มี demo UI"

## Alternatives Considered

### Alternative 1: `frontend/` Only

ทางนี้เร็วที่สุดสำหรับทำหน้าจอแรก แต่ไม่เหมาะกับ POC นี้ เพราะ data, schema, baseline และ metric จะปนอยู่กับ UI ง่ายเกินไป

เลือกไม่ใช้เป็นแกนหลัก เพราะโปรเจกต์นี้ต้องมี fixed test split, evaluator และรายงานเปรียบเทียบ ไม่ใช่แค่หน้าเว็บที่เรียก model แล้วแสดงผล (source: AGENTS.md, docs/poc-plan.md)

### Alternative 2: Notebook-First

ทางนี้เหมาะกับการทดลองโมเดลเร็ว ๆ โดยเฉพาะ fine-tuning แต่ถ้าใช้ notebook เป็นแกน repo จะทำให้ workflow สำหรับ generate, split และ evaluate รันซ้ำยาก

เลือกให้ notebook อยู่ใต้ `ml/notebooks/` แทน เพื่อใช้เป็นพื้นที่ทดลองหรือ Colab guide ส่วน command ที่ต้อง reproducible ควรอยู่ใน `scripts/` (source: docs/poc-plan.md, docs/References.md)

### Alternative 3: Put Training Inside Frontend

ทางนี้อาจดูสะดวกเพราะ logic อยู่ในที่เดียว แต่จะผูก dependency หนักของ ML เข้ากับ demo app

เลือกไม่ใช้ เพราะ POC ต้องมี path ที่รันได้โดยไม่ต้อง GPU และ frontend ควร consume adapter หรือ endpoint ไม่ใช่นำ training code เข้ามาโดยตรง (source: AGENTS.md)

### Alternative 4: Put Everything At Repo Root

ทางนี้เริ่มง่าย แต่เมื่อมี dataset, generated split, evaluator output, training script, checkpoint และ UI มากขึ้น root จะอ่านยากทันที

เลือกไม่ใช้ เพราะ repo structure ควรบอกบทบาทของไฟล์ตั้งแต่แรก คนเปิด repo ควรเห็นได้ทันทีว่าอะไรคือ data, อะไรคือ script, อะไรคือ training, อะไรคือ report และอะไรคือ frontend

## Decision

ใช้ repo structure แบบแยกบทบาท:

```text
data/      ข้อมูลและ schema
scripts/   workflow ที่รันซ้ำได้
ml/        fine-tuning และ inference ฝั่งโมเดล
reports/   ผล evaluation และ comparison
frontend/  demo UI และ shared triage logic
```

การตัดสินใจนี้ช่วยให้ Day 1 ไม่ใช่แค่ scaffold project แต่เป็นการวาง foundation ให้ Day 2 dataset, Day 3 baseline, Day 4 evaluator, Day 5 adapters, Day 6 UI และ Day 7 fine-tuning/report เดินต่อกันได้ (source: docs/Day1.md, docs/poc-plan.md)

## How To Use This In Day 1

สำหรับ Day 1 เรายังไม่จำเป็นต้องลงมือสร้างทุกไฟล์ทันที เอกสารนี้ใช้เป็นเหตุผลประกอบก่อนลงมือ:

- ถ้าจะสร้าง `data/` ให้ถามว่า schema และ split จะอยู่ตรงไหน
- ถ้าจะสร้าง `scripts/` ให้ถามว่า workflow ไหนต้องรันซ้ำได้
- ถ้าจะสร้าง `ml/` ให้ถามว่าอะไรต้องแยกจาก frontend เพราะ dependency หรือ GPU
- ถ้าจะสร้าง `reports/` ให้ถามว่า metric อะไรต้องเก็บเพื่อเทียบผล
- ถ้าจะทำ `frontend/` ให้ถามว่า UI ใช้ shared triage logic ตรงไหน และอะไรไม่ควรปนเข้ามา

เมื่อจะเริ่ม implementation จริง ค่อยใช้เอกสารนี้เป็น checkpoint ว่าโครงที่สร้างยังรับใช้เป้าหมาย evaluation-first อยู่หรือไม่

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created project structure rationale page | `docs/project-structure-rationale.md` | Drafted |
| 2026-05-16 | Codex | Clarified Python-first role for reproducible scripts | `scripts/`, `frontend/` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | แยก repo structure ตามบทบาทของ POC | งานนี้ต้องพิสูจน์ผลด้วย data, scripts, ML training, reports และ UI ไม่ใช่ frontend อย่างเดียว | Day 1 foundation จะต่อกับ dataset, evaluator, fine-tuning และ comparison report ได้ |
| 2026-05-16 | เก็บ training path แยกจาก frontend | fine-tuning มี dependency และ environment คนละชุดกับ demo UI | frontend ยังรันได้แม้ไม่มี GPU และ `ml/` ขยายต่อได้โดยไม่ทำ app หนัก |
| 2026-05-16 | ให้ `scripts/` เป็น Python-first | command ที่สร้าง dataset และวัดผลต้องต่อกับ ML/evaluation ecosystem ได้ง่าย | `scripts/` จะเก็บ Python workflow เป็นหลัก ส่วน TypeScript อยู่ใน `frontend/` |

## Related pages

- [[Day1]]
- [[Day2]]
- [[poc-plan]]
- [[References]]

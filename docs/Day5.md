# Day 5: Fine-Tuning Path With Unsloth

**Summary**

วันที่ห้าสร้างทาง fine-tune small model ด้วย Unsloth โดยเริ่มจาก LoRA หรือ QLoRA เป้าหมายคือให้มี training script, config และ inference path ที่ต่อกับ dataset ของ repo ได้ ไม่จำเป็นต้อง train จบในเครื่อง dev ถ้าไม่มี GPU

**Sources**

- `docs/poc-plan.md` สำหรับ fine-tuning plan และ model candidate (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ fine-tuning guidance และ separation ระหว่าง frontend กับ training code (source: AGENTS.md)
- `References.md` สำหรับ Unsloth, Axolotl และ Hugging Face TRL (source: References.md)
- `docs/raw/What Small Language Model Is Best for Fine-Tuning.md` สำหรับเหตุผลที่เลือก LFM2-350M เป็น candidate แรกเมื่อทรัพยากรจำกัด (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md)
- `llm-wiki/SKILL.md` สำหรับ source tracking และ append-only log (source: SKILL.md)

**Last updated**

2026-05-16

## Goal

มี fine-tuning workflow ที่คนอื่นเปิดตามได้ ตั้งแต่ config, dataset path, training command, output adapter และ inference command

## Scope

- เพิ่ม `ml/unsloth/config.example.yaml`
- เพิ่ม `ml/unsloth/train_lora.py`
- เพิ่ม `ml/unsloth/inference.py`
- เพิ่ม `docs/fine-tuning-notes.md`
- ระบุ LFM2-350M เป็น model candidate รอบแรก
- ระบุ hardware assumption และ fallback path
- อธิบายวิธี export LoRA adapter หรือ merged model

## Checklist

- [ ] เลือก LFM2-350M เป็น base model candidate รอบแรก
- [ ] กำหนด prompt formatting สำหรับ train
- [ ] map JSONL dataset เข้ากับ training format
- [ ] เพิ่ม LoRA config
- [ ] เพิ่ม validation split config
- [ ] เพิ่ม output directory convention
- [ ] เพิ่ม inference script สำหรับ checkpoint
- [ ] เพิ่ม notes สำหรับ Colab/GPU
- [ ] บันทึก known limitations

## Acceptance Criteria

- training script อ่าน `data/splits/train.jsonl` ได้
- validation ใช้ `data/splits/validation.jsonl`
- test split ไม่ถูกใช้ระหว่าง training
- config แยกจาก script
- คนที่มี GPU สามารถเริ่ม train จาก docs ได้
- คนที่ไม่มี GPU ยังรันส่วน frontend, dataset และ evaluation ได้

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 5 plan page | `docs/Day5.md` | Planned |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ Unsloth เป็น path หลัก | เหมาะกับ LoRA/QLoRA และ small model POC | training assets อยู่ใน `ml/unsloth/` |
| 2026-05-16 | เอาแนว config discipline จาก Axolotl | training run ต้องย้อนดูค่าได้ | เพิ่ม `config.example.yaml` ตั้งแต่แรก |
| 2026-05-16 | เริ่ม fine-tune ด้วย LFM2-350M | เครื่องมีทรัพยากรจำกัด และ LFM2-350M เป็นโมเดลเล็กที่ benchmark ภายนอกชี้ว่า tunable สูง | Qwen 1.5B/3B/4B ถูกเลื่อนไปเป็น candidate สำหรับรอบเปรียบเทียบภายหลัง |

## Notes

fine-tune รอบแรกไม่ต้องไล่ benchmark หลายโมเดล ให้เริ่มจาก LFM2-350M เพื่อประหยัดทรัพยากร สิ่งที่ต้องได้คือ training path ที่ reproducible และ output ที่ evaluator เรียกเทียบกับ baseline ได้

## Related pages

- [[Day4]]
- [[Day6]]
- [[poc-plan]]
- [[References]]

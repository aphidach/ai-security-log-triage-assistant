# Day 6: GPU Training, Fine-Tuned Evaluation And Comparison Report

**Summary**

วันที่หกเริ่มจากเติม GPU training implementation ใน `ml/unsloth/train_lora.py` ก่อน จากนั้นค่อยเอา fine-tuned adapter ที่ได้มาวัดกับ fixed test split เดียวกับ baseline แล้วเขียน comparison report แบบตรงไปตรงมา เป้าหมายคืออธิบายให้ได้ว่า fine-tune ช่วยตรงไหน ยังพลาดตรงไหน และควรปรับ dataset หรือ prompt อย่างไรต่อ

**Sources**

- `docs/poc-plan.md` สำหรับ evaluation plan และ report format (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ evaluation rules และคำเตือนเรื่อง overclaim (source: AGENTS.md)
- `docs/References.md` สำหรับ lm-evaluation-harness, SigmaHQ และ Unsloth mapping (source: docs/References.md)
- `docs/Day5.md` สำหรับ fine-tuning path ที่เตรียมไว้ก่อน Day 6 (source: docs/Day5.md)
- `docs/fine-tuning-notes.md` สำหรับ GPU/Colab notes, limitation และ Day 6 handoff (source: docs/fine-tuning-notes.md)
- `ml/unsloth/train_lora.py` สำหรับ preflight entrypoint ที่ต้องเติม GPU training body (source: ml/unsloth/train_lora.py)
- `ml/unsloth/config.example.yaml` สำหรับ model, LoRA, training และ output config (source: ml/unsloth/config.example.yaml)
- `llm-wiki/SKILL.md` สำหรับ log append-only และ related pages (source: SKILL.md)

**Last updated**

2026-05-17

## Goal

ทำ GPU train รอบแรกให้ได้ LoRA adapter ก่อน แล้วสร้างผลเทียบ baseline vs fine-tuned model ที่มีตัวเลข, error analysis และข้อสรุปที่เอาไปคุยกับ stakeholder ได้

## Scope

- เติม GPU training implementation ใน `ml/unsloth/train_lora.py`
- รัน train ด้วย `ml/unsloth/config.example.yaml`
- smoke test LoRA adapter ด้วย `ml/unsloth/inference.py`
- รัน evaluator กับ fine-tuned adapter หรือ endpoint ที่ expose แบบ OpenAI-compatible
- เขียน `reports/finetuned-eval.json`
- update `reports/comparison.md`
- วิเคราะห์ false positive และ false negative
- ตรวจ evidence quality
- บันทึก limitation และ next experiment

## Checklist

- [ ] เติม GPU training implementation ใน `ml/unsloth/train_lora.py`
- [ ] รัน training บน GPU/Colab ด้วย config รอบแรก
- [ ] save LoRA adapter ไปที่ `ml/unsloth/outputs/lfm2-350m-security-triage-lora`
- [ ] smoke test adapter ด้วย `ml/unsloth/inference.py`
- [ ] รัน evaluation ด้วย fixed test split
- [ ] เก็บ raw outputs เท่าที่จำเป็นสำหรับ debug
- [ ] เขียน `reports/finetuned-eval.json`
- [ ] update `reports/comparison.md`
- [ ] เพิ่มตาราง metric เทียบ heuristic, base model และ fine-tuned model
- [ ] เพิ่ม error analysis ราย label
- [ ] เพิ่ม note ว่า dataset เป็น synthetic
- [ ] ระบุ next dataset improvements

## Acceptance Criteria

- baseline และ fine-tuned ใช้ test split เดียวกัน
- training ไม่อ่าน `data/splits/test.jsonl`
- มี LoRA adapter output หรือบันทึกชัดเจนว่ารัน GPU ไม่สำเร็จเพราะอะไร
- local inference smoke test ผ่านอย่างน้อย 1 log หรือบันทึก error ชัดเจน
- report บอก metric ครบ
- ถ้า fine-tuned แพ้บาง metric ต้องเขียนไว้ตรง ๆ
- มีตัวอย่าง error อย่างน้อย 3-5 เคส
- ไม่มีการ claim ว่า model ยืนยันการถูก hack ได้จาก log เส้นเดียว

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 6 plan page | `docs/Day6.md` | Planned |
| 2026-05-17 | Codex | Moved GPU training implementation into the first Day 6 task | `docs/Day6.md`, `docs/fine-tuning-notes.md` | Planned |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ fixed test split เท่านั้น | comparison ต้องแฟร์และรันซ้ำได้ | ห้ามแตะ test split ระหว่าง train |
| 2026-05-16 | report ต้องบอกข้อจำกัดชัดเจน | synthetic dataset อาจทำให้ผลดูดีเกินจริง | stakeholder จะเข้าใจว่า POC ยังไม่ใช่ production detector |
| 2026-05-17 | เริ่ม Day 6 ด้วย GPU training body ก่อน evaluation | Day 5 เตรียม config, split guard, training format และ inference path แล้ว แต่ยังไม่มี adapter output ถ้าไม่ train ก่อนก็ evaluate fine-tuned model ไม่ได้ | `ml/unsloth/train_lora.py` เป็นงานแรกของ Day 6; evaluation/report ทำหลังมี adapter หรือมีเหตุผลว่าทำไม train ไม่สำเร็จ |

## Notes

วันที่หกเป็นวันที่ POC เริ่มมีน้ำหนัก เพราะมีทั้ง adapter จากการ train และตัวเลขให้คุย ถ้า train ไม่สำเร็จหรือผลยังไม่สวย ให้เก็บเป็น insight ว่า environment, dataset หรือ schema ยังต้องปรับ ไม่ต้องกลบจุดอ่อน

## Related pages

- [[Day5]]
- [[Day7]]
- [[poc-plan]]
- [[References]]

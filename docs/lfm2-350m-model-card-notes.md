# LFM2-350M Model Card Notes

**Summary**

หน้านี้สรุปคำแนะนำจาก model card ของ `unsloth/LFM2-350M` บน Hugging Face และแปลผลเข้ากับ POC `AI Security Log Triage Assistant` โดยเฉพาะ config v3.3, training format, inference parameters และ runtime caveat จุดสำคัญคือ model card แนะนำให้ fine-tune LFM2 model บน use case แคบ ๆ ซึ่งเข้ากับงาน structured security-log triage ของเรา แต่ยังต้องวัดด้วย hard-contrast probe และ mini semantic eval แทนการเชื่อว่า model card guarantee คุณภาพในโดเมนนี้ (source: https://huggingface.co/unsloth/LFM2-350M, source: docs/output-structure-fix/phase-6-v3-3-targeted-canary.md)

**Sources**

- Hugging Face model card `unsloth/LFM2-350M` สำหรับ model details, recommended generation parameters, chat template, runtime notes และ fine-tuning notebooks (source: https://huggingface.co/unsloth/LFM2-350M)
- `ml/unsloth/config.v3-3.yaml` สำหรับ config ปัจจุบันของ v3.3 targeted hard-contrast training run (source: ml/unsloth/config.v3-3.yaml)
- `ml/unsloth/training_format.py` สำหรับการ render dataset เป็น chat messages ด้วย tokenizer chat template (source: ml/unsloth/training_format.py)
- `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md` สำหรับ run order ว่า hard-contrast probe ต้องมาก่อน mini semantic eval และ fixed split (source: docs/output-structure-fix/phase-6-v3-3-targeted-canary.md)
- `docs/slm-fine-tuning-model-choice.md` สำหรับ rationale เดิมที่เลือก LFM2-350M เป็น candidate แรกของ POC (source: docs/slm-fine-tuning-model-choice.md)

**Last updated**

2026-05-21

## Model Card Takeaways

คำแนะนำหลักจาก model card:

- LFM2 เป็น hybrid model สำหรับ edge/on-device deployment ที่เน้น quality, speed และ memory efficiency
- รุ่น `350M` มีประมาณ 354M parameters, precision เป็น `bfloat16`, context length 32,768 tokens และใช้ architecture ผสม short convolution กับ grouped-query attention
- เพราะ model มีขนาดเล็ก เขาแนะนำให้ fine-tune บน narrow use cases เพื่อดึง performance ออกมาให้คุ้ม
- use case ที่เขาระบุว่าเหมาะ ได้แก่ agentic tasks, data extraction, RAG, creative writing และ multi-turn conversations
- เขาไม่แนะนำให้ใช้กับงานที่ knowledge-intensive มากหรือ programming-heavy
- recommended generation parameters คือ `temperature=0.3`, `min_p=0.15`, และ `repetition_penalty=1.05`
- chat template เป็น ChatML-like และควรใช้ `tokenizer.apply_chat_template()`
- fine-tuning path ที่เขาชี้ไว้คือ SFT + LoRA ผ่าน TRL และอีก path คือ DPO

## Fit For This Project

งานของเราเข้าข่าย narrow use case ที่ model card แนะนำ เพราะ label taxonomy จำกัดไว้ที่ 5 labels, output schema คงที่, และ evidence ต้องเป็น substring จาก log input ไม่ใช่ความรู้เปิดกว้างจากโลกภายนอก (source: AGENTS.md, docs/label-taxonomy.md, data/schemas/triage-output.schema.json)

ดังนั้น direction ปัจจุบันยังสมเหตุสมผล:

- ใช้ `unsloth/LFM2-350M` เป็น first fine-tuning candidate
- ใช้ SFT + LoRA ก่อน DPO หรือ model sweep
- ใช้ `apply_chat_template()` ผ่าน training formatter
- โฟกัส hard contrast examples และ targeted weighting แทนการเพิ่ม prompt ยาว ๆ
- วัดด้วย hard-contrast probe, mini semantic eval และ fixed split ตามลำดับ

## Config Implications

สิ่งที่ config v3.3 ตรงกับ model card แล้ว:

| Model-card guidance | Current repo status |
| --- | --- |
| Fine-tune on narrow use cases | v3.3 split เจาะ security-log triage 5 labels และเพิ่ม SQLi/port-scan targeted cases |
| Use SFT + LoRA | `ml/unsloth/train_lora.py` ใช้ SFT training path กับ LoRA config |
| Use ChatML-like chat template | `ml/unsloth/training_format.py` ใช้ tokenizer chat template |
| Use `bfloat16` where available | `ml/unsloth/config.v3-3.yaml` ตั้ง `dtype: bfloat16` |
| Keep generation controlled | adapter/eval path ควรทดสอบ `repetition_penalty=1.05` และ `temperature=0.3` หลัง v3.3 train |

สิ่งที่ควรระวัง:

- model card แนะนำ `min_p=0.15` แต่ OpenAI-compatible runtimes บางตัวอาจไม่รองรับ `min_p`; ถ้า backend ไม่รับ parameter นี้ ห้ามบังคับใส่จน request fail
- structured-output eval อาจต้องใช้ deterministic หรือ constrained decoding มากกว่า sampling recommendation ปกติ ให้ถือ generation parameters เป็น candidate สำหรับ probe ไม่ใช่ default ที่ต้องใช้ทุก run
- README/model card text ระบุว่า vLLM support is coming ในส่วน run instructions ดังนั้น vLLM path ของเราต้องยังผ่าน smoke/probe จริงก่อนเสมอ แม้หน้า Hugging Face UI จะมี generated vLLM snippet

## Recommended Next Probe

หลัง train v3.3 และ serve endpoint แล้ว ให้ทดสอบสองชุดก่อนตัดสินใจ:

1. hard-contrast memorization probe เดิมด้วย structured output mode ที่ผ่าน contract แล้ว
2. generation-parameter probe ที่ลองเพิ่ม `repetition_penalty=1.05` และถ้า runtime รองรับให้ลอง `temperature=0.3`, `min_p=0.15`

ถ้า parameter ชุดนี้ช่วยลด loop หรือ collapse ให้บันทึกใน report เป็น runtime-setting decision แยกจาก training-data decision ไม่ควรปนกับ fixed test split (source: docs/output-structure-fix/phase-6-v3-3-targeted-canary.md)

## Decision

ยังไม่ต้องเปลี่ยน base model จาก LFM2-350M จาก model card เพียงอย่างเดียว เพราะ official guidance สนับสนุนงานเฉพาะทางแบบเราอยู่แล้ว สิ่งที่ควรทำต่อคือวัดว่า v3.3 targeted training และ generation settings ช่วย SQLi/port-scan canary จริงหรือไม่

ถ้า v3.3 ยังไม่ขยับหลัง hard-contrast probe ให้ค่อยแยก decision เป็นสองทาง:

- data/training issue: เพิ่มหรือปรับ targeted examples ต่อ
- model/runtime issue: เทียบ model candidate ใหญ่ขึ้นหรือเปลี่ยน serving runtime

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Created model-card note for `unsloth/LFM2-350M` and mapped guidance to v3.3 training/eval workflow | `ml/unsloth/config.v3-3.yaml`, `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md` | Created |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Keep LFM2-350M as the current narrow-task fine-tuning candidate | Hugging Face model card recommends fine-tuning small LFM2 models on narrow use cases, and this project is a narrow structured triage task | Continue v3.3 hard-contrast workflow before considering larger model candidates |
| 2026-05-21 | Treat recommended generation parameters as probe candidates, not fixed defaults | Structured-output evaluation may need constrained or deterministic decoding, and not every runtime supports `min_p` | Try `temperature=0.3`, `min_p=0.15`, and `repetition_penalty=1.05` only in explicit runtime probes |

## Related pages

- [[fine-tuning-notes]]
- [[slm-fine-tuning-model-choice]]
- [[output-structure-fix/phase-6-v3-3-targeted-canary]]
- [[model-repetition-loop-diagnostics]]
- [[References]]

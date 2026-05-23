# Small Model Fine-Tuning Candidates For 6GB GPU

**Summary**

หน้านี้สรุปตัวเลือก small model สำหรับ fine-tune งาน security log triage ภายใต้ข้อจำกัด GPU VRAM ประมาณ `6GB` และขนาดโมเดลไม่เกิน `4B` parameters จุดยืนหลักคือให้ใช้ LoRA/QLoRA ก่อน full fine-tuning, เริ่มจากโมเดลระดับ `0.6B-1.7B` เพื่อให้ workflow นิ่ง แล้วค่อยลอง `3B-4B` เป็น stretch target

**Sources**

- `docs/raw/What Small Language Model Is Best for Fine-Tuning.md` สำหรับผลสรุป Distil Labs SLM benchmark และเหตุผลด้าน tunability/performance tradeoff (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md)
- `docs/slm-fine-tuning-model-choice.md` สำหรับ decision เดิมที่เริ่มจาก LFM2-350M ใน POC รอบแรก (source: docs/slm-fine-tuning-model-choice.md)
- `docs/poc-plan.md` สำหรับ project mission, output schema, fixed test split และ evaluation-first workflow (source: docs/poc-plan.md)
- `docs/fine-tuning-notes.md` สำหรับ Unsloth LoRA/QLoRA path และสถานะ fine-tuning ใน repo (source: docs/fine-tuning-notes.md)
- Unsloth VRAM requirements: https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements (source: Unsloth docs)
- Qwen3-1.7B model card: https://huggingface.co/Qwen/Qwen3-1.7B (source: Hugging Face model card)
- Qwen3-4B-Instruct-2507 model card: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 (source: Hugging Face model card)
- LiquidAI LFM2-1.2B model card: https://huggingface.co/LiquidAI/LFM2-1.2B (source: Hugging Face model card)
- Phi-4-mini-instruct model card: https://huggingface.co/microsoft/Phi-4-mini-instruct (source: Hugging Face model card)
- Gemma-3-1B-it model card: https://huggingface.co/google/gemma-3-1b-it (source: Hugging Face model card)
- Llama-3.2-3B-Instruct model card: https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct (source: Hugging Face model card)

**Last updated**

2026-05-23

## Scope

ใช้หน้านี้เป็น candidate intake note สำหรับรอบทดลองต่อจาก `LFM2-350M` ไม่ใช่ leaderboard สรุปว่าโมเดลไหนดีที่สุดในงาน security log triage จริง งานนี้ยังต้องยึด evaluator ของ repo, hard-contrast probe, schema gate และ fixed split policy เดิม

ขอบเขตของหน้านี้:

- พิจารณาเฉพาะโมเดลขนาดไม่เกิน `4B`
- สมมติ GPU VRAM ประมาณ `6GB`
- เน้น supervised fine-tuning แบบ LoRA/QLoRA
- ใช้กับ output schema และ label taxonomy เดิมของ POC
- ไม่เปิด `data/splits/test.jsonl` เพื่อจูน candidate

## Memory Rule Of Thumb

GPU `6GB` ควรถูกมองเป็นพื้นที่สำหรับ QLoRA 4-bit และ short-context experiment มากกว่า full fine-tuning โมเดล 3B-4B อาจโหลดได้ในบาง setup แต่ training memory ไม่ได้ขึ้นกับ parameter count อย่างเดียว ยังมี activation memory, sequence length, batch size, optimizer state, LoRA target modules, tokenizer และ runtime overhead ด้วย (source: Unsloth docs)

ค่าเริ่มต้นที่ควรใช้ก่อน:

```yaml
model:
  load_in_4bit: true
  max_seq_length: 1024 # ลดเป็น 512 ถ้า OOM

training:
  per_device_train_batch_size: 1
  gradient_accumulation_steps: 8
  max_steps: 100-300
  gradient_checkpointing: true

lora:
  r: 8
  lora_alpha: 16
  lora_dropout: 0.0
```

ถ้า OOM ให้ลดตามลำดับนี้ก่อนเปลี่ยนโมเดล: `max_seq_length`, batch/effective batch, LoRA rank, target modules แล้วค่อยลดขนาด base model

## Candidate Shortlist

| Priority | Model | Size | Role | 6GB fit | Why it is interesting | Caveat |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | `Qwen/Qwen3-1.7B` | 1.7B | first non-LFM capacity pilot | Good | ใหญ่กว่า LFM2-350M ชัดเจน แต่ยังไม่หนักเท่า 3B-4B; เป็น candidate ที่สมดุลที่สุดสำหรับ 6GB | ต้อง benchmark กับ hard-contrast ของ repo เอง ห้ามสรุปจาก model card |
| 2 | `LiquidAI/LFM2-1.2B` หรือ LFM2.5 1.2B instruct | 1.2B | same-family capacity increase | Good | ยังอยู่ใน LiquidAI/LFM family ที่ benchmark เดิมชี้เรื่อง tunability และต่อยอดจาก LFM2-350M ได้ตรง | อาจยังติดข้อจำกัดเชิง semantic boundary คล้าย LFM2-350M ต้องวัดจริง |
| 3 | `Qwen/Qwen3-0.6B` | 0.6B | fast iteration / smoke candidate | Excellent | เหมาะกับการทดสอบ data format, prompt, schema, LoRA config และ runtime pipeline แบบเร็ว | capacity ceiling ต่ำกว่า 1.7B/3B |
| 4 | `meta-llama/Llama-3.2-1B-Instruct` | 1B | small instruct baseline | Good | เป็น instruct baseline ที่น่าเทียบกับ Qwen/LFM ในงาน structured triage | มี gated access และ license เฉพาะ ต้องจัดการสิทธิ์ก่อนใช้ |
| 5 | `meta-llama/Llama-3.2-3B-Instruct` | 3B | architecture comparator | Borderline | อยู่ใต้ 4B และเป็น benchmark family ที่คนรู้จักดี | 6GB ต้องคุม sequence/batch แน่นมาก |
| 6 | `microsoft/Phi-4-mini-instruct` | 3.8B | reasoning-heavy stretch target | Borderline | ขนาดยังไม่เกิน 4B และน่าสนใจถ้าต้องการ reasoning/structured answer ที่ดีกว่า | ควรลองหลัง pipeline 1B-1.7B นิ่งแล้ว เพราะ memory เสี่ยงกว่า |
| 7 | `Qwen/Qwen3-4B-Instruct-2507` | 4B | strongest <=4B stretch target | Borderline | Distil Labs benchmark จัด Qwen3-4B เป็นตัวเลือก fine-tuned performance สูงมากในกลุ่มเล็ก | ไม่ควรเป็นตัวแรกบน 6GB; ต้อง short sequence และ QLoRA เท่านั้น |
| 8 | `google/gemma-3-1b-it` | 1B | lightweight extra baseline | Good | เป็นอีกตระกูลหนึ่งสำหรับเทียบ behavior ของ small instruct model | ต้องดู license/model format และอย่าใช้เป็น path หลักก่อน candidate ข้างบน |
| 9 | `google/gemma-3-4b-it` | 4B | Gemma stretch comparator | Borderline | มีประโยชน์ถ้าอยากเทียบ family ใต้ 4B | เป็น image-text-to-text model และหนักกว่า 1B; ไม่ใช่ first pick บน 6GB |

## Recommended Experiment Order

1. เริ่มจาก `Qwen/Qwen3-1.7B` ด้วย QLoRA 4-bit เพราะเป็นจุดสมดุลระหว่าง capacity กับ memory risk
2. ลอง `LiquidAI/LFM2-1.2B` หรือ LFM2.5 1.2B instruct ถ้าต้องการเพิ่ม capacity แต่ยังรักษา family เดิมของ LFM2
3. ใช้ `Qwen/Qwen3-0.6B` เป็น fast-iteration candidate เมื่ออยากทดสอบ dataset/prompt/training code โดยไม่เสีย GPU time มาก
4. ขยับไป `Llama-3.2-3B-Instruct` หรือ `Phi-4-mini-instruct` หลังจาก 1B-1.7B pipeline ผ่าน output/schema และ hard-contrast gate แล้ว
5. เก็บ `Qwen/Qwen3-4B-Instruct-2507` เป็น stretch target ใต้ 4B ไม่ใช่ candidate แรกสำหรับ GPU 6GB

## Evaluation Gates

candidate ใหม่ทุกตัวต้องผ่าน gate เดียวกับงาน fine-tuning เดิม:

- ห้ามใช้ `data/splits/test.jsonl` ระหว่าง candidate tuning
- ต้องผ่าน output contract ก่อนดู semantic metric: JSON parse success, schema success และ invalid output count
- ต้องรัน smoke output-contract split ก่อน hard-contrast
- ต้องรัน hard-contrast probe ด้วย prompt/schema เดิมก่อนเปิด mini semantic eval
- ควรให้ hard-contrast `label_accuracy >= 0.90`, JSON/schema `1.0`, invalid `0` ก่อนพิจารณา fixed split gate
- ต้องเทียบกับ heuristic baseline และ LFM2 run เดิม ไม่ใช่ดูผลเดี่ยว ๆ
- ต้องบันทึก runtime setting เช่น temperature, max tokens, context length, quantization, LoRA rank และ GPU memory behavior

## Decision For This Repo

ภายใต้ GPU `6GB` และ requirement ว่าโมเดลต้องไม่เกิน `4B`, candidate ถัดไปที่เหมาะสุดคือ `Qwen/Qwen3-1.7B` ไม่ใช่ `Qwen3-4B` ทันที เหตุผลคือ 1.7B ใหญ่กว่า LFM2-350M มากพอจะทดสอบ capacity hypothesis แต่ยังน่าคุม memory ได้กว่า 3B-4B

`Qwen3-4B-Instruct-2507` ยังเป็น candidate ที่น่าสนใจมากจาก benchmark ด้าน fine-tuned performance แต่ใน repo นี้ควรอยู่ในกลุ่ม stretch target จนกว่า QLoRA pipeline, prompt/schema contract และ hard-contrast gate ของ candidate เล็กกว่าจะนิ่งก่อน

`LFM2-350M` ยังเป็น resource-constrained baseline ที่ถูกต้องสำหรับพิสูจน์ workflow ส่วน `LFM2-1.2B` เป็น candidate ที่ดีถ้าอยากขยายภายใน LiquidAI/LFM family โดยไม่กระโดดไป 4B เร็วเกินไป

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-23 | Codex | Created 6GB small-model candidate guidance from local SLM benchmark notes and current model-card research | `docs/small-model-fine-tuning-candidates-6gb.md` | Drafted |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Start the next <=4B/6GB candidate search with `Qwen/Qwen3-1.7B` | It offers a better capacity step than 350M while staying more realistic on 6GB than 3B-4B models | Future candidate config should begin below 2B, with 4B kept as a stretch experiment |

## Related pages

- [[fine-tuning-notes]]
- [[slm-fine-tuning-model-choice]]
- [[poc-plan]]
- [[References]]
- [[output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan]]

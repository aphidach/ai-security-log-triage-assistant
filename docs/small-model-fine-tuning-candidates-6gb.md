# Small Model Fine-Tuning Candidates For 6GB GPU

**Summary**

หน้านี้สรุปตัวเลือก small model สำหรับ fine-tune งาน security log triage ภายใต้ข้อจำกัด GPU VRAM ประมาณ `6GB` และขนาดโมเดลไม่เกิน `4B` parameters จุดยืนหลักคือให้ใช้ LoRA/QLoRA ก่อน full fine-tuning, เริ่มจากโมเดลระดับ `1.2B-2B` เพื่อให้ workflow นิ่ง แล้วค่อยลอง `3B-4B` เป็น stretch target

**Sources**

- `docs/raw/What Small Language Model Is Best for Fine-Tuning.md` สำหรับผลสรุป Distil Labs SLM benchmark และเหตุผลด้าน tunability/performance tradeoff (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md)
- `docs/slm-fine-tuning-model-choice.md` สำหรับ decision เดิมที่เริ่มจาก LFM2-350M ใน POC รอบแรก (source: docs/slm-fine-tuning-model-choice.md)
- `docs/poc-plan.md` สำหรับ project mission, output schema, fixed test split และ evaluation-first workflow (source: docs/poc-plan.md)
- `docs/fine-tuning-notes.md` สำหรับ Unsloth LoRA/QLoRA path และสถานะ fine-tuning ใน repo (source: docs/fine-tuning-notes.md)
- Unsloth VRAM requirements: https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements (source: Unsloth docs)
- Qwen3-1.7B model card: https://huggingface.co/Qwen/Qwen3-1.7B (source: Hugging Face model card)
- Qwen3-4B-Instruct-2507 model card: https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507 (source: Hugging Face model card)
- LiquidAI LFM2-1.2B model card: https://huggingface.co/LiquidAI/LFM2-1.2B (source: Hugging Face model card)
- LiquidAI LFM2.5-1.2B-Instruct model card: https://huggingface.co/LiquidAI/LFM2.5-1.2B-Instruct (source: Hugging Face model card)
- Qwen3.5-2B model card: https://huggingface.co/Qwen/Qwen3.5-2B (source: Hugging Face model card)
- Qwen3.5-4B model card: https://huggingface.co/Qwen/Qwen3.5-4B (source: Hugging Face model card)
- IBM Granite 4.1 3B model card: https://huggingface.co/ibm-granite/granite-4.1-3b (source: Hugging Face model card)
- SmolLM3 Transformers docs: https://huggingface.co/docs/transformers/model_doc/smollm3 (source: Hugging Face Transformers docs)
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

## Newer Candidates Found

หลังจากเช็ก Hugging Face เพิ่มเมื่อ `2026-05-23`, มี candidate ที่ใหม่กว่ารายชื่อรอบแรกและควรขยับขึ้นมาใน shortlist:

- `LiquidAI/LFM2.5-1.2B-Instruct`: ตัวแทนใหม่ของสาย LFM2 1.2B, text-only, model card ระบุว่า checkpoint native เหมาะกับ fine-tuning และ inference ผ่าน Transformers/vLLM (source: Hugging Face model card)
- `Qwen/Qwen3.5-2B`: candidate ใหม่กว่า `Qwen3-1.7B` และยังอยู่ในขนาดที่น่าลองบน 6GB มากกว่า 4B (source: Hugging Face model card)
- `Qwen/Qwen3.5-4B`: ใหม่กว่า `Qwen3-4B-Instruct-2507` แต่เป็น 4B-class multimodal model จึงยังเป็น stretch target สำหรับ training บน 6GB (source: Hugging Face model card)
- `ibm-granite/granite-4.1-3b`: text-generation/instruct 3B, release date `April 29th, 2026`, Apache 2.0, long-context และผ่าน post-training pipeline ที่เน้น instruction following/tool calling (source: Hugging Face model card)
- `HuggingFaceTB/SmolLM3-3B`: 3B fully open compact model, long-context, multilingual, optimized for reasoning/tool use และ docs มีตัวอย่าง bitsandbytes 4-bit loading (source: Hugging Face Transformers docs)

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
| 1 | `LiquidAI/LFM2.5-1.2B-Instruct` | 1.17B | lowest-risk newer LFM upgrade | Good | ใหม่กว่า `LFM2-1.2B`, text-only, ยังคงอยู่ใน family ที่ repo เริ่มจาก LFM2 และ model card ระบุ native checkpoint สำหรับ fine-tuning/inference | License เป็น `lfm1.0`; ต้องเช็ก compatibility กับ training stack ก่อนล็อกเป็น default |
| 2 | `Qwen/Qwen3.5-2B` | 2B | first newer Qwen capacity pilot | Good to borderline | ใหม่กว่า `Qwen3-1.7B`, ขนาดยังไม่ถึง 3B-4B และเหมาะกับ task-specific fine-tuning/prototyping ตาม model card | เป็น Qwen3.5 family ที่มี multimodal path; ต้องเลือก text-only workflow ให้ชัด |
| 3 | `Qwen/Qwen3-1.7B` | 1.7B | stable Qwen fallback | Good | ยังเป็น Qwen candidate ที่ memory risk ต่ำกว่า 3B-4B และเป็น fallback ถ้า Qwen3.5 toolchain ยังไม่นิ่ง | เก่ากว่า Qwen3.5-2B แล้ว จึงไม่ใช่ first pick ล่าสุด |
| 4 | `Qwen/Qwen3-0.6B` | 0.6B | fast iteration / smoke candidate | Excellent | เหมาะกับการทดสอบ data format, prompt, schema, LoRA config และ runtime pipeline แบบเร็ว | capacity ceiling ต่ำกว่า 1.2B-3B |
| 5 | `ibm-granite/granite-4.1-3b` | 3B | newest text-only 3B stretch | Borderline | release date `April 29th, 2026`, Apache 2.0, text-generation/instruct, long-context และน่าสนใจสำหรับ structured triage | 3B QLoRA บน 6GB ต้องคุม sequence/batch และต้อง verify Unsloth/TRL support |
| 6 | `HuggingFaceTB/SmolLM3-3B` | 3B | fully open 3B comparator | Borderline | fully open, long-context, reasoning/tool-use oriented และมีตัวอย่าง 4-bit loading ใน Transformers docs | ไม่ใหม่เท่า Granite 4.1/Qwen3.5 แต่ดีมากสำหรับ comparator |
| 7 | `meta-llama/Llama-3.2-1B-Instruct` | 1B | small instruct baseline | Good | เป็น instruct baseline ที่น่าเทียบกับ Qwen/LFM ในงาน structured triage | มี gated access และ license เฉพาะ ต้องจัดการสิทธิ์ก่อนใช้ |
| 8 | `meta-llama/Llama-3.2-3B-Instruct` | 3B | architecture comparator | Borderline | อยู่ใต้ 4B และเป็น benchmark family ที่คนรู้จักดี | 6GB ต้องคุม sequence/batch แน่นมาก |
| 9 | `microsoft/Phi-4-mini-instruct` | 3.8B | reasoning-heavy stretch target | Borderline | ขนาดยังไม่เกิน 4B และน่าสนใจถ้าต้องการ reasoning/structured answer ที่ดีกว่า | ควรลองหลัง pipeline 1B-2B นิ่งแล้ว เพราะ memory เสี่ยงกว่า |
| 10 | `Qwen/Qwen3.5-4B` | 4B | newest Qwen 4B stretch | High risk on 6GB | ใหม่กว่า `Qwen3-4B-Instruct-2507` และน่าลองเมื่ออยากวัด capacity ceiling ใต้ 4B | เป็น 4B-class multimodal model; training บน 6GB เสี่ยง OOM สูง ต้องใช้ QLoRA/short sequence เท่านั้น |
| 11 | `Qwen/Qwen3-4B-Instruct-2507` | 4B | legacy benchmark stretch target | Borderline | Distil Labs benchmark จัด Qwen3-4B เป็นตัวเลือก fine-tuned performance สูงมากในกลุ่มเล็ก | เก่ากว่า Qwen3.5-4B; ใช้เป็น benchmark reference มากกว่า next run |
| 12 | `google/gemma-3-1b-it` | 1B | lightweight extra baseline | Good | เป็นอีกตระกูลหนึ่งสำหรับเทียบ behavior ของ small instruct model | ต้องดู license/model format และอย่าใช้เป็น path หลักก่อน candidate ข้างบน |
| 13 | `google/gemma-3-4b-it` | 4B | Gemma stretch comparator | Borderline | มีประโยชน์ถ้าอยากเทียบ family ใต้ 4B | เป็น image-text-to-text model และหนักกว่า 1B; ไม่ใช่ first pick บน 6GB |

## Recommended Experiment Order

1. เริ่มจาก `LiquidAI/LFM2.5-1.2B-Instruct` ถ้าต้องการ path ที่เสี่ยง memory ต่ำกว่าและยังต่อยอดจาก LFM family เดิม
2. ลอง `Qwen/Qwen3.5-2B` เป็น first newer Qwen capacity pilot ถ้าต้องการโมเดลใหม่กว่า `Qwen3-1.7B`
3. ใช้ `Qwen/Qwen3-0.6B` หรือ `Qwen/Qwen3-1.7B` เป็น fallback เมื่ออยาก debug training/prompt/runtime โดยลดความเสี่ยงจาก Qwen3.5 multimodal toolchain
4. ขยับไป `ibm-granite/granite-4.1-3b` หรือ `HuggingFaceTB/SmolLM3-3B` เมื่อ 1.2B-2B pipeline ผ่าน output/schema และ hard-contrast gate แล้ว
5. เก็บ `Qwen/Qwen3.5-4B`, `Qwen/Qwen3-4B-Instruct-2507`, `Phi-4-mini-instruct` และ 4B-class models เป็น stretch target ใต้ 4B ไม่ใช่ candidate แรกสำหรับ GPU 6GB

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

ภายใต้ GPU `6GB` และ requirement ว่าโมเดลต้องไม่เกิน `4B`, candidate ถัดไปควรเริ่มจาก `LiquidAI/LFM2.5-1.2B-Instruct` หรือ `Qwen/Qwen3.5-2B` ไม่ใช่ `Qwen3.5-4B` ทันที เหตุผลคือสองตัวแรกให้ capacity เพิ่มจาก `LFM2-350M` ชัดเจน แต่ยังคุม memory risk ได้ดีกว่า 3B-4B

ถ้าต้องการทดลองแบบ conservative ให้เริ่มจาก `LFM2.5-1.2B-Instruct` ก่อน เพราะเป็น text-only และอยู่ในสาย LFM ที่ repo มีบริบทเดิมอยู่แล้ว ถ้าต้องการวัด capacity/architecture ใหม่ ให้เลือก `Qwen3.5-2B` เป็น pilot

`Qwen3.5-4B` และ `Granite-4.1-3B` น่าสนใจมากกว่า list เก่าในแง่ freshness แต่สำหรับ 6GB ต้อง treat เป็น stretch path หลังจาก 1.2B-2B pipeline ผ่าน gate แล้วเท่านั้น ส่วน `LFM2-350M` ยังเป็น resource-constrained baseline ที่ถูกต้องสำหรับพิสูจน์ workflow ไม่ควรถูกลบออกจาก comparison

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-23 | Codex | Created 6GB small-model candidate guidance from local SLM benchmark notes and current model-card research | `docs/small-model-fine-tuning-candidates-6gb.md` | Drafted |
| 2026-05-23 | Codex | Refreshed candidate list with newer Qwen3.5, Granite 4.1, LFM2.5, and SmolLM3 options | `docs/small-model-fine-tuning-candidates-6gb.md`, `docs/References.md` | Updated |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Start the next <=4B/6GB candidate search with `Qwen/Qwen3-1.7B` | It offers a better capacity step than 350M while staying more realistic on 6GB than 3B-4B models | Future candidate config should begin below 2B, with 4B kept as a stretch experiment |
| 2026-05-23 | Refresh the first-choice candidates to `LiquidAI/LFM2.5-1.2B-Instruct` and `Qwen/Qwen3.5-2B` | Newer candidate search found LFM2.5 1.2B, Qwen3.5 2B/4B, Granite 4.1 3B, and SmolLM3 3B; 1.2B-2B remains the safer starting band for 6GB | Candidate configs should try LFM2.5 or Qwen3.5-2B before 3B/4B stretch runs |

## Related pages

- [[fine-tuning-notes]]
- [[slm-fine-tuning-model-choice]]
- [[poc-plan]]
- [[References]]
- [[output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan]]

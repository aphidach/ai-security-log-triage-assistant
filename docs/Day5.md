# Day 5: Fine-Tuning Path With Unsloth

**Summary**

วันที่ห้าสร้างทาง fine-tune small model ด้วย Unsloth โดยเริ่มจาก LoRA หรือ QLoRA เป้าหมายคือให้มี training script, config และ inference path ที่ต่อกับ dataset ของ repo ได้ ไม่จำเป็นต้อง train จบในเครื่อง dev ถ้าไม่มี GPU

**Sources**

- `docs/poc-plan.md` สำหรับ fine-tuning plan และ model candidate (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ fine-tuning guidance และ separation ระหว่าง frontend กับ training code (source: AGENTS.md)
- `docs/References.md` สำหรับ Unsloth, Axolotl และ Hugging Face TRL (source: docs/References.md)
- `docs/raw/What Small Language Model Is Best for Fine-Tuning.md` สำหรับเหตุผลที่เลือก LFM2-350M เป็น candidate แรกเมื่อทรัพยากรจำกัด (source: docs/raw/What Small Language Model Is Best for Fine-Tuning.md)
- Hugging Face/Unsloth model card สำหรับ model id `unsloth/LFM2-350M` (source: https://huggingface.co/unsloth/LFM2-350M)
- `scripts/model_adapters/prompt_contract.py` สำหรับ prompt contract ที่ใช้ร่วมกันระหว่าง adapter, evaluator และ training format (source: scripts/model_adapters/prompt_contract.py)
- `data/schemas/triage-output.schema.json` สำหรับ required field และ enum ของ output เดิม (source: data/schemas/triage-output.schema.json)
- `ml/unsloth/train_lora.py` สำหรับ training config preflight และ split guard (source: ml/unsloth/train_lora.py)
- `ml/unsloth/inference.py` สำหรับ checkpoint inference path หลัง train (source: ml/unsloth/inference.py)
- Unsloth inference docs สำหรับ `FastLanguageModel.from_pretrained()` และ `FastLanguageModel.for_inference()` (source: https://unsloth.ai/docs/basics/inference-and-deployment/unsloth-inference)
- `llm-wiki/SKILL.md` สำหรับ source tracking และ append-only log (source: SKILL.md)

**Last updated**

2026-05-17

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

- [x] เลือก LFM2-350M เป็น base model candidate รอบแรก
- [x] กำหนด prompt formatting สำหรับ train
- [x] map JSONL dataset เข้ากับ training format
- [x] เพิ่ม LoRA config
- [x] เพิ่ม validation split config
- [x] เพิ่ม output directory convention
- [x] เพิ่ม inference script สำหรับ checkpoint
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
| 2026-05-17 | Codex | Locked the first Unsloth config scaffold to LFM2-350M | `ml/unsloth/config.example.yaml`, `docs/Day5.md` | Done |
| 2026-05-17 | Codex | Added SFT training format utility for JSONL triage records | `ml/unsloth/training_format.py`, `ml/unsloth/config.example.yaml`, `docs/Day5.md` | Done |
| 2026-05-17 | Codex | Added first-pass LoRA/QLoRA hyperparameters | `ml/unsloth/config.example.yaml`, `docs/Day5.md` | Done |
| 2026-05-17 | Codex | Tuned the first QLoRA config to a short Unsloth-style trial run | `ml/unsloth/config.example.yaml`, `docs/Day5.md` | Done |
| 2026-05-17 | Codex | Added train/validation split guard preflight | `ml/unsloth/train_lora.py`, `docs/Day5.md` | Done |
| 2026-05-17 | Codex | Added checkpoint inference path for fine-tuned LoRA adapters | `ml/unsloth/inference.py`, `docs/Day5.md` | Done |
| 2026-05-17 | Codex | Aligned inference tokenization with tokenizer chat template generation path | `ml/unsloth/inference.py`, `docs/Day5.md` | Done |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ Unsloth เป็น path หลัก | เหมาะกับ LoRA/QLoRA และ small model POC | training assets อยู่ใน `ml/unsloth/` |
| 2026-05-16 | เอาแนว config discipline จาก Axolotl | training run ต้องย้อนดูค่าได้ | เพิ่ม `config.example.yaml` ตั้งแต่แรก |
| 2026-05-16 | เริ่ม fine-tune ด้วย LFM2-350M | เครื่องมีทรัพยากรจำกัด และ LFM2-350M เป็นโมเดลเล็กที่ benchmark ภายนอกชี้ว่า tunable สูง | Qwen 1.5B/3B/4B ถูกเลื่อนไปเป็น candidate สำหรับรอบเปรียบเทียบภายหลัง |
| 2026-05-17 | ตั้ง `LiquidAI/LFM2-350M` เป็นค่าเริ่มต้นใน config | รอบแรกต้องพิสูจน์ workflow ให้ครบก่อน ตั้งแต่ dataset, train, inference จนถึง evaluation จึงเริ่มจากโมเดลเล็กที่ debug และรันซ้ำง่ายกว่า | `train_lora.py` และ `inference.py` รอบถัดไปควรอ่านค่า model จาก `ml/unsloth/config.example.yaml` แทนการ hard-code |
| 2026-05-17 | ใช้ `chat_messages` เป็น training record format | LFM2 tokenizer มี chat template ของตัวเอง จึงควรเก็บ record เป็น `system/user/assistant` ก่อน แล้วให้ tokenizer render เป็น training text ตอน train จริง | `ml/unsloth/training_format.py` reuse prompt contract เดียวกับ model adapter และตรวจ output field ตาม schema เดิม |
| 2026-05-17 | เริ่ม LoRA/QLoRA ด้วย config ขนาดเล็ก | dataset รอบแรกมี 350 training records จึงควรลดโอกาส overfit และคุม VRAM ก่อนเพิ่ม rank, batch หรือ epoch | `train_lora.py` รอบถัดไปควรอ่าน `lora` และ `training` จาก `ml/unsloth/config.example.yaml` และ verify `target_modules` หลังโหลด model จริง |
| 2026-05-17 | ไม่เก็บ Trainer boilerplate ทุกตัวใน config | config ควรมีค่าที่ตั้งใจเปลี่ยนระหว่าง experiment ส่วนค่า SFTTrainer ที่ใช้ซ้ำทุก run ให้เป็น default ใน `train_lora.py` | `remove_unused_columns`, `dataset_text_field`, `dataset_kwargs` และ `max_length` ควรถูก set ใน script โดย derive `max_length` จาก `model.max_seq_length` |
| 2026-05-17 | บังคับ test split ออกจาก training path | test split ต้องเป็น fixed holdout สำหรับเทียบหลัง train เท่านั้น ถ้าเอาเข้า train metric จะรั่วและ comparison ไม่มีความหมาย | `ml/unsloth/train_lora.py` อ่านเฉพาะ `data/splits/train.jsonl` และ `data/splits/validation.jsonl`; `data/splits/test.jsonl` ใช้กับ `scripts/evaluate.py` หลัง train |
| 2026-05-17 | แยก local checkpoint smoke test ออกจาก evaluator หลัก | `inference.py` มีไว้ทดสอบ base model + LoRA adapter กับ log เดี่ยว ส่วน comparison หลักควรใช้ OpenAI-compatible fine-tuned endpoint ผ่าน evaluator เดิม | `ml/unsloth/inference.py` validate JSON/schema; `scripts/evaluate.py --adapter openai-finetune` ยังเป็นทางวัด fixed test split |
| 2026-05-17 | ใช้ tokenizer chat template tokenization โดยตรงตอน inference | inference ควรให้ tokenizer render และ tokenize prompt ใน step เดียว เพื่อลดความเสี่ยง format/tokenization ไม่ตรงกับ model template | `ml/unsloth/inference.py` เรียก `apply_chat_template(..., tokenize=True, return_dict=True, add_generation_prompt=True)` และยังใช้ deterministic generation |

## Notes

fine-tune รอบแรกไม่ต้องไล่ benchmark หลายโมเดล ให้เริ่มจาก LFM2-350M เพื่อประหยัดทรัพยากร สิ่งที่ต้องได้คือ training path ที่ reproducible และ output ที่ evaluator เรียกเทียบกับ baseline ได้

### Base Model Config

`ml/unsloth/config.example.yaml` ตั้งค่าเริ่มต้นเป็น `base_model: unsloth/LFM2-350M`, `max_seq_length: 2048`, `load_in_4bit: true`, `use_gradient_checkpointing: unsloth` และ `output_dir: ml/unsloth/outputs/lfm2-350m-security-triage-lora`

เหตุผลของค่าเริ่มต้นชุดนี้คือ POC ยังต้องพิสูจน์เส้นทางหลักให้ครบก่อน: dataset -> train -> inference -> evaluate ถ้าเริ่มจากโมเดลเล็ก จะใช้ทรัพยากรน้อยกว่า debug ง่ายกว่า และเห็นปัญหาของ dataset, prompt format หรือ schema ได้เร็วกว่า ส่วน `max_seq_length` ตั้งไว้ที่ 2048 เพราะ log รอบแรกเป็น single-line/short log เป็นหลัก ถ้ารอบหลังเพิ่ม multi-line event หรือ incident context ค่อยขยายค่านี้พร้อมวัด VRAM ใหม่

### Training Format

`ml/unsloth/training_format.py` อ่าน record จาก `data/splits/train.jsonl` หรือ split อื่น แล้วแปลงเป็น `chat_messages`:

- `system`: ใช้ `TRIAGE_SYSTEM_PROMPT` ชุดเดียวกับ adapter
- `user`: ใช้ `build_triage_user_prompt(record["input"])`
- `assistant`: เป็น JSON string ของ `record["output"]` เท่านั้น

ตัว formatter ตรวจว่า assistant output มี field เดิมครบและไม่มี field เกิน: `label`, `severity`, `is_suspicious`, `evidence`, `reason`, `recommended_action` ถ้า label เป็น `normal` ต้องตั้ง `is_suspicious=false` และ label อื่นต้องตั้ง `is_suspicious=true`

คำสั่งตรวจ format:

```bash
python3 ml/unsloth/training_format.py --split data/splits/train.jsonl
python3 ml/unsloth/training_format.py --split data/splits/validation.jsonl
```

ถ้าต้องการดูตัวอย่าง record ที่แปลงแล้ว:

```bash
python3 ml/unsloth/training_format.py --split data/splits/train.jsonl --preview 1
```

ตอนเขียน `train_lora.py` ให้โหลด tokenizer ของ `unsloth/LFM2-350M` แล้วเรียก `tokenizer.apply_chat_template(..., add_generation_prompt=False)` ผ่าน helper `apply_tokenizer_chat_template()` เพื่อให้ prompt text เข้ากับ chat template ของ LFM2 จริง

### LoRA/QLoRA Config

รอบแรกใช้ `r: 16`, `lora_alpha: 16`, `lora_dropout: 0.0`, `bias: none`, `random_state: 3407`, `use_rslora: false` และ `loftq_config: null`

`method: qlora` ไม่ได้จำเป็นต้องอยู่ใน config ตอนนี้ เพราะ QLoRA ในทางปฏิบัติคือการใส่ LoRA adapter บน base model ที่โหลดแบบ quantized 4-bit ดังนั้น config ชุดนี้บอกความเป็น QLoRA ผ่าน `load_in_4bit: true` ใน section `model` และค่าของ LoRA ใน section `lora`

training config ตั้ง `per_device_train_batch_size: 2`, `per_device_eval_batch_size: 2` และ `gradient_accumulation_steps: 4` เพื่อให้ effective batch size ประมาณ 8 ใช้ `warmup_steps: 5`, `max_steps: 30`, `learning_rate: 0.0002`, `num_train_epochs: 1`, `optim: adamw_8bit`, `weight_decay: 0.001`, scheduler แบบ `linear`, `seed: 3407` และ `report_to: none`

`target_modules` รอบแรกใช้ projection names ทั่วไปของ causal LM: `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` แต่ค่านี้ยังต้อง verify ตอน `train_lora.py` โหลด LFM2 จริง ถ้า module name ไม่ตรง ให้แก้ config ไม่ใช่ hard-code ใน script

ค่า SFTTrainer ที่เป็น boilerplate ซ้ำ ๆ ยังไม่ต้องอยู่ใน config รอบนี้ ให้ `train_lora.py` set เอง เช่น `remove_unused_columns=False`, `dataset_text_field=""`, `dataset_kwargs={"skip_prepare_dataset": True}` และ `max_length` ที่อิงจาก `model.max_seq_length`

### Split Guard

`ml/unsloth/train_lora.py` มี preflight guard สำหรับ split policy แล้ว ตอนนี้ script จะ validate ว่า:

- `data.train_path` ต้องเป็น `data/splits/train.jsonl`
- `data.validation_path` ต้องเป็น `data/splits/validation.jsonl`
- train และ validation ต้องไม่ใช่ไฟล์เดียวกัน
- ทั้งสองไฟล์ต้องอยู่ใต้ `data/splits/` และมีอยู่จริง
- `data/splits/test.jsonl` ห้ามใช้ใน training path

คำสั่งตรวจ preflight:

```bash
python3 ml/unsloth/train_lora.py --preflight-only
```

ถ้าจะ evaluate หลัง train จบ ให้ใช้ fixed test split ผ่าน evaluator เท่านั้น:

```bash
python3 scripts/evaluate.py --adapter openai-finetune --split data/splits/test.jsonl
```

script รอบนี้ยังเป็น preflight ก่อน ไม่โหลด Unsloth/model จริง เพื่อให้ตรวจ config และ split policy ได้แม้เครื่องที่ไม่มี GPU

### Checkpoint Inference

`ml/unsloth/inference.py` เป็น path สำหรับลอง checkpoint หลัง train จบ โดยโหลดค่า default จาก `ml/unsloth/config.example.yaml`:

- base model จาก `model.base_model`
- `max_seq_length`, `dtype`, `load_in_4bit`
- LoRA adapter path จาก `output.output_dir`
- schema จาก `data/schemas/triage-output.schema.json`

script ใช้ prompt contract เดียวกับ adapter/evaluator แล้วให้ tokenizer ทำ chat template + tokenization ใน step เดียวด้วย `apply_chat_template(..., tokenize=True, return_dict=True, add_generation_prompt=True)` จากนั้น generate แบบ deterministic (`do_sample=False`), extract JSON object และ validate กับ schema เดิม ถ้า output ไม่ใช่ JSON หรือ field ผิด จะ exit non-zero แทนที่จะเดาเอง

ตรวจ wiring โดยไม่โหลด model:

```bash
python3 ml/unsloth/inference.py \
  --preflight-only \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'
```

หลัง train แล้ว ให้ชี้ไปที่ LoRA adapter:

```bash
python3 ml/unsloth/inference.py \
  --adapter-path ml/unsloth/outputs/lfm2-350m-security-triage-lora \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'
```

สำหรับ evaluation จริง ให้ expose checkpoint เป็น OpenAI-compatible endpoint แล้วใช้ evaluator เดิม:

```bash
python3 scripts/evaluate.py --adapter openai-finetune --split data/splits/test.jsonl
```

แนวนี้ทำให้ local inference ใช้เป็น smoke test ได้ ส่วน metric comparison ยังอยู่ใน `scripts/evaluate.py` และใช้ fixed test split เดิม

## Related pages

- [[Day4]]
- [[Day6]]
- [[poc-plan]]
- [[References]]

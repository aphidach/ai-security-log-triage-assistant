# Fine-Tuning Notes

**Summary**

หน้านี้เก็บ notes สำหรับ fine-tuning path ของ POC โดยเน้นสิ่งที่ต้องรู้ก่อนรัน GPU จริง: config ปัจจุบัน, วิธีเตรียม Colab/GPU environment, command flow, ข้อจำกัดที่ยังไม่ควรกลบ และ handoff ไป Day 6

**Sources**

- `AGENTS.md` สำหรับ fine-tuning guidance, GPU-optional path และ schema stability (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ POC success criteria, repo structure และ training/evaluation flow (source: docs/poc-plan.md)
- `docs/Day5.md` สำหรับสถานะ fine-tuning path รอบปัจจุบัน (source: docs/Day5.md)
- `docs/References.md` สำหรับ Unsloth, Axolotl และ Hugging Face TRL เป็น design references (source: docs/References.md)
- `ml/unsloth/config.example.yaml` สำหรับ base model, LoRA/QLoRA config, split path และ output directory (source: ml/unsloth/config.example.yaml)
- `ml/unsloth/train_lora.py` สำหรับ preflight guard ของ config และ split policy (source: ml/unsloth/train_lora.py)
- `ml/unsloth/inference.py` สำหรับ local checkpoint inference path หลัง train (source: ml/unsloth/inference.py)
- `requirements-gpu.txt` สำหรับ pinned GPU package set ของ Day 6 training path (source: requirements-gpu.txt)
- `scripts/setup_gpu_env.sh` สำหรับแปลง notebook/Colab install flow เป็น terminal setup script ที่รันซ้ำได้ (source: scripts/setup_gpu_env.sh)

**Last updated**

2026-05-18

## Current Day 5 Status

Day 5 ตอนนี้มี fine-tuning path ระดับ wiring ครบแล้ว: config, training format, split guard และ inference script สำหรับโหลด base model + LoRA adapter หลัง train (source: docs/Day5.md)

สิ่งที่มีแล้ว:

- `ml/unsloth/config.example.yaml` ระบุ base model เป็น `unsloth/LFM2-350M`, เปิด 4-bit loading และตั้ง output directory สำหรับ LoRA adapter (source: ml/unsloth/config.example.yaml)
- `ml/unsloth/training_format.py` แปลง JSONL record เป็น `system/user/assistant` chat messages โดยใช้ schema เดิม (source: ml/unsloth/training_format.py)
- `ml/unsloth/train_lora.py` ตรวจ config, train split และ validation split ได้โดยไม่ต้องมี GPU (source: ml/unsloth/train_lora.py)
- `ml/unsloth/inference.py` เตรียม path สำหรับลอง checkpoint หลัง train และ validate output ตาม schema เดิม (source: ml/unsloth/inference.py)

ตอนนี้ path นี้มี GPU training body แบบ first pass แล้วใน `ml/unsloth/train_lora.py` และ smoke test บน `.venv-gpu` สามารถ train 30-step trial run จน save LoRA adapter ได้จริง โดยยังคง split guard เดิมและใช้ Unsloth-first import contract ตาม official notebooks

## Colab/GPU Notes

รอบแรกควรรันบน GPU environment แยกจากเครื่อง dev หลัก เช่น Colab หรือเครื่อง CUDA ที่ติดตั้ง dependency ฝั่ง ML ได้ครบ ส่วนเครื่องที่ไม่มี GPU ยังใช้รัน dataset generator, heuristic baseline, evaluator และ preflight ได้ตามเดิม

แนวทางเตรียม environment:

1. ใช้ Python environment ใหม่สำหรับ training เพื่อไม่ให้ dependency ของ frontend หรือ evaluator ปนกับ GPU stack และรอบนี้ควรสร้างด้วย `uv venv --seed .venv-gpu` เพื่อให้ environment มี `pip` seed package มาตั้งแต่ต้น
2. ติดตั้ง package กลุ่ม Unsloth/Transformers/BitsAndBytes ผ่าน `scripts/setup_gpu_env.sh` ซึ่งใช้ `uv pip --python ...` เป็นตัวติดตั้งหลักและจะบังคับให้รันภายใน virtual environment เท่านั้น เพื่อคง install order และ flags ที่ดึงมาจาก notebook/Colab cell เดิมไว้ในรูปที่รันจาก terminal ได้ (source: scripts/setup_gpu_env.sh)
3. script ใต้ `ml/unsloth/` ต้อง import `unsloth` ก่อน `trl`, `transformers` และ `peft` เพื่อให้ Unsloth patch `SFTTrainer` และ compatibility path สำหรับ `tokenizer=...` ทำงานเหมือนใน official notebooks (source: ml/unsloth/train_lora.py, source: ml/unsloth/inference.py)
4. ตรวจว่า runtime เห็น GPU และ framework ใช้ CUDA ได้ก่อนเริ่ม train
5. รัน preflight ก่อนเสมอ:

```bash
python3 ml/unsloth/train_lora.py --preflight-only
```

6. รัน train จริงจาก config เดิม โดยยังห้ามใช้ `data/splits/test.jsonl` ระหว่าง train

config รอบแรกตั้งใจให้เป็น trial run สั้น ๆ: `max_steps: 30`, batch ต่อ device เท่ากับ `2`, gradient accumulation เท่ากับ `4`, `load_in_4bit: true` และ `use_gradient_checkpointing: unsloth` เพื่อคุม VRAM และ debug workflow ก่อนเพิ่มขนาดงาน (source: ml/unsloth/config.example.yaml)

ก่อนรัน preflight ให้ติดตั้ง GPU stack ก่อน:

```bash
uv venv .venv-gpu --python 3.13
source .venv-gpu/bin/activate
bash scripts/setup_gpu_env.sh
```

`requirements-gpu.txt` เก็บ target package set สำหรับ stack นี้ แต่ install จริงควรผ่าน script ข้างบน เพราะไฟล์ requirements ปกติไม่สามารถเก็บเงื่อนไขแบบ notebook, `--no-deps` และ `--no-build-isolation` ได้ครบ (source: requirements-gpu.txt, source: scripts/setup_gpu_env.sh)

## Command Flow

ตรวจ training config และ split guard:

```bash
bash scripts/setup_gpu_env.sh
python3 ml/unsloth/train_lora.py --preflight-only
```

รัน train trial profile จาก config ปัจจุบัน:

```bash
python3 ml/unsloth/train_lora.py
```

ตรวจ inference wiring โดยไม่โหลด model:

```bash
python3 ml/unsloth/inference.py \
  --preflight-only \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'
```

หลัง train ได้ LoRA adapter แล้ว ให้ smoke test กับ log เส้นเดียว:

```bash
python3 ml/unsloth/inference.py \
  --adapter-path ml/unsloth/outputs/lfm2-350m-security-triage-lora \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'
```

ถ้าต้อง debug ว่าโมเดลตอบอะไรจริงก่อน parse JSON ให้เพิ่ม `--show-raw-output` ซึ่งจะพิมพ์ completion ดิบไปที่ `stderr` โดยไม่ทับ JSON output ปกติบน `stdout`:

```bash
python3 ml/unsloth/inference.py \
  --adapter-path ml/unsloth/outputs/lfm2-350m-security-triage-lora \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500' \
  --show-raw-output
```

ถ้าจะวัด fixed test split ให้ expose checkpoint เป็น OpenAI-compatible endpoint แล้วใช้ evaluator เดิม:

```bash
python3 scripts/evaluate.py --adapter openai-finetune --split data/splits/test.jsonl
```

## Known Limitations

- training profile ปัจจุบันยังเป็น short trial run ที่ `max_steps: 30` เพื่อพิสูจน์ workflow ก่อน ไม่ใช่ quality-tuned checkpoint สำหรับ evaluation จริง
- มี LoRA adapter output ใน `ml/unsloth/outputs/lfm2-350m-security-triage-lora/` แล้วจาก smoke test แต่ inference output ยังไม่เสถียรพอสำหรับ schema-valid JSON ทุกครั้ง
- `target_modules` ใน config เป็นค่า first-pass projection names ต้อง verify หลังโหลด LFM2 จริง ถ้า module name ไม่ตรงให้แก้ config ไม่ใช่ hard-code ใน script
- dataset รอบแรกเป็น synthetic 500 records จึงเหมาะกับ POC/evaluation flow แต่ยังไม่แทน production telemetry
- test split ต้องเป็น holdout สำหรับหลัง train เท่านั้น ห้ามใช้ debug training loss หรือ prompt ระหว่าง train
- install flow ของ Unsloth ยังเปราะกับเวอร์ชัน CUDA/Torch; `requirements-gpu.txt` เป็น target package set และ `scripts/setup_gpu_env.sh` encode install order ปัจจุบันผ่าน `uv pip --python ...` แต่ยังควร verify กับ official Unsloth install instructions ณ วันที่รันจริงถ้า dependency upstream เปลี่ยน (source: requirements-gpu.txt, source: scripts/setup_gpu_env.sh)
- ถ้ามี script หรือ notebook ใด import `trl`, `transformers` หรือ `peft` ก่อน `unsloth` ใน process เดียวกัน training path นี้อาจกลับไปใช้ trainer API ดิบของ TRL และพังที่ keyword อย่าง `tokenizer` ได้
- evaluator แบบ `openai-finetune` ต้องมี endpoint ที่ expose แบบ OpenAI-compatible ก่อน จึงจะวัด fixed test split ของ checkpoint ได้
- token usage จาก endpoint บางตัวอาจเป็นศูนย์ ถ้า backend ไม่ส่ง usage metadata กลับมา ต้องแยกจาก latency/accuracy metric
- ยังไม่ได้ merge base model + LoRA adapter เป็น full checkpoint รอบแรกให้เก็บ adapter-first ก่อนจนกว่าการ evaluate จะนิ่ง

## Day 6 Follow-up

หลัง path แรก train ได้แล้ว งานถัดไปของ Day 6 ควรเน้นคุณภาพและการวัดผล:

- ปรับ hyperparameters จาก trial profile ปัจจุบันให้เหมาะกับ evaluation จริงมากขึ้น
- ตรวจว่า `target_modules` ควรเปิดใช้งาน explicit list หรือปล่อย `all-linear` ต่อไปสำหรับ LFM2-350M
- ปรับ prompt/training examples เพื่อเพิ่มโอกาสให้ inference ตอบกลับเป็น schema-valid JSON
- วัด checkpoint ที่ได้กับ fixed test split ผ่าน adapter/evaluator path เดิม แทนการสรุปจาก training loss อย่างเดียว

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-17 | Codex | Created fine-tuning notes for GPU/Colab setup, command flow, limitations, and Day 6 handoff | `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Added repo-native GPU setup path with `requirements-gpu.txt` and `scripts/setup_gpu_env.sh` | `requirements-gpu.txt`, `scripts/setup_gpu_env.sh`, `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Switched the GPU setup script to use `uv` as the primary installer | `scripts/setup_gpu_env.sh`, `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Documented the Unsloth-first import contract for training and inference scripts | `ml/unsloth/train_lora.py`, `ml/unsloth/inference.py`, `README.md`, `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Updated fine-tuning notes after validating a full 30-step Unsloth training run | `ml/unsloth/train_lora.py`, `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Added an inference debug flag to show raw model completions | `ml/unsloth/inference.py`, `docs/fine-tuning-notes.md` | Done |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-17 | ปิด Day 5 ที่ config, preflight, docs และ inference wiring | GPU training จริงขึ้นกับ environment และควรเริ่มเป็นงาน Day 6 เพื่อแยกช่วงเตรียม path ออกจากช่วงรัน train | `ml/unsloth/train_lora.py` ยังเป็น preflight ใน Day 5; Day 6 เริ่มจากเติม training body |
| 2026-05-17 | ใช้ adapter-first หลัง train | รอบ POC ต้องวัดผลให้ได้ก่อน ยังไม่จำเป็นต้อง merge model เต็ม | output แรกควรเป็น LoRA adapter directory แล้วค่อยพิจารณา merged export หลัง evaluation นิ่ง |
| 2026-05-18 | แยก GPU dependency ออกจาก `requirements.txt` หลัก | install flow ของ Unsloth มีลำดับและ flags แบบ notebook ที่เก็บใน plain requirements ไม่ครบ | base deps อยู่ใน `requirements.txt`; GPU stack อยู่ใน `requirements-gpu.txt` และ `scripts/setup_gpu_env.sh` |
| 2026-05-18 | ให้ `scripts/setup_gpu_env.sh` ผูกการติดตั้งกับ `uv` และ interpreter ของ virtualenv ที่ active อยู่ | ลดการพึ่ง `python -m pip`, แก้ปัญหา venv ที่ไม่มี `pip` และลดโอกาสลง package ผิด environment | script จะ fail fast ถ้าไม่มี `uv` หรือยังไม่ได้ activate virtualenv และจะ install ผ่าน `uv pip --python ...` |
| 2026-05-18 | ยึด Unsloth-first import contract สำหรับ path ใต้ `ml/unsloth/` | official notebooks ของ Unsloth พึ่ง runtime patch ของ `unsloth` เพื่อรองรับ `SFTTrainer(..., tokenizer=...)` และ backward compatibility กับ TRL | script training/inference ต้อง import `unsloth` ก่อน `trl`, `transformers` และ `peft`; docs ต้องเตือนเรื่องนี้ชัดเจน |
| 2026-05-18 | ให้ SFTTrainer เป็นคน tokenize dataset `text` เองแทนการข้าม `prepare_dataset` | dataset ของ path นี้อยู่ในรูป chat-formatted text; การตั้ง `skip_prepare_dataset` ทำให้ dataloader ไม่มี `input_ids` และพังทันทีเมื่อเริ่ม train | `SFTConfig` ต้องระบุ `dataset_text_field`/`dataset_num_proc` และปล่อยให้ trainer สร้าง tokenized features เอง |

## Related pages

- [[Day5]]
- [[Day6]]
- [[poc-plan]]
- [[References]]

# Fine-Tuning Notes

**Summary**

หน้านี้เก็บ notes สำหรับ fine-tuning path ของ POC โดยเน้นสิ่งที่ต้องรู้ก่อนรัน GPU จริง: config ปัจจุบัน, วิธีเตรียม Colab/GPU environment, command flow, ข้อจำกัดที่ยังไม่ควรกลบ และ handoff ไป Day 6

**Sources**

- `AGENTS.md` สำหรับ fine-tuning guidance, GPU-optional path และ schema stability (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ POC success criteria, repo structure และ training/evaluation flow (source: docs/poc-plan.md)
- `docs/Day5.md` สำหรับสถานะ fine-tuning path รอบปัจจุบัน (source: docs/Day5.md)
- `docs/References.md` สำหรับ Unsloth, Axolotl และ Hugging Face TRL เป็น design references (source: docs/References.md)
- `docs/lfm2-350m-model-card-notes.md` สำหรับคำแนะนำจาก Hugging Face model card ของ `unsloth/LFM2-350M` ที่กระทบ config, chat template, generation parameters และ runtime probe (source: docs/lfm2-350m-model-card-notes.md)
- `ml/unsloth/config.example.yaml` สำหรับ base model, LoRA/QLoRA config, split path และ output directory (source: ml/unsloth/config.example.yaml)
- `ml/unsloth/config.v3-4.yaml` สำหรับ v3.4 boundary repair training run ถัดไป (source: ml/unsloth/config.v3-4.yaml)
- `ml/unsloth/train_lora.py` สำหรับ preflight guard ของ config และ split policy (source: ml/unsloth/train_lora.py)
- `ml/unsloth/inference.py` สำหรับ local checkpoint inference path หลัง train (source: ml/unsloth/inference.py)
- `ml/unsloth/merge_adapter.py` สำหรับ merge LoRA adapter เป็น standalone checkpoint หรือ export เป็น GGUF หลัง adapter พร้อม serve/export (source: ml/unsloth/merge_adapter.py)
- `requirements-gpu.txt` สำหรับ pinned GPU package set ของ Day 6 training path (source: requirements-gpu.txt)
- `scripts/setup_gpu_env.sh` สำหรับแปลง notebook/Colab install flow เป็น terminal setup script ที่รันซ้ำได้ (source: scripts/setup_gpu_env.sh)

**Last updated**

2026-05-22

## Current Day 5 Status

Day 5 ตอนนี้มี fine-tuning path ระดับ wiring ครบแล้ว: config, training format, split guard และ inference script สำหรับโหลด base model + LoRA adapter หลัง train (source: docs/Day5.md)

สิ่งที่มีแล้ว:

- `ml/unsloth/config.example.yaml` ระบุ base model เป็น `unsloth/LFM2-350M`, เปิด 4-bit loading และตั้ง output directory สำหรับ LoRA adapter (source: ml/unsloth/config.example.yaml)
- `ml/unsloth/training_format.py` แปลง JSONL record เป็น `system/user/assistant` chat messages โดยใช้ schema เดิม (source: ml/unsloth/training_format.py)
- `ml/unsloth/train_lora.py` ตรวจ config, train split และ validation split ได้โดยไม่ต้องมี GPU (source: ml/unsloth/train_lora.py)
- `ml/unsloth/inference.py` เตรียม path สำหรับลอง checkpoint หลัง train และ validate output ตาม schema เดิม (source: ml/unsloth/inference.py)
- `ml/unsloth/merge_adapter.py` เตรียม path สำหรับ merge adapter เป็น model checkpoint แยก หรือ export GGUF สำหรับ llama.cpp/Ollama/LM Studio โดยมี `--preflight-only` สำหรับตรวจ config/path ก่อนโหลดโมเดล (source: ml/unsloth/merge_adapter.py)

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

config ปัจจุบันเป็น v3.3 targeted recovery profile หลัง v3.2 hard-contrast probe ยังพลาด `sql_injection_attempt` และ `port_scan_or_recon`: `format.prompt_version` ถูก align กับ runtime เป็น `triage-json-v2.1`, `data.train_path` ชี้ไป `data/splits/train-v3-3-targeted-hard-contrast.jsonl` จำนวน 550 records และ validation ชี้ไป `data/splits/validation-v3-3-targeted-hard-contrast.jsonl` จำนวน 75 records โดยยังไม่ใช้ fixed test split (source: ml/unsloth/config.example.yaml, ml/unsloth/config.v3-3.yaml, scripts/create_v3_3_training_split.py, docs/output-structure-fix/phase-6-v3-3-targeted-canary.md)

training profile ยังใช้ base model `unsloth/LFM2-350M` เดิมและ train LoRA adapter ใหม่ ไม่ใช่ train ต่อจาก adapter v2 ตอนนี้ hyperparameters ตั้งไว้ที่ `max_steps: 180`, `learning_rate: 0.0002`, `warmup_steps: 8`, batch ต่อ device เท่ากับ `2`, gradient accumulation เท่ากับ `4`, `eval_strategy: steps`, `eval_steps: 0.1`, `save_strategy: steps` และ `save_steps: 30` ส่วน output directory เปลี่ยนเป็น `ml/unsloth/outputs/lfm2-350m-v3-3-targeted-hard-contrast-security-triage-lora` เพื่อไม่เขียนทับ v3.2 เดิม (source: ml/unsloth/config.example.yaml, ml/unsloth/config.v3-3.yaml, docs/output-structure-fix/phase-6-v3-2-hard-contrast-probe.md)

model card ของ `unsloth/LFM2-350M` สนับสนุนทิศทางนี้เพราะแนะนำให้ fine-tune LFM2 model บน narrow use cases และใช้ ChatML-like chat template ผ่าน `apply_chat_template()` ส่วน recommended generation parameters (`temperature=0.3`, `min_p=0.15`, `repetition_penalty=1.05`) ควรถูกลองเป็น runtime probe หลัง v3.3 train ไม่ใช่เปลี่ยนเป็น default ของทุก eval ทันที (source: docs/lfm2-350m-model-card-notes.md)

หลัง v3.3 temp 0.3 probe ยังไม่ผ่าน canary จึงมี config แยกสำหรับรอบถัดไปที่ `ml/unsloth/config.v3-4.yaml`: train path ชี้ไป `data/splits/train-v3-4-boundary-repair.jsonl` จำนวน 710 records, validation ชี้ไป `data/splits/validation-v3-4-boundary-repair.jsonl` จำนวน 75 records และ output directory คือ `ml/unsloth/outputs/lfm2-350m-v3-4-boundary-repair-security-triage-lora` โดย fixed test split ยังถูก hold ไว้เหมือนเดิม (source: ml/unsloth/config.v3-4.yaml, source: scripts/create_v3_4_boundary_repair_dataset.py)

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

ตรวจ v3.4 boundary repair config โดยตรง:

```bash
python3 ml/unsloth/train_lora.py --preflight-only --config ml/unsloth/config.v3-4.yaml
```

รัน train trial profile จาก config ปัจจุบัน:

```bash
python3 ml/unsloth/train_lora.py
```

รัน train v3.4 boundary repair profile:

```bash
python3 ml/unsloth/train_lora.py --config ml/unsloth/config.v3-4.yaml
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

หลัง adapter นิ่งพอสำหรับ serve/export ให้ตรวจ merge preflight ก่อน:

```bash
python3 ml/unsloth/merge_adapter.py --preflight-only
```

จากนั้น merge LoRA adapter default จาก `output.output_dir` ใน config เข้า base model แล้ว save ไปที่ `ml/unsloth/outputs/lfm2-350m-security-triage-merged`:

```bash
python3 ml/unsloth/merge_adapter.py
```

ถ้าต้องกำหนด path เอง:

```bash
python3 ml/unsloth/merge_adapter.py \
  --adapter-path ml/unsloth/outputs/lfm2-350m-security-triage-lora \
  --output-dir ml/unsloth/outputs/lfm2-350m-security-triage-merged \
  --save-method merged_16bit
```

ถ้าต้อง export เป็น GGUF สำหรับ llama.cpp/Ollama/LM Studio ให้ใช้ `--export-format gguf` แล้วเลือก quantization ตามต้องการ:

```bash
# Q8_0: คุณภาพใกล้ full precision แต่ไฟล์ใหญ่กว่า
python3 ml/unsloth/merge_adapter.py \
  --export-format gguf \
  --gguf-quantization q8_0

# F16: 16-bit GGUF, ใหญ่และช้ากว่า แต่ loss จาก quantization ต่ำ
python3 ml/unsloth/merge_adapter.py \
  --export-format gguf \
  --gguf-quantization f16

# Q4_K_M: default ที่เหมาะกับ local run มากกว่าในหลายกรณี
python3 ml/unsloth/merge_adapter.py \
  --export-format gguf \
  --gguf-quantization q4_k_m
```

ถ้าต้อง export หลาย quantization ในคำสั่งเดียว ให้ repeat flag:

```bash
python3 ml/unsloth/merge_adapter.py \
  --export-format gguf \
  --gguf-quantization q8_0 \
  --gguf-quantization f16 \
  --gguf-quantization q4_k_m
```

ถ้าต้อง push GGUF ไป Hugging Face Hub ให้ตั้ง token ผ่าน environment แล้วระบุ repo id:

```bash
export HF_TOKEN="..."
python3 ml/unsloth/merge_adapter.py \
  --export-format gguf \
  --gguf-quantization q4_k_m \
  --hub-repo your-username/lfm2-security-triage-gguf
```

ถ้าจะวัด fixed test split ให้ expose checkpoint เป็น OpenAI-compatible endpoint แล้วใช้ evaluator เดิม:

```bash
python3 scripts/evaluate.py --adapter openai-finetune --split data/splits/test.jsonl
```

## Known Limitations

- training profile ปัจจุบันยังเป็น short v2-aligned profile ที่ `max_steps: 30` เพื่อให้เทียบกับ v2 snapshot ได้ง่ายก่อน ไม่ใช่ quality-tuned checkpoint สำหรับ evaluation จริง
- มี LoRA adapter output ใน `ml/unsloth/outputs/lfm2-350m-security-triage-lora/` แล้วจาก smoke test แต่ inference output ยังไม่เสถียรพอสำหรับ schema-valid JSON ทุกครั้ง
- merged checkpoint ควรสร้างหลัง adapter quality นิ่งพอแล้ว เพราะการ merge ไม่ได้แก้คุณภาพคำตอบหรือบังคับ JSON เพิ่มเอง เป็นเพียงขั้นตอน export/serve
- GGUF export ก็เป็น export/serve step เช่นกัน ถ้า inference ยังหลุด schema-valid JSON ใน Unsloth checkpoint อยู่ GGUF จะไม่แก้ปัญหานั้นเอง และตอนนำไปใช้กับ Ollama/LM Studio ต้องระวัง chat template และ EOS token ให้ตรงกับตอน train
- `target_modules` ใน config เป็นค่า first-pass projection names ต้อง verify หลังโหลด LFM2 จริง ถ้า module name ไม่ตรงให้แก้ config ไม่ใช่ hard-code ใน script
- dataset รอบแรกเป็น synthetic 500 records จึงเหมาะกับ POC/evaluation flow แต่ยังไม่แทน production telemetry
- test split ต้องเป็น holdout สำหรับหลัง train เท่านั้น ห้ามใช้ debug training loss หรือ prompt ระหว่าง train
- install flow ของ Unsloth ยังเปราะกับเวอร์ชัน CUDA/Torch; `requirements-gpu.txt` เป็น target package set และ `scripts/setup_gpu_env.sh` encode install order ปัจจุบันผ่าน `uv pip --python ...` แต่ยังควร verify กับ official Unsloth install instructions ณ วันที่รันจริงถ้า dependency upstream เปลี่ยน (source: requirements-gpu.txt, source: scripts/setup_gpu_env.sh)
- ถ้ามี script หรือ notebook ใด import `trl`, `transformers` หรือ `peft` ก่อน `unsloth` ใน process เดียวกัน training path นี้อาจกลับไปใช้ trainer API ดิบของ TRL และพังที่ keyword อย่าง `tokenizer` ได้
- evaluator แบบ `openai-finetune` ต้องมี endpoint ที่ expose แบบ OpenAI-compatible ก่อน จึงจะวัด fixed test split ของ checkpoint ได้
- token usage จาก endpoint บางตัวอาจเป็นศูนย์ ถ้า backend ไม่ส่ง usage metadata กลับมา ต้องแยกจาก latency/accuracy metric
- `merge_adapter.py` มี path สำหรับ merge base model + LoRA adapter แล้ว แต่ควรยังเก็บ adapter-first เป็น source artifact หลักจนกว่าการ evaluate จะนิ่ง

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
| 2026-05-18 | Codex | Added a merge-adapter command path for exporting LoRA adapters as standalone checkpoints | `ml/unsloth/merge_adapter.py`, `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Extended the adapter export path to GGUF quantizations | `ml/unsloth/merge_adapter.py`, `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Aligned fine-tuning notes with the current 90-step v1 config while preserving the earlier 30-step smoke-trial note | `ml/unsloth/config.example.yaml`, `docs/model-output/v1-lfm2-350m-security-triage.md` | Done |
| 2026-05-21 | Codex | Aligned config example notes with the v2 model-output training snapshot | `ml/unsloth/config.example.yaml`, `docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md` | Done |
| 2026-05-21 | Codex | Updated fine-tuning notes after creating v3 train/validation split files | `data/splits/train-v3-hard-contrast.jsonl`, `data/splits/validation-v3-hard-contrast.jsonl` | Done |
| 2026-05-21 | Codex | Updated fine-tuning notes for v3.3 targeted SQLi and port-scan recovery profile | `ml/unsloth/config.v3-3.yaml`, `data/splits/train-v3-3-targeted-hard-contrast.jsonl` | Done |
| 2026-05-21 | Codex | Linked LFM2-350M model-card guidance into current fine-tuning notes | `docs/lfm2-350m-model-card-notes.md`, `ml/unsloth/config.v3-3.yaml` | Done |
| 2026-05-22 | Codex | Added v3.4 boundary repair config and train command notes | `ml/unsloth/config.v3-4.yaml`, `data/splits/train-v3-4-boundary-repair.jsonl` | Prepared |

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
| 2026-05-18 | แยก merge adapter เป็น script ของตัวเอง | merge เป็น export/serve step หลัง training ไม่ควรปนกับ train หรือ one-log inference | เพิ่ม `ml/unsloth/merge_adapter.py` พร้อม `--preflight-only`; default output อยู่ที่ `ml/unsloth/outputs/lfm2-350m-security-triage-merged` |
| 2026-05-18 | รองรับ GGUF export ใน merge script เดิม | GGUF เป็น deployment format สำหรับ llama.cpp/Ollama/LM Studio และควรใช้ adapter/config เดียวกับ training path | `merge_adapter.py --export-format gguf` รองรับ `q8_0`, `f16`, `q4_k_m` และ optional `--hub-repo` |
| 2026-05-21 | Mirror v2 model-output hyperparameters in `config.example.yaml` | ผู้ใช้ต้องการให้ config example ใช้ config model v2 จาก `docs/model-output`; v2 ยังเป็น LoRA run บน base `unsloth/LFM2-350M` ไม่ใช่ base model ใหม่ | repo-native config now uses the v2-aligned short profile while still training a fresh adapter from the base model |
| 2026-05-21 | Make v3.3 the current training profile | v3.2 hard-contrast canary improved but SQLi and port scan remained under-learned | `config.example.yaml` now points to the v3.3 targeted split and output directory; fixed test split remains held |
| 2026-05-22 | Keep v3.4 as an explicit config before promoting default config | v3.4 is prepared for the next training run but still needs training and canary/mini-eval results before becoming a promoted path | Use `--config ml/unsloth/config.v3-4.yaml`; fixed test split remains held |

## Related pages

- [[Day5]]
- [[Day6]]
- [[poc-plan]]
- [[References]]
- [[lfm2-350m-model-card-notes]]

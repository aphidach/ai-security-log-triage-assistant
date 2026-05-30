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
- `ml/unsloth/config.v4.yaml` สำหรับ Phase 8 v4 SQLi-first repair training run (source: ml/unsloth/config.v4.yaml)
- `ml/unsloth/config.v4-1.yaml` สำหรับ Phase 8 v4.1 SQLi-boundary repair training run (source: ml/unsloth/config.v4-1.yaml)
- `ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml` สำหรับ Qwen3.5 exploratory LoRA smoke pilot ที่ใช้ loader แบบ `fast_vision_model` (source: ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml)
- `ml/unsloth/train_lora_vision_qwen.py` สำหรับ Qwen3.5 exploratory LoRA smoke pilot ที่ใช้ `FastVisionModel` และ vision data collator แบบแยกจาก LFM2 trainer หลัก (source: ml/unsloth/train_lora_vision_qwen.py)
- `docs/raw/Qwen3_5_(0_8B)_Vision.ipynb` สำหรับตัวอย่าง Unsloth official path ของ `FastVisionModel` กับ `unsloth/Qwen3.5-0.8B` (source: docs/raw/Qwen3_5_(0_8B)_Vision.ipynb)
- `scripts/model_adapters/prompt_contract.py` และ `scripts/model_adapters/openai_compatible.py` สำหรับ v4.2/v4.3 runtime diagnostics ที่ไม่ train adapter ใหม่ (source: scripts/model_adapters/prompt_contract.py, source: scripts/model_adapters/openai_compatible.py)
- `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md` สำหรับ capacity/architecture diagnostic ของ `unsloth/Qwen3.5-0.8B` หลัง v4.2 held (source: docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md)
- v4.3 Qwen3.5 base-model probe reports สำหรับตัดสินใจว่า future Qwen LoRA pilot ยังไม่ควรเป็น gate ถัดไป (source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-smoke.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json)
- v4.4 boundary audit สำหรับย้ำว่า Qwen train ยังไม่ควรเป็น default gate (source: docs/output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan.md, source: reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.json)
- v4.5 trained-Qwen LoRA pilot result และ hard-contrast report สำหรับบันทึกผลหลัง Qwen train สำเร็จ (source: docs/output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe.md, source: reports/phase-8/phase-8-v4-5-qwen35-lora-training-result.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json)
- v4.6 Qwen normal/severity calibration workflow และผลหลัง train/probe (source: docs/output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan.md, source: ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml, source: reports/phase-8/phase-8-v4-6-qwen35-lora-training-result.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json)
- v4.7 Qwen auth/SQLi/severity calibration workflow สำหรับรอบ train ถัดไป (source: docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md, source: ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml, source: data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl)
- `ml/unsloth/train_lora.py` สำหรับ preflight guard ของ config และ split policy (source: ml/unsloth/train_lora.py)
- `ml/unsloth/inference.py` สำหรับ local checkpoint inference path หลัง train (source: ml/unsloth/inference.py)
- `ml/unsloth/merge_adapter.py` สำหรับ merge LoRA adapter เป็น standalone checkpoint หรือ export เป็น GGUF หลัง adapter พร้อม serve/export (source: ml/unsloth/merge_adapter.py)
- `requirements-gpu.txt` สำหรับ pinned GPU package set ของ Day 6 training path (source: requirements-gpu.txt)
- `scripts/setup_gpu_env.sh` สำหรับแปลง notebook/Colab install flow เป็น terminal setup script ที่รันซ้ำได้ (source: scripts/setup_gpu_env.sh)

**Last updated**

2026-05-23

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

หลัง Phase 7 fixed split comparison ตัดสินใจ `hold` v3.5 จึงมี config ใหม่สำหรับ Phase 8 ที่ `ml/unsloth/config.v4.yaml`: train path ชี้ไป `data/splits/train-v4-sqli-boundary-repair.jsonl` จำนวน 1070 records, validation ชี้ไป `data/splits/validation-v4-sqli-boundary-repair.jsonl` จำนวน 75 records, `max_seq_length=2048`, `max_steps=540` และ output directory คือ `ml/unsloth/outputs/lfm2-350m-v4-2048-sqli-boundary-repair-security-triage-lora` โดย fixed test split ไม่ถูกใช้ใน v4 tuning (source: ml/unsloth/config.v4.yaml, source: docs/output-structure-fix/phase-8-v4-sqli-boundary-repair-plan.md)

v4 train เสร็จแล้วด้วย `train_loss=0.5690714741470637`, runtime `401.7052` seconds และ serve เป็น alias `lfm2-security-triage-v4` สำหรับ hard-contrast probes แต่ผลยัง held: temp 0 และ temp 0.3 ได้ label accuracy `0.84`, JSON/schema `1.0`, invalid `0`, normal `8/10`, traversal/brute-force/port-recon `10/10`, แต่ SQLi ยัง `4/10` ต่ำกว่า gate `8/10` จึงยังไม่ควรเปิด mini semantic eval หรือ fixed comparison จาก checkpoint นี้ (source: reports/phase-8/phase-8-v4-sqli-boundary-training-result.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json)

หลัง v4 held จึงมี config ใหม่สำหรับ v4.1 ที่ `ml/unsloth/config.v4-1.yaml`: train path ชี้ไป `data/splits/train-v4-1-sqli-boundary-repair.jsonl` จำนวน 1220 records, validation ชี้ไป `data/splits/validation-v4-1-sqli-boundary-repair.jsonl` จำนวน 75 records, `max_seq_length=2048`, `max_steps=610` และ output directory คือ `ml/unsloth/outputs/lfm2-350m-v4-1-2048-sqli-boundary-repair-security-triage-lora` โดย config นี้ train จาก base `unsloth/LFM2-350M` ไม่ใช่ v4 adapter และ fixed test split ยังไม่ถูกใช้ (source: ml/unsloth/config.v4-1.yaml, source: docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md)

v4.1 train เสร็จแล้วด้วย `train_loss=0.5194365828985074`, runtime `459.4452` seconds และ serve เป็น alias `lfm2-security-triage-v4-1` สำหรับ hard-contrast probes ผลดีขึ้นแต่ยัง held: temp 0 ได้ label accuracy `0.88`, SQLi `6/10`, JSON/schema `1.0`, invalid `0`; temp 0.3 ได้ label accuracy `0.90`, SQLi `7/10`, JSON/schema `1.0`, invalid `0`. เพราะ SQLi ยังต่ำกว่า gate `8/10` จึงยังไม่ควรเปิด mini semantic eval หรือ fixed comparison จาก checkpoint นี้ (source: reports/phase-8/phase-8-v4-1-sqli-boundary-training-result.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json)

v4.2 ไม่ใช่ training profile และไม่มี `ml/unsloth/config.v4-2.yaml` เพราะใช้ v4.1 adapter เดิมเพื่อทดสอบ prompt priority ผ่าน `OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.2-sqli-priority` เท่านั้น default training/runtime prompt ยังเป็น `triage-json-v2.1` เพื่อไม่ให้ v3/v4/v4.1 configs และ UI path เปลี่ยนความหมายย้อนหลัง ผล hard-contrast ทำให้ v4.2 ถูก hold: temp 0 ได้ label accuracy `0.64`, SQLi `4/10`, traversal `4/10`; temp 0.3 ได้ label accuracy `0.62`, JSON/schema `0.98`, invalid `1` จึงไม่ควรเปิด mini semantic eval จาก prompt profile นี้ (source: scripts/model_adapters/prompt_contract.py, source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.json)

v4.3 ก็ไม่ใช่ training profile และไม่มี `ml/unsloth/config.v4-3.yaml` เป้าหมายคือ capacity/architecture diagnostic โดย serve `unsloth/Qwen3.5-0.8B` เป็น base model ตรงจาก Hub ไม่ใช่ model ที่ train/LoRA แล้ว จากนั้นคง prompt `triage-json-v2.1`, schema และ hard-contrast probe เดิม เพื่อเทียบว่ารุ่น/สถาปัตยกรรมที่แรงกว่าแยก SQLi/traversal/recon ได้หรือไม่ก่อนลงทุนทำ synthetic data หรือ LoRA รอบใหม่ ผู้ใช้รัน fixed split sanity check กับ v4.1 แล้วได้ label accuracy `0.893333`, JSON/schema `1.0`, invalid `0` แต่ผลนี้เป็น context เท่านั้น ไม่ใช่ gate หรือ tuning feedback ของ Phase 8 (source: docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md, source: docs/output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan.md)

ผล v4.3 base model `unsloth/Qwen3.5-0.8B` รอบแรกสรุปได้ชัดว่า output contract ไม่ใช่ blocker: smoke, hard-contrast temp 0, และ hard-contrast temp 0.3 ได้ JSON/schema `1.0` และ invalid `0` ทั้งหมด แต่ hard-contrast semantic ยังต่ำมาก โดย temp 0 ได้ label accuracy `0.50`, SQLi `3/10`; temp 0.3 ได้ label accuracy `0.48`, SQLi `2/10` และ suspicious classes หลายตัวถูกทายเป็น `normal` ดังนั้น future Qwen LoRA pilot ถ้าจะทำ ต้องเปิดเป็น exploratory training แยกต่างหาก ไม่ใช่ gate ถัดไปของ v4.3 (source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-smoke.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json)

v4.4 audit ตอกย้ำ decision เดิมจาก base-model evidence: union label failures มี `26` IDs, persistent failures มี `25` IDs และ failure หลักคือ SQLi/traversal/recon -> `normal` (`20/50` ที่ temp 0 และ `22/50` ที่ temp 0.3) ดังนั้น fine-tuning Qwen ทันทีจะเสี่ยงกลายเป็นการจำ hard-contrast forms มากกว่าพิสูจน์ boundary understanding รอบถัดไปควรเลือก candidate model ที่มี security-log semantics ดีกว่า หรือเปิด prompt/data boundary repair แบบ scoped ชัด ๆ ก่อนสร้าง train config ใหม่ (source: docs/output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan.md, source: reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.json)

ตอนนี้มี Qwen3.5 exploratory LoRA smoke pilot แยกจาก gate แล้วที่ `ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml`: config นี้ระบุ `model.loader: fast_vision_model`, ใช้ `unsloth/Qwen3.5-0.8B`, เปิด 4-bit สำหรับ smoke, ไม่ตั้ง `dtype`, ระบุ `target_modules` เป็น projection modules ชุดเดียวกับ LFM2 pilot และตั้ง `finetune_vision_layers: false` แต่เปิด language/attention/MLP LoRA สำหรับงาน security-log text-only โดยรันผ่าน `ml/unsloth/train_lora_vision_qwen.py` เพื่อใช้ `UnslothVisionDataCollator` และ text-only `messages` format ตาม vision path (source: ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml, source: ml/unsloth/train_lora_vision_qwen.py)

เหตุผลที่ใช้ loader นี้มาจาก Unsloth notebook สำหรับ Qwen3.5-0.8B โดยตรง: notebook โหลดโมเดลด้วย `FastVisionModel.from_pretrained("unsloth/Qwen3.5-0.8B", ...)`, ใส่ LoRA ผ่าน `FastVisionModel.get_peft_model(...)`, และสลับ train/inference ด้วย `FastVisionModel.for_training()` / `FastVisionModel.for_inference()` (source: docs/raw/Qwen3_5_(0_8B)_Vision.ipynb)

v4.5 บันทึกผล Qwen3.5 LoRA pilot หลัง train สำเร็จแล้ว: config เดิม train บน `data/splits/train-v4-1-sqli-boundary-repair.jsonl` จำนวน `1220` records และ validation `75` records, output อยู่ที่ `ml/unsloth/outputs/qwen3-5-0-8b-security-triage-pilot-lora-smoke`, train loss `0.41032123460123937`, runtime `597.8327` seconds จากนั้น serve ผ่าน vLLM LoRA alias `qwen3.6-8B-triage-v1` และรัน hard-contrast temp 0 ด้วย structured outputs ได้ label accuracy `0.88`, JSON/schema `1.0`, invalid `0`, evidence partial match `0.98` แต่ยัง held เพราะ normal accuracy แค่ `4/10` และ severity accuracy `0.72` (source: reports/phase-8/phase-8-v4-5-qwen35-lora-training-result.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json)

v4.6 train จาก base `unsloth/Qwen3.5-0.8B` อีกครั้ง ไม่ใช่ train ต่อจาก adapter v4.5: train path เป็น `data/splits/train-v4-6-qwen35-normal-severity-calibration.jsonl` จำนวน `1340` records, validation path เป็น `data/splits/validation-v4-6-qwen35-normal-severity-calibration.jsonl` จำนวน `100` records, มี probe split แยกที่ `data/splits/v4-6-normal-severity-calibration-probe.jsonl` จำนวน `25` records, ตั้ง `learning_rate: 0.00008`, `max_steps: 260` และ output directory เป็น `ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration-lora` ผล train complete มี train loss `0.2689869593255795`, runtime `1419.9621` seconds และ throughput `1.465` samples/sec (source: ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml, source: reports/phase-8/phase-8-v4-6-qwen35-lora-training-result.json)

หลัง serve เป็น alias `qwen3.6-8B-triage-v2` และรันผ่าน structured outputs ที่ `temperature=0`, v4.6 ได้ calibration probe label accuracy `0.84`, severity `0.80`, JSON/schema `1.0`, invalid `0`; hard-contrast probe ได้ label accuracy `0.90`, severity `0.90`, suspicious accuracy `0.96`, evidence `0.98`, JSON/schema `1.0`, invalid `0` แต่ยัง held เพราะ hard-contrast `normal` อยู่ที่ `7/10`, SQLi อยู่ที่ `8/10`, calibration normal อยู่ที่ `11/15`, และ brute-force medium severity ใน calibration probe ถูกยกเป็น `high` ครบ `4/4` เคส (source: reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json, source: docs/output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan.md)

v4.7 เตรียม train จาก base `unsloth/Qwen3.5-0.8B` อีกครั้ง โดย base split คือ v4.6 train/validation แล้วเพิ่ม targeted supplement สำหรับ benign auth, SQLi auth-context, brute-force medium severity, limited port/recon medium และ traversal exact evidence: train path เป็น `data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl` จำนวน `1460` records, validation path เป็น `data/splits/validation-v4-7-qwen35-auth-sqli-severity-calibration.jsonl` จำนวน `130` records, probe split แยกที่ `data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl` จำนวน `30` records, ตั้ง `learning_rate: 0.00008`, `max_steps: 275` และ output directory เป็น `ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration-lora`; fixed split ยังปิดจนกว่าจะมี non-fixed v4.7 probes ผ่าน gate (source: ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml, source: docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md)

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

ตรวจและรัน v4 SQLi-first repair profile:

```bash
python3 ml/unsloth/train_lora.py --preflight-only --config ml/unsloth/config.v4.yaml
python3 ml/unsloth/train_lora.py --config ml/unsloth/config.v4.yaml
```

ตรวจและรัน v4.1 SQLi-boundary repair profile:

```bash
python3 ml/unsloth/train_lora.py --preflight-only --config ml/unsloth/config.v4-1.yaml
python3 ml/unsloth/train_lora.py --config ml/unsloth/config.v4-1.yaml
```

v4.2 ไม่มี train command ให้รันเฉพาะ prompt diagnostic pre-probe checks:

```bash
python3 scripts/create_v4_2_sqli_priority_diagnostic_slice.py
python3 -m unittest tests/test_openai_adapter_config.py tests/test_v4_2_sqli_priority_prompt_workflow.py
```

v4.3 gate ไม่มี train command เพราะ base model Qwen3.5-0.8B ยัง held จาก hard-contrast probes แล้ว ถ้าจะรัน Qwen LoRA smoke ต้องถือเป็น exploratory pilot แยกจาก gate นี้:

```bash
python3 -m unittest tests/test_openai_adapter_config.py tests/test_v4_2_sqli_priority_prompt_workflow.py tests/test_v4_3_capacity_diagnostic_plan.py
python3 -m py_compile scripts/model_adapters/prompt_contract.py scripts/model_adapters/openai_compatible.py
```

ตรวจและรัน Qwen3.5 exploratory LoRA smoke pilot:

```bash
python3 ml/unsloth/train_lora_vision_qwen.py --preflight-only --config ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml
python3 ml/unsloth/train_lora_vision_qwen.py --config ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml
```

ถ้า smoke train สำเร็จ ให้บันทึกเป็น pilot artifact แยกต่างหากก่อนเพิ่ม `max_steps` หรือใช้ผลไปออกแบบ experiment ใหม่ ห้ามใช้เป็นเหตุผลเปิด `data/splits/test.jsonl` โดยตรง (source: ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml, source: docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md)

ตรวจและรัน Qwen3.5 v4.6 normal/severity calibration profile:

```bash
python3 ml/unsloth/train_lora_vision_qwen.py \
  --preflight-only \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml

python3 ml/unsloth/train_lora_vision_qwen.py \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml
```

ตรวจและรัน Qwen3.5 v4.7 auth/SQLi/severity calibration profile:

```bash
python3 ml/unsloth/train_lora_vision_qwen.py \
  --preflight-only \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml

python3 ml/unsloth/train_lora_vision_qwen.py \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml
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
| 2026-05-22 | Codex | Added v4 SQLi-first repair config and command notes | `ml/unsloth/config.v4.yaml`, `data/splits/train-v4-sqli-boundary-repair.jsonl` | Prepared |
| 2026-05-22 | Codex | Added v4.1 SQLi-boundary repair config and command notes | `ml/unsloth/config.v4-1.yaml`, `data/splits/train-v4-1-sqli-boundary-repair.jsonl` | Prepared |
| 2026-05-22 | User/Codex | Recorded v4.1 training completion and hard-contrast result notes | `reports/phase-8/phase-8-v4-1-sqli-boundary-training-result.json`, `ml/unsloth/config.v4-1.yaml` | Held |
| 2026-05-22 | Codex | Added v4.2 prompt diagnostic notes without adding a training config | `scripts/model_adapters/prompt_contract.py`, `docs/output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan.md` | Prepared |
| 2026-05-22 | Codex | Recorded v4.2 hard-contrast prompt diagnostic result | `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.json` | Held |
| 2026-05-22 | Codex | Added v4.3 capacity diagnostic notes without adding a training config | `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md`, `tests/test_v4_3_capacity_diagnostic_plan.py` | Planned |
| 2026-05-23 | User/Codex | Recorded that v4.3 Qwen3.5 probes do not promote a Qwen train gate | `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-smoke.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json` | Held |
| 2026-05-23 | Codex | Added v4.4 boundary audit note that keeps Qwen LoRA outside the default gate | `docs/output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan.md`, `reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.json` | Audit complete; training still held |
| 2026-05-23 | User/Codex | Clarified that v4.3/v4.4 Qwen3.5 evidence is base-model evidence, not a trained Qwen model result | `docs/fine-tuning-notes.md` | Clarified |
| 2026-05-23 | Codex | Added Qwen3.5 exploratory LoRA smoke pilot notes using Unsloth `FastVisionModel` | `ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml`, `docs/raw/Qwen3_5_(0_8B)_Vision.ipynb`, `ml/unsloth/train_lora.py` | Pilot wiring prepared |
| 2026-05-23 | Codex | Split Qwen3.5 exploratory LoRA smoke pilot into a dedicated vision trainer | `ml/unsloth/train_lora_vision_qwen.py`, `ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml` | Pilot trainer separated |
| 2026-05-23 | User/Codex | Recorded v4.5 trained-Qwen LoRA completion and hard-contrast probe result | `reports/phase-8/phase-8-v4-5-qwen35-lora-training-result.json`, `docs/output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe.md` | Trained/probed; calibration held |
| 2026-05-23 | Codex | Added Qwen3.5 v4.6 normal/severity calibration config and command notes | `ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml`, `data/splits/train-v4-6-qwen35-normal-severity-calibration.jsonl` | Prepared; training pending |
| 2026-05-23 | User/Codex | Recorded Qwen3.5 v4.6 training completion and probe results | `reports/phase-8/phase-8-v4-6-qwen35-lora-training-result.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json` | Improved but held |
| 2026-05-23 | Codex | Added Qwen3.5 v4.7 auth/SQLi/severity calibration config and command notes | `ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml`, `data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl` | Prepared; training pending |

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
| 2026-05-22 | Keep v4 as an explicit Phase 8 config | v4 is a new SQLi-first repair experiment after Phase 7 held v3.5, not a promoted default path yet | Use `--config ml/unsloth/config.v4.yaml`; hard-contrast gates must pass before any broader evaluation |
| 2026-05-22 | Do not create a v4.2 training config | v4.1 already tested a narrow data repair and still held at SQLi `6/10` temp 0 | v4.2 stays runtime-only; if it fails, next work should be capacity pilot rather than more synthetic data by default |
| 2026-05-22 | Hold v4.2 prompt profile | Prompt priority damaged normal, traversal, port/recon, and temp 0.3 output contract while SQLi stayed `4/10` | Do not promote `triage-json-v2.2-sqli-priority`; keep `triage-json-v2.1` as default and plan capacity/architecture work next |
| 2026-05-22 | Do not create a v4.3 training config | v4.3 is intended to answer whether model/runtime capacity is the blocker | Use hard-contrast probes with prompt v2.1 against candidate served model aliases before any new LoRA/data work |
| 2026-05-23 | Do not promote future Qwen3.5-0.8B LoRA as a v4.3 gate | The base-model diagnostic passes JSON/schema but fails semantic gates, with hard-contrast SQLi only `3/10` and `2/10` | Any Qwen fine-tune should be explicitly marked exploratory and should not reopen fixed split |
| 2026-05-23 | Do not create a v4.4 Qwen training config from the audit | v4.4 shows a broad suspicious-to-normal semantic collapse, not a train-script or output-contract blocker | Keep Qwen LoRA as exploratory only; default next work is another capacity candidate or scoped boundary repair |
| 2026-05-23 | Use `FastVisionModel` for Qwen3.5-0.8B pilot training | The Unsloth Qwen3.5 notebook uses the vision-capable loader and exposes layer-level LoRA flags for this model family | `train_lora.py`, `inference.py`, and `merge_adapter.py` now choose loader from `model.loader`; LFM2 configs default to `fast_language_model` |
| 2026-05-23 | Keep Qwen3.5 pilot training outside `train_lora.py` | The Qwen path needs `UnslothVisionDataCollator`, `dataset_kwargs.skip_prepare_dataset`, and `messages` records, while the LFM2 path should keep trainer-side tokenization from `text` | Use `ml/unsloth/train_lora_vision_qwen.py` for Qwen smoke runs and keep `ml/unsloth/train_lora.py` unchanged for language-model configs |
| 2026-05-23 | Hold v4.5 before fixed split | Qwen LoRA now catches suspicious hard-contrast labels well, but normal false positives and severity calibration still fail the gate | Keep fixed split closed; next work should target normal/severity calibration first |
| 2026-05-23 | Train v4.6 from base Qwen, not v4.5 adapter | A clean comparison needs a fresh adapter trained on the updated mixture rather than continuing from a held calibration result | Use the v4.6 config output directory and keep v4.5 as historical evidence |
| 2026-05-23 | Hold v4.6 before fixed split | v4.6 improves hard-contrast overall label/severity metrics but still misses normal, SQLi, calibration-normal, and brute-force severity gates | Keep the Qwen path in calibration mode before any fixed split or export decision |

## Related pages

- [[Day5]]
- [[Day6]]
- [[poc-plan]]
- [[References]]
- [[lfm2-350m-model-card-notes]]

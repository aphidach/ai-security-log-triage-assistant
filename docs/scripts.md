# Script Runbook

**Summary**

เอกสารนี้รวมคำสั่งหลักสำหรับรันโปรเจกต์ `AI Security Log Triage Assistant` ตั้งแต่ setup, generate dataset, รัน heuristic baseline, evaluate, probe OpenAI-compatible endpoint, เปิด frontend, ไปจนถึงเส้นทาง optional สำหรับ Unsloth LoRA/QLoRA บน GPU

ใช้หน้านี้เป็น runbook กลางเวลาอยากรู้ว่า "ต้องรันอะไร" ส่วนรายละเอียด design, metric, limitation และ rationale ให้ตามไปอ่านจากหน้า related docs แต่ละส่วน

**Sources**

- `AGENTS.md` สำหรับ mission, schema, label scope, evaluation rules และข้อกำหนดว่า GPU fine-tuning ต้องเป็น optional path (source: AGENTS.md)
- `README.md` สำหรับ setup พื้นฐานของ Python, frontend และ GPU environment (source: README.md)
- `.env.example` สำหรับตัวแปร `OPENAI_COMPATIBLE_*` และ `OPENAI_FINETUNE_*` (source: .env.example)
- `config-adapter.example.yml` สำหรับตัวอย่าง adapter runtime config เช่น `temperature`, `top_p` และ `extra_body` (source: config-adapter.example.yml)
- `frontend/package.json` สำหรับ frontend scripts ที่มีจริงใน repo (source: frontend/package.json)
- `scripts/generate_dataset.py` สำหรับ dataset generation command และ output path (source: scripts/generate_dataset.py)
- `scripts/create_v3_3_training_split.py` สำหรับ v3.3 targeted SQLi/port-scan training split ที่ไม่ใช้ fixed test split (source: scripts/create_v3_3_training_split.py)
- `scripts/baseline_heuristic.py` สำหรับ heuristic baseline CLI options (source: scripts/baseline_heuristic.py)
- `scripts/evaluate.py` สำหรับ evaluator adapters, report flags และ metric workflow (source: scripts/evaluate.py)
- `scripts/model_adapters/prompt_contract.py` สำหรับ prompt contract inspection CLI (source: scripts/model_adapters/prompt_contract.py)
- `docs/openai-adapter-runtime-config.md` สำหรับรายละเอียด precedence ของ env/YAML และตัวอย่าง runtime probe (source: docs/openai-adapter-runtime-config.md)
- `scripts/probe_openai_structured_output.py` สำหรับ direct structured-output probe modes (source: scripts/probe_openai_structured_output.py)
- `scripts/create_mini_semantic_eval_split.py` และ `scripts/run_phase5_mini_semantic_eval.sh` สำหรับ mini semantic eval workflow (source: scripts/create_mini_semantic_eval_split.py, source: scripts/run_phase5_mini_semantic_eval.sh)
- `ml/unsloth/training_format.py`, `ml/unsloth/train_lora.py`, `ml/unsloth/inference.py`, `ml/unsloth/merge_adapter.py`, `ml/unsloth/simple_unsloth_save.py` และ `scripts/convert_hf_checkpoint_to_gguf.sh` สำหรับ training format, LoRA training, local inference, checkpoint export, Unsloth native-save debug และ llama.cpp GGUF conversion commands (source: ml/unsloth/training_format.py, source: ml/unsloth/train_lora.py, source: ml/unsloth/inference.py, source: ml/unsloth/merge_adapter.py, source: ml/unsloth/simple_unsloth_save.py, source: scripts/convert_hf_checkpoint_to_gguf.sh)
- `docs/Day2.md`, `docs/Day3.md`, `docs/Day4.md`, `docs/Day5.md`, `docs/Day6.md` และ `docs/output-structure-fix/phase-5-mini-semantic-eval.md` สำหรับ workflow status และข้อจำกัดของแต่ละช่วง (source: docs/Day2.md, source: docs/Day3.md, source: docs/Day4.md, source: docs/Day5.md, source: docs/Day6.md, source: docs/output-structure-fix/phase-5-mini-semantic-eval.md)

**Last updated**

2026-05-28

## Recommended Order

ถ้าเริ่มจาก clone ใหม่และอยากพิสูจน์ workflow แบบไม่ใช้ GPU/API key ให้เดินตามลำดับนี้ก่อน:

1. สร้าง Python environment และติดตั้ง dependency พื้นฐาน
2. รัน dataset generator เฉพาะเมื่อต้องการ refresh `data/generated/` และ `data/splits/`
3. ลอง heuristic baseline กับ log เดี่ยว
4. รัน evaluator กับ `heuristic` adapter บน fixed test split
5. เปิด frontend แล้วรัน typecheck/lint/dev server
6. ถ้ามี endpoint ค่อยตั้ง `.env` แล้ว probe structured output
7. ถ้ามี GPU ค่อยเข้าเส้นทาง Unsloth training, inference และ export

คำสั่งบางชุดเขียนไฟล์ tracked เช่น dataset split, report หรือ LoRA output ให้ดู note ในแต่ละ section ก่อนรัน

## Base Python Environment

ใช้ environment นี้สำหรับ dataset, baseline, evaluator, adapter และ probe ที่ไม่ต้องใช้ GPU

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

เช็กว่า Python เห็น package หลักได้:

```bash
python3 scripts/evaluate.py --help
python3 scripts/baseline_heuristic.py --help
```

`requirements.txt` ตั้งใจเก็บ dependency ฝั่ง base workflow เท่านั้น ส่วน GPU training แยกไป `requirements-gpu.txt` และติดตั้งผ่าน `scripts/setup_gpu_env.sh`

## Frontend

frontend อยู่ใต้ `frontend/` และใช้ Next.js ตาม scripts ใน `frontend/package.json`

ใช้ npm:

```bash
cd frontend
npm install
npx tsc --noEmit
npm run lint
npm run dev
```

หรือใช้ Bun:

```bash
cd frontend
bun install
bunx tsc --noEmit
bun run lint
bun run dev
```

หลัง dev server ขึ้น เปิด `http://localhost:3000`

สำหรับ production-style check ฝั่ง frontend:

```bash
cd frontend
npm run build
npm run start
```

## Dataset Workflow

คำสั่งนี้สร้าง synthetic dataset รอบแรกแบบ deterministic และเขียนไฟล์ output ลง `data/generated/` กับ `data/splits/`

```bash
python3 scripts/generate_dataset.py
```

ผลลัพธ์หลัก:

```text
data/generated/synthetic-security-triage.jsonl
data/splits/train.jsonl
data/splits/validation.jsonl
data/splits/test.jsonl
```

ใช้คำสั่งนี้เมื่ออยาก refresh dataset จาก generator เท่านั้น เพราะจะเขียนไฟล์ split ใหม่ตาม logic ใน script

## Heuristic Baseline

ใช้ baseline นี้เมื่อต้องการ triage log แบบ local ไม่ใช้ model key และไม่ใช้ GPU

รันกับ log เดี่ยว:

```bash
python3 scripts/baseline_heuristic.py \
  --input '192.0.2.10 - - [17/May/2026:10:15:00 +0700] "GET /login?username=admin%27%20OR%20%271%27%3D%271 HTTP/1.1" 200' \
  --pretty
```

รันกับไฟล์ plain text ที่มีหนึ่ง log ต่อหนึ่งบรรทัด:

```bash
python3 scripts/baseline_heuristic.py --file logs.txt --pretty
```

รันจาก stdin:

```bash
printf '%s\n' 'May 17 10:00:00 auth-01 sshd[1234]: Failed password for admin from 192.0.2.20 port 51111 ssh2; repeated 15 times' \
  | python3 scripts/baseline_heuristic.py --pretty
```

output จะเป็น JSON ตาม triage schema เดียวกับ evaluator และ model adapters

## Evaluation

evaluator ใช้ adapter interface เดียวกันสำหรับ heuristic, OpenAI-compatible base model และ fine-tuned endpoint

รัน heuristic baseline บน fixed test split:

```bash
python3 scripts/evaluate.py \
  --adapter heuristic \
  --split data/splits/test.jsonl
```

ค่า default ของ `heuristic` จะเขียน:

```text
reports/baseline/baseline-eval.json
reports/phase-7/comparison.md
```

ถ้าต้องการตรวจ metric โดยไม่เขียน report:

```bash
python3 scripts/evaluate.py \
  --adapter heuristic \
  --split data/splits/test.jsonl \
  --no-write
```

ถ้าต้องการปิด progress ระหว่างรัน:

```bash
python3 scripts/evaluate.py \
  --adapter heuristic \
  --split data/splits/test.jsonl \
  --no-progress
```

กำหนด report path เอง:

```bash
python3 scripts/evaluate.py \
  --adapter heuristic \
  --split data/splits/test.jsonl \
  --out reports/baseline/baseline-eval.json \
  --comparison-out reports/phase-7/comparison.md
```

adapter ที่รองรับตอนนี้:

```text
heuristic
openai-compatible
openai-finetune
```

ห้ามใช้ `data/splits/test.jsonl` ระหว่าง training ให้ใช้ fixed test split นี้เฉพาะตอน evaluate หลัง training หรือหลังปรับ runtime contract แล้ว

## Prompt Contract Inspection

ใช้ script นี้เมื่อต้องการดู prompt source เดียวกับ Python adapters และ Unsloth training format

พิมพ์ system prompt:

```bash
python3 scripts/model_adapters/prompt_contract.py
```

พิมพ์ prompt version:

```bash
python3 scripts/model_adapters/prompt_contract.py --kind version
```

พิมพ์ user prompt สำหรับ log หนึ่งบรรทัด:

```bash
python3 scripts/model_adapters/prompt_contract.py \
  --kind user \
  --log-line '127.0.0.1 - - [10/May/2026] "GET /login HTTP/1.1" 200'
```

## OpenAI-Compatible Adapters

คัดลอก `.env.example` เป็น `.env` แล้วแก้ค่า endpoint ให้ตรง runtime ที่ใช้จริง ห้าม commit secret หรือ token จริงลง repo

```bash
cp .env.example .env
```

ถ้าอยากลดการ export env ยาว ๆ ให้คัดลอก adapter config ตัวอย่าง:

```bash
cp config-adapter.example.yml config-adapter.yml
```

`config-adapter.yml` ถูก ignore โดย git และ adapter จะอ่านให้อัตโนมัติถ้าไฟล์อยู่ที่ repo root หรือชี้ผ่าน `OPENAI_COMPATIBLE_CONFIG_PATH`, `OPENAI_FINETUNE_CONFIG_PATH`, หรือ `OPENAI_ADAPTER_CONFIG_PATH` ค่า env ยัง override YAML ได้เหมือนเดิม รายละเอียดอยู่ที่ [[openai-adapter-runtime-config]]

ตัวอย่าง local config สำหรับ vLLM/OpenAI-compatible endpoint:

```yaml
openai-compatible:
  base_url: http://192.168.8.141:8080/v1
  api_key: local
  model: lfm2-security-triage-v3-3
  timeout_seconds: 120
  max_retries: 0
  max_tokens: 512
  response_format: structured_outputs
  schema_path: data/schemas/triage-output.schema.json
  request:
    temperature: 0
```

ค่าที่ใส่ใน `request` แล้ว adapter ส่งต่อให้ OpenAI-compatible client ตอนนี้มี:

```text
temperature
top_p
frequency_penalty
presence_penalty
seed
stop
```

ถ้า backend เป็น vLLM หรือ server ที่มี parameter เพิ่ม ให้ใส่ไว้ใต้ `extra_body` และใช้เฉพาะ probe ที่ตั้งชื่อ report ชัดเจน เพราะค่ากลุ่มนี้ไม่ใช่ standard OpenAI API parameter:

```yaml
openai-compatible:
  request:
    temperature: 0.3
    top_p: 0.9
    extra_body:
      min_p: 0.15
      repetition_penalty: 1.05
```

คำสั่ง eval แบบใช้ไฟล์ config:

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-runtime-probe.json \
  --comparison-out reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-runtime-probe.md
```

ถ้าเป็น canonical comparison ให้คง `temperature: 0` ก่อน ส่วนค่าแนว model card เช่น `temperature: 0.3`, `min_p: 0.15`, `repetition_penalty: 1.05` ให้รันเป็น runtime probe แยก report เพื่อย้อนดูผลได้ชัดเจน

ชุด env สำหรับ base model endpoint:

```text
OPENAI_COMPATIBLE_BASE_URL
OPENAI_COMPATIBLE_API_KEY
OPENAI_COMPATIBLE_MODEL
OPENAI_COMPATIBLE_TIMEOUT_SECONDS
OPENAI_COMPATIBLE_MAX_RETRIES
OPENAI_COMPATIBLE_MAX_TOKENS
OPENAI_COMPATIBLE_RESPONSE_FORMAT
OPENAI_COMPATIBLE_SCHEMA_PATH
OPENAI_COMPATIBLE_CONFIG_PATH
```

ชุด env สำหรับ fine-tuned endpoint:

```text
OPENAI_FINETUNE_BASE_URL
OPENAI_FINETUNE_API_KEY
OPENAI_FINETUNE_MODEL
OPENAI_FINETUNE_TIMEOUT_SECONDS
OPENAI_FINETUNE_MAX_RETRIES
OPENAI_FINETUNE_MAX_TOKENS
OPENAI_FINETUNE_RESPONSE_FORMAT
OPENAI_FINETUNE_SCHEMA_PATH
OPENAI_FINETUNE_CONFIG_PATH
```

รัน base model adapter ผ่าน evaluator:

```bash
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/structured-output/smoke/openai-compatible-smoke.json \
  --comparison-out reports/structured-output/smoke/openai-compatible-smoke.md
```

รัน fine-tuned endpoint ผ่าน evaluator:

```bash
python3 scripts/evaluate.py \
  --adapter openai-finetune \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/structured-output/smoke/openai-finetune-smoke.json \
  --comparison-out reports/structured-output/smoke/openai-finetune-smoke.md
```

เริ่มจาก smoke split ก่อนเสมอ ถ้า JSON/schema ยังไม่ผ่าน อย่าเพิ่งรัน fixed test split เต็ม เพราะจะปนปัญหา output contract กับ semantic accuracy

## Structured-Output Probe

probe นี้ยิง OpenAI-compatible endpoint โดยตรงผ่าน OpenAI Python client เพื่อแยกว่า runtime บังคับ structured output ได้จริงไหม ก่อนเอา endpoint เข้า evaluator path

รัน `responses_parse` กับ sample แรกของ smoke split:

```bash
python3 scripts/probe_openai_structured_output.py \
  --env-prefix OPENAI_COMPATIBLE \
  --mode responses_parse \
  --sample-index 0
```

รัน `json_schema`:

```bash
python3 scripts/probe_openai_structured_output.py \
  --env-prefix OPENAI_COMPATIBLE \
  --mode json_schema \
  --sample-index 0
```

รัน vLLM-style `structured_outputs`:

```bash
python3 scripts/probe_openai_structured_output.py \
  --env-prefix OPENAI_COMPATIBLE \
  --mode structured_outputs \
  --sample-index 0
```

รัน legacy `guided_json`:

```bash
python3 scripts/probe_openai_structured_output.py \
  --env-prefix OPENAI_COMPATIBLE \
  --mode guided_json \
  --sample-index 0
```

รันครบทุก record ใน smoke split และเขียน report:

```bash
python3 scripts/probe_openai_structured_output.py \
  --env-prefix OPENAI_COMPATIBLE \
  --mode structured_outputs \
  --all-smoke \
  --out reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-smoke.md \
  --json-out reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-smoke.json \
  --force
```

ทดสอบ adversarial instruction ที่พยายามดึง model ให้ออก markdown fence:

```bash
python3 scripts/probe_openai_structured_output.py \
  --env-prefix OPENAI_COMPATIBLE \
  --mode structured_outputs \
  --all-smoke \
  --adversarial-format markdown_fence \
  --out reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-adversarial.md \
  --json-out reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-adversarial.json \
  --force
```

รองรับ mode เหล่านี้:

```text
responses_parse
json_schema
structured_outputs
guided_json
json_object
plain
```

## Mini Semantic Eval

mini semantic eval ใช้ validation-derived split ขนาดเล็กและ balanced เพื่อดู semantic behavior หลัง output contract เริ่มนิ่ง โดยยังไม่แตะ fixed test split

สร้าง split:

```bash
python3 scripts/create_mini_semantic_eval_split.py \
  --source data/splits/validation.jsonl \
  --out data/splits/mini-semantic-eval.jsonl \
  --per-label 5 \
  --exclude data/splits/test.jsonl \
  --exclude data/splits/smoke-output-contract.jsonl \
  --force
```

รัน helper script สำหรับ Phase 5 mini semantic eval:

```bash
scripts/run_phase5_mini_semantic_eval.sh
```

กำหนด endpoint/report path ผ่าน env ได้:

```bash
OPENAI_COMPATIBLE_BASE_URL=http://localhost:8000/v1 \
OPENAI_COMPATIBLE_API_KEY=local \
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
PHASE5_JSON_REPORT=reports/structured-output/mini-semantic-eval/openai-compatible-mini-semantic-eval.json \
PHASE5_MARKDOWN_REPORT=reports/structured-output/mini-semantic-eval/openai-compatible-mini-semantic-eval.md \
scripts/run_phase5_mini_semantic_eval.sh
```

## Optional GPU And Unsloth

เส้นทางนี้ใช้สำหรับ LoRA/QLoRA fine-tuning ด้วย Unsloth ต้องมี GPU environment ที่พร้อมก่อน ส่วน workflow dataset, baseline, evaluator และ frontend ยังรันได้โดยไม่ต้องมี GPU

สร้าง GPU venv และติดตั้ง dependency:

```bash
uv venv --seed .venv-gpu
source .venv-gpu/bin/activate
bash scripts/setup_gpu_env.sh
```

ถ้าใช้ WSL แล้ว `nvidia-smi` ไม่เจอทั้งที่ driver พร้อมอยู่ ให้ลอง:

```bash
export PATH="/usr/lib/wsl/lib:$PATH"
nvidia-smi
```

ตรวจ training format:

```bash
python3 ml/unsloth/training_format.py --split data/splits/train.jsonl
python3 ml/unsloth/training_format.py --split data/splits/validation.jsonl
```

ดูตัวอย่าง formatted record:

```bash
python3 ml/unsloth/training_format.py \
  --split data/splits/train.jsonl \
  --preview 1
```

ตรวจ config, split guard และ dataset wiring โดยไม่เริ่ม train:

```bash
python3 ml/unsloth/train_lora.py --preflight-only
```

เตรียม v3.3 targeted SQLi/port-scan split ใหม่:

```bash
python3 scripts/create_v3_3_training_split.py
python3 ml/unsloth/train_lora.py --preflight-only --config ml/unsloth/config.v3-3.yaml
```

เริ่ม train ตาม `ml/unsloth/config.example.yaml`:

```bash
python3 ml/unsloth/train_lora.py
```

ถ้าต้องการใช้ config อื่น:

```bash
python3 ml/unsloth/train_lora.py --config ml/unsloth/config.v3-3.yaml
```

training path นี้ตั้งใจไม่อ่าน `data/splits/test.jsonl`; รอบ v3.3 ต้อง train แล้วรัน hard-contrast probe บน `data/generated/v3-hard-contrast-security-triage.jsonl` ก่อน mini semantic eval และยังไม่ใช้ fixed test split

## Local LoRA Inference

ใช้ local inference เป็น smoke test ของ checkpoint หรือ LoRA adapter หลัง train ไม่ใช่ evaluation หลักของ fixed split

preflight โดยไม่โหลด model:

```bash
python3 ml/unsloth/inference.py \
  --preflight-only \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'
```

รัน inference กับ adapter default จาก config:

```bash
python3 ml/unsloth/inference.py \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'
```

ชี้ adapter path เอง:

```bash
python3 ml/unsloth/inference.py \
  --adapter-path ml/unsloth/outputs/lfm2-350m-security-triage-lora \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'
```

อ่าน log จากไฟล์:

```bash
python3 ml/unsloth/inference.py --log-file one-log.txt
```

อ่านจาก stdin:

```bash
printf '%s\n' '2026-05-17T10:00:00+07:00 firewall: SYN scan detected src=192.0.2.20 ports=21,22,23,25,80,443' \
  | python3 ml/unsloth/inference.py --stdin
```

debug raw completion ก่อน JSON parsing:

```bash
python3 ml/unsloth/inference.py \
  --show-raw-output \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'
```

สำหรับ comparison จริง ให้ expose model เป็น OpenAI-compatible endpoint แล้วใช้ `scripts/evaluate.py --adapter openai-finetune`

## Merge And GGUF Export

merge/export เป็น packaging step หลัง adapter พร้อม ไม่ได้แก้ปัญหา schema adherence หรือ semantic quality ด้วยตัวเอง

preflight merge:

```bash
python3 ml/unsloth/merge_adapter.py --preflight-only
```

export merged Hugging Face checkpoint:

```bash
python3 ml/unsloth/merge_adapter.py \
  --export-format merged \
  --output-dir ml/unsloth/outputs/lfm2-350m-security-triage-merged \
  --force
```

preflight GGUF:

```bash
python3 ml/unsloth/merge_adapter.py \
  --export-format gguf \
  --gguf-quantization q4_k_m \
  --preflight-only
```

export GGUF:

```bash
python3 ml/unsloth/merge_adapter.py \
  --export-format gguf \
  --gguf-quantization q4_k_m \
  --output-dir ml/unsloth/outputs/lfm2-350m-security-triage-gguf \
  --force
```

quantization ที่ script รองรับ:

```text
q8_0
f16
q4_k_m
```

ถ้าต้องการลอง save helper ของ Unsloth โดยตรงแบบ minimal เพื่อแยกปัญหาจาก wrapper หลัก ให้ใช้ script นี้:

```bash
.venv-gpu/bin/python ml/unsloth/simple_unsloth_save.py \
  --mode merged \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml \
  --output-dir ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-7-simple-unsloth-merged \
  --load-in-4bit false \
  --force
```

ลอง `save_pretrained_gguf` ของ Unsloth เอง:

```bash
.venv-gpu/bin/python ml/unsloth/simple_unsloth_save.py \
  --mode gguf \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml \
  --output-dir ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-7-simple-unsloth-gguf \
  --gguf-quantization f16 \
  --load-in-4bit false \
  --force
```

ถ้ามี clean merged Hugging Face checkpoint อยู่แล้วและต้องการแปลงด้วย `llama.cpp` โดยตรง ให้ใช้ script นี้แทน path Unsloth GGUF:

```bash
LLAMA_CPP_DIR="$HOME/llama.cpp" \
GGUF_QUANTIZATIONS=q4_k_m \
scripts/convert_hf_checkpoint_to_gguf.sh
```

default ของ script ชี้ไปที่ clean Qwen3.5 v4-7 merged checkpoint:

```text
ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration-merged-bf16-clean
```

สำหรับ v4-7 ให้คง default `GGUF_CONVERT_ARGS=--no-mtp` ไว้ เพราะ clean checkpoint ไม่มี MTP tensors; GGUF ที่ยังมี `qwen35.nextn_predict_layers=1` จะโหลดใน `llama.cpp` ไม่ผ่านด้วย error แนว `missing tensor 'blk.24.attn_norm.weight'` (source: scripts/convert_hf_checkpoint_to_gguf.sh)

override input/output ได้ด้วย environment variables:

```bash
MODEL_DIR=ml/unsloth/outputs/my-clean-merged-checkpoint \
GGUF_OUT_DIR=ml/unsloth/outputs/my-model-gguf \
GGUF_BASENAME=my-model \
GGUF_OUTTYPE=f16 \
GGUF_QUANTIZATIONS=q4_k_m,q8_0 \
GGUF_CONVERT_ARGS=--no-mtp \
LLAMA_CPP_DIR="$HOME/llama.cpp" \
scripts/convert_hf_checkpoint_to_gguf.sh
```

ผลลัพธ์หลักจะได้ intermediate `*-f16.gguf` และ final quantized เช่น `*-q4_k_m.gguf` สำหรับ `llama-server`:

```bash
llama-server \
  -m ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-7-gguf/qwen3-5-0-8b-security-triage-v4-7-q4_k_m.gguf \
  --port 8080 \
  -c 2048 \
  -ngl 99
```

## Common Checks

ตรวจ CLI help โดยไม่เขียน output:

```bash
python3 scripts/baseline_heuristic.py --help
python3 scripts/evaluate.py --help
python3 scripts/probe_openai_structured_output.py --help
python3 ml/unsloth/train_lora.py --help
python3 ml/unsloth/inference.py --help
python3 ml/unsloth/merge_adapter.py --help
python3 ml/unsloth/simple_unsloth_save.py --help
bash -n scripts/convert_hf_checkpoint_to_gguf.sh
```

ตรวจ frontend scripts ที่มีจริง:

```bash
cd frontend
npm run
```

ตรวจว่า report path ไม่ทับงานสำคัญก่อนรัน endpoint eval:

```bash
ls reports/
```

## Troubleshooting Notes

- ถ้า `scripts/evaluate.py` เขียน report โดยไม่ตั้งใจ ให้ rerun ด้วย `--no-write` ตอนแค่ตรวจ metric
- ถ้า endpoint ตอบ prose หรือ markdown fence ให้ใช้ `scripts/probe_openai_structured_output.py` ก่อน เพื่อแยกว่า backend บังคับ structured output จริงไหม
- ถ้า smoke split ยังมี `invalid_output_count` สูง ให้หยุดที่ output-contract gate ก่อน อย่าเพิ่งรัน fixed test split
- ถ้า GPU setup fail ให้แยก base workflow ออกมาก่อน: dataset, heuristic, evaluator และ frontend ยังใช้ `.venv` ปกติได้
- ถ้า local LoRA inference output parse ไม่ผ่าน ให้เพิ่ม `--show-raw-output` เพื่อดู raw completion ก่อนแก้ prompt, schema หรือ training data
- ถ้า GGUF conversion fail เพราะหา `convert_hf_to_gguf.py` หรือ `llama-quantize` ไม่เจอ ให้ตั้ง `LLAMA_CPP_DIR` ไปที่ llama.cpp checkout ที่ build แล้ว หรือ override `CONVERT_SCRIPT` / `LLAMA_QUANTIZE_BIN`
- ถ้าจะใช้ log จริง ห้าม commit production log, secret, token, cookie, session id, hostname หรือ user ที่ยังไม่ sanitize

## Work Log

Append-only log สำหรับบันทึกว่า runbook นี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Created canonical script runbook for setup, local workflows, endpoint probes, frontend, and optional Unsloth/GPU commands | `docs/scripts.md` | Drafted |
| 2026-05-21 | Codex | Added `config-adapter.yml` usage examples for OpenAI-compatible runtime parameters | `config-adapter.example.yml`, `docs/openai-adapter-runtime-config.md` | Updated |
| 2026-05-26 | Codex | Added direct llama.cpp GGUF conversion command for clean merged checkpoints | `scripts/convert_hf_checkpoint_to_gguf.sh`, `docs/scripts.md` | Updated |
| 2026-05-26 | Codex | Added minimal Unsloth native-save debug command | `ml/unsloth/simple_unsloth_save.py`, `docs/scripts.md` | Updated |
| 2026-05-28 | Codex | Documented the v4-7 no-MTP GGUF conversion guard | `scripts/convert_hf_checkpoint_to_gguf.sh`, `docs/scripts.md` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | วาง runbook คำสั่งไว้ที่ `docs/scripts.md` | ผู้ใช้เลือกให้ไฟล์อยู่ใน docs และ repo มีคำสั่งกระจายอยู่ใน README, day plans, scripts และ fine-tuning notes | `docs/scripts.md` เป็น entrypoint กลางสำหรับคำสั่งรันโปรเจกต์ ส่วน README ยังเป็น quickstart ได้เหมือนเดิม |
| 2026-05-28 | ใช้ `--no-mtp` เป็นค่า default สำหรับ direct GGUF conversion ของ v4-7 | clean Qwen3.5 v4-7 checkpoint ไม่มี MTP tensors แต่ GGUF ที่ฝัง `nextn_predict_layers=1` ทำให้ `llama.cpp` เรียกหา `blk.24.*` ที่ไม่มีจริง | Direct conversion script สร้าง GGUF ที่โหลดได้ใน `llama.cpp` โดย default; ถ้าต้องการทดลอง MTP ต้อง override `GGUF_CONVERT_ARGS` เอง |

## Related pages

- [[index]]
- [[poc-plan]]
- [[Day2]]
- [[Day3]]
- [[Day4]]
- [[Day5]]
- [[Day6]]
- [[Day7]]
- [[fine-tuning-notes]]
- [[output-contract-hardening]]
- [[output-structure-fix/phase-5-mini-semantic-eval]]

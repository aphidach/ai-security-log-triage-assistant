# AI Security Log Triage Assistant

![AI Security Log Triage Assistant hero](docs/assets/readme-hero.png)

POC สำหรับวิเคราะห์ security log ด้วย small model และ fine-tuning

เป้าหมายคือพิสูจน์ workflow ให้ครบ: สร้าง dataset, ทำ baseline, fine-tune โมเดลขนาดเล็ก, evaluate ด้วย test set เดียวกัน แล้วเทียบผลก่อน-หลัง fine-tune ไม่ใช่ทำระบบ SOC อัตโนมัติหรือฟันธงว่าเครื่องถูกเจาะจาก log เส้นเดียว

fine-tuning รอบแรกจะเริ่มจาก **LFM2-350M** ก่อน เพราะทรัพยากรเครื่องมีจำกัดและต้องการพิสูจน์ workflow ให้จบด้วยโมเดลที่เล็กมาก

## Scope รอบแรก

เริ่มจาก label เล็ก ๆ เพื่อให้วัดผลได้จริง:

- `normal`
- `failed_login_bruteforce`
- `sql_injection_attempt`
- `directory_traversal_attempt`
- `port_scan_or_recon`

ผลลัพธ์ของ analyzer ควรมี field หลัก: `label`, `severity`, `is_suspicious`, `evidence`, `reason`, `recommended_action`

## Installation

### Base Python environment

สำหรับ dataset, baseline, evaluator และ adapter ฝั่ง Python:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
```

### Frontend

สำหรับ demo UI:

```bash
cd frontend
npm install
npx tsc --noEmit
npm run lint
npm run dev
```

ถ้าใช้ Bun:

```bash
cd frontend
bun install
bunx tsc --noEmit
bun run lint
bun run dev
```

เปิดที่ `http://localhost:3000`

### Optional GPU fine-tuning environment

สำหรับ Day 6 Unsloth LoRA/QLoRA path ให้ใช้ `uv` เป็นตัวหลักในการสร้าง environment แยก แล้วค่อยติดตั้งผ่าน setup script ของ repo:

```bash
uv venv --seed .venv-gpu
source .venv-gpu/bin/activate
bash scripts/setup_gpu_env.sh
```

จากนั้นตรวจ preflight:

```bash
python3 ml/unsloth/train_lora.py --preflight-only
python3 ml/unsloth/inference.py \
  --preflight-only \
  --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'
```

`scripts/setup_gpu_env.sh` ใช้ `uv pip --python ...` เป็นตัวติดตั้งหลัก และจะหยุดทันทีถ้ายังไม่ได้ activate virtual environment ส่วน `requirements-gpu.txt` เก็บ target package set ของ GPU stack แต่ install จริงควรผ่าน script เพราะ stack นี้ต้องอาศัย install order และ flags แบบ notebook เช่น `--no-deps` และ `--no-build-isolation`

training path นี้ยึด `unsloth` เป็น runtime หลัก ดังนั้น script ใต้ `ml/unsloth/` ต้อง import `unsloth` ก่อน `trl`, `transformers` และ `peft` ใน process เดียวกัน เพื่อให้ compatibility patch ของ Unsloth ทำงานเหมือนตัวอย่าง Colab

ถ้าใช้ WSL และ `nvidia-smi` ขึ้น `command not found` ทั้งที่ driver พร้อมอยู่แล้ว ให้ลอง:

```bash
export PATH="/usr/lib/wsl/lib:$PATH"
nvidia-smi
```

## Quickstart

เริ่มจาก frontend ก่อนถ้าต้องการเปิด demo UI เร็วที่สุด:

```bash
cd frontend
npm install
npm run dev -- --port 3000
```

เปิดที่ `http://localhost:3000`

คำสั่งตรวจ frontend:

```bash
cd frontend
npx tsc --noEmit
npm run lint
npm run build
```

shared triage contract อยู่ที่:

- `data/schemas/triage-output.schema.json` - JSON Schema กลางของ output
- `frontend/lib/labels.ts` - label taxonomy ฝั่ง TypeScript
- `frontend/lib/triage-schema.ts` - runtime validator และ type ของ triage output
- `frontend/lib/heuristic-baseline.ts` - heuristic analyzer สำหรับ demo UI ที่รันได้โดยไม่ต้องใช้ model key

## สถานะ

ตอนนี้ repo ผ่าน foundation ถึง Phase 6 repair/evaluation investigation แล้ว และมี Day 7 demo UI ที่รัน local ได้:

- มี deterministic synthetic dataset และ fixed `train/validation/test` splits
- มี heuristic baseline ที่รัน local และ evaluator ที่เก็บ metrics ซ้ำได้
- มี OpenAI-compatible adapter path และ structured-output runtime notes
- มี Unsloth/LFM2-350M LoRA training path พร้อม v3.5 repair artifacts
- มี Next.js demo UI สำหรับ paste log, sample picker, analyzer selector, structured result, evidence highlight, raw JSON และ comparison panel

ข้อจำกัดล่าสุด: Phase 6 ปิดแบบ `closed_with_limitations`; fixed `data/splits/test.jsonl` ยัง held สำหรับ Phase 7 fixed-split comparison เพราะ v3.5 ยังมี SQLi/quote-heavy weakness และ canonical temp 0 ยังไม่ผ่าน gate เดิมครบ

## Planned Workflow

1. Output schema และ label taxonomy - done
2. Synthetic JSONL dataset และ fixed splits - done
3. Heuristic baseline และ evaluation runner - done
4. Model adapters และ structured-output runtime probes - done
5. LFM2-350M Unsloth LoRA/QLoRA path - done through v3.5 repair run
6. Demo UI สำหรับ paste log, analyze และ highlight evidence - done for heuristic baseline
7. Phase 7 fixed-split comparison - held until go/no-go gate clears

## Docs

- `docs/poc-plan.md` - แผน POC หลัก
- `docs/Day1.md` ถึง `docs/Day7.md` - แผนรายวันพร้อม Work Log และ Decision Log
- `docs/demo-script.md` - talk track สำหรับ demo 2-3 นาที
- `docs/References.md` - repo และเอกสารอ้างอิง
- `docs/raw/What Small Language Model Is Best for Fine-Tuning.md` - clipping ที่ใช้เป็น rationale สำหรับ LFM2-350M
- `AGENTS.md` - กติกาสำหรับ coding agents
- `.codex/skills/llm-docs/` - skill สำหรับดูแลเอกสารของโปรเจกต์นี้

## Security Note

ห้าม commit production logs, secrets, tokens, credentials หรือข้อมูลลูกค้า

ระบบนี้ควรใช้ภาษาแบบ triage เช่น suspicious, likely pattern และ recommended investigation ไม่ควร claim ว่ายืนยันการถูก hack แล้วถ้าไม่มีหลักฐานจากระบบอื่นประกอบ

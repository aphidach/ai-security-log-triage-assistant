# Phase 6 V3 Hard Contrast Dataset

**Summary**

หน้าเอกสารนี้บันทึก v3 hard-contrast dataset supplement ที่สร้างหลัง Phase 6.1 พบว่า output contract ผ่านแล้ว แต่ mini semantic eval ยังเกิด prediction collapse ไปทาง `failed_login_bruteforce` หนักเกินไป ชุดนี้จึงเน้นตัวอย่างคู่เปรียบเทียบและ hard negatives สำหรับแก้ label boundary ไม่ใช่เพิ่ม synthetic data แบบสุ่ม (source: reports/openai-compatible-vllm-structured-outputs-phase6-1-mini-semantic-eval.json, reports/phase-6-semantic-error-taxonomy-infographic.html)

**Sources**

- `reports/openai-compatible-vllm-structured-outputs-phase6-1-mini-semantic-eval.json` สำหรับ metric และ predicted-label collapse หลัง Phase 6.1 (source: reports/openai-compatible-vllm-structured-outputs-phase6-1-mini-semantic-eval.json)
- `reports/phase-6-semantic-error-taxonomy-infographic.html` สำหรับ semantic error taxonomy และ v3 backlog (source: reports/phase-6-semantic-error-taxonomy-infographic.html)
- `docs/output-structure-fix/phase-6-v3-or-runtime-decision.md` สำหรับ Phase 6 decision rules และ v3 training data plan (source: docs/output-structure-fix/phase-6-v3-or-runtime-decision.md)
- `docs/label-imbalance-and-prediction-collapse.md` สำหรับแนวทาง hard contrast examples และกติกาไม่ downsample `failed_login_bruteforce` ทันที (source: docs/label-imbalance-and-prediction-collapse.md)
- `scripts/create_v3_hard_contrast_dataset.py` สำหรับ generator ของชุดข้อมูลนี้ (source: scripts/create_v3_hard_contrast_dataset.py)
- `scripts/create_v3_training_split.py` สำหรับสร้าง v3 train/validation split โดยไม่แตะ fixed test split (source: scripts/create_v3_training_split.py)
- `scripts/create_v3_1_training_split.py` สำหรับสร้าง v3.1 weighted hard-contrast split โดยไม่แตะ fixed test split (source: scripts/create_v3_1_training_split.py)
- `data/generated/v3-hard-contrast-security-triage.jsonl` สำหรับ JSONL output ที่สร้างแล้ว (source: data/generated/v3-hard-contrast-security-triage.jsonl)
- `data/splits/train-v3-hard-contrast.jsonl` และ `data/splits/validation-v3-hard-contrast.jsonl` สำหรับ split ที่ config v3 ใช้ train/validate (source: data/splits/train-v3-hard-contrast.jsonl, data/splits/validation-v3-hard-contrast.jsonl)
- `data/splits/train-v3-1-hard-contrast.jsonl` และ `data/splits/validation-v3-1-hard-contrast.jsonl` สำหรับ v3.1 recovery training profile (source: data/splits/train-v3-1-hard-contrast.jsonl, data/splits/validation-v3-1-hard-contrast.jsonl)

**Last updated**

2026-05-21

## Status

Created and validated locally. Dataset นี้เป็น training supplement เท่านั้น ยังไม่ใช่ fixed eval split และยังไม่ควรถูกใช้แทน `data/splits/test.jsonl`

## Generated Artifact

```text
scripts/create_v3_hard_contrast_dataset.py
scripts/create_v3_training_split.py
scripts/create_v3_1_training_split.py
data/generated/v3-hard-contrast-security-triage.jsonl
data/generated/train-plus-v3-hard-contrast.jsonl
data/generated/train-plus-v3-1-hard-contrast.jsonl
data/splits/train-v3-hard-contrast.jsonl
data/splits/validation-v3-hard-contrast.jsonl
data/splits/train-v3-1-hard-contrast.jsonl
data/splits/validation-v3-1-hard-contrast.jsonl
```

รันใหม่ได้ด้วยคำสั่ง:

```bash
rtk .venv/bin/python scripts/create_v3_hard_contrast_dataset.py
rtk .venv/bin/python scripts/create_v3_training_split.py
rtk .venv/bin/python scripts/create_v3_1_training_split.py
```

ผลลัพธ์:

```text
records: 50
normal: 10
failed_login_bruteforce: 10
sql_injection_attempt: 10
directory_traversal_attempt: 10
port_scan_or_recon: 10
```

v3 training split:

```text
train-v3-hard-contrast: 400 records, 80 per label
validation-v3-hard-contrast: 75 records, 15 per label
fixed test split: not read or modified
```

v3.1 weighted recovery split:

```text
train-v3-1-hard-contrast: 500 records, 100 per label
validation-v3-1-hard-contrast: 75 records, 15 per label
weighted hard contrast records: 150 records, 30 per label
fixed test split: not read or modified
```

## Why This Dataset Exists

Phase 6.1 mini eval ผ่าน JSON/schema แล้ว แต่ยังมี semantic blocker:

- expected split balanced label ละ 5 ตัวอย่าง
- predicted `failed_login_bruteforce` = 20/25
- `label_accuracy = 0.36`
- `json_parse_success_rate = 1.0`
- `schema_success_rate = 1.0`
- `invalid_output_count = 0`

ดังนั้นงาน v3 ไม่ควรเริ่มจากการเพิ่มจำนวนข้อมูลแบบกว้าง ๆ แต่ควรเพิ่มตัวอย่างที่จงใจชนกับ confusion จริงของ Phase 6.1

## Dataset Buckets

| Bucket | Count | Purpose |
| --- | ---: | --- |
| `normal` hard negatives | 10 | สอนว่า single failed login, benign search terms และ single connection ไม่ใช่ suspicious pattern |
| `failed_login_bruteforce` positives | 10 | ทำ paired contrast กับ normal โดยใช้ repeated failures, lockout, rate limit และ auth burst |
| `sql_injection_attempt` | 10 | ย้ำ quote, tautology, `UNION SELECT`, `SLEEP(`, `information_schema` และ payload ใน login fields |
| `directory_traversal_attempt` | 10 | ย้ำ `../`, encoded traversal, Unix sensitive paths และ Windows path traversal |
| `port_scan_or_recon` | 10 | ย้ำ `unique_ports`, `nmap fingerprint`, `SYN scan detected`, horizontal scan และ service enumeration |

## Paired Contrast Examples

ชุดนี้ตั้งใจให้มีเคสที่หน้าตาคล้ายกันแต่ label ต่างกัน:

| Normal | Suspicious pair | Contrast |
| --- | --- | --- |
| `v3-hard-000001` | `v3-hard-000011` | `failed_attempts=1` เทียบกับ `failed_attempts=12 window=3m` |
| `v3-hard-000002` | `v3-hard-000012` | app login failed ครั้งเดียว เทียบกับ `failures=18` และ `outcome=blocked` |
| `v3-hard-000003` | `v3-hard-000013` | Windows `count=1` เทียบกับ `count=16` |
| `v3-hard-000004` / `v3-hard-000005` | `v3-hard-000022` | benign `select`/`union` search เทียบกับ `UNION SELECT username,password FROM users--` |
| `v3-hard-000006` | `v3-hard-000024` | benign `sleep+tracking` เทียบกับ `SLEEP(5)` timing payload |
| `v3-hard-000008` | `v3-hard-000041` | single allowed connection เทียบกับ sequential attempts และ `unique_ports=4` |

## Validation Rules

Generator ตรวจสิ่งต่อไปนี้ก่อนเขียนไฟล์:

- record IDs unique
- label distribution ต้องเท่ากัน label ละ 10
- record shape ต้องเป็น `id`, `instruction`, `input`, `output`
- output field ต้องตรงกับ schema
- `is_suspicious` ต้อง match label
- `evidence` ต้องมี 1-3 exact substrings จาก input และแต่ละชิ้นไม่เกิน 160 characters
- SFT formatter ต้องรับ record ได้ และ assistant target ต้องเป็น raw JSON ตาม `triage-json-v2.1`

ตรวจซ้ำได้ด้วย:

```bash
rtk .venv/bin/python scripts/create_v3_hard_contrast_dataset.py
rtk .venv/bin/python ml/unsloth/training_format.py \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --preview 1
```

## How To Use For V3 Training

ชุดนี้ควรใช้เป็น supplement ของ training split ไม่ใช่ eval split:

```bash
rtk sh -c 'cat data/splits/train.jsonl data/generated/v3-hard-contrast-security-triage.jsonl > data/generated/train-plus-v3-hard-contrast.jsonl'
rtk .venv/bin/python scripts/create_v3_training_split.py
```

จากนั้นให้ train v3 ด้วย `data/splits/train-v3-hard-contrast.jsonl` และ validate ด้วย `data/splits/validation-v3-hard-contrast.jsonl` ส่วน fixed `data/splits/test.jsonl` ยังเก็บไว้สำหรับ Phase 7 เท่านั้น

หลัง v3 model mini semantic eval ยังได้ `label_accuracy = 0.36` และยังทาย `failed_login_bruteforce` 17/25 ให้ขยับไป v3.1 recovery profile แทน:

```bash
rtk .venv/bin/python scripts/create_v3_1_training_split.py
rtk .venv/bin/python ml/unsloth/train_lora.py --preflight-only
```

v3.1 ใช้ canonical train 350 records รวมกับ hard contrast แบบ weighted 150 records รวมเป็น 500 records โดยยัง balanced ที่ label ละ 100 ส่วน `format.prompt_version` ใน config ต้องตรงกับ runtime prompt contract `triage-json-v2.1` ก่อนเริ่ม train จริง (source: ml/unsloth/config.example.yaml, ml/unsloth/train_lora.py, scripts/create_v3_1_training_split.py)

ก่อนใช้ fixed split ต้องทำตามลำดับนี้:

1. Validate training render format
2. Train v3 ด้วย train + hard contrast supplement
3. Rerun smoke output-contract gate
4. Rerun mini semantic eval
5. เปรียบเทียบ distribution และ confusion matrix ว่ายัง collapse ไป `failed_login_bruteforce` หรือไม่
6. ใช้ `data/splits/test.jsonl` เฉพาะเมื่อ Phase 6 decision พร้อมเข้า Phase 7 แล้ว

## What Not To Do

- อย่าเพิ่มชุดนี้เข้า validation/test
- อย่าใช้ `data/splits/test.jsonl` เพื่อเลือก hard cases หรือ prompt wording
- อย่าถือว่าชุดนี้แก้ model capacity แล้วจนกว่าจะ rerun mini semantic eval
- อย่า downsample `failed_login_bruteforce` ทันที เพราะชุดข้อมูลหลักยัง balanced และปัญหาที่เห็นคือ prediction collapse

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Created v3 hard contrast dataset supplement and documentation | `scripts/create_v3_hard_contrast_dataset.py`, `data/generated/v3-hard-contrast-security-triage.jsonl` | Created |
| 2026-05-21 | Codex | Created v3 train and validation split files without touching fixed test | `scripts/create_v3_training_split.py`, `data/splits/train-v3-hard-contrast.jsonl`, `data/splits/validation-v3-hard-contrast.jsonl` | Created |
| 2026-05-21 | Codex | Created v3.1 weighted hard-contrast split files after v3 mini eval still collapsed toward brute force | `scripts/create_v3_1_training_split.py`, `data/splits/train-v3-1-hard-contrast.jsonl`, `data/splits/validation-v3-1-hard-contrast.jsonl` | Created |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Keep v3 hard contrast data as a training supplement, not an eval split | Phase 6.1 error analysis needs targeted label-boundary examples without contaminating validation/test evidence | v3 training can mix this file into training, while smoke/mini/fixed test remain separate |
| 2026-05-21 | Use balanced hard contrast records, 10 per label | Prediction collapse is not proven source imbalance, so a balanced supplement teaches contrasts without changing label prior aggressively | v3 data targets hard cases while preserving a clear distribution policy |
| 2026-05-21 | Use v3.1 weighted hard contrast rather than fixed-test tuning | v3 model kept `label_accuracy = 0.36` on mini semantic eval, so the next recovery run should increase hard-case weight while preserving balanced labels and holding out the fixed test split | v3.1 train becomes 500 records with 100 per label; fixed `data/splits/test.jsonl` remains untouched |

## Related pages

- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[output-structure-fix/phase-6-1-evidence-constraints]]
- [[label-imbalance-and-prediction-collapse]]
- [[data-card]]
- [[data-formats-for-llm-training]]

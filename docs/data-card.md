# Data Card: Synthetic Security Triage Dataset

**Summary**

เอกสารนี้อธิบาย dataset รอบแรกของ POC ว่าสร้างจากอะไร ใช้ทำอะไรได้บ้าง และมีข้อจำกัดตรงไหน ข้อมูลชุดนี้เป็น synthetic ทั้งหมด สร้างด้วย `scripts/generate_dataset.py` เพื่อใช้พิสูจน์ workflow ของ security log triage ตั้งแต่ dataset, baseline, evaluation ไปจนถึง fine-tuning รอบแรก ไม่ใช่ตัวแทนของ production log จริง (source: AGENTS.md, docs/poc-plan.md, scripts/generate_dataset.py)

**Sources**

- `AGENTS.md` สำหรับ label scope, output schema, dataset rules และ privacy rules (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ dataset size, split และ POC success criteria (source: docs/poc-plan.md)
- `docs/Day2.md` สำหรับ Day 2 scope และ acceptance criteria (source: docs/Day2.md)
- `docs/dataset-input-output-format.md` สำหรับ JSONL record contract และ template-based generation rationale (source: docs/dataset-input-output-format.md)
- `docs/log-type-examples.md` สำหรับคำอธิบาย log format ที่ generator จำลองไว้ (source: docs/log-type-examples.md)
- `scripts/generate_dataset.py` สำหรับ generator, seed, template และ validation logic (source: scripts/generate_dataset.py)
- `data/schemas/triage-output.schema.json` สำหรับ output schema contract (source: data/schemas/triage-output.schema.json)

**Last updated**

2026-05-21

## Dataset Name

`synthetic-security-triage`

## Generated Files

```text
data/generated/synthetic-security-triage.jsonl
data/generated/v3-hard-contrast-security-triage.jsonl
data/generated/train-plus-v3-1-hard-contrast.jsonl
data/splits/train.jsonl
data/splits/validation.jsonl
data/splits/test.jsonl
data/splits/train-v3-1-hard-contrast.jsonl
data/splits/validation-v3-1-hard-contrast.jsonl
```

## Purpose

dataset นี้มีไว้สร้างฐานวัดผลรอบแรกให้ repeat ได้ ทุก record มี `instruction`, `input` และ `output` ตาม schema กลาง เพื่อให้ใช้ร่วมกันได้ทั้ง heuristic baseline, model baseline, evaluator และ fine-tuning path

เป้าหมายไม่ใช่พิสูจน์ว่า model ตรวจจับการ compromise ได้จริง แต่คือพิสูจน์ว่า workflow ของการ triage suspicious pattern ทำงานครบและวัดผลซ้ำได้ (source: docs/poc-plan.md)

## Generation Method

ข้อมูลสร้างด้วย Python script:

```bash
python3 scripts/generate_dataset.py
```

generator ใช้แนวทาง `template + variable pool + deterministic seed` โดย seed ปัจจุบันคือ `20260517` ทำให้รันซ้ำแล้วได้ชุดข้อมูลเดิม โครงนี้ช่วยให้รู้ชัดว่า log แต่ละบรรทัดควรมี label อะไร evidence อยู่ตรงไหน และควร split ไปชุดไหน (source: scripts/generate_dataset.py, docs/dataset-input-output-format.md)

log ที่สร้างมีหลาย format เช่น web access log, SSH auth log, application auth log, WAF log, Windows failed logon, firewall log, IDS log และ netflow-style log แบบสั้น รายละเอียดและตัวอย่างของแต่ละชนิดอยู่ใน [[log-type-examples]]

## Labels And Counts

รอบแรกเป็น label-balanced dataset จำนวน 500 records:

| Label | Count |
| --- | ---: |
| `normal` | 100 |
| `failed_login_bruteforce` | 100 |
| `sql_injection_attempt` | 100 |
| `directory_traversal_attempt` | 100 |
| `port_scan_or_recon` | 100 |

## Split

ใช้ split แบบ stratified `70/15/15`:

| Split | Records | Per label |
| --- | ---: | ---: |
| `train` | 350 | 70 |
| `validation` | 75 | 15 |
| `test` | 75 | 15 |

`test` split ต้องคงที่สำหรับ comparison และห้ามนำไปใช้ train หรือ tune prompt ระหว่าง evaluation (source: AGENTS.md, docs/poc-plan.md)

## Record Contract

แต่ละบรรทัดเป็น JSON object หนึ่ง record:

```json
{
  "id": "sample-000001",
  "instruction": "Analyze this security log and classify whether it is suspicious.",
  "input": "192.0.2.125 - - [17/May/2026:08:11:30 +0700] \"GET /health HTTP/1.1\" 200 243 \"-\" \"kube-probe/1.29\"",
  "output": {
    "label": "normal",
    "severity": "low",
    "is_suspicious": false,
    "evidence": ["GET /health", "200", "kube-probe/1.29"],
    "reason": "The request is a routine service health check with a successful response.",
    "recommended_action": "No immediate action required. Continue normal monitoring."
  }
}
```

`output` ต้องตรงกับ `data/schemas/triage-output.schema.json` และห้ามมี field เกิน schema (source: data/schemas/triage-output.schema.json)

## Validation

`scripts/generate_dataset.py` ตรวจในตัวก่อนเขียนไฟล์:

- จำนวน record รวมต้องเป็น 500
- แต่ละ label ต้องมี 100 records
- split ต้องเป็น `350/75/75`
- train, validation และ test ต้องไม่มี `id` ซ้ำข้ามกัน
- ทุก record ต้องมี `id`, `instruction`, `input`, `output`
- `output` ต้องมีเฉพาะ field ที่ schema กำหนด
- `label`, `severity` และ `is_suspicious` ต้องอยู่ใน contract
- `evidence` ต้องเป็น string ที่ไม่ว่าง และต้องพบอยู่ใน `input`

## Intended Uses

- ใช้ train/validation/test สำหรับ POC รอบแรก
- ใช้ทดสอบ rule-based heuristic baseline
- ใช้ทดสอบ evaluator ว่าวัด `label_accuracy`, `severity_accuracy`, `evidence_partial_match` และ schema validity ได้จริง
- ใช้เป็นชุดเริ่มต้นสำหรับ fine-tuning LFM2-350M หรือ model candidate ขนาดเล็กในภายหลัง

## V3 Hard Contrast Supplement

หลัง Phase 6.1 พบว่า mini semantic eval ผ่าน JSON/schema แล้วแต่ยังมี prediction collapse ไปทาง `failed_login_bruteforce` จึงเพิ่ม training supplement แบบแยกไฟล์:

```text
data/generated/v3-hard-contrast-security-triage.jsonl
```

ชุดนี้มี 50 records, label ละ 10 records และสร้างด้วย `scripts/create_v3_hard_contrast_dataset.py` เพื่อใช้ผสมกับ training split เท่านั้น ไม่ใช่ validation/test split (source: scripts/create_v3_hard_contrast_dataset.py, docs/output-structure-fix/phase-6-v3-hard-contrast-dataset.md)

เป้าหมายของ supplement นี้คือเพิ่ม hard negatives และ paired contrast examples เช่น `failed_attempts=1` เทียบกับ `failed_attempts=12`, benign `select`/`union` search เทียบกับ `UNION SELECT`, encoded traversal และ port scan signal อย่าง `unique_ports`, `nmap fingerprint`, `SYN scan detected`

หลัง v3 model ยังได้ `label_accuracy = 0.36` บน mini semantic eval จึงเพิ่ม v3.1 weighted split โดยใช้ canonical train 350 records รวมกับ hard contrast แบบ weighted 150 records:

```text
data/generated/train-plus-v3-1-hard-contrast.jsonl
data/splits/train-v3-1-hard-contrast.jsonl
data/splits/validation-v3-1-hard-contrast.jsonl
```

v3.1 train มี 500 records หรือ label ละ 100 ส่วน validation ยังเป็น canonical validation 75 records หรือ label ละ 15 และ fixed `data/splits/test.jsonl` ยังไม่ถูกใช้สำหรับ train/tune (source: scripts/create_v3_1_training_split.py, reports/openai-compatible-vllm-structured-outputs-v3-model-mini-semantic-eval.json)

## Limitations

dataset นี้ยังเป็น synthetic และ template-based จึงมีข้อจำกัดสำคัญ:

- log pattern ยังสะอาดและสม่ำเสมอกว่า production log จริง
- ยังไม่ครอบคลุม noise จากระบบจริง เช่น multiline logs, missing fields, proxy chain, timezone หลากหลาย หรือ parser artifact
- severity เป็น heuristic จาก template ไม่ใช่ risk scoring จาก environment จริง
- false-positive edge case มีแล้วแต่ยังน้อย ต้องเพิ่มเรื่อย ๆ หลังเห็นผล evaluator
- ไม่ควรใช้ตัวเลข evaluation จากชุดนี้ไปอ้างว่า model พร้อมใช้ใน SOC จริง

## Privacy

ชุดข้อมูลนี้ใช้ documentation IP ranges เช่น `192.0.2.0/24`, `198.51.100.0/24` และ `203.0.113.0/24` รวมถึง username และ hostname ปลอม ไม่มี production log, token, credential, cookie, session id หรือข้อมูลลูกค้า (source: scripts/generate_dataset.py, AGENTS.md)

## Refresh Instructions

เมื่อต้องการสร้าง dataset ใหม่:

```bash
python3 scripts/generate_dataset.py
```

ถ้าเปลี่ยน schema, label taxonomy, split policy หรือ generation logic ต้องอัปเดตหน้านี้, `docs/Day2.md`, `docs/dataset-input-output-format.md` และเอกสาร evaluation ที่เกี่ยวข้องพร้อมกัน

## Work Log

Append-only log สำหรับบันทึกว่า data card นี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-17 | Codex | Created first data card for the synthetic security triage dataset | `scripts/generate_dataset.py`, `data/generated/synthetic-security-triage.jsonl`, `data/splits/*.jsonl` | Drafted |
| 2026-05-17 | Codex | Linked the data card to log type examples | `docs/log-type-examples.md` | Updated |
| 2026-05-21 | Codex | Documented v3 hard contrast training supplement | `scripts/create_v3_hard_contrast_dataset.py`, `data/generated/v3-hard-contrast-security-triage.jsonl` | Updated |
| 2026-05-21 | Codex | Documented v3.1 weighted hard contrast split | `scripts/create_v3_1_training_split.py`, `data/splits/train-v3-1-hard-contrast.jsonl` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-17 | ใช้ synthetic template-based dataset เป็นชุดแรก | ต้องการ dataset ที่ repeat ได้ อธิบาย label/evidence ได้ และวัด evaluator ได้ก่อนใช้ log จริง | เหมาะกับ POC รอบแรก แต่ต้องระบุ limitation ชัดเจน |
| 2026-05-21 | ใช้ v3.1 weighted hard contrast เป็น training split ไม่ใช่ eval split | v3 mini eval ยังเกิด prediction collapse แต่ fixed test split ต้องคงไว้สำหรับ comparison เท่านั้น | train เพิ่มน้ำหนัก hard cases ได้โดยไม่ปน validation/test evidence |

## Related pages

- [[Day2]]
- [[dataset-input-output-format]]
- [[log-type-examples]]
- [[label-taxonomy]]
- [[triage-output-schema]]
- [[poc-plan]]

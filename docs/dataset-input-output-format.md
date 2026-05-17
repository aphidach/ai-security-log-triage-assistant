# Dataset Input Output Format

**Summary**

เอกสารนี้อธิบายรูปแบบ dataset รอบแรกของ POC ว่าแต่ละ record ต้องมี `instruction`, `input` และ `output` อย่างไร ใช้ JSONL เป็น format หลัก และบังคับให้ `output` ตรงกับ `data/schemas/triage-output.schema.json` เพื่อให้ข้อมูลชุดเดียวกันใช้ได้ทั้ง fine-tuning, baseline evaluation และ demo workflow (source: AGENTS.md, docs/poc-plan.md, data/schemas/triage-output.schema.json)

**Sources**

- `AGENTS.md` สำหรับ dataset rules, expected output schema และ privacy rules (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ dataset plan, label count และ split รอบแรก (source: docs/poc-plan.md)
- `docs/Day2.md` สำหรับ Day 2 dataset checklist และ acceptance criteria (source: docs/Day2.md)
- `data/schemas/triage-output.schema.json` สำหรับ schema ของ `output` (source: data/schemas/triage-output.schema.json)
- `docs/triage-output-schema.md` และ `docs/label-taxonomy.md` สำหรับคำอธิบาย field, label และ evidence (source: docs/triage-output-schema.md, docs/label-taxonomy.md)
- `docs/log-type-examples.md` สำหรับคำอธิบายและตัวอย่าง log format ที่ generator จำลองไว้ (source: docs/log-type-examples.md)

**Last updated**

2026-05-17

## เป้าหมายของ dataset

dataset รอบแรกมีไว้พิสูจน์ workflow ให้ครบ ไม่ใช่พิสูจน์ว่า model พร้อมใช้กับ production log แล้ว เป้าหมายคือสร้างข้อมูลที่วัดซ้ำได้ ใช้ train ได้ ใช้ validation ได้ และใช้ test split เดียวกันเทียบ baseline กับ fine-tuned model ได้อย่างแฟร์

รอบแรกจะใช้ synthetic data ก่อน เพราะควบคุม label, evidence และ edge case ได้ง่ายกว่า log จริง แต่ต้องเขียนข้อจำกัดไว้ใน data card ภายหลัง (source: docs/Day2.md)

## File Format

ใช้ JSONL เป็น format หลัก:

```text
data/splits/train.jsonl
data/splits/validation.jsonl
data/splits/test.jsonl
```

หนึ่งบรรทัดคือหนึ่ง record ที่ parse เป็น JSON ได้เอง ห้ามทำเป็น JSON array ก้อนใหญ่ เพราะ training และ evaluator ควรอ่านทีละ record ได้

## Record Shape

แต่ละ record ต้องมี 4 field หลัก:

```json
{
  "id": "sample-000001",
  "instruction": "Analyze this security log and classify whether it is suspicious.",
  "input": "192.168.1.20 - - [10/May/2026] \"GET /login?user=admin' OR '1'='1 HTTP/1.1\" 200",
  "output": {
    "label": "sql_injection_attempt",
    "severity": "high",
    "is_suspicious": true,
    "evidence": ["admin' OR '1'='1"],
    "reason": "The request contains a common SQL injection pattern.",
    "recommended_action": "Review web application logs and block or rate-limit the source IP."
  }
}
```

| Field | Type | ความหมาย |
| --- | --- | --- |
| `id` | string | id คงที่ของ sample เช่น `sample-000001` ใช้ trace ตอน debug และ report |
| `instruction` | string | คำสั่งกลางที่บอก task ให้ model วิเคราะห์ security log |
| `input` | string | log line หรือกลุ่ม log สั้น ๆ ที่ต้องวิเคราะห์ |
| `output` | object | expected triage result ที่ต้องตรงกับ schema กลาง |

## Instruction

รอบแรกให้ใช้ instruction เดียวกันก่อน:

```text
Analyze this security log and classify whether it is suspicious.
```

เหตุผลคือเรายังต้องการวัดผลจาก log pattern และ output schema ก่อน ไม่อยากให้ variation ของ instruction กลายเป็นตัวแปรหลักตั้งแต่ dataset ชุดแรก

## Input

`input` คือ security log หนึ่งบรรทัด หรือกลุ่ม log สั้น ๆ ที่พอจะสรุป pattern ได้ใน record เดียว ตัวอย่าง source format ที่ generator ใช้จำลองได้:

- web access log
- SSH auth log
- application auth log
- WAF log
- Windows failed logon
- firewall log
- IDS log
- netflow-style log แบบสั้น

คำอธิบายและตัวอย่างของ log แต่ละแบบอยู่ใน [[log-type-examples]]

รอบแรกควรมีทั้งเคสง่ายและเคสหลอก เช่น:

- normal request ที่มีคำว่า `admin` แต่เป็น login สำเร็จ
- failed login 1 ครั้งที่ยังไม่ถึง brute force
- encoded traversal payload เช่น `..%2f`
- SQL-like text ที่ไม่ใช่ payload จริง
- probe แค่ครั้งเดียวที่ยังไม่พอเรียก scan

## Output

`output` ต้องตรงกับ `data/schemas/triage-output.schema.json` เสมอ:

```json
{
  "label": "sql_injection_attempt",
  "severity": "high",
  "is_suspicious": true,
  "evidence": ["admin' OR '1'='1"],
  "reason": "The request contains a common SQL injection pattern.",
  "recommended_action": "Review web application logs and block or rate-limit the source IP."
}
```

field ที่ต้องมี:

- `label`: หนึ่งใน 5 label รอบแรก
- `severity`: `low`, `medium`, `high` หรือ `critical`
- `is_suspicious`: boolean
- `evidence`: array ของ string ที่อ้างอิงจาก `input`
- `reason`: เหตุผลสั้น ๆ ว่าทำไมเลือก label นี้
- `recommended_action`: action ถัดไปที่ analyst ควรตรวจสอบ

ถ้า `output` มี field เกินจาก schema เช่น `confidence` หรือ `mitre_id` ให้ถือว่า invalid ในรอบแรก จนกว่าจะตัดสินใจเพิ่ม schema อย่างเป็นทางการ

## Dataset Size And Split

รอบแรกใช้ 500 records แบบ label-balanced:

```text
normal: 100
failed_login_bruteforce: 100
sql_injection_attempt: 100
directory_traversal_attempt: 100
port_scan_or_recon: 100
```

split ใช้ `70/15/15`:

```text
train: 350 records
validation: 75 records
test: 75 records
```

test split ต้องคงที่สำหรับ comparison ห้ามเอา test examples ไปใช้ train หรือ tune prompt ระหว่างทำ evaluation

## Example Records

### Normal

```json
{
  "id": "sample-000001",
  "instruction": "Analyze this security log and classify whether it is suspicious.",
  "input": "10.0.0.12 - - [10/May/2026] \"GET /health HTTP/1.1\" 200",
  "output": {
    "label": "normal",
    "severity": "low",
    "is_suspicious": false,
    "evidence": ["GET /health", "200"],
    "reason": "The request is a routine health check with a successful response.",
    "recommended_action": "No immediate action required. Continue normal monitoring."
  }
}
```

### Failed Login Brute Force

```json
{
  "id": "sample-000102",
  "instruction": "Analyze this security log and classify whether it is suspicious.",
  "input": "May 10 12:45:31 auth sshd[1842]: Failed password for admin from 203.0.113.24 port 49222 ssh2; repeated 8 times in 2 minutes",
  "output": {
    "label": "failed_login_bruteforce",
    "severity": "high",
    "is_suspicious": true,
    "evidence": ["Failed password", "repeated 8 times"],
    "reason": "The log shows repeated failed authentication attempts against the admin account.",
    "recommended_action": "Review authentication logs for the source IP and consider blocking or rate-limiting it."
  }
}
```

### SQL Injection Attempt

```json
{
  "id": "sample-000203",
  "instruction": "Analyze this security log and classify whether it is suspicious.",
  "input": "198.51.100.44 - - [10/May/2026] \"GET /search?q=' UNION SELECT username,password FROM users-- HTTP/1.1\" 500",
  "output": {
    "label": "sql_injection_attempt",
    "severity": "high",
    "is_suspicious": true,
    "evidence": ["UNION SELECT", "users--"],
    "reason": "The request contains SQL query syntax in a user-controlled parameter.",
    "recommended_action": "Review web application logs for the source IP and check whether the request reached the database layer."
  }
}
```

## Validation Rules

ก่อนใช้ dataset ต้องตรวจอย่างน้อย:

- ทุกบรรทัด parse เป็น JSON ได้
- ทุก record มี `id`, `instruction`, `input`, `output`
- `id` ไม่ซ้ำกัน
- `output` validate ผ่าน `data/schemas/triage-output.schema.json`
- `label` อยู่ใน 5 label รอบแรก
- `evidence` เป็น array ของ string ที่ไม่ว่าง
- split ไม่มี record ซ้ำข้าม `train`, `validation`, `test`
- test split ไม่ถูกใช้ระหว่าง train

## Generator Guidelines

เมื่อเขียน `scripts/generate_dataset.py` ให้ยึดหลักนี้:

- deterministic ด้วย seed คงที่
- สร้าง label ละ 100 records
- มีหลาย template ต่อ label
- ใส่ edge case ที่ทำให้ heuristic/model ต้องระวัง false positive
- ให้ `evidence` มาจาก `input` ให้มากที่สุด เพื่อให้ evaluator ตรวจ partial match ได้
- ห้ามใช้ production log จริงหรือข้อมูลลูกค้า

## Template-Based Generation Rationale

`scripts/generate_dataset.py` จะสร้าง text ด้วยแนวทาง `template + variable pool + deterministic seed` ก่อน ไม่ใช้ LLM generate dataset สดในรอบ Day 2

เหตุผลหลักคือ dataset รอบแรกต้องวัดซ้ำได้และอธิบายได้ ถ้า log ถูกสร้างจาก template เราจะรู้แน่นอนว่า payload อยู่ตรงไหน label มาจาก rule ไหน และ evidence ใดควรอยู่ใน `output.evidence` ตรงนี้ทำให้ evaluation เช่น `label_accuracy`, `schema_success_rate` และ `evidence_partial_match` มีความหมายมากขึ้น เพราะ expected answer ไม่ได้มาจากข้อความที่เดาเอาเอง (source: AGENTS.md, docs/Day2.md)

การให้ LLM generate ตัวอย่างโดยตรงตั้งแต่รอบแรกมีความเสี่ยงหลายอย่าง: output อาจไม่ deterministic, อาจใส่ field นอก schema, อาจแต่ง evidence ที่ไม่มีอยู่จริงใน log, อาจสร้าง label ปน taxonomy อื่น และทำให้ test split ย้อนรอยยากว่า record นั้นควรถูกต้องเพราะอะไร ดังนั้นในรอบแรก LLM ใช้ได้แค่เป็นผู้ช่วยเสนอไอเดีย template หรือ edge case แต่ record ที่เข้าชุด train/validation/test ต้องถูกสร้างและ validate โดย Python script เสมอ

แนวทางนี้ยังช่วยให้ใส่ false-positive edge case ได้ตั้งแต่ต้น เช่น normal log ที่มีคำว่า `admin`, failed login ครั้งเดียวที่ยังไม่ใช่ brute force, SQL-like text ที่เป็น search ปกติ หรือ probe เดี่ยวที่ยังไม่พอเรียก port scan ข้อจำกัดคือข้อมูลยังเป็น synthetic อยู่ จึงต้องเขียนไว้ใน `docs/data-card.md` ว่า dataset นี้ใช้พิสูจน์ workflow ไม่ใช่ตัวแทน production log จริง

## Python-First Workflow

workflow สำหรับ dataset, validation, baseline evaluation และ fine-tuning ให้ใช้ Python เป็นหลัก ส่วน TypeScript ให้เป็นฝั่ง frontend/UI contract

คำสั่งเริ่มต้นของ Day 2 ควรเป็น:

```bash
python3 scripts/generate_dataset.py
```

script นี้ควรสร้างไฟล์หลักอย่างน้อย:

```text
data/generated/synthetic-security-triage.jsonl
data/splits/train.jsonl
data/splits/validation.jsonl
data/splits/test.jsonl
```

เหตุผลที่เลือก Python คือ dataset และ fine-tuning จะต่อกับ tooling ฝั่ง ML ได้ตรงกว่า เช่น JSONL processing, schema validation, evaluator, notebook และ Unsloth training path ขณะที่ frontend ยังอ่านผลลัพธ์ผ่าน JSON/JSONL ได้โดยไม่ต้องเอา generator ไปผูกกับ Next.js

## Current Generator

`scripts/generate_dataset.py` ถูกใช้เป็น generator รอบแรกแล้ว script นี้สร้าง records แบบ deterministic จำนวน 500 records, split เป็น `train/validation/test` แบบ `350/75/75`, ตรวจ id ซ้ำ, ตรวจ label count, ตรวจ split overlap และตรวจว่า `evidence` ทุกตัวอยู่ใน `input` ก่อนเขียนไฟล์ (source: scripts/generate_dataset.py)

ไฟล์ที่ได้:

```text
data/generated/synthetic-security-triage.jsonl
data/splits/train.jsonl
data/splits/validation.jsonl
data/splits/test.jsonl
```

รายละเอียดข้อจำกัดและวิธีใช้ dataset รอบแรกอยู่ใน `docs/data-card.md`

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created dataset input/output format page | `docs/dataset-input-output-format.md` | Drafted |
| 2026-05-16 | Codex | Added Python-first generator workflow guidance | `scripts/generate_dataset.py`, `data/splits/*.jsonl` | Updated |
| 2026-05-17 | Codex | Documented why Day 2 uses template-based generation before LLM-generated records | `scripts/generate_dataset.py`, `docs/Day2.md` | Updated |
| 2026-05-17 | Codex | Added current generator status and generated dataset file paths | `scripts/generate_dataset.py`, `docs/data-card.md` | Updated |
| 2026-05-17 | Codex | Linked input format guidance to log type examples | `docs/log-type-examples.md` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ `instruction`, `input`, `output` เป็น record contract | format นี้ใช้ต่อได้ทั้ง SFT, evaluator และ demo workflow | dataset generator, trainer และ evaluator ต้องยึด shape เดียวกัน |
| 2026-05-16 | ใช้ 500 records แบบ label-balanced ในรอบแรก | ทรัพยากรจำกัดและต้องการวัด workflow ก่อนขยายข้อมูล | Day 2 generator ต้องสร้าง label ละ 100 records และ split `350/75/75` |
| 2026-05-16 | ใช้ Python เป็นภาษาหลักของ data workflow | workflow ฝั่ง dataset, validation, evaluation และ fine-tuning อยู่ใกล้ Python tooling มากกว่า TypeScript | script หลักเปลี่ยนเป็น `scripts/generate_dataset.py`; TypeScript ใช้เฉพาะ frontend contract และ UI |
| 2026-05-17 | ใช้ template-based generation เป็นค่าเริ่มต้นของ Day 2 | ต้องการ dataset ที่ deterministic, ตรวจ evidence ได้ และย้อนเหตุผลของ label ได้ชัดกว่า LLM-generated records | `scripts/generate_dataset.py` ต้องสร้าง log จาก template และ variable pool; LLM ใช้ได้แค่ช่วยเสนอ template ภายหลัง ไม่ใช่ source of truth ของ split แรก |
| 2026-05-17 | ให้ generator ตรวจ evidence substring ก่อนเขียน dataset | metric ฝั่ง evidence จะมีความหมายก็ต่อเมื่อ expected evidence ย้อนกลับไปหา log ได้จริง | templates ต้องเลือก evidence ที่ปรากฏใน `input` โดยตรง |

## Related pages

- [[Day2]]
- [[poc-plan]]
- [[triage-output-schema]]
- [[label-taxonomy]]
- [[data-card]]
- [[log-type-examples]]
- [[dataset-source-strategy]]

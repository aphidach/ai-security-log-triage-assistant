# POC Plan: AI Security Log Triage Assistant

เอกสารนี้คือแผนทำ POC สำหรับระบบช่วยคัดกรอง security log ด้วย small language model และ fine-tuning

เป้าหมายไม่ใช่ทำระบบ SOC เต็มรูปแบบตั้งแต่วันแรก แต่คือพิสูจน์ให้ได้ว่าเราสามารถสร้าง dataset เล็ก ๆ, วัด baseline, fine-tune โมเดลขนาดเล็ก แล้วเทียบผลก่อน-หลัง fine-tune ได้อย่างเป็นระบบ

## 1. เป้าหมายของ POC

ระบบควรรับ log หนึ่งรายการ หรือชุด log สั้น ๆ แล้วตอบกลับเป็นผลวิเคราะห์แบบมีโครงสร้าง

สิ่งที่ต้องตอบให้ได้:

- log นี้เป็นเหตุการณ์ปกติหรือผิดปกติ
- ถ้าน่าสงสัย เข้ากับ pattern แบบไหน
- หลักฐานอยู่ตรงไหนใน log
- severity ควรเป็นระดับไหน
- เหตุผลสั้น ๆ คืออะไร
- ควรตรวจสอบอะไรต่อ

ตัวอย่างคำตอบที่ต้องการ:

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

สิ่งสำคัญคือระบบนี้ใช้เพื่อ **triage** ไม่ใช่ตัดสินว่าเครื่องถูกเจาะแล้วแน่นอน คำตอบควรชี้ว่า “น่าสงสัยเพราะอะไร” และ “ควรตรวจอะไรต่อ” มากกว่าฟันธงเกินหลักฐาน

## 2. ขอบเขตรอบแรก

เริ่มจาก label น้อย ๆ ก่อน เพื่อให้ dataset และ evaluation คุมได้จริง

label สำหรับ POC รอบแรก:

- `normal`
- `failed_login_bruteforce`
- `sql_injection_attempt`
- `directory_traversal_attempt`
- `port_scan_or_recon`

ยังไม่ทำ:

- malware classification เต็มรูปแบบ
- incident response automation
- SIEM integration จริง
- multi-step attack chain reconstruction
- RAG จากเอกสาร policy หรือ knowledge base
- การยืนยันว่าระบบถูก compromise แล้วจริงหรือไม่

ถ้ารอบแรกวัดผลได้ดี ค่อยขยายไป XSS, command injection, suspicious user-agent, privilege escalation, cloud audit log หรือ Windows event log ทีหลัง

## 3. Success Criteria

POC ถือว่าสำเร็จถ้ามีของครบชุดนี้:

- มี dataset แบบ JSONL อย่างน้อย 300 ตัวอย่าง
- แบ่ง `train`, `validation`, `test` ชัดเจน
- มี baseline ที่รันได้โดยไม่ต้องใช้ GPU หรือ API key
- มี evaluation script ที่ให้ผลซ้ำได้
- มี adapter สำหรับเรียก baseline model หรือ fine-tuned model
- มี training script หรือ notebook path สำหรับ Unsloth LoRA/QLoRA
- มีรายงานเทียบ baseline กับ fine-tuned model
- มี demo UI หรือ CLI ที่เอาให้คนอื่นลองได้

ตัวเลขเป้าหมายรอบแรก:

```text
Label accuracy: >= 80% บน synthetic test set
JSON parse success: >= 95%
Evidence partial match: >= 70%
Average latency: บันทึกเป็นตัวเลข ยังไม่ต้อง optimize
```

ตัวเลขพวกนี้ไม่ใช่คำสัญญาว่าระบบพร้อม production แต่เป็นเกณฑ์ให้รู้ว่า POC เดินถูกทางหรือยัง

## 4. โครง repo ที่จะใช้

โครงหลัก:

```text
ai-security-log-triage-assistant/
  AGENTS.md
  README.md

  data/
    raw/
    generated/
    splits/
      train.jsonl
      validation.jsonl
      test.jsonl
    schemas/
      triage-output.schema.json

  docs/
    poc-plan.md
    data-card.md
    evaluation-method.md
    fine-tuning-notes.md

  scripts/
    generate-dataset.ts
    split-dataset.ts
    evaluate.ts

  frontend/
    app/
    components/
    lib/
      labels.ts
      triage-schema.ts
      prompts.ts
      baseline-analyzer.ts
      model-adapters/
        heuristic.ts
        openai-compatible.ts
        local-ollama.ts
        fine-tuned.ts
      evaluation/
        metrics.ts
        runner.ts

  ml/
    unsloth/
      train_lora.py
      inference.py
      config.example.yaml
    notebooks/
      fine_tune_colab.md

  reports/
    baseline-eval.json
    finetuned-eval.json
    comparison.md
```

เหตุผลของโครงนี้:

- `data/` เก็บข้อมูลและ schema แยกจาก code
- `scripts/` เก็บ command-line workflow ที่ใช้สร้าง dataset และวัดผล
- `frontend/lib/` เป็นแกน logic ที่ UI, API และ CLI ใช้ร่วมกัน
- `ml/` แยก training ออกจาก frontend เพราะ fine-tune มี dependency และ environment คนละชุด
- `reports/` เก็บผลที่นำไปโชว์หรือคุยกับ stakeholder ได้

## 5. Dataset Plan

รอบแรกใช้ synthetic data เพราะควบคุม label, evidence และ edge case ได้ง่าย

format ต่อหนึ่ง record:

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

จำนวนข้อมูลตั้งต้น:

```text
normal: 100-200
failed_login_bruteforce: 100-200
sql_injection_attempt: 100-200
directory_traversal_attempt: 100-200
port_scan_or_recon: 100-200
```

รวมประมาณ 500-1,000 records

ตัวอย่างแหล่ง pattern ที่ใช้เป็น reference:

- OWASP attack taxonomy สำหรับชื่อและความหมายของ attack pattern
- SigmaHQ สำหรับแนวคิด detection rule, evidence, false positive
- Loghub สำหรับแนวทาง log analytics dataset
- Splunk BOTS และ OTRF Security Datasets สำหรับ scenario แบบ SOC

ข้อควรระวัง:

- synthetic data มักง่ายกว่า log จริง ต้องเขียน `docs/data-card.md` อธิบายข้อจำกัดไว้
- ห้าม commit log production จริง
- ถ้าใช้ log จริงภายหลัง ต้อง sanitize IP, hostname, username, token, cookie, session id และข้อมูลลูกค้าก่อนเสมอ

## 6. Baseline Plan

ต้องมี baseline ที่รันได้ทันทีโดยไม่ต้อง fine-tune

baseline รอบแรกมี 2 แบบ:

1. `heuristic baseline`

ใช้ rule ง่าย ๆ ตรวจ pattern เช่น:

- SQL injection: `' OR '1'='1`, `UNION SELECT`, `--`, `SLEEP(`, `information_schema`
- directory traversal: `../`, `..%2f`, `/etc/passwd`, `boot.ini`
- brute force: repeated failed login, `401`, `invalid password`, user เดิมหรือ IP เดิมซ้ำหลายครั้ง
- port scan/recon: หลาย port หรือหลาย path ในเวลาสั้น, `nmap`, `masscan`, repeated connection refused

ข้อดีคือรันได้แน่นอนและใช้เป็น floor สำหรับเทียบกับ model

2. `model baseline`

เรียก model ที่ยังไม่ fine-tune เช่น:

- OpenAI-compatible endpoint
- Ollama
- LM Studio
- vLLM

adapter ทุกตัวควรคืน output schema เดียวกัน เพื่อให้ evaluator ไม่ต้องรู้ว่าเบื้องหลังเป็น model ไหน

## 7. Fine-Tuning Plan

รอบแรกใช้ supervised fine-tuning บน small instruct model

model ที่น่าลอง:

- Qwen 1.5B หรือ 3B class instruct model
- Phi small instruct model
- small Llama-family instruct model

แนวทาง:

- ใช้ LoRA หรือ QLoRA ก่อน
- ใช้ Unsloth เป็น training path หลัก เพราะเหมาะกับงาน POC ที่อยาก fine-tune small model ด้วยทรัพยากรจำกัด
- เก็บ script ไว้ใน `ml/unsloth/`
- training data ใช้จาก `data/splits/train.jsonl`
- validation ใช้ `data/splits/validation.jsonl`
- test split ห้ามแตะระหว่าง train

output ที่ควรได้จากการ train:

```text
ml/unsloth/outputs/
  security-log-triage-lora/
```

หลัง train เสร็จ ต้องมี inference path ที่รับ log แล้วคืน JSON schema เดิม

## 8. Evaluation Plan

evaluation ต้องเป็นหัวใจของ repo นี้

metrics รอบแรก:

- `label_accuracy`: label ตรงกับ expected output หรือไม่
- `json_parse_success_rate`: model ตอบเป็น JSON ที่ parse ได้หรือไม่
- `schema_success_rate`: field ครบและ type ถูกหรือไม่
- `severity_accuracy`: severity ตรงหรือไม่
- `evidence_partial_match`: evidence ที่ตอบมี substring ตรงกับ expected evidence หรือไม่
- `average_latency_ms`: เวลาเฉลี่ยต่อ sample
- `invalid_output_count`: จำนวน output ที่ใช้ต่อไม่ได้

ผล evaluation ควรออกทั้ง JSON และ markdown:

```text
reports/
  baseline-eval.json
  finetuned-eval.json
  comparison.md
```

ตัวอย่างตารางที่ต้องการ:

```text
Metric                 Heuristic   Base Model   Fine-tuned
Label accuracy          0.82       0.76         0.90
JSON success            1.00       0.88         0.98
Severity accuracy       0.78       0.70         0.86
Evidence partial match  0.74       0.61         0.82
Avg latency             10ms       1200ms       650ms
```

ถ้า fine-tuned model แพ้ heuristic baseline บาง metric ต้องเขียนตรง ๆ ใน report เพราะนั่นคือข้อมูลสำคัญ ไม่ใช่ความล้มเหลวของ POC

## 9. Demo Plan

demo ควรเป็นเครื่องมือใช้งานจริง ไม่ใช่ landing page

หน้าจอหลัก:

- textarea สำหรับ paste log
- sample log picker
- selector เลือก analyzer: heuristic, base model, fine-tuned model
- ปุ่ม Analyze
- structured result card
- evidence highlight ใน log
- comparison panel สำหรับผล baseline vs fine-tuned

ข้อมูลที่แสดง:

- label
- severity
- suspicious / normal
- evidence
- reason
- recommended action
- raw JSON output

ถ้ายังไม่มี fine-tuned model จริง UI ต้องแสดงสถานะว่า adapter ยังไม่ได้ configure ไม่ควร fake result ว่าเป็น fine-tuned แล้ว

## 10. Development Milestones

### Milestone 1: Project Foundation

สิ่งที่ทำ:

- สร้าง Next.js/TypeScript project
- เพิ่ม schema และ labels
- เพิ่ม README ขั้นต้น
- เพิ่ม docs หลัก

ผลลัพธ์:

- repo เปิดแล้วเข้าใจว่า POC นี้ทำอะไร
- dev server รันได้

### Milestone 2: Dataset And Baseline

สิ่งที่ทำ:

- เขียน dataset generator
- generate synthetic records
- split train/validation/test
- เขียน heuristic baseline

ผลลัพธ์:

- มี `data/splits/*.jsonl`
- analyze log ได้โดยไม่ต้องใช้ model

### Milestone 3: Evaluation Harness

สิ่งที่ทำ:

- เขียน evaluator
- วัด metric หลัก
- export report

ผลลัพธ์:

- มี baseline score จริง
- คุยเรื่องคุณภาพ model ด้วยตัวเลขได้

### Milestone 4: Model Adapter

สิ่งที่ทำ:

- เพิ่ม OpenAI-compatible adapter
- เพิ่ม local model adapter เช่น Ollama หรือ LM Studio
- enforce JSON output parsing

ผลลัพธ์:

- เทียบ heuristic กับ base model ได้

### Milestone 5: Fine-Tuning Path

สิ่งที่ทำ:

- เพิ่ม Unsloth training script
- เพิ่ม config ตัวอย่าง
- เพิ่ม inference script
- document วิธีรันบน GPU/Colab

ผลลัพธ์:

- มีทาง fine-tune small model จริง
- มี checkpoint หรือ adapter output ให้ทดลอง

### Milestone 6: Demo And Report

สิ่งที่ทำ:

- ทำ UI
- เพิ่มหน้า comparison
- เขียน `reports/comparison.md`
- polish README

ผลลัพธ์:

- demo ได้ใน 2-3 นาที
- อธิบายกับ stakeholder ได้ว่า baseline เป็นอย่างไร fine-tune ดีขึ้นตรงไหน และยังมีข้อจำกัดอะไร

## 11. Suggested Timeline

```text
Day 1: repo setup, schema, labels, docs
Day 2: dataset generator และ synthetic dataset รอบแรก
Day 3: heuristic baseline และ evaluator
Day 4: model baseline adapter
Day 5: Unsloth fine-tuning script และ training notes
Day 6: evaluate fine-tuned model และทำ comparison report
Day 7: demo UI, README, video/demo script
```

ถ้าเวลาน้อย ให้ตัด model baseline adapter ออกก่อน แล้วทำ heuristic baseline + fine-tuned comparison เป็นแกนหลัก

## 12. Risks And Mitigations

### Dataset ง่ายเกินไป

ความเสี่ยงคือ model ท่อง pattern จาก synthetic data แล้วดูเหมือนเก่งเกินจริง

วิธีลดความเสี่ยง:

- เพิ่ม normal case ที่หน้าตาคล้าย attack
- เพิ่ม encoded payload
- เพิ่ม noisy log fields
- แยก pattern ใน test set ไม่ให้เหมือน train 100%
- เขียน data-card อธิบายข้อจำกัด

### Model ตอบ JSON ไม่คงที่

ความเสี่ยงคือ evaluator ใช้งานยากและ UI พัง

วิธีลดความเสี่ยง:

- ใช้ schema validation
- เพิ่ม retry/repair เฉพาะจุด
- วัด JSON success rate แยกจาก label accuracy
- fine-tune ให้ตอบเฉพาะ JSON

### Fine-tune ไม่ชนะ baseline

เรื่องนี้เกิดได้ โดยเฉพาะเมื่อ label ง่ายและ heuristic จับ pattern ได้ตรง

วิธีลดความเสี่ยง:

- เพิ่มเคส ambiguous ที่ heuristic พลาด
- วัด evidence quality และ reason quality เพิ่ม
- อย่าเปรียบเทียบแค่ accuracy
- รายงานผลตรง ๆ ว่า model ชนะตรงไหน แพ้ตรงไหน

### Overclaim เรื่อง security

ระบบนี้ไม่ควรบอกว่า “ถูก hack แล้ว” จาก log เส้นเดียว

วิธีลดความเสี่ยง:

- ใช้คำว่า suspicious, likely, recommended investigation
- แสดง evidence เสมอ
- ใส่ disclaimer ใน README และ UI

## 13. Definition Of Done

รอบ POC แรกถือว่า done เมื่อ:

- generate dataset ได้จาก command เดียว
- run evaluator ได้จาก command เดียว
- baseline report ถูกเขียนลง `reports/`
- UI วิเคราะห์ sample log ได้
- fine-tuning path มี script และคำอธิบายครบพอให้รันต่อได้
- README อธิบาย setup, run, evaluate, train ได้
- ไม่มีการ commit secret หรือ log จริงที่ยังไม่ sanitize

## 14. Next Steps

งานถัดไปหลังเอกสารนี้:

1. สร้าง project foundation ด้วย Next.js และ TypeScript
2. เพิ่ม `data/schemas/triage-output.schema.json`
3. เพิ่ม `frontend/lib/labels.ts` และ `frontend/lib/triage-schema.ts`
4. เขียน `scripts/generate-dataset.ts`
5. generate dataset รอบแรก แล้วค่อยเริ่ม baseline/evaluation

# AI Security Log Triage Assistant

POC นี้ทดลองทำระบบช่วยคัดกรอง security log ด้วยโมเดลขนาดเล็กและ fine-tuning

เป้าหมายไม่ใช่สร้าง SOC อัตโนมัติ หรือฟันธงว่าเครื่องถูกเจาะแล้วจาก log เส้นเดียว แต่คือพิสูจน์ให้ได้ว่าเราสร้าง dataset เล็ก ๆ, มี baseline ที่วัดได้, fine-tune โมเดล แล้วเทียบผลก่อน-หลัง fine-tune ได้อย่างเป็นระบบ

ผลลัพธ์ที่ระบบต้องคืนกลับมาคือ triage แบบมีโครงสร้าง: เหตุการณ์ปกติหรือน่าสงสัย, เข้ากับ pattern ไหน, หลักฐานอยู่ตรงไหนใน log, severity เท่าไหร่, เหตุผลสั้น ๆ คืออะไร และควรตรวจอะไรต่อ

## สถานะตอนนี้

repo นี้ยังอยู่ช่วงวาง foundation

ของที่มีแล้ว:

- แผน POC ใน `docs/poc-plan.md`
- กติกาการทำงานของ agent ใน `AGENTS.md`
- README ฉบับตั้งต้นนี้

ของที่ยังต้องทำ:

- output schema และ label taxonomy ในโค้ด
- synthetic dataset generator
- train / validation / test split
- heuristic baseline
- evaluation runner
- model adapters
- Next.js demo UI
- Unsloth LoRA / QLoRA training path
- evaluation report

## ขอบเขตรอบแรก

รอบแรกตั้งใจคุม taxonomy ให้เล็กก่อน เพื่อให้ dataset และ evaluator เช็กคุณภาพได้จริง

label ที่รองรับ:

- `normal`
- `failed_login_bruteforce`
- `sql_injection_attempt`
- `directory_traversal_attempt`
- `port_scan_or_recon`

ยังไม่ทำในรอบแรก:

- malware classification เต็มรูปแบบ
- incident response automation
- SIEM integration จริง
- multi-step attack chain reconstruction
- RAG จาก policy หรือ knowledge base
- การยืนยันว่า host ถูก compromise แล้วจริง

## Output Schema

baseline, model adapter, API และ UI ควรใช้ schema เดียวกันทั้งหมด

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

ถ้า schema เปลี่ยน ต้องอัปเดตพร้อมกันทั้ง dataset generator, evaluator, API, UI และเอกสาร เพราะไม่อย่างนั้นผล evaluation จะเทียบกันไม่ได้

## Dataset

ข้อมูลรอบแรกใช้ JSONL และเริ่มจาก synthetic data ก่อน เพื่อคุม label, evidence และ edge case ได้ง่าย

ตัวอย่าง record:

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

เป้าหมายตั้งต้นคือ 500-1,000 records แบ่งเป็น `train`, `validation` และ `test` ชัดเจน

ข้อจำกัดสำคัญ: synthetic log มักง่ายกว่า log จริง ผลที่ได้จึงบอกได้แค่ว่า POC เริ่มแยก pattern พื้นฐานได้หรือยัง ไม่ใช่หลักฐานว่าระบบพร้อมใช้กับ production traffic

## Baseline และ Evaluation

หัวใจของ repo นี้คือการวัดผล ไม่ใช่แค่ทำ demo ให้ดูเหมือนฉลาด

baseline แรกควรเป็น rule-based heuristic ที่รันได้ในเครื่องโดยไม่ต้องใช้ GPU หรือ API key เช่นจับ pattern ของ SQL injection, directory traversal, brute force และ port scan

metric ที่ต้องเก็บอย่างน้อย:

- `label_accuracy`
- `json_parse_success_rate`
- `schema_success_rate`
- `severity_accuracy`
- `evidence_partial_match`
- `average_latency_ms`
- `invalid_output_count`

ถ้า fine-tuned model แพ้ heuristic baseline บาง metric ก็ต้องรายงานตรง ๆ เพราะนั่นคือข้อมูลสำคัญของ POC เหมือนกัน

## โครงสร้าง repo ที่ตั้งใจ

```text
data/
  raw/
  generated/
  splits/
  schemas/
docs/
  poc-plan.md
  data-card.md
  evaluation-method.md
  fine-tuning-notes.md
ml/
  unsloth/
  notebooks/
reports/
scripts/
src/
  app/
  components/
  lib/
```

แนวคิดหลักคือแยก training ออกจาก web app ให้ชัด `src/lib/` เป็นที่เก็บ logic ร่วมของ schema, label, baseline, prompt และ evaluator ส่วน `ml/` เก็บของที่ต้องใช้ environment ด้าน fine-tuning

## เส้นทาง implementation

ลำดับงานที่ควรทำ:

1. เพิ่ม output schema และ label taxonomy
2. เขียน synthetic JSONL dataset generator
3. แบ่ง train / validation / test split แบบ deterministic
4. ทำ heuristic baseline ที่รัน local ได้
5. ทำ evaluation runner พร้อม metrics
6. เพิ่ม model adapters สำหรับ OpenAI-compatible API, Ollama / LM Studio และ fine-tuned model
7. ทำ Next.js demo UI สำหรับ paste log, วิเคราะห์ผล และ highlight evidence
8. เพิ่ม Unsloth LoRA / QLoRA training script
9. เขียน report เทียบ baseline กับ fine-tuned model

## การใช้งานระหว่างพัฒนา

ตอนนี้ยังไม่มี project scaffold หรือ command ที่รันได้จริง คำสั่ง setup, generate dataset, evaluate และ train จะเติมหลังทำ milestone ที่เกี่ยวข้องเสร็จแล้ว

เริ่มอ่านจากแผนหลักได้ที่:

```bash
open docs/poc-plan.md
```

เมื่องาน foundation เสร็จ README นี้ควรมีคำสั่งอย่างน้อย:

```bash
npm install
npm run generate:dataset
npm run evaluate
npm run dev
```

ส่วน fine-tuning ควรแยกเป็น path ของตัวเอง เช่น:

```bash
cd ml/unsloth
python train_lora.py --config config.example.yaml
```

## Security และ Privacy

ห้าม commit log production จริง, secret, credential, token, private IP inventory หรือข้อมูลลูกค้า

ถ้าจะใช้ log จริงในอนาคต ต้อง sanitize อย่างน้อย:

- IP address
- hostname
- username
- cookie
- authorization header
- session ID
- customer-specific field

ระบบนี้ควรใช้คำว่า suspicious, likely และ recommended investigation ไม่ควรเขียนว่า “ยืนยันว่าถูก hack แล้ว” เว้นแต่มีหลักฐานจากระบบอื่นประกอบ

## เอกสารที่เกี่ยวข้อง

- `docs/poc-plan.md` - แผน POC, milestone, risks และ definition of done
- `AGENTS.md` - กติกาและขอบเขตสำหรับ coding agents ใน repo นี้

README นี้จะมีประโยชน์ที่สุดเมื่อเดินคู่กับ evaluator เพราะสุดท้ายระบบ triage ที่ดีต้องอธิบายได้ทั้งคำตอบและคะแนนของตัวเอง

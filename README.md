# AI Security Log Triage Assistant

POC สำหรับวิเคราะห์ security log ด้วย small model และ fine-tuning

เป้าหมายคือพิสูจน์ workflow ให้ครบ: สร้าง dataset, ทำ baseline, fine-tune โมเดลขนาดเล็ก, evaluate ด้วย test set เดียวกัน แล้วเทียบผลก่อน-หลัง fine-tune ไม่ใช่ทำระบบ SOC อัตโนมัติหรือฟันธงว่าเครื่องถูกเจาะจาก log เส้นเดียว

## Scope รอบแรก

เริ่มจาก label เล็ก ๆ เพื่อให้วัดผลได้จริง:

- `normal`
- `failed_login_bruteforce`
- `sql_injection_attempt`
- `directory_traversal_attempt`
- `port_scan_or_recon`

ผลลัพธ์ของ analyzer ควรมี field หลัก: `label`, `severity`, `is_suspicious`, `evidence`, `reason`, `recommended_action`

## สถานะ

ตอนนี้ repo อยู่ช่วง foundation:

- มีแผน POC และแผนรายวันใน `docs/`
- มี reference หลักใน `References.md`
- มี local skill สำหรับดูแลเอกสารแบบ mini LLM-Wiki ใน `.codex/skills/llm-docs/`
- มี Next.js scaffold ใน `frontend/`

ยังต้องทำต่อ: dataset generator, baseline, evaluator, model adapters, fine-tuning script และ demo UI จริง

## Run Frontend

```bash
cd frontend
bun install
bun run dev
```

ถ้าไม่ใช้ Bun:

```bash
cd frontend
npm install
npm run dev
```

เปิดที่ `http://localhost:3000`

## Planned Workflow

1. เพิ่ม output schema และ label taxonomy
2. สร้าง synthetic JSONL dataset
3. แบ่ง `train`, `validation`, `test`
4. ทำ heuristic baseline ที่รันได้ local
5. ทำ evaluation runner และ metrics
6. เพิ่ม model adapters
7. fine-tune small model ด้วย Unsloth LoRA/QLoRA
8. ทำ report เทียบ baseline กับ fine-tuned model
9. ทำ demo UI สำหรับ paste log, analyze และ highlight evidence

## Docs

- `docs/poc-plan.md` - แผน POC หลัก
- `docs/Day1.md` ถึง `docs/Day7.md` - แผนรายวันพร้อม Work Log และ Decision Log
- `References.md` - repo และเอกสารอ้างอิง
- `AGENTS.md` - กติกาสำหรับ coding agents
- `.codex/skills/llm-docs/` - skill สำหรับดูแลเอกสารของโปรเจกต์นี้

## Security Note

ห้าม commit production logs, secrets, tokens, credentials หรือข้อมูลลูกค้า

ระบบนี้ควรใช้ภาษาแบบ triage เช่น suspicious, likely pattern และ recommended investigation ไม่ควร claim ว่ายืนยันการถูก hack แล้วถ้าไม่มีหลักฐานจากระบบอื่นประกอบ


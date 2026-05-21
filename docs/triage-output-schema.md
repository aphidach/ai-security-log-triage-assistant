# Triage Output Schema

**Summary**

เอกสารนี้อธิบาย `data/schemas/triage-output.schema.json` ซึ่งเป็นสัญญากลางของผลลัพธ์ security log triage ใน POC นี้ ใช้ร่วมกันทั้ง dataset generator, baseline, model adapter, evaluator และ UI เพื่อให้ทุกส่วนส่งผลลัพธ์รูปแบบเดียวกัน (source: data/schemas/triage-output.schema.json, AGENTS.md)

**Sources**

- `data/schemas/triage-output.schema.json` สำหรับ JSON Schema ตัวจริงที่ใช้ validate output (source: data/schemas/triage-output.schema.json)
- `AGENTS.md` สำหรับ expected output schema, label scope และกติกา schema stability (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ POC goal, dataset format และ evaluation plan (source: docs/poc-plan.md)
- `docs/Day1.md` สำหรับ Day 1 checklist และ schema-first decision (source: docs/Day1.md)

**Last updated**

2026-05-21

## หน้าที่ของ schema นี้

`triage-output.schema.json` ไม่ได้เป็นแค่ตัวอย่าง JSON แต่เป็น contract กลางของระบบ ถ้า baseline, model, dataset หรือ UI คืนผลลัพธ์ไม่ตรง schema นี้ evaluator ต้องจับได้ทันที

ใน POC นี้ schema สำคัญเป็นพิเศษ เพราะเป้าหมายไม่ได้มีแค่ให้โมเดลตอบถูก แต่ต้องตอบในรูปแบบที่เอาไปวัดผลและแสดงใน UI ต่อได้ด้วย (source: AGENTS.md)

## Output Shape

ผลลัพธ์ triage ต้องเป็น object ที่มี field ครบ 6 ตัว:

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

schema ตั้งค่า `additionalProperties: false` ไว้ หมายความว่าถ้ามี field เกินจากนี้ เช่น `confidence`, `attack_type`, `raw_log` หรือ `mitre_id` จะถือว่าไม่ผ่าน schema จนกว่าจะมีการตัดสินใจเพิ่ม field นั้นอย่างเป็นทางการ

## Field Reference

| Field | Type | Required | ความหมาย |
| --- | --- | --- | --- |
| `label` | string enum | yes | label หลักของเหตุการณ์ ใช้บอกว่า log นี้เป็น normal หรือเข้ากับ attack/activity pattern ใด |
| `severity` | string enum | yes | ระดับความเร่งด่วนสำหรับการตรวจสอบต่อ ไม่ใช่การยืนยันว่าเกิด incident แล้ว |
| `is_suspicious` | boolean | yes | บอกว่า log ควรถูกส่งต่อเป็นเหตุการณ์น่าสงสัยหรือไม่ |
| `evidence` | string array | yes | substring หรือข้อเท็จจริงจาก log ที่รองรับ label นั้น |
| `reason` | string | yes | เหตุผลสั้น ๆ ว่าทำไมถึงเลือก label นี้ |
| `recommended_action` | string | yes | action ถัดไปที่ analyst ควรตรวจสอบ |

## Label Enum

รอบแรก schema ยอมรับแค่ 5 label นี้:

```text
normal
failed_login_bruteforce
sql_injection_attempt
directory_traversal_attempt
port_scan_or_recon
```

เหตุผลที่จำกัด label ไว้ก่อน คือ dataset, evaluator และ baseline ต้องนิ่งก่อน ค่อยขยาย taxonomy ทีหลัง ถ้าเพิ่ม label ใหม่ ต้องอัปเดต schema, label list ฝั่ง frontend, dataset generator, evaluator, prompts, docs และ report พร้อมกัน (source: AGENTS.md)

ความหมาย วิธีใช้ และ false-positive caveat ของแต่ละ label อยู่ใน [[label-taxonomy]] เพื่อให้ dataset, baseline, evaluator และ UI ใช้คำจำกัดความเดียวกัน

## Severity Enum

schema ยอมรับ severity 4 ระดับ:

```text
low
medium
high
critical
```

สำหรับ `normal` ให้ใช้ `severity: "low"` และ `is_suspicious: false` ในรอบแรก วิธีนี้ช่วยให้ evaluator ทำงานง่าย เพราะทุก record ยังมี severity ตาม schema เดียวกัน

## Evidence Rules

`evidence` ต้องเป็น array ของ string จำนวน 1-3 รายการ และแต่ละ item ต้องไม่ว่างเปล่าหรือยาวเกิน 160 ตัวอักษร จุดประสงค์คือบังคับให้ output อธิบายได้ว่าตัดสินจากอะไร ไม่ใช่แค่ทาย label หรือวนเติมหลักฐานยาว ๆ จน output ไม่จบ

ตัวอย่าง evidence ที่ดี:

- payload เช่น `"' OR '1'='1"`
- path เช่น `"../../etc/passwd"`
- token จาก tool เช่น `"nmap"`
- pattern จาก log เช่น `"invalid password"` หรือ `"401"`

ถ้าเป็น `normal` และไม่มี substring น่าสงสัย ให้ใส่ evidence ที่อธิบายความปกติได้ เช่น `"GET /health 200"` หรือ substring routine ที่อยู่ใน log แทนการปล่อย array ว่าง

## ใช้ตรงไหนบ้าง

schema นี้ควรถูกใช้เป็นแหล่งอ้างอิงในงานต่อไป:

- dataset generator ต้องเขียน `output` ให้ตรง schema นี้
- heuristic baseline ต้องคืน object รูปแบบเดียวกัน
- model adapter ต้อง parse และ validate model output ก่อนส่งต่อ
- evaluator ต้องนับ `schema_success_rate` และ invalid/missing field จาก schema นี้
- UI ต้อง render field ตาม schema นี้ ไม่เดา field เพิ่มเอง
- fine-tuning dataset ต้องสอนโมเดลให้ตอบ JSON ตาม schema นี้

## Change Rules

ถ้าจะเปลี่ยน schema ห้ามแก้ไฟล์นี้โดด ๆ เพราะจะกระทบหลายส่วนพร้อมกัน

ก่อนเปลี่ยน schema ต้องตรวจอย่างน้อย:

- `data/schemas/triage-output.schema.json`
- `frontend/lib/labels.ts`
- `frontend/lib/triage-schema.ts`
- dataset generator และ split ที่สร้างไว้
- baseline/model adapters
- evaluator metrics และ report format
- UI result view
- docs ที่อธิบาย schema และ POC plan

กติกานี้ช่วยกันไม่ให้ dataset ใช้ field ชุดหนึ่ง แต่ UI หรือ evaluator คาดหวังอีกชุดหนึ่ง

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created triage output schema explanation page | `docs/triage-output-schema.md` | Drafted |
| 2026-05-16 | Codex | Linked schema label enum to the label taxonomy wiki page | `docs/label-taxonomy.md` | Updated |
| 2026-05-21 | Codex | Documented Phase 6.1 evidence count and length constraints | `data/schemas/triage-output.schema.json`, `scripts/model_adapters/openai_compatible.py` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | อธิบาย schema เป็นหน้า wiki แยก | schema เป็น contract ที่หลายส่วนต้องใช้ร่วมกัน | dataset, evaluator, adapters และ UI มี reference เดียวกัน |
| 2026-05-21 | จำกัด `evidence` เป็น 1-3 exact substrings ยาวไม่เกิน 160 ตัวอักษร | Phase 6 พบว่า JSON-constrained generation วนซ้ำใน unbounded `evidence` | schema, prompt, evaluator, local inference, dataset validation และ UI validator ต้อง enforce constraint เดียวกัน |

## Related pages

- [[Day1]]
- [[poc-plan]]
- [[label-taxonomy]]
- [[evaluation-metrics-rationale]]
- [[index]]

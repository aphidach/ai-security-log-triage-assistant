# Label Taxonomy

**Summary**

เอกสารนี้อธิบาย label ชุดแรกของ POC ว่าแต่ละอันหมายถึงอะไร ใช้เมื่อไร และควรระวัง false positive แบบไหน label ชุดนี้เป็นขอบเขตเริ่มต้นของ dataset, baseline, evaluator, model adapter และ UI ยังไม่ใช่ taxonomy เต็มของงาน SOC (source: AGENTS.md, data/schemas/triage-output.schema.json)

**Sources**

- `AGENTS.md` สำหรับ scope ของ label รอบแรกและข้อกำหนดว่า project นี้เป็น security log triage ไม่ใช่การยืนยัน incident (source: AGENTS.md)
- `data/schemas/triage-output.schema.json` สำหรับ enum ของ label ที่ output schema ยอมรับ (source: data/schemas/triage-output.schema.json)
- `docs/poc-plan.md` สำหรับเป้าหมาย POC, dataset plan และข้อจำกัดของ synthetic data รอบแรก (source: docs/poc-plan.md)
- `docs/triage-output-schema.md` สำหรับ output contract ที่ label taxonomy ต้องใช้ร่วมกัน (source: docs/triage-output-schema.md)

**Last updated**

2026-05-16

## ใช้ taxonomy นี้เพื่ออะไร

taxonomy นี้เป็นคำจำกัดความกลางของ 5 label แรกใน POC เวลาสร้าง dataset, เขียน heuristic baseline, ทำ prompt, validate model output หรืออธิบายผลใน UI ให้ยึดความหมายในหน้านี้เป็นหลัก

เป้าหมายคือให้ระบบตอบแบบ triage: log นี้ดูปกติหรือเข้าข่าย pattern ไหน หลักฐานคืออะไร และ analyst ควรตรวจต่ออย่างไร ไม่ใช่ฟันธงว่าเครื่องถูกเจาะแล้วแน่นอน (source: AGENTS.md)

## Label Reference

| Label | ความหมาย | ใช้เมื่อ | หลักฐานที่มักเห็น | ข้อควรระวัง |
| --- | --- | --- | --- | --- |
| `normal` | เหตุการณ์ปกติ หรือไม่พบ pattern น่าสงสัยใน scope รอบแรก | log เป็น request/operation ปกติ เช่น health check, page view, login สำเร็จ หรือ system event ทั่วไป | status ปกติ เช่น `200`, `204`, `success`, `GET /health`, หรือข้อความ routine operation | อย่าใช้ `normal` แค่เพราะ evidence ไม่ชัด ถ้า log มี signal น่าสงสัยแต่ label ไม่พอ ควรเก็บเป็น edge case สำหรับ taxonomy รอบถัดไป |
| `failed_login_bruteforce` | ความพยายาม login ล้มเหลวซ้ำ ๆ ที่อาจเป็น password guessing หรือ brute force | มี failed authentication หลายครั้งจาก IP เดิม, user เดิม, หรือช่วงเวลาสั้น ๆ เดียวกัน หรือ log ระบุชัดว่าเกิด repeated failed login | `failed password`, `authentication failed`, `invalid user`, `401`, `403`, จำนวน attempt สูง, user/IP ซ้ำ | failed login ครั้งเดียวอาจยังไม่ใช่ brute force ต้องดูจำนวนครั้ง ความถี่ และบริบทของ log |
| `sql_injection_attempt` | ความพยายามใส่ payload SQL ผ่าน input, query string, form field หรือ request path | พบ pattern ที่มักใช้โจมตี SQL injection เช่น boolean tautology, UNION query, SQL comment หรือคำสั่ง SQL ที่ไม่ควรอยู่ใน request | `' OR '1'='1`, `UNION SELECT`, `--`, `DROP TABLE`, `sleep(`, `information_schema` | apostrophe หรือคำว่า `select` ที่อยู่ในข้อความปกติไม่พอ ต้องมีบริบทว่าเป็น payload หรือ input ที่ผิดธรรมชาติ |
| `directory_traversal_attempt` | ความพยายามไต่ path เพื่ออ่านไฟล์หรือ directory นอกขอบเขตที่ควรเข้าถึง | request มี path traversal sequence หรืออ้างไฟล์ระบบที่ไม่ควรถูกเรียกผ่าน web/app endpoint | `../`, `..%2f`, `%2e%2e%2f`, `/etc/passwd`, `boot.ini`, `win.ini` | บางระบบมี path ที่มีจุดในชื่อไฟล์ตามปกติ ต้องดูว่าเป็น traversal sequence จริงหรือแค่ชื่อไฟล์ธรรมดา |
| `port_scan_or_recon` | พฤติกรรมสำรวจเป้าหมาย เช่น scan port, probe service, หรือเก็บข้อมูลก่อนโจมตี | มี connection attempt หลาย port/หลาย service, scanner signature, probe endpoint จำนวนมาก หรือ log ระบุว่าเป็น scan/recon | `nmap`, `masscan`, `SYN scan`, หลาย destination port, `connection refused` หลายรายการ, probe path จำนวนมาก | connection fail ครั้งเดียวหรือ request แปลกครั้งเดียวอาจยังไม่พอ ต้องดู pattern ซ้ำหรือสัญญาณว่าเป็นการสำรวจ |

## Severity ตั้งต้น

severity เป็นระดับความเร่งด่วนในการตรวจต่อ ไม่ใช่คำตัดสินว่า incident เกิดขึ้นแล้ว รอบแรกให้ใช้แนวทางนี้เพื่อให้ dataset และ evaluator สม่ำเสมอ:

| Label | Severity ตั้งต้น | เหตุผล |
| --- | --- | --- |
| `normal` | `low` | ไม่ควรถูกยกระดับเป็น suspicious event |
| `failed_login_bruteforce` | `medium` หรือ `high` | ใช้ `medium` เมื่อเห็นความพยายามซ้ำระดับหนึ่ง ใช้ `high` เมื่อจำนวน attempt สูงหรือมีหลายบัญชี/หลาย host |
| `sql_injection_attempt` | `high` | payload แบบ SQL injection มักเป็นสัญญาณโจมตี web/app โดยตรง |
| `directory_traversal_attempt` | `high` | อาจนำไปสู่การอ่านไฟล์ระบบหรือข้อมูล sensitive |
| `port_scan_or_recon` | `medium` หรือ `high` | ใช้ `medium` สำหรับ recon ทั่วไป ใช้ `high` เมื่อ scan กว้าง เร็ว หรือแตะ service สำคัญหลายจุด |

`critical` ควรใช้เมื่อ log มีหลักฐานผลกระทบชัดเจนมาก เช่น payload สำเร็จตาม status/response หรือมีข้อความบอกว่าการเข้าถึง sensitive resource สำเร็จ ไม่ควรใช้เพราะ pattern ดูรุนแรงอย่างเดียว

## Evidence Guidelines

ทุก label ต้องมี `evidence` เป็น string array ที่อ้างอิงจาก log หรือข้อเท็จจริงที่เห็นใน log ได้จริง เพราะ evaluator จะใช้ส่วนนี้วัดว่าโมเดลไม่ได้แค่เดา label (source: docs/triage-output-schema.md)

evidence ที่ดีควรเป็น:

- substring สำคัญจาก log เช่น `"' OR '1'='1"` หรือ `"../../etc/passwd"`
- token ที่ชี้ pattern เช่น `"failed password"` หรือ `"nmap"`
- ข้อเท็จจริงจากกลุ่ม log เช่น `"5 failed logins from 10.0.0.8"`

สำหรับ `normal` ยังควรใส่ evidence ที่อธิบายความปกติ เช่น `"GET /health 200"` หรือ `"successful routine request"` แทนการปล่อยว่าง

## Change Rules

ถ้าจะเพิ่ม label ใหม่ ต้องอัปเดตพร้อมกันอย่างน้อย:

- `data/schemas/triage-output.schema.json`
- `docs/label-taxonomy.md`
- `docs/triage-output-schema.md`
- dataset generator และ split
- heuristic baseline
- evaluator
- frontend label list และ result UI
- evaluation report หรือ data card ที่อ้าง taxonomy

กติกานี้ช่วยกันไม่ให้ dataset ใช้ label ชุดหนึ่ง แต่ schema, UI หรือ evaluator คาดหวังอีกชุดหนึ่ง

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created first-pass label taxonomy definitions | `docs/label-taxonomy.md` | Drafted |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | แยก label taxonomy เป็น wiki page ของตัวเอง | label definition ต้องถูกใช้ซ้ำทั้ง dataset, baseline, evaluator และ UI | มี reference กลางสำหรับความหมายของ label รอบแรก |

## Related pages

- [[triage-output-schema]]
- [[poc-plan]]
- [[Day1]]
- [[evaluation-metrics-rationale]]

# Dataset Source Strategy

**Summary**

เอกสารนี้เก็บแนวทางใช้แหล่งข้อมูลภายนอกสำหรับงาน security log triage ของ POC นี้ โดยสรุปว่าแหล่งไหนเหมาะกับอะไร ควรใช้ช่วงไหน และต้องระวังอะไร ก่อนแปลงเป็น JSONL สำหรับ fine-tuning หรือ evaluation

**Sources**

- `AGENTS.md` สำหรับ label scope, output schema, dataset rule และข้อห้ามเรื่อง production logs (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับแผนใช้ synthetic dataset รอบแรกและการแบ่ง train/validation/test (source: docs/poc-plan.md)
- `docs/References.md` สำหรับ external references ที่ใช้ในโปรเจกต์นี้ (source: docs/References.md)
- Loghub: https://github.com/logpai/loghub
- Splunk BOTS v2: https://github.com/splunk/botsv2
- OTRF/Mordor via MSTICPy docs: https://msticpy.readthedocs.io/en/latest/data_acquisition/MordorData.html
- SigmaHQ: https://sigmahq.io/
- Splunk Security Content Attack Data: https://research.splunk.com/attack_data/
- Kaggle Synthetic Security Logs V1 candidate: https://www.kaggle.com/datasets/beaaaaaan/programmatically-generated-security-logs-v1

**Last updated**

2026-05-16

## Position

แหล่งข้อมูลเหล่านี้มีประโยชน์มาก แต่ไม่ควรเอาเข้ามาเป็นฐานข้อมูลหลักตั้งแต่ Day 1 เพราะ POC ยังต้องพิสูจน์ schema, label taxonomy, generator, baseline และ evaluator ให้รันซ้ำได้ก่อน (source: AGENTS.md, docs/poc-plan.md)

แนวทางที่ควรใช้คือทำ dataset ภายในแบบ deterministic ก่อน แล้วค่อยใช้ external datasets เป็นชั้นเพิ่ม realism ทีละรอบ ไม่ปนข้อมูลหลายที่มาโดยไม่มี data-card และ license note (source: AGENTS.md, docs/poc-plan.md)

## Recommended Order

| Order | Source | Best use | Why now or later | Risk |
| --- | --- | --- | --- | --- |
| 1 | Internal synthetic generator | dataset v0 สำหรับ label ทั้ง 5 ตัว | คุม label, evidence และ schema ได้ดีที่สุดในรอบแรก | อาจง่ายกว่า log จริง ต้องเขียน limitation ชัด |
| 2 | Loghub | raw log format และ normal/background variation | ใช้ดูหน้าตา log จริงจากหลายระบบ เช่น OpenSSH, Apache, Linux, Windows | หลายชุดไม่ได้มี label ตรงกับ POC และบาง log อาจไม่ได้ sanitize |
| 3 | OTRF/Mordor | adversary-emulation evaluation | มี attack scenario และ mapping ไป MITRE ATT&CK เหมาะกับ eval รอบที่ต้องสมจริงขึ้น | ต้อง map MITRE technique กลับมาเป็น label 5 ตัวของเรา |
| 4 | SigmaHQ | rule/evidence reference | ไม่ใช่ dataset แต่ช่วยออกแบบ heuristic baseline, evidence extraction และ false-positive notes | rule format ไม่เท่ากับ training record โดยตรง |
| 5 | Splunk BOTS | SOC scenario และ multi-source investigation | เหมาะกับ demo/evaluation ที่ต้องมีบริบทหลาย sourcetype | ข้อมูลใหญ่ เป็น Splunk pre-indexed format และต้องใช้ tooling เพิ่ม |
| 6 | Splunk Attack Data | technique-aligned future cases | มีรายการ attack data ผูกกับ MITRE technique เหมาะกับรอบขยาย taxonomy | ยังต้องตรวจ format, license และ mapping ก่อนใช้ |
| 7 | Kaggle Synthetic Security Logs V1 | optional supplemental synthetic eval | อาจใช้ดู multi-vendor synthetic scenario หรือ correlation task | ต้อง verify license, schema, download path และความตรงกับ label ของเรา |

## How To Use Them Later

เมื่อ generator/evaluator พร้อมแล้ว ค่อยเพิ่ม external source ด้วย pipeline แบบนี้:

1. ทำ source inventory: บันทึก link, license, file format, log source, จำนวน record, label ที่มี และข้อจำกัด
2. เลือกเฉพาะส่วนที่ map เข้ากับ label รอบแรกได้ เช่น failed login, SQL injection, path traversal หรือ scan/recon
3. normalize log เป็น `input` string เดียวก่อน เพื่อให้เข้ากับ schema รอบแรก
4. map label เป็นหนึ่งใน `normal`, `failed_login_bruteforce`, `sql_injection_attempt`, `directory_traversal_attempt`, `port_scan_or_recon`
5. extract `evidence` เป็น substring ที่อยู่ใน log จริง ไม่ fabricate หลักฐานเพิ่ม
6. เขียน record เป็น JSONL ตาม output schema กลาง
7. แยก train/validation/test โดยไม่ให้ scenario เดียวกันรั่วข้าม split
8. เขียนหรืออัปเดต `docs/data-card.md` ทุกครั้งที่เพิ่มแหล่งข้อมูลใหม่

## Practical Mapping Notes

Loghub เหมาะกับการเพิ่ม noise และ format variation มากกว่าการเป็น labeled attack dataset โดยตรง ถ้าใช้ OpenSSH/Apache/Linux logs ควรเริ่มจาก normal/background หรือ rule-labeled examples เท่านั้น

OTRF/Mordor เหมาะกับ evaluation รอบหลัง เพราะมีบริบท attack simulation และ MITRE mapping แต่ต้องระวังว่า MITRE technique หนึ่งไม่ได้ map เป็น label ของเราแบบหนึ่งต่อหนึ่งเสมอ เช่น credential access บางอย่างไม่เท่ากับ `failed_login_bruteforce`

Splunk BOTS และ Splunk Attack Data เหมาะกับ scenario ที่อยากให้ model แนะนำ investigation action ได้ดีขึ้น แต่ยังไม่เหมาะเป็น Day 2 dependency เพราะจะทำให้ POC หนักเกินก่อน evaluator พร้อม

SigmaHQ ควรใช้เป็น design reference สำหรับ heuristic baseline และ evidence logic ไม่ใช่เอามาแทน dataset เพราะ Sigma rule บอกเงื่อนไข detection แต่ไม่ได้ให้ training examples ครบตาม schema ของเรา

Kaggle synthetic datasets ใช้เป็นแหล่งเปรียบเทียบหรือ inspiration ได้ แต่ต้องแยกจาก fixed test split หลัก ไม่อย่างนั้นอาจทำให้ metric ดูดีจาก template ที่สะอาดเกินจริง

## Current Decision

ตอนนี้ยังไม่ import external dataset เข้า repo ให้เริ่มจาก internal synthetic dataset 500 records ตาม [[Day2]] ก่อน แล้วเก็บแหล่งภายนอกเหล่านี้เป็น backlog สำหรับปรับความสมจริงหลัง evaluator และ data-card พร้อมแล้ว (source: docs/poc-plan.md)

## Open Questions

- ต้องทำ license checklist สำหรับแต่ละ source ก่อนนำข้อมูลจริงเข้า `data/raw/`
- ต้องกำหนด mapping matrix ระหว่าง MITRE ATT&CK, Sigma rule family และ label 5 ตัวของ POC
- ต้องตัดสินใจว่า external dataset จะใช้เพื่อ training, validation หรือ evaluation เท่านั้น
- ต้องมี policy ว่าข้อมูลที่ยังไม่ sanitize จะอยู่ใน git ได้หรือไม่ คำตอบเริ่มต้นคือไม่ควรอยู่ใน git (source: AGENTS.md)

## Work Log

Append-only log สำหรับบันทึกการเปลี่ยนแปลงในหน้านี้

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created dataset source strategy page from dataset-source discussion | `docs/dataset-source-strategy.md` | Drafted |

## Decision Log

Append-only log สำหรับบันทึก decision หรือ tradeoff ที่เกี่ยวกับแหล่งข้อมูล

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | เก็บ external datasets เป็น backlog ก่อน | POC ต้องพิสูจน์ schema, generator, baseline และ evaluator ก่อนเพิ่ม dataset จริงที่มี license/format/labeling complexity | Day 2 ยังเริ่มจาก internal synthetic dataset 500 records |

## Related pages

- [[poc-plan]]
- [[Day2]]
- [[evaluation-metrics-rationale]]
- [[References]]

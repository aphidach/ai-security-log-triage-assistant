# Log Type Examples

**Summary**

หน้านี้อธิบาย log format ที่ synthetic dataset รอบแรกจำลองไว้ เช่น web access log, SSH auth log, application auth log, WAF log, Windows failed logon, firewall log, IDS log และ netflow-style log แบบสั้น จุดประสงค์คือให้คนอ่าน dataset รู้ว่า log แต่ละแบบมาจากระบบชนิดไหน และ evidence แบบใดที่ model หรือ baseline ควรมองหา (source: scripts/generate_dataset.py, docs/data-card.md)

**Sources**

- `scripts/generate_dataset.py` สำหรับ template ที่ generator ใช้สร้าง log แต่ละชนิด (source: scripts/generate_dataset.py)
- `docs/data-card.md` สำหรับภาพรวม dataset และข้อจำกัดของ synthetic log รอบแรก (source: docs/data-card.md)
- `docs/dataset-input-output-format.md` สำหรับ record contract และ input/output rules (source: docs/dataset-input-output-format.md)
- `AGENTS.md` สำหรับ scope ของ POC และ security/privacy guardrails (source: AGENTS.md)

**Last updated**

2026-05-17

## Overview

dataset รอบแรกไม่ได้ใช้ log format เดียว เพราะถ้า model เห็นแต่ Apache-style log หรือ SSH log อย่างเดียว อาจจำรูปประโยคมากกว่าจำ pattern ที่ควร triage จริง ๆ Generator จึงผสม log หลายหน้าตา แต่ยังคุมให้อยู่ใน 5 labels แรกของ POC (source: scripts/generate_dataset.py)

## Log Types

| Log type | คืออะไร | ตัวอย่าง |
| --- | --- | --- |
| **web access log** | log จาก web server เช่น Apache หรือ Nginx บอกว่า client request path ไหน ใช้ method อะไร และได้ HTTP status อะไร | `203.0.113.10 - - [17/May/2026:10:21:03 +0700] "GET /login HTTP/1.1" 200` |
| **SSH auth log** | log การ login ผ่าน SSH เช่น password ผิด, login สำเร็จ หรือพยายามเข้า user สำคัญ | `May 17 10:22:11 auth-01 sshd[2190]: Failed password for admin from 198.51.100.23 port 50122 ssh2` |
| **application auth log** | log authentication ที่ application เขียนเอง เช่นเว็บหรือ API บันทึก event login failed, login success, account blocked | `2026-05-17T10:23:01+07:00 app=auth event=login_failed user=admin src_ip=203.0.113.44 failures=12` |
| **WAF log** | log จาก Web Application Firewall ที่อยู่หน้าเว็บและตรวจ request น่าสงสัย เช่น SQL injection, directory traversal หรือ brute force | `waf: blocked request src=198.51.100.22 uri="/files/../../etc/passwd" rule=path_traversal status=403` |
| **Windows failed logon** | log login ล้มเหลวจาก Windows Event Log มักใช้ `event_id=4625` เพื่อบอก failed logon | `2026-05-17T10:24:10+07:00 winlog event_id=4625 host=web-01 target_user=administrator src_ip=203.0.113.55 count=8 status=failed_logon` |
| **firewall log** | log จาก firewall ที่บอกว่า traffic จาก IP ไหนไป IP/port ไหน และถูก allow หรือ block | `2026-05-17T10:25:00+07:00 firewall: SYN scan detected src=203.0.113.44 dst=198.51.100.10 ports=22,80,443 action=blocked` |
| **IDS log** | log จาก Intrusion Detection System เช่นระบบที่จับ signature หรือ behavior น่าสงสัยใน network | `2026-05-17T10:26:44+07:00 ids: nmap fingerprint from 203.0.113.88 to 198.51.100.20; probed_ports=22,80,443` |
| **netflow-style log** | log สรุป network flow แบบสั้น ไม่เก็บ payload แต่บอก source, destination, port, จำนวน port และช่วงเวลา | `2026-05-17T10:27:30+07:00 netflow: sequential connection attempts src=203.0.113.20 dst=198.51.100.10 dst_ports=22,80,443 unique_ports=3 window=45s` |

## How To Read Them

จำง่าย ๆ:

- **web access log** และ **WAF log** อยู่ฝั่งเว็บ ใช้ดู path, query, payload, HTTP status และ rule ที่ match
- **SSH auth log**, **application auth log** และ **Windows failed logon** อยู่ฝั่ง login ใช้ดู failed/success, user, source IP, count และ repeated attempts
- **firewall log**, **IDS log** และ **netflow-style log** อยู่ฝั่ง network ใช้ดู port, scan signature, connection pattern และช่วงเวลา

## Evidence Hints

สิ่งที่ควรมองหาใน log แต่ละกลุ่ม:

| Pattern | Evidence ตัวอย่าง |
| --- | --- |
| `failed_login_bruteforce` | `Failed password`, `failures=18`, `count=20`, `status=401 repeated=20` |
| `sql_injection_attempt` | `' OR '1'='1`, `UNION SELECT`, `SLEEP(5)`, `information_schema` |
| `directory_traversal_attempt` | `../../etc/passwd`, `..%2f..%2f`, `windows\win.ini`, `rule=path_traversal` |
| `port_scan_or_recon` | `SYN scan detected`, `nmap fingerprint`, `probed_ports=22,80,443`, `unique_ports=4` |
| `normal` | `GET /health`, `Successful login`, `failed_attempts=1`, `session_count=1` |

## Notes

log ใน dataset นี้เป็น synthetic จึงตั้งใจให้มี evidence ชัดกว่า production log จริง ข้อดีคือใช้วัด workflow ได้ง่าย ข้อจำกัดคือยังไม่สะท้อน noise, parser artifact, missing fields หรือ context เฉพาะ environment จริง ต้องเพิ่มความหลากหลายหลัง baseline และ evaluator เริ่มทำงานแล้ว (source: docs/data-card.md)

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-17 | Codex | Created log type examples page for the synthetic dataset wiki | `scripts/generate_dataset.py`, `docs/data-card.md` | Drafted |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-17 | แยกคำอธิบาย log type เป็นหน้าเฉพาะ | data-card ควรเก็บภาพรวม dataset ส่วน log format examples ควรเปิดอ่านแยกได้ | เพิ่ม `docs/log-type-examples.md` และ link กลับจากหน้า dataset ที่เกี่ยวข้อง |

## Related pages

- [[data-card]]
- [[dataset-input-output-format]]
- [[label-taxonomy]]
- [[triage-output-schema]]
- [[Day2]]

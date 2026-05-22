# Phase 6 V3.4 Boundary Repair Plan

**Summary**

หน้าเอกสารนี้เป็นแผนงาน v3.4 หลัง v3.3 temp 0.3 hard-contrast runtime probe ขยับ label accuracy จาก `0.60` เป็น `0.64` แต่ยังไม่ผ่าน canary gate เพราะ `sql_injection_attempt` ยังถูกแค่ `2/10`, `port_scan_or_recon` ยัง `6/10` และ prediction ยังถูกดูดไป `failed_login_bruteforce` มากเกินไป งาน v3.4 จึงควรเป็น boundary repair ที่เน้น SQLi, port scan และ brute-force gravity โดยยังไม่ใช้ fixed `data/splits/test.jsonl` (source: docs/output-structure-fix/phase-6-v3-3-targeted-canary.md, reports/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json)

**Sources**

- `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md` สำหรับผล v3.3 canonical/temp 0.3, confusion matrix และ decision ให้ hold fixed test split (source: docs/output-structure-fix/phase-6-v3-3-targeted-canary.md)
- `reports/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json` สำหรับ per-sample failure slice, predicted distribution และ runtime metadata ของ temp 0.3 probe (source: reports/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json)
- `reports/phase-6-v3-3-temp-03-hard-contrast-memorization-probe-infographic.html` สำหรับ stakeholder-readable summary ของ v3.3 temp 0.3 probe (source: reports/phase-6-v3-3-temp-03-hard-contrast-memorization-probe-infographic.html)
- `reports/phase-6-v3-4-boundary-failure-slice.json` และ `.md` สำหรับ failure bucket, diagnosis และ dataset implication ก่อนสร้าง v3.4 supplement (source: reports/phase-6-v3-4-boundary-failure-slice.json, source: reports/phase-6-v3-4-boundary-failure-slice.md)
- `scripts/create_v3_4_boundary_repair_dataset.py` สำหรับ deterministic v3.4 supplement และ train/validation split generator (source: scripts/create_v3_4_boundary_repair_dataset.py)
- `data/generated/v3-4-boundary-repair-security-triage.jsonl`, `data/splits/train-v3-4-boundary-repair.jsonl` และ `data/splits/validation-v3-4-boundary-repair.jsonl` สำหรับ v3.4 generated artifacts (source: data/generated/v3-4-boundary-repair-security-triage.jsonl, source: data/splits/train-v3-4-boundary-repair.jsonl, source: data/splits/validation-v3-4-boundary-repair.jsonl)
- `ml/unsloth/config.v3-4.yaml` สำหรับ v3.4 training config และ output directory (source: ml/unsloth/config.v3-4.yaml)
- `docs/label-imbalance-and-prediction-collapse.md` สำหรับ rationale เรื่อง prediction collapse และ hard contrast mitigation (source: docs/label-imbalance-and-prediction-collapse.md)
- `docs/openai-adapter-runtime-config.md` สำหรับวิธีแยก canonical eval ออกจาก runtime probe ด้วย `config-adapter.yml` (source: docs/openai-adapter-runtime-config.md)

**Last updated**

2026-05-22

## Status

Dataset and config prepared. v3.4 ยังไม่ใช่ training result และยังไม่ใช่ Phase 7 candidate

งานถัดไปคือ train adapter ด้วย `ml/unsloth/config.v3-4.yaml` แล้ว serve เป็น alias ใหม่ เช่น `lfm2-security-triage-v3-4` ก่อน probe บน hard-contrast/mini-boundary split เท่านั้น ยังไม่ใช้ `data/splits/test.jsonl`

## Problem Statement

v3.3 temp 0.3 ทำให้ output contract นิ่งและช่วย label accuracy เล็กน้อย แต่ปัญหาหลักยังเป็น semantic boundary:

| Expected label | Correct | Main wrong predictions | Read |
| --- | ---: | --- | --- |
| `normal` | `8/10` | `failed_login_bruteforce=2` | single failed login / Windows 4625 ยังถูกอ่านเป็น brute force |
| `failed_login_bruteforce` | `10/10` | none | label นี้แข็งแรงเกิน label อื่น และดึง false positives เข้ามา |
| `sql_injection_attempt` | `2/10` | `failed_login_bruteforce=4`, `directory_traversal_attempt=2`, `normal=1`, `port_scan_or_recon=1` | SQLi signal ยังไม่เด่นพอเมื่ออยู่ใน login/API/search context |
| `directory_traversal_attempt` | `6/10` | กระจายไปทุก label อย่างละบางเคส | ดีขึ้นจาก canonical แต่ยังไม่นิ่ง |
| `port_scan_or_recon` | `6/10` | `failed_login_bruteforce=3`, `normal=1` | port/recon signal ยังถูกอ่านเป็น brute force หรือ benign monitoring |

predicted distribution รอบ temp 0.3 ยังเอนแรงไปที่ `failed_login_bruteforce=20/50` ทั้งที่ expected distribution เป็น label ละ 10 records (source: reports/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json)

## Failure Slice To Build First

ก่อนสร้าง dataset ให้ทำ slice จาก report v3.3 temp 0.3 แล้วเขียนเป็น report สั้น ๆ เพื่อไม่ให้ v3.4 กลายเป็นการเพิ่มตัวอย่างแบบเดาสุ่ม

Planned artifact:

```text
reports/phase-6-v3-4-boundary-failure-slice.md
reports/phase-6-v3-4-boundary-failure-slice.json
```

Completed artifact:

```text
scripts/create_v3_4_failure_slice.py
reports/phase-6-v3-4-boundary-failure-slice.json
reports/phase-6-v3-4-boundary-failure-slice.md
```

ผล slice ล่าสุดมี label failures `18/50` แยกเป็น 7 buckets: normal -> brute force `2`, SQLi -> brute force `4`, SQLi -> traversal `2`, SQLi -> normal/port `2`, traversal boundary drift `4`, port/recon -> brute force `3`, และ port/recon -> normal `1` โดยยังยืนยันว่า fixed test split ไม่ถูกใช้ (source: reports/phase-6-v3-4-boundary-failure-slice.json)

Failure buckets ที่ต้องแยก:

| Bucket | Current examples | What to inspect |
| --- | --- | --- |
| SQLi -> brute force | `v3-hard-000021`, `v3-hard-000023`, `v3-hard-000024`, `v3-hard-000029` | login/API context ทำให้ model สนใจ failed/auth/status มากกว่า SQL payload หรือไม่ |
| SQLi -> traversal | `v3-hard-000026`, `v3-hard-000028` | quote/comment marker ถูกอ่านเป็น path/file-ish signal หรือไม่ |
| SQLi -> normal/port | `v3-hard-000025`, `v3-hard-000030` | SQL vocabulary หรือ `OR` token เดี่ยวไม่พอทำให้ model เห็น attack boundary |
| Port -> brute force | `v3-hard-000042`, `v3-hard-000046`, `v3-hard-000049` | `nmap fingerprint`, `service enumeration`, `unique_ports` ยังไม่ชนะ generic suspicious/brute pattern |
| Port -> normal | `v3-hard-000044` | horizontal scan/unique hosts ต้องมี contrast กับ inventory/monitoring benign cases |
| Normal -> brute force | `v3-hard-000001`, `v3-hard-000003` | single failed login และ single Windows 4625 ต้องถูกสอนให้เป็น normal หรือ low-signal event |

## V3.4 Dataset Recipe

v3.4 ควรเป็น targeted boundary supplement ไม่ใช่เพิ่มทุก label เท่า ๆ กัน เป้าหมายคือสอนว่า signal แบบไหน “พอ” และแบบไหน “ยังไม่พอ” สำหรับแต่ละ boundary

Planned artifacts:

```text
scripts/create_v3_4_boundary_repair_dataset.py
data/generated/v3-4-boundary-repair-security-triage.jsonl
data/generated/train-plus-v3-4-boundary-repair.jsonl
data/splits/train-v3-4-boundary-repair.jsonl
data/splits/validation-v3-4-boundary-repair.jsonl
ml/unsloth/config.v3-4.yaml
```

Completed artifacts:

```text
scripts/create_v3_4_boundary_repair_dataset.py
data/generated/v3-4-boundary-repair-security-triage.jsonl
data/generated/train-plus-v3-4-boundary-repair.jsonl
data/splits/train-v3-4-boundary-repair.jsonl
data/splits/validation-v3-4-boundary-repair.jsonl
ml/unsloth/config.v3-4.yaml
tests/test_v3_4_boundary_repair_workflow.py
```

v3.4 supplement มี 160 records: `normal=60`, `failed_login_bruteforce=20`, `sql_injection_attempt=40`, `directory_traversal_attempt=0`, `port_scan_or_recon=40` ส่วน train split รวมมี 710 records: `normal=170`, `failed_login_bruteforce=120`, `sql_injection_attempt=160`, `directory_traversal_attempt=100`, `port_scan_or_recon=160`; validation ยังเป็น canonical balanced 75 records หรือ label ละ 15 และ fixed test split ยังไม่ถูกใช้ (source: scripts/create_v3_4_boundary_repair_dataset.py, source: data/splits/train-v3-4-boundary-repair.jsonl)

Recommended supplement size: 120-160 records before weighting. รอบนี้ใช้ 160 records เพื่อให้ครบทุก bucket ตาม failure slice โดยยังไม่ duplicate-weight เพิ่มนอกเหนือจาก records ที่สร้างโดยตรง

| Bucket | Target count | Purpose |
| --- | ---: | --- |
| SQLi positives | 35-45 | ย้ำ payload ชัด: quote + tautology, `UNION SELECT`, `SLEEP(`, `information_schema`, SQL comment `--`, encoded SQLi, stacked query |
| SQLi hard negatives | 20-30 | มีคำ `select`, `union`, `sleep`, `information_schema` ใน docs/search/DB-admin context แต่ไม่มี attack payload |
| Port/recon positives | 35-45 | ย้ำ `unique_ports>=10`, `nmap fingerprint`, `SYN scan detected`, horizontal scan, service enumeration, many hosts/ports |
| Port/recon hard negatives | 20-30 | authorized inventory, health check, one-port monitoring, known scanner with allowlist และไม่มี recon threshold |
| Brute-force anti-gravity negatives | 20-30 | มีคำ `failed`, `blocked`, `attempt`, `403`, `401`, `4625` แต่ไม่ใช่ repeated login burst |
| Paired examples | 20+ pairs | คู่ log คล้ายกันมากแต่ label ต่างกัน เช่น `failed_attempts=1` vs `failed_attempts=12`, `unique_ports=1` vs `unique_ports=24` |

ถ้าใช้ hard-contrast 50 records เดิมเป็น memorization canary ต่อได้ ให้เพิ่ม v3.4 supplement เป็น near-duplicate/neighboring variants มากกว่า copy exact line ทั้งหมด เพื่อให้เห็นว่า model ขยับ boundary จริง ไม่ใช่จำบรรทัดเดิมอย่างเดียว

## Label Boundary Rules To Encode

### SQLi

ให้ label เป็น `sql_injection_attempt` เมื่อ log มี payload หรือ query structure ที่บ่งชี้ injection โดยตรง เช่น:

- quote + tautology: `' OR '1'='1`, `" OR "1"="1`
- stacked/comment payload: `;DROP TABLE audit_log--`, `admin'--`
- time-based payload: `SLEEP(5)`, `WAITFOR DELAY`
- schema discovery: `information_schema.tables` เมื่ออยู่ใน request parameter ที่น่าสงสัย
- encoded variants: `%27%20OR%20%271%27%3D%271`, `%22%20OR%20%221%22%3D%221`

อย่าให้คำเดี่ยวอย่าง `select`, `union`, `sleep`, `schema` ใน benign search/docs context กลายเป็น SQLi ถ้าไม่มี payload boundary

### Port Scan Or Recon

ให้ label เป็น `port_scan_or_recon` เมื่อ log มี scan/recon pattern ที่ชัด เช่น:

- `unique_ports` สูง เช่น `unique_ports=12`, `unique_ports=24`
- `nmap fingerprint`, `SYN scan detected`, `service enumeration`
- horizontal scan หลาย host เช่น `unique_hosts=18`
- probing หลาย service ในช่วงเวลาสั้น

อย่าให้ single connection, allowlisted inventory, health check หรือ one-port monitoring กลายเป็น recon

### Failed Login Brute Force

ให้ label เป็น `failed_login_bruteforce` เมื่อมี repeated failures หรือ burst pattern เท่านั้น เช่น:

- `failed_attempts>=10`
- `repeated 15 times`
- many usernames from same source
- auth failure burst in short window

single failed login, isolated `4625`, หรือ request ที่ `status=401/403` เพราะ SQLi/WAF block ไม่ควรถูกดูดเข้า brute force

## Training Plan

1. Create v3.4 boundary supplement from deterministic generator
2. Keep validation at canonical balanced 75 records unless there is a separate v3.4 boundary validation split
3. Keep fixed `data/splits/test.jsonl` untouched and unread
4. Train from base model or selected adapter according to the current LoRA workflow decision, but keep output dir versioned as v3.4
5. Serve as a new alias, for example `lfm2-security-triage-v3-4`
6. Run hard-contrast memorization probe with canonical `temperature=0`
7. Run temp/runtime probe only after canonical result is recorded
8. If hard-contrast passes, run mini semantic eval
9. Use fixed test split only after hard-contrast and mini semantic eval both pass

## Evaluation Commands

Canonical hard-contrast probe:

```bash
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v3-4 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v3-4-hard-contrast-memorization-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v3-4-hard-contrast-memorization-probe.md
```

Runtime probe with adapter config:

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v3-4-temp-03-hard-contrast-memorization-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v3-4-temp-03-hard-contrast-memorization-probe.md
```

Mini semantic eval only after canary improves:

```bash
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v3-4 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/mini-semantic-eval.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v3-4-mini-semantic-eval.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v3-4-mini-semantic-eval.md
```

## Exit Criteria

v3.4 ถึงจะขยับต่อได้เมื่อผ่านเงื่อนไขขั้นต่ำเหล่านี้:

| Gate | Required result |
| --- | --- |
| JSON parse success | `1.0` |
| Schema success | `1.0` |
| Invalid output count | `0` |
| Hard-contrast label accuracy | `>= 0.80` |
| SQLi canary accuracy | `>= 7/10` |
| Port-scan canary accuracy | `>= 8/10` |
| Normal hard-negative accuracy | `>= 8/10` |
| Predicted brute-force count on 50-record canary | ideally `<= 14/50` |
| Mini semantic eval label accuracy | materially above v3.1/v3.3, target `>= 0.60` before fixed split |

ถ้า v3.4 ยังต่ำกว่า gate ให้ทำ error taxonomy อีกรอบก่อนเพิ่ม training data รอบใหม่ อย่าข้ามไป fixed split เพื่อเลือก hard cases

## Hold Fixed Test

`data/splits/test.jsonl` ยังต้อง hold ต่อไป เพราะ v3.4 เป็น tuning phase

- ห้ามใช้ fixed test เพื่อเลือก v3.4 examples
- ห้ามดู fixed test confusion matrix เพื่อแก้ prompt/training
- ห้ามนำ fixed test failures กลับเข้า train
- fixed split ใช้เฉพาะ Phase 7 comparison หลังผ่าน canary + mini semantic eval แล้ว

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Created v3.4 boundary repair plan after v3.3 temp 0.3 canary remained below gate | `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md`, `reports/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json` | Planned |
| 2026-05-22 | Codex | Created v3.4 boundary failure slice from the v3.3 temp 0.3 hard-contrast report | `scripts/create_v3_4_failure_slice.py`, `reports/phase-6-v3-4-boundary-failure-slice.json`, `reports/phase-6-v3-4-boundary-failure-slice.md` | Done |
| 2026-05-22 | Codex | Created v3.4 boundary repair supplement, train/validation splits, config, and regression test | `scripts/create_v3_4_boundary_repair_dataset.py`, `data/generated/v3-4-boundary-repair-security-triage.jsonl`, `data/splits/train-v3-4-boundary-repair.jsonl`, `ml/unsloth/config.v3-4.yaml`, `tests/test_v3_4_boundary_repair_workflow.py` | Prepared |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Make v3.4 a boundary repair run, not a fixed split comparison | v3.3 temp 0.3 improved label accuracy only to `0.64`, while SQLi remained `2/10` and brute-force overprediction remained visible | Next work focuses on SQLi/port-scan boundaries and brute-force anti-gravity examples |
| 2026-05-21 | Keep canonical eval and runtime probe separate | temp 0.3 helped label accuracy but reduced severity/evidence and increased latency | v3.4 should record `temperature=0` first, then run `config-adapter.yml` runtime probe as a separate report |
| 2026-05-21 | Continue holding fixed `data/splits/test.jsonl` | Current changes are still tuning decisions driven by hard-contrast and mini semantic diagnostics | Phase 7 fixed split comparison remains blocked until canary and mini semantic eval pass |

## Related pages

- [[output-structure-fix/phase-6-v3-3-targeted-canary]]
- [[output-structure-fix/phase-6-v3-hard-contrast-dataset]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[label-imbalance-and-prediction-collapse]]
- [[openai-adapter-runtime-config]]
- [[fine-tuning-notes]]

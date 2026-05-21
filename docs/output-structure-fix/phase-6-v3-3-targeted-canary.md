# Phase 6 V3.3 Targeted Canary Preparation

**Summary**

หน้าเอกสารนี้บันทึก preparation สำหรับ v3.3 หลัง v3.2 hard-contrast memorization probe ดีขึ้นแต่ยังพลาดหนักใน `sql_injection_attempt` และ `port_scan_or_recon` รอบนี้จึงเพิ่ม training-only targeted layer ที่ weight SQLi และ port-scan positives โดยตรง พร้อม normal pairs ที่มีคำคล้ายกัน แต่ยังใช้ original hard-contrast 50 records เป็น canary probe และยังไม่ใช้ fixed `data/splits/test.jsonl` (source: docs/output-structure-fix/phase-6-v3-2-hard-contrast-probe.md, scripts/create_v3_3_training_split.py)

**Sources**

- `docs/output-structure-fix/phase-6-v3-2-hard-contrast-probe.md` สำหรับ v3.2 failure profile และ decision ให้ทำ v3.3 targeted canary (source: docs/output-structure-fix/phase-6-v3-2-hard-contrast-probe.md)
- `scripts/create_v3_3_training_split.py` สำหรับ v3.3 targeted supplement และ weighted split generator (source: scripts/create_v3_3_training_split.py)
- `data/generated/v3-3-targeted-hard-contrast-security-triage.jsonl` สำหรับ 30 new targeted examples (source: data/generated/v3-3-targeted-hard-contrast-security-triage.jsonl)
- `data/splits/train-v3-3-targeted-hard-contrast.jsonl` และ `data/splits/validation-v3-3-targeted-hard-contrast.jsonl` สำหรับ v3.3 train/validation split (source: data/splits/train-v3-3-targeted-hard-contrast.jsonl, data/splits/validation-v3-3-targeted-hard-contrast.jsonl)
- `ml/unsloth/config.v3-3.yaml` และ `ml/unsloth/config.example.yaml` สำหรับ v3.3 training config paths and output directory (source: ml/unsloth/config.v3-3.yaml, ml/unsloth/config.example.yaml)
- `ml/unsloth/train_lora.py` สำหรับ split guard ที่อนุญาต v3.3 train/validation และยัง block fixed test split ระหว่าง training (source: ml/unsloth/train_lora.py)

**Last updated**

2026-05-21

## Status

Prepared locally. v3.3 ยังไม่ใช่ evaluation result และยังไม่ใช่ Phase 7 candidate จนกว่าจะ train adapter แล้วผ่าน hard-contrast canary ดีพอ

## Generated Artifacts

```text
scripts/create_v3_3_training_split.py
data/generated/v3-3-targeted-hard-contrast-security-triage.jsonl
data/generated/train-plus-v3-3-targeted-hard-contrast.jsonl
data/splits/train-v3-3-targeted-hard-contrast.jsonl
data/splits/validation-v3-3-targeted-hard-contrast.jsonl
ml/unsloth/config.v3-3.yaml
```

รันซ้ำ:

```bash
rtk .venv/bin/python scripts/create_v3_3_training_split.py
rtk .venv/bin/python ml/unsloth/train_lora.py --preflight-only --config ml/unsloth/config.v3-3.yaml
```

## Data Mixture

v3.3 เริ่มจาก v3.1 balanced train 500 records แล้วเพิ่ม targeted weighted layer อีก 50 records

| Label | V3.1 base train | V3.3 added weight | V3.3 train total |
| --- | ---: | ---: | ---: |
| `normal` | 100 | 10 | 110 |
| `failed_login_bruteforce` | 100 | 0 | 100 |
| `sql_injection_attempt` | 100 | 20 | 120 |
| `directory_traversal_attempt` | 100 | 0 | 100 |
| `port_scan_or_recon` | 100 | 20 | 120 |

validation ยังเป็น canonical validation 75 records หรือ label ละ 15 เพื่อไม่ให้ targeted training mixture ปนกับ validation signal (source: scripts/create_v3_3_training_split.py)

## Targeted Examples

v3.3 เพิ่ม examples ใหม่ 30 records ก่อน weighting:

| Bucket | Count | Purpose |
| --- | ---: | --- |
| SQLi-like normal pairs | 6 | มีคำอย่าง quote, tautology, Union Select, sleep และ `information_schema` ในบริบท benign docs/search |
| Port-like normal pairs | 4 | มีคำอย่าง `unique_ports`, service enumeration และ fingerprint ในบริบท monitoring/inventory ที่ไม่ใช่ recon |
| `sql_injection_attempt` positives | 10 | ย้ำ quote, tautology, `UNION SELECT`, `SLEEP(`, `information_schema`, encoded payload และ SQL comment markers |
| `port_scan_or_recon` positives | 10 | ย้ำ `unique_ports`, `nmap fingerprint`, `SYN scan detected`, horizontal scan และ service enumeration |

weighted layer ใช้ normal pairs อย่างละ 1 copy แต่ SQLi และ port-scan positives อย่างละ 2 copies เพื่อแก้ under-prediction ที่เห็นใน v3.2 โดยไม่เพิ่ม brute force หรือ traversal เพิ่ม (source: scripts/create_v3_3_training_split.py)

## Run Order

ลำดับที่ต้องทำหลังเตรียม split:

1. Train adapter ด้วย `ml/unsloth/config.v3-3.yaml`
2. Serve model ด้วยชื่อแยก เช่น `lfm2-security-triage-v3-3`
3. Rerun hard-contrast memorization probe บน `data/generated/v3-hard-contrast-security-triage.jsonl`
4. ใช้ report path ใหม่ เช่น `reports/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-memorization-probe.json`
5. ถ้า hard-contrast canary ขยับใกล้ `0.80+` ค่อยรัน mini semantic eval
6. ใช้ `data/splits/test.jsonl` เฉพาะตอนเข้า Phase 7 fixed split comparison เท่านั้น

## Hold Fixed Test

v3.3 ยังเป็น tuning/canary phase ไม่ใช่ fixed comparison phase

- ห้ามใช้ `data/splits/test.jsonl` เพื่อเลือก hard cases
- ห้ามรัน fixed split เพื่อตัดสินใจว่าจะเพิ่มตัวอย่าง SQLi หรือ port scan อีกไหม
- hard-contrast canary ใช้ `data/generated/v3-hard-contrast-security-triage.jsonl` เพราะเป็น training supplement diagnostic ที่ตั้งใจวัด memorization/label boundary
- mini semantic eval ยังมาหลัง hard-contrast probe ไม่ใช่ก่อน

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Prepared v3.3 targeted weighted split, config, and canary run order | `scripts/create_v3_3_training_split.py`, `ml/unsloth/config.v3-3.yaml`, `data/splits/train-v3-3-targeted-hard-contrast.jsonl` | Prepared |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Use targeted training-time weighting for v3.3 | v3.2 hard probe improved globally but SQLi was `1/10` and port scan was `2/10`, so the next run should focus on those two boundaries rather than add every label equally | v3.3 train has SQLi and port scan at 120 records each, normal at 110, brute force/traversal at 100, while validation and fixed test remain unchanged |
| 2026-05-21 | Run hard-contrast probe before mini semantic eval | v3.2 failed the memorization canary on the hard-contrast supplement itself, so mini semantic eval would be premature until that canary improves | Next report should be v3.3 hard-contrast memorization probe; fixed test remains held |

## Related pages

- [[output-structure-fix/phase-6-v3-2-hard-contrast-probe]]
- [[output-structure-fix/phase-6-v3-hard-contrast-dataset]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[label-imbalance-and-prediction-collapse]]
- [[fine-tuning-notes]]

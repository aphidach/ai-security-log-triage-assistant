# Phase 6 V3.3 Targeted Canary Preparation

**Summary**

หน้าเอกสารนี้บันทึก v3.3 targeted canary หลัง v3.2 hard-contrast memorization probe ดีขึ้นแต่ยังพลาดหนักใน `sql_injection_attempt` และ `port_scan_or_recon` รอบนี้จึงเพิ่ม training-only targeted layer ที่ weight SQLi และ port-scan positives โดยตรง พร้อม normal pairs ที่มีคำคล้ายกัน ตอนนี้ v3.3 train แล้วและมี hard-contrast runtime probe ด้วย `config-adapter.yml` ที่ `temperature=0.3`, `top_p=0.9`, `min_p=0.15`, `repetition_penalty=1.05`; label accuracy ขยับเป็น `0.64` แต่ยังต่ำกว่า canary gate และยังไม่ใช้ fixed `data/splits/test.jsonl` (source: docs/output-structure-fix/phase-6-v3-2-hard-contrast-probe.md, scripts/create_v3_3_training_split.py, reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json)

**Sources**

- `docs/output-structure-fix/phase-6-v3-2-hard-contrast-probe.md` สำหรับ v3.2 failure profile และ decision ให้ทำ v3.3 targeted canary (source: docs/output-structure-fix/phase-6-v3-2-hard-contrast-probe.md)
- `scripts/create_v3_3_training_split.py` สำหรับ v3.3 targeted supplement และ weighted split generator (source: scripts/create_v3_3_training_split.py)
- `data/generated/v3-3-targeted-hard-contrast-security-triage.jsonl` สำหรับ 30 new targeted examples (source: data/generated/v3-3-targeted-hard-contrast-security-triage.jsonl)
- `data/splits/train-v3-3-targeted-hard-contrast.jsonl` และ `data/splits/validation-v3-3-targeted-hard-contrast.jsonl` สำหรับ v3.3 train/validation split (source: data/splits/train-v3-3-targeted-hard-contrast.jsonl, data/splits/validation-v3-3-targeted-hard-contrast.jsonl)
- `ml/unsloth/config.v3-3.yaml` และ `ml/unsloth/config.example.yaml` สำหรับ v3.3 training config paths and output directory (source: ml/unsloth/config.v3-3.yaml, ml/unsloth/config.example.yaml)
- `ml/unsloth/train_lora.py` สำหรับ split guard ที่อนุญาต v3.3 train/validation และยัง block fixed test split ระหว่าง training (source: ml/unsloth/train_lora.py)
- `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-memorization-probe.json` สำหรับ v3.3 canonical hard-contrast probe ที่ `temperature=0` (source: reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-memorization-probe.json)
- `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json` และ `.md` สำหรับ v3.3 runtime probe ผ่าน `config-adapter.yml` ที่ `temperature=0.3`, `top_p=0.9`, `min_p=0.15`, `repetition_penalty=1.05` (source: reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json, source: reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.md)
- `reports/phase-6/phase-6-v3-3-temp-03-hard-contrast-memorization-probe-infographic.html` สำหรับ HTML infographic ของ runtime probe รอบนี้ (source: reports/phase-6/phase-6-v3-3-temp-03-hard-contrast-memorization-probe-infographic.html)
- `config-adapter.example.yml` และ `docs/openai-adapter-runtime-config.md` สำหรับ runtime config pattern ที่ใช้แยก canonical eval ออกจาก runtime probe (source: config-adapter.example.yml, source: docs/openai-adapter-runtime-config.md)

**Last updated**

2026-05-21

## Status

Trained and probed locally. v3.3 ยังไม่ใช่ Phase 7 candidate เพราะ hard-contrast canary ล่าสุดอยู่ที่ `label_accuracy=0.64` ยังต่ำกว่า target ประมาณ `0.80+` และ fixed `data/splits/test.jsonl` ยังต้อง hold ไว้ก่อน

## Generated Artifacts

```text
scripts/create_v3_3_training_split.py
data/generated/v3-3-targeted-hard-contrast-security-triage.jsonl
data/generated/train-plus-v3-3-targeted-hard-contrast.jsonl
data/splits/train-v3-3-targeted-hard-contrast.jsonl
data/splits/validation-v3-3-targeted-hard-contrast.jsonl
ml/unsloth/config.v3-3.yaml
reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-memorization-probe.json
reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-memorization-probe.md
reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json
reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.md
reports/phase-6/phase-6-v3-3-temp-03-hard-contrast-memorization-probe-infographic.html
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
4. ใช้ report path ใหม่ เช่น `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-hard-contrast-memorization-probe.json`
5. ถ้า hard-contrast canary ขยับใกล้ `0.80+` ค่อยรัน mini semantic eval
6. ใช้ `data/splits/test.jsonl` เฉพาะตอนเข้า Phase 7 fixed split comparison เท่านั้น

## Training Result

ผู้ใช้ train v3.3 ด้วย `ml/unsloth/config.v3-3.yaml` แล้วได้ adapter ที่:

```text
ml/unsloth/outputs/lfm2-350m-v3-3-targeted-hard-contrast-security-triage-lora
```

training run ใช้ `train_records=550`, `validation_records=75`, final `train_loss=1.3164117424024475`, runtime ประมาณ `152.3259s`, throughput ประมาณ `9.453 train_samples_per_second` ตามข้อมูล run ที่ผู้ใช้ส่งเข้ามาใน session นี้

## Hard-Contrast Probe Results

ทั้งสองรอบใช้ split เดียวกันคือ `data/generated/v3-hard-contrast-security-triage.jsonl` จำนวน 50 records และยังเป็น canary/memorization probe ไม่ใช่ fixed split comparison

| Run | Runtime settings | Label accuracy | JSON/schema | Severity | Suspicious | Evidence | Latency | Invalid |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v3.3 canonical | `temperature=0` | `0.60` | `1.0 / 1.0` | `0.76` | `0.88` | `0.98` | `463.621951 ms` | `0` |
| v3.3 runtime probe | `temperature=0.3`, `top_p=0.9`, `min_p=0.15`, `repetition_penalty=1.05` | `0.64` | `1.0 / 1.0` | `0.70` | `0.90` | `0.94` | `564.14384 ms` | `0` |

ผลรอบ `temperature=0.3` ดีขึ้นเล็กน้อยที่ label accuracy จาก `0.60` เป็น `0.64` และ `is_suspicious_accuracy` จาก `0.88` เป็น `0.90` แต่ tradeoff คือ `severity_accuracy` ลดจาก `0.76` เป็น `0.70`, evidence partial match ลดจาก `0.98` เป็น `0.94`, latency สูงขึ้นราว `100 ms`

## Temp 0.3 Confusion Matrix

แถวคือ expected label และคอลัมน์คือ predicted label จาก report `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json`

| Expected \ Predicted | `normal` | `failed_login_bruteforce` | `sql_injection_attempt` | `directory_traversal_attempt` | `port_scan_or_recon` |
| --- | ---: | ---: | ---: | ---: | ---: |
| `normal` | 8 | 2 | 0 | 0 | 0 |
| `failed_login_bruteforce` | 0 | 10 | 0 | 0 | 0 |
| `sql_injection_attempt` | 1 | 4 | 2 | 2 | 1 |
| `directory_traversal_attempt` | 1 | 1 | 1 | 6 | 1 |
| `port_scan_or_recon` | 1 | 3 | 0 | 0 | 6 |

จุดที่ดีขึ้นจาก canonical run คือ `directory_traversal_attempt` จาก `4/10` เป็น `6/10` แต่ SQLi ยังอยู่ `2/10` และ port scan ยังอยู่ `6/10` เท่าเดิม ภาพรวมยังมีแรงดึงกลับไปทาย `failed_login_bruteforce` อยู่ โดย predicted distribution รอบ temp 0.3 คือ `failed_login_bruteforce=20/50`, `normal=11/50`, `directory_traversal_attempt=8/50`, `port_scan_or_recon=8/50`, `sql_injection_attempt=3/50`

## Current Decision

`temperature=0.3` เป็น runtime probe ที่น่าจดไว้ เพราะช่วย label accuracy เล็กน้อยและ output contract ยังนิ่ง แต่ยังไม่พอให้เปิด fixed test split

งานถัดไปควรแก้ semantic boundary ต่อ โดยเฉพาะ SQLi ที่ยังถูกทายเป็น brute force/traversal/normal และ port scan ที่ยังถูกดูดเข้า brute force บางส่วน ทางเลือกที่ควรทำก่อน fixed split คือเพิ่ม targeted SQLi examples ที่ชัดกว่าเดิมหรือแยก mini probe สำหรับ SQLi/port-scan boundary โดยไม่ใช้ `data/splits/test.jsonl`

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
| 2026-05-21 | User/Codex | Recorded v3.3 temp 0.3 hard-contrast runtime probe | `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json` | Canary improved to `label_accuracy=0.64`, fixed test still held |
| 2026-05-21 | Codex | Added v3.3 temp 0.3 hard-contrast HTML infographic | `reports/phase-6/phase-6-v3-3-temp-03-hard-contrast-memorization-probe-infographic.html` | Added |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Use targeted training-time weighting for v3.3 | v3.2 hard probe improved globally but SQLi was `1/10` and port scan was `2/10`, so the next run should focus on those two boundaries rather than add every label equally | v3.3 train has SQLi and port scan at 120 records each, normal at 110, brute force/traversal at 100, while validation and fixed test remain unchanged |
| 2026-05-21 | Run hard-contrast probe before mini semantic eval | v3.2 failed the memorization canary on the hard-contrast supplement itself, so mini semantic eval would be premature until that canary improves | Next report should be v3.3 hard-contrast memorization probe; fixed test remains held |
| 2026-05-21 | Keep fixed test split held after v3.3 temp 0.3 probe | Runtime probe improved label accuracy from `0.60` to `0.64`, but SQLi remains `2/10` and overall canary is still below the approximate `0.80+` gate | Continue tuning with hard-contrast/mini boundary probes before Phase 7 fixed split comparison |

## Related pages

- [[output-structure-fix/phase-6-v3-2-hard-contrast-probe]]
- [[output-structure-fix/phase-6-v3-hard-contrast-dataset]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[label-imbalance-and-prediction-collapse]]
- [[fine-tuning-notes]]

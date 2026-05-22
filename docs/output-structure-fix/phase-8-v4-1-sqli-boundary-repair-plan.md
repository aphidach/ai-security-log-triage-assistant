# Phase 8 V4.1 SQLi Boundary Repair Plan

**Summary**

v4.1 เป็น repair รอบแคบต่อจาก v4 ที่ถูก hold เป้าหมายคือแก้ SQLi boundary โดยตรง โดยเฉพาะเคส SQLi ที่ถูกทายเป็น `directory_traversal_attempt` พร้อม guard เล็ก ๆ สำหรับ normal-vs-bruteforce, traversal และ port/recon รอบนี้ยังไม่เปลี่ยน schema, label taxonomy, evaluator metric หรือ UI API และไม่ใช้ `data/splits/test.jsonl` เป็น tuning feedback

**Sources**

- `reports/phase-8-v4-sqli-boundary-training-result.json` สำหรับผล v4 training/probe และ decision `held` (source: reports/phase-8-v4-sqli-boundary-training-result.json)
- `reports/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json` และ temp 0.3 report สำหรับ v4 hard-contrast failure source (source: reports/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json, source: reports/openai-compatible-vllm-structured-outputs-v4-temp-03-2048-hard-contrast-memorization-probe.json)
- `scripts/create_v4_1_sqli_failure_slice.py`, `reports/phase-8-v4-1-sqli-boundary-failure-slice.json` และ `.md` สำหรับ v4.1 failure buckets (source: scripts/create_v4_1_sqli_failure_slice.py, source: reports/phase-8-v4-1-sqli-boundary-failure-slice.json)
- `scripts/create_v4_1_sqli_boundary_repair_dataset.py`, `data/generated/v4-1-sqli-boundary-repair-security-triage.jsonl`, `data/splits/train-v4-1-sqli-boundary-repair.jsonl` และ `data/splits/validation-v4-1-sqli-boundary-repair.jsonl` สำหรับ deterministic supplement และ split artifacts (source: scripts/create_v4_1_sqli_boundary_repair_dataset.py)
- `ml/unsloth/config.v4-1.yaml` สำหรับ v4.1 training config (source: ml/unsloth/config.v4-1.yaml)
- `tests/test_v4_1_sqli_boundary_repair_workflow.py` สำหรับ regression checks (source: tests/test_v4_1_sqli_boundary_repair_workflow.py)

**Last updated**

2026-05-22

## Status

Prepared for training. v4.1 failure slice, 150-record supplement, 1220-record train split, unchanged balanced 75-record validation copy, training config, preflight allowlist และ regression test พร้อมแล้ว ขั้นต่อไปคือ train จาก base `unsloth/LFM2-350M` ด้วย `ml/unsloth/config.v4-1.yaml` แล้ว serve alias `lfm2-security-triage-v4-1` เพื่อรัน hard-contrast gates เท่านั้นก่อน

## Failure Slice

`scripts/create_v4_1_sqli_failure_slice.py` อ่านเฉพาะ v4 temp 0/temp 0.3 hard-contrast reports และ source hard-contrast split ไม่อ่าน fixed test split แล้วเขียน:

```text
reports/phase-8-v4-1-sqli-boundary-failure-slice.json
reports/phase-8-v4-1-sqli-boundary-failure-slice.md
```

union label failures มี `8` ids:

```text
v3-hard-000001
v3-hard-000003
v3-hard-000021
v3-hard-000023
v3-hard-000024
v3-hard-000025
v3-hard-000026
v3-hard-000029
```

temp 0 buckets:

| Bucket | Count | Repair intent |
| --- | ---: | --- |
| `normal_to_bruteforce` | `2` | ลด false positive จาก single/isolated auth failure |
| `sqli_to_normal` | `1` | ดัน schema-discovery SQLi ไม่ให้กลายเป็น benign search |
| `sqli_to_port` | `1` | แยก time-delay/API-error SQLi ออกจาก generic recon |
| `sqli_to_traversal` | `4` | แยก SQL quote/comment/stacked-query cue ออกจาก traversal/file-read cue |

temp 0.3 buckets:

| Bucket | Count | Repair intent |
| --- | ---: | --- |
| `normal_to_bruteforce` | `2` | ลด false positive จาก single/isolated auth failure |
| `sqli_to_normal` | `1` | ดัน schema-discovery SQLi ไม่ให้กลายเป็น benign search |
| `sqli_to_traversal` | `5` | แยก SQL quote/comment/time-delay cue ออกจาก traversal/file-read cue |

## Dataset Recipe

v4.1 ใช้ existing v4 train split เป็นฐาน แล้ว append supplement `150` records:

| Label | Supplement | Final train |
| --- | ---: | ---: |
| `normal` | `24` | `279` |
| `failed_login_bruteforce` | `6` | `136` |
| `sql_injection_attempt` | `100` | `415` |
| `directory_traversal_attempt` | `16` | `191` |
| `port_scan_or_recon` | `4` | `199` |

validation ยังเป็น balanced 75 records จาก v4 validation และ generated supplement ถูกตรวจว่าไม่มี exact input duplication กับ `data/generated/v3-hard-contrast-security-triage.jsonl`

## Training And Gates

Pre-train checks:

```bash
rtk .venv/bin/python scripts/create_v4_1_sqli_failure_slice.py
rtk .venv/bin/python scripts/create_v4_1_sqli_boundary_repair_dataset.py
rtk .venv/bin/python -m unittest tests/test_v4_1_sqli_boundary_repair_workflow.py
rtk .venv/bin/python ml/unsloth/inference.py --preflight-only --config ml/unsloth/config.v4-1.yaml
```

Train command:

```bash
rtk .venv/bin/python ml/unsloth/train_lora.py --config ml/unsloth/config.v4-1.yaml
```

After serving alias `lfm2-security-triage-v4-1`, run hard-contrast only first:

```bash
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v4-1 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TEMPERATURE=0 \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.md
```

Acceptance gates for both temp 0 and temp 0.3: JSON/schema `1.0`, invalid `0`, label accuracy `>=0.90`, SQLi `>=8/10`, SQLi predicted as traversal `<=2/10`, normal `>=8/10`, traversal `>=9/10`, port/recon `>=9/10`, predicted brute-force `<=14/50`

## Hold Fixed Test

`data/splits/test.jsonl` must not be used again in Phase 8. If v4.1 later needs a final comparison, plan it separately and prefer a new frozen holdout if the goal is genuinely unseen evidence

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-22 | Codex | Created v4.1 failure slice, deterministic supplement, config, split artifacts, and regression tests | `scripts/create_v4_1_sqli_failure_slice.py`, `scripts/create_v4_1_sqli_boundary_repair_dataset.py`, `ml/unsloth/config.v4-1.yaml`, `tests/test_v4_1_sqli_boundary_repair_workflow.py` | Prepared |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-22 | Make v4.1 a narrow SQLi-boundary repair | v4 restored JSON/schema reliability but stayed at SQLi `4/10`, mostly SQLi predicted as traversal | Supplement weights SQLi more heavily than v4 while keeping only small guard sets |
| 2026-05-22 | Use v4 train as the base split but train from base model | Need preserve v4 guard data while avoiding adapter-to-adapter drift | v4.1 train grows to 1220 records, config starts from `unsloth/LFM2-350M` |
| 2026-05-22 | Stop data-only repair if v4.1 SQLi stays `<=6/10` | Repeated SQLi failure after a narrow supplement would suggest capacity, prompt, or serving architecture needs diagnosis | Next phase should be capacity/architecture diagnostic rather than another broad data append |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-sqli-boundary-repair-plan]]
- [[output-structure-fix/phase-7-fixed-split-comparison]]
- [[data-card]]
- [[fine-tuning-notes]]

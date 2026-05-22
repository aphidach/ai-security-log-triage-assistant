# Phase 8 V4 SQLi Boundary Repair Plan

**Summary**

Phase 8 / v4 เป็น experiment ใหม่หลัง Phase 7 ตัดสินใจ `hold` v3.5 เป้าหมายคือแก้ SQLi/quote-heavy boundary ที่ยังอ่อน โดยเพิ่ม guard เล็ก ๆ สำหรับ normal-vs-bruteforce, traversal, port/recon และ severity calibration รอบนี้ไม่ใช้ `data/splits/test.jsonl` เป็น tuning feedback และไม่ถือว่าเป็น fixed-split comparison รอบใหม่

**Sources**

- `reports/comparison.md` สำหรับ Phase 7 historical context และ decision `hold` (source: reports/comparison.md)
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-2048-hard-contrast-memorization-probe.json` สำหรับ v3.5 deterministic hard-contrast failure source (source: reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-2048-hard-contrast-memorization-probe.json)
- `scripts/create_v4_sqli_failure_slice.py`, `reports/phase-8-v4-sqli-boundary-failure-slice.json` และ `.md` สำหรับ v4 failure buckets (source: scripts/create_v4_sqli_failure_slice.py, source: reports/phase-8-v4-sqli-boundary-failure-slice.json)
- `scripts/create_v4_sqli_boundary_repair_dataset.py`, `data/generated/v4-sqli-boundary-repair-security-triage.jsonl`, `data/splits/train-v4-sqli-boundary-repair.jsonl` และ `data/splits/validation-v4-sqli-boundary-repair.jsonl` สำหรับ deterministic supplement และ split artifacts (source: scripts/create_v4_sqli_boundary_repair_dataset.py)
- `ml/unsloth/config.v4.yaml` สำหรับ v4 training config (source: ml/unsloth/config.v4.yaml)
- `tests/test_v4_sqli_boundary_repair_workflow.py` สำหรับ regression checks (source: tests/test_v4_sqli_boundary_repair_workflow.py)
- `reports/phase-8-v4-sqli-boundary-training-result.json` และ `.md` สำหรับ training metrics และ hard-contrast gate decision (source: reports/phase-8-v4-sqli-boundary-training-result.json)
- `reports/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json` และ `reports/openai-compatible-vllm-structured-outputs-v4-temp-03-2048-hard-contrast-memorization-probe.json` สำหรับ v4 hard-contrast probes (source: reports/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json)
- `docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md` สำหรับ next repair หลัง v4 held (source: docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md)

**Last updated**

2026-05-22

## Status

Trained and hard-contrast probed; held. v4 trained from base `unsloth/LFM2-350M`, served as alias `lfm2-security-triage-v4`, and passed JSON/schema contract on both temp 0 and temp 0.3 hard-contrast probes. It still misses the Phase 8 semantic gate because label accuracy stays at `0.84` and SQLi remains `4/10`, so mini semantic eval and any new fixed comparison stay blocked.

## Failure Slice

`scripts/create_v4_sqli_failure_slice.py` อ่านเฉพาะ v3.5 temp 0 2048 hard-contrast report และ source hard-contrast split ไม่อ่าน fixed test split แล้วเขียน:

```text
reports/phase-8-v4-sqli-boundary-failure-slice.json
reports/phase-8-v4-sqli-boundary-failure-slice.md
```

label failures มี `8/50` buckets:

| Bucket | Count | Repair intent |
| --- | ---: | --- |
| `normal_to_bruteforce` | `2` | ลด false positive จาก single/low-signal auth failure |
| `sqli_to_invalid` | `1` | เพิ่ม quote-heavy SQLi ที่ต้อง escape JSON ให้ถูก |
| `sqli_to_normal` | `1` | ดัน schema-discovery/encoded SQLi ไม่ให้ถูกมอง benign |
| `sqli_to_traversal` | `4` | แยก SQL comment/quote cue ออกจาก traversal/file-read cue |

## Dataset Recipe

v4 ใช้ v3.5 train split เป็นฐาน แล้ว append supplement `160` records:

| Label | Supplement | Final train |
| --- | ---: | ---: |
| `normal` | `40` | `255` |
| `failed_login_bruteforce` | `10` | `130` |
| `sql_injection_attempt` | `80` | `315` |
| `directory_traversal_attempt` | `20` | `175` |
| `port_scan_or_recon` | `10` | `195` |

validation ยังเป็น balanced 75 records จาก v3.5 validation และ fixed `data/splits/test.jsonl` ไม่ถูกอ่านหรือแก้

## Training And Gates

Pre-train checks:

```bash
rtk .venv/bin/python scripts/create_v4_sqli_failure_slice.py
rtk .venv/bin/python scripts/create_v4_sqli_boundary_repair_dataset.py
rtk .venv/bin/python -m unittest tests/test_v4_sqli_boundary_repair_workflow.py
rtk .venv/bin/python ml/unsloth/inference.py --preflight-only --config ml/unsloth/config.v4.yaml
```

Train command:

```bash
rtk .venv/bin/python ml/unsloth/train_lora.py --config ml/unsloth/config.v4.yaml
```

After serving alias `lfm2-security-triage-v4`, run hard-contrast only first:

```bash
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v4 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TEMPERATURE=0 \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.md
```

Acceptance gates before mini semantic eval: JSON/schema `1.0`, invalid `0`, label accuracy `>=0.90`, SQLi `>=8/10`, normal `>=8/10`, traversal `>=9/10`, port/recon `>=9/10`, and predicted brute force `<=14/50`. Temp 0.3 runtime probe must also keep JSON/schema `1.0`, invalid `0`, label accuracy `>=0.90`, and SQLi `>=8/10`

## Training Result

User-provided training completion for `ml/unsloth/config.v4.yaml`:

| Field | Value |
| --- | ---: |
| Train records | `1070` |
| Validation records | `75` |
| Epoch | `4.029906542056075` |
| Train loss | `0.5690714741470637` |
| Train runtime | `401.7052` seconds |
| Train samples/sec | `10.754` |
| Train steps/sec | `1.344` |

`/v1/models` showed `lfm2-security-triage-v4` served on vLLM with parent `unsloth/LFM2-350M` and adapter root under the v4 output directory before the probes ran.

## Hard-Contrast Result

Both v4 probes used only `data/generated/v3-hard-contrast-security-triage.jsonl`; fixed `data/splits/test.jsonl` was not used.

| Probe | Label accuracy | JSON/schema | Invalid | SQLi | Normal | Traversal | Port/recon | Predicted brute-force | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| temp 0 | `0.84` | `1.0 / 1.0` | `0` | `4/10` | `8/10` | `10/10` | `10/10` | `12/50` | Held |
| temp 0.3 | `0.84` | `1.0 / 1.0` | `0` | `4/10` | `8/10` | `10/10` | `10/10` | `12/50` | Held |

v4 repaired the hard-contrast invalid-output issue and kept the small guard labels stable, but the SQLi boundary did not improve. Remaining temp 0 SQLi label misses are mostly SQLi predicted as traversal (`4`) plus one normal and one port/recon. Temp 0.3 shifts the same weakness to SQLi predicted as traversal (`5`) plus one normal.

## Hold Fixed Test

`data/splits/test.jsonl` must not be used again in Phase 8. If v4 later needs a final comparison, plan it separately and prefer a new frozen holdout if the goal is genuinely unseen evidence.

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-22 | Codex | Created v4 SQLi-first failure slice, deterministic supplement, config, split artifacts, and regression tests | `scripts/create_v4_sqli_failure_slice.py`, `scripts/create_v4_sqli_boundary_repair_dataset.py`, `ml/unsloth/config.v4.yaml`, `tests/test_v4_sqli_boundary_repair_workflow.py` | Prepared |
| 2026-05-22 | User/Codex | Recorded v4 training completion and ran temp 0/temp 0.3 hard-contrast probes | `reports/phase-8-v4-sqli-boundary-training-result.json`, `reports/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json`, `reports/openai-compatible-vllm-structured-outputs-v4-temp-03-2048-hard-contrast-memorization-probe.json` | Held |
| 2026-05-22 | Codex | Prepared v4.1 as the next narrow SQLi-boundary repair | `docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md`, `data/splits/train-v4-1-sqli-boundary-repair.jsonl`, `ml/unsloth/config.v4-1.yaml` | Follow-up prepared |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-22 | Make v4 SQLi-first with guards | Phase 7 and v3.5 hard-contrast failures are concentrated in SQLi/quote boundaries, while normal/brute-force needs only a guard set | Supplement heavily weights SQLi but keeps small guard sets for other labels |
| 2026-05-22 | Train v4 from `unsloth/LFM2-350M` base | Need a clean read on dataset repair rather than inherited adapter drift | Config creates a new adapter/output dir and serve alias should be `lfm2-security-triage-v4` |
| 2026-05-22 | Do not reuse fixed split for v4 tuning | Phase 7 fixed split is already historical evidence for v3.5 | v4 gates use hard-contrast and mini semantic eval only until a separately planned final comparison |
| 2026-05-22 | Hold v4 before mini semantic eval | v4 passes JSON/schema on hard-contrast but stays at label accuracy `0.84` and SQLi `4/10` | Do not run mini semantic eval or fixed comparison from this v4 checkpoint; the next change should target SQLi-vs-traversal/normal/port boundaries more directly or reconsider model capacity |
| 2026-05-22 | Use v4.1 as the immediate follow-up | v4 failure slice shows the remaining hard-contrast blocker is concentrated in SQLi boundary errors | v4.1 uses v4 train as base, adds a 150-record SQLi-heavy supplement, and keeps fixed test held |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-6-v3-5-boundary-repair-plan]]
- [[output-structure-fix/phase-7-fixed-split-comparison]]
- [[output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan]]
- [[data-card]]
- [[fine-tuning-notes]]

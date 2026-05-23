# Phase 8 V4.7 Qwen3.5 Auth SQLi Severity Calibration Plan

**Summary**

v4.7 เป็น calibration run แบบแคบต่อจาก v4.6 เป้าหมายคือซ่อม failure ที่ยังเหลือโดยไม่เปิด fixed split: benign auth ยังถูก over-alert เป็น brute force, SQLi บน login/auth route ถูกทายเป็น brute force, brute-force severity `medium` ยังลอยเป็น `high`, port/recon medium หนึ่งเคสลอยเป็น `high`, และ traversal หนึ่งเคสยัง miss evidence partial match (source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json)

**Sources**

- v4.7 failure slice artifacts (source: scripts/create_v4_7_qwen35_auth_sqli_severity_calibration_slice.py, source: reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-slice.json, source: reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-slice.md)
- v4.7 calibration dataset artifacts (source: scripts/create_v4_7_qwen35_auth_sqli_severity_calibration_dataset.py, source: data/generated/v4-7-qwen35-auth-sqli-severity-calibration-security-triage.jsonl, source: data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl, source: data/splits/validation-v4-7-qwen35-auth-sqli-severity-calibration.jsonl, source: data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl)
- v4.7 Qwen training config (source: ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml)
- v4.7 regression tests (source: tests/test_v4_7_qwen35_auth_sqli_severity_calibration_workflow.py)
- v4.6 result page for prior checkpoint and hold decision (source: docs/output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan.md)

**Last updated**

2026-05-23

## Status

Prepared for training. v4.7 now has:

- failure slice from v4.6 hard-contrast and calibration probe outputs
- 150-record calibration supplement
- 1460-record train split
- 130-record validation split
- 30-record non-fixed calibration probe split
- Qwen3.5 LoRA config
- regression tests for artifact determinism, split guardrails, evidence, and config preflight

No `data/splits/test.jsonl` run was opened or used in v4.7 preparation.

## Failure Slice

Artifacts:

```text
reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-slice.json
reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-slice.md
```

Bucket summary:

| Bucket | Count | IDs |
| --- | ---: | --- |
| `normal_to_bruteforce` | `7` | `v3-hard-000001`, `v3-hard-000002`, `v3-hard-000003`, `v4-6-qwen35-cal-000121`, `000122`, `000123`, `000124` |
| `sqli_to_bruteforce` | `2` | `v3-hard-000021`, `v3-hard-000025` |
| `bruteforce_medium_to_high` | `7` | `v3-hard-000015`, `v3-hard-000016`, `v3-hard-000018`, `v4-6-qwen35-cal-000136`, `000137`, `000138`, `000139` |
| `port_recon_medium_to_high` | `1` | `v3-hard-000050` |
| `traversal_evidence_miss` | `1` | `v3-hard-000035` |

## Dataset Artifacts

v4.7 starts from the v4.6 train/validation splits, then adds a train-only supplement plus a small non-fixed probe holdout.

```text
data/generated/v4-7-qwen35-auth-sqli-severity-calibration-security-triage.jsonl
data/generated/train-plus-v4-7-qwen35-auth-sqli-severity-calibration.jsonl
data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl
data/splits/validation-v4-7-qwen35-auth-sqli-severity-calibration.jsonl
data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl
```

Supplement labels:

| Label | Count |
| --- | ---: |
| `normal` | `69` |
| `failed_login_bruteforce` | `39` |
| `sql_injection_attempt` | `23` |
| `directory_traversal_attempt` | `9` |
| `port_scan_or_recon` | `10` |

Train split:

| Label | Count |
| --- | ---: |
| `normal` | `405` |
| `failed_login_bruteforce` | `186` |
| `sql_injection_attempt` | `439` |
| `directory_traversal_attempt` | `205` |
| `port_scan_or_recon` | `225` |

Validation split:

| Label | Count |
| --- | ---: |
| `normal` | `45` |
| `failed_login_bruteforce` | `26` |
| `sql_injection_attempt` | `21` |
| `directory_traversal_attempt` | `17` |
| `port_scan_or_recon` | `21` |

The 30-record calibration probe split is deliberately not the fixed split:

| Label | Count |
| --- | ---: |
| `normal` | `15` |
| `failed_login_bruteforce` | `7` |
| `sql_injection_attempt` | `5` |
| `directory_traversal_attempt` | `1` |
| `port_scan_or_recon` | `2` |

## Training Config

Config:

```text
ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml
```

Key settings:

| Field | Value |
| --- | --- |
| Base model | `unsloth/Qwen3.5-0.8B` |
| Loader | `fast_vision_model` |
| Train path | `data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl` |
| Validation path | `data/splits/validation-v4-7-qwen35-auth-sqli-severity-calibration.jsonl` |
| Max sequence length | `1024` |
| LoRA rank | `16` |
| Learning rate | `0.00008` |
| Max steps | `275` |
| Output dir | `ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration-lora` |

## Command Runbook

Regenerate the v4.7 failure slice:

```bash
python3 scripts/create_v4_7_qwen35_auth_sqli_severity_calibration_slice.py
```

Regenerate the v4.7 supplement and splits:

```bash
python3 scripts/create_v4_7_qwen35_auth_sqli_severity_calibration_dataset.py
```

Preflight Qwen training config:

```bash
python3 ml/unsloth/train_lora_vision_qwen.py \
  --preflight-only \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml
```

Run the v4.7 Qwen training job from the base model:

```bash
python3 ml/unsloth/train_lora_vision_qwen.py \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml
```

After training, serve the adapter through vLLM with a new alias such as `qwen3.6-8B-triage-v3`, then run non-fixed probes with the model alias set by env var:

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
OPENAI_COMPATIBLE_MODEL=qwen3.6-8B-triage-v3 \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.md
```

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
OPENAI_COMPATIBLE_MODEL=qwen3.6-8B-triage-v3 \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.md
```

## Gate Before Fixed Split

Open fixed split only if v4.7 clears these non-fixed checks:

| Gate | Target |
| --- | ---: |
| JSON/schema | `1.0 / 1.0` |
| Invalid outputs | `0` |
| Hard-contrast label accuracy | `>= 0.92` |
| Hard-contrast `normal` | `>= 8/10` |
| Hard-contrast SQLi | `>= 9/10` |
| Every suspicious hard-contrast label | `>= 9/10` |
| Hard-contrast severity | `>= 0.90` |
| v4.7 calibration label/severity | `>= 0.90 / >= 0.90` |
| v4.7 normal auth probe | `>= 14/15` |
| v4.7 SQLi auth-context probe | `5/5` |
| v4.7 brute-force medium severity probe | `>= 5/5` |
| Specific repaired severity IDs | `v3-hard-000015`, `000016`, `000018`, `000050` corrected |
| Specific repaired evidence ID | `v3-hard-000035` evidence partial match corrected |

Decision at preparation time: fixed split remains closed until these probes exist and pass.

## Verification

Local deterministic checks to run:

```bash
python3 -m unittest \
  tests/test_v4_6_qwen35_normal_calibration_workflow.py \
  tests/test_v4_7_qwen35_auth_sqli_severity_calibration_workflow.py \
  tests/test_qwen35_training_pilot_config.py

python3 -m py_compile \
  scripts/create_v4_7_qwen35_auth_sqli_severity_calibration_slice.py \
  scripts/create_v4_7_qwen35_auth_sqli_severity_calibration_dataset.py \
  ml/unsloth/train_lora.py \
  ml/unsloth/train_lora_vision_qwen.py
```

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-23 | Codex | Prepared v4.7 Qwen auth/SQLi/severity calibration workflow from v4.6 non-fixed failures | `reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-slice.json`, `data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl`, `ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml` | Prepared; training pending |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Create v4.7 as narrow auth/SQLi/severity calibration | v4.6 already reaches overall hard-contrast label/severity `0.90`, so broad data expansion would blur the remaining failure causes | Add targeted normal-auth, SQLi-auth-context, medium brute-force, limited recon, and exact traversal evidence examples; keep fixed split closed |
| 2026-05-23 | Keep v4.7 training from base Qwen3.5, not the v4.6 adapter | Prior Qwen runs are recorded as separate LoRA experiments and should remain reproducible from the same base model | v4.7 config points directly to `unsloth/Qwen3.5-0.8B` and new train/validation splits |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan]]
- [[fine-tuning-notes]]
- [[data-card]]
- [[openai-adapter-runtime-config]]

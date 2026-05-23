# Phase 8 V4.6 Qwen3.5 Normal Severity Calibration Plan

**Summary**

v4.6 เป็น calibration workflow ต่อจาก v4.5 trained-Qwen LoRA probe รอบ v4.5 แก้ suspicious-to-normal collapse ได้ดีมาก แต่แลกมาด้วย normal false positives (`normal` เหลือ `4/10`) และ severity calibration ยังต่ำ (`0.72`) รอบนี้จึงสร้าง failure slice จาก v4.5, เพิ่ม normal-heavy supplement, เพิ่ม severity calibration examples, สร้าง train/validation/probe split ใหม่ และเตรียม Qwen3.5 LoRA config ใหม่ โดยยังไม่เปิด fixed split

**Sources**

- v4.5 trained-Qwen probe result (source: docs/output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe.md, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json)
- v4.6 calibration slice artifacts (source: scripts/create_v4_6_qwen35_normal_calibration_slice.py, source: reports/phase-8-v4-6-qwen35-normal-calibration-slice.json, source: reports/phase-8-v4-6-qwen35-normal-calibration-slice.md)
- v4.6 calibration dataset artifacts (source: scripts/create_v4_6_qwen35_normal_calibration_dataset.py, source: data/generated/v4-6-qwen35-normal-severity-calibration-security-triage.jsonl, source: data/splits/train-v4-6-qwen35-normal-severity-calibration.jsonl, source: data/splits/validation-v4-6-qwen35-normal-severity-calibration.jsonl, source: data/splits/v4-6-normal-severity-calibration-probe.jsonl)
- v4.6 Qwen training config (source: ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml)
- v4.6 regression tests (source: tests/test_v4_6_qwen35_normal_calibration_workflow.py)

**Last updated**

2026-05-23

## Status

Prepared; training pending. v4.6 now has:

- failure slice report from v4.5 hard-contrast output
- 145-record calibration supplement
- 1340-record train split
- 100-record validation split
- 25-record non-fixed calibration probe split
- Qwen3.5 LoRA config
- regression tests for artifact determinism and split guardrails

No `data/splits/test.jsonl` run was opened or used.

## Why This Exists

v4.5 changed the failure shape. The trained Qwen LoRA adapter caught all suspicious hard-contrast labels (`failed_login_bruteforce`, `sql_injection_attempt`, `directory_traversal_attempt`, `port_scan_or_recon`) at `10/10`, but it over-alerted normal hard negatives:

| Expected | Predicted | Count |
| --- | --- | ---: |
| `normal` | `failed_login_bruteforce` | `3` |
| `normal` | `sql_injection_attempt` | `2` |
| `normal` | `directory_traversal_attempt` | `1` |

Severity also needs calibration:

| Bucket | Count | Read |
| --- | ---: | --- |
| Brute force severity too high | `3` | medium brute-force examples became high |
| Port/recon severity too low | `5` | clear scan/recon examples became medium |
| Evidence miss | `1` | traversal label was correct but evidence missed the expected substring |

So v4.6 should not add more broad SQLi data. The useful next step is to restore normal precision and severity boundaries while preserving v4.5 suspicious recall.

## Calibration Slice

Artifacts:

```text
reports/phase-8-v4-6-qwen35-normal-calibration-slice.json
reports/phase-8-v4-6-qwen35-normal-calibration-slice.md
```

Headline:

| Metric | Value |
| --- | ---: |
| Label failures | `6` |
| Severity failures | `14` |
| Severity-only failures | `8` |
| Evidence failures | `1` |
| Fixed test split used | `false` |

Bucket summary:

| Bucket | Count | IDs |
| --- | ---: | --- |
| Normal -> brute force | `3` | `v3-hard-000001`, `v3-hard-000002`, `v3-hard-000003` |
| Normal -> SQLi | `2` | `v3-hard-000005`, `v3-hard-000009` |
| Normal -> traversal | `1` | `v3-hard-000007` |
| Brute force severity too high | `3` | `v3-hard-000015`, `v3-hard-000016`, `v3-hard-000018` |
| Port/recon severity too low | `5` | `v3-hard-000042`, `v3-hard-000043`, `v3-hard-000044`, `v3-hard-000046`, `v3-hard-000047` |
| Evidence miss | `1` | `v3-hard-000035` |

## Dataset Artifacts

v4.6 starts from v4.1 train/validation sources because v4.5 Qwen used the v4.1 split. It then adds train-only calibration examples plus a small non-fixed probe holdout.

```text
data/generated/v4-6-qwen35-normal-severity-calibration-security-triage.jsonl
data/generated/train-plus-v4-6-qwen35-normal-severity-calibration.jsonl
data/splits/train-v4-6-qwen35-normal-severity-calibration.jsonl
data/splits/validation-v4-6-qwen35-normal-severity-calibration.jsonl
data/splits/v4-6-normal-severity-calibration-probe.jsonl
```

Supplement labels:

| Label | Count |
| --- | ---: |
| `normal` | `87` |
| `failed_login_bruteforce` | `22` |
| `sql_injection_attempt` | `7` |
| `directory_traversal_attempt` | `7` |
| `port_scan_or_recon` | `22` |

Train split:

| Label | Count |
| --- | ---: |
| `normal` | `351` |
| `failed_login_bruteforce` | `154` |
| `sql_injection_attempt` | `421` |
| `directory_traversal_attempt` | `197` |
| `port_scan_or_recon` | `217` |

Validation split:

| Label | Count |
| --- | ---: |
| `normal` | `30` |
| `failed_login_bruteforce` | `19` |
| `sql_injection_attempt` | `16` |
| `directory_traversal_attempt` | `16` |
| `port_scan_or_recon` | `19` |

The 25-record calibration probe split is deliberately not the fixed split:

| Label | Count |
| --- | ---: |
| `normal` | `15` |
| `failed_login_bruteforce` | `4` |
| `sql_injection_attempt` | `1` |
| `directory_traversal_attempt` | `1` |
| `port_scan_or_recon` | `4` |

## Training Config

Config:

```text
ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml
```

Key settings:

| Field | Value |
| --- | --- |
| Base model | `unsloth/Qwen3.5-0.8B` |
| Loader | `fast_vision_model` |
| Train path | `data/splits/train-v4-6-qwen35-normal-severity-calibration.jsonl` |
| Validation path | `data/splits/validation-v4-6-qwen35-normal-severity-calibration.jsonl` |
| Max sequence length | `1024` |
| LoRA rank | `16` |
| Learning rate | `0.00008` |
| Max steps | `140` |
| Output dir | `ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration-lora` |

The learning rate is slightly lower than v4.5 (`0.00008` vs `0.0001`) because this is a calibration pass, not a broad class-learning pass.

## Command Runbook

Regenerate the calibration slice:

```bash
python3 scripts/create_v4_6_qwen35_normal_calibration_slice.py
```

Regenerate the v4.6 supplement and splits:

```bash
python3 scripts/create_v4_6_qwen35_normal_calibration_dataset.py
```

Preflight Qwen training config:

```bash
python3 ml/unsloth/train_lora_vision_qwen.py \
  --preflight-only \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml
```

Run the v4.6 Qwen training job:

```bash
python3 ml/unsloth/train_lora_vision_qwen.py \
  --config ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml
```

After training, serve the adapter through vLLM using a new alias such as `qwen3.6-8B-triage-v4-6`, then run:

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/v4-6-normal-severity-calibration-probe.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.md
```

Then rerun the hard-contrast probe:

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.md
```

## Gate Before Fixed Split

Open fixed split only if v4.6 clears these checks on non-fixed probes:

| Gate | Target |
| --- | ---: |
| JSON/schema | `1.0 / 1.0` |
| Invalid outputs | `0` |
| Hard-contrast label accuracy | `>= 0.90` |
| Hard-contrast `normal` | `>= 8/10` |
| Suspicious hard-contrast labels | `>= 9/10` each |
| Severity accuracy | `>= 0.85` |
| Calibration probe normal accuracy | `>= 12/15` |
| Calibration probe suspicious recall | no class collapses |

## Non-Goals

- No fixed split run
- No taxonomy expansion
- No prompt default change
- No production detection claim
- No merge/export decision until calibration is measured

## Verification

Local checks passed:

```bash
python3 -m unittest tests/test_v4_6_qwen35_normal_calibration_workflow.py tests/test_qwen35_training_pilot_config.py
python3 -m py_compile scripts/create_v4_6_qwen35_normal_calibration_slice.py scripts/create_v4_6_qwen35_normal_calibration_dataset.py ml/unsloth/train_lora.py ml/unsloth/train_lora_vision_qwen.py
```

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-23 | Codex | Prepared v4.6 Qwen normal/severity calibration workflow from v4.5 failure slice | `reports/phase-8-v4-6-qwen35-normal-calibration-slice.json`, `data/splits/train-v4-6-qwen35-normal-severity-calibration.jsonl`, `ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml` | Prepared; training pending |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Create v4.6 as calibration, not broad repair | v4.5 already catches suspicious labels but over-alerts normal and miscalibrates severity | Add normal-heavy and severity-boundary data while preserving suspicious recall guards; keep fixed split closed |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe]]
- [[fine-tuning-notes]]
- [[data-card]]
- [[openai-adapter-runtime-config]]

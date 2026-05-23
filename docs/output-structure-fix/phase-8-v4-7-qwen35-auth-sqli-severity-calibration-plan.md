# Phase 8 V4.7 Qwen3.5 Auth SQLi Severity Calibration Plan

**Summary**

v4.7 เป็น calibration run แบบแคบต่อจาก v4.6 เป้าหมายคือซ่อม failure ที่ยังเหลือโดยไม่เปิด fixed split: benign auth ยังถูก over-alert เป็น brute force, SQLi บน login/auth route ถูกทายเป็น brute force, brute-force severity `medium` ยังลอยเป็น `high`, port/recon medium หนึ่งเคสลอยเป็น `high`, และ traversal หนึ่งเคสยัง miss evidence partial match (source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json)

หลัง train/probe แล้ว v4.7 ทำ hard-contrast headline ดีขึ้นเป็น label accuracy `0.92`, severity accuracy `0.92`, JSON/schema `1.0`, invalid `0`, และ evidence partial match `1.0` แต่ไม่ผ่าน calibration gate เพราะ probe เฉพาะ v4.7 เหลือ label accuracy `0.366667`, severity accuracy `0.60`, normal-auth label `0/15`, SQLi-auth-context `1/5`, และ brute-force `medium` severity `0/7` (source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json)

**Sources**

- v4.7 failure slice artifacts (source: scripts/create_v4_7_qwen35_auth_sqli_severity_calibration_slice.py, source: reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-slice.json, source: reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-slice.md)
- v4.7 calibration dataset artifacts (source: scripts/create_v4_7_qwen35_auth_sqli_severity_calibration_dataset.py, source: data/generated/v4-7-qwen35-auth-sqli-severity-calibration-security-triage.jsonl, source: data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl, source: data/splits/validation-v4-7-qwen35-auth-sqli-severity-calibration.jsonl, source: data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl)
- v4.7 Qwen training config (source: ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml)
- v4.7 non-fixed evaluation reports (source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json)
- v4.7 HTML summary report (source: reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-report.html)
- v4.8 follow-up diagnostic audit (source: docs/output-structure-fix/phase-8-v4-8-qwen35-auth-sqli-diagnostic-plan.md, source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json)
- v4.7 regression tests (source: tests/test_v4_7_qwen35_auth_sqli_severity_calibration_workflow.py)
- v4.6 result page for prior checkpoint and hold decision (source: docs/output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan.md)

**Last updated**

2026-05-23

## Status

Trained and probed on non-fixed v4.7 calibration and hard-contrast splits. v4.7 now has:

- failure slice from v4.6 hard-contrast and calibration probe outputs
- 150-record calibration supplement
- 1460-record train split
- 130-record validation split
- 30-record non-fixed calibration probe split
- Qwen3.5 LoRA config
- regression tests for artifact determinism, split guardrails, evidence, and config preflight
- non-fixed probe reports for auth/SQLi/severity calibration and hard-contrast regression
- HTML report for the v4.7 gate decision

Decision: held before fixed split. No `data/splits/test.jsonl` run was opened or used in v4.7 preparation, training, or probing.

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

```bash
{
  "status": "training_complete",
  "config_path": "ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml",
  "output_dir": "ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration-lora",
  "train_records": 1460,
  "validation_records": 130,
  "metrics": {
    "epoch": 1.504109589041096,
    "total_flos": 4933374473088768.0,
    "train_loss": 0.26452613711357115,
    "train_runtime": 1709.8471,
    "train_samples_per_second": 1.287,
    "train_steps_per_second": 0.161
  }
}

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

```
adapter: openai-compatible
split: data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl
samples: 30
label_accuracy: 0.366667
json_parse_success_rate: 1.0
schema_success_rate: 1.0
severity_accuracy: 0.6
is_suspicious_accuracy: 0.666667
evidence_partial_match: 1.0
average_latency_ms: 6592.079815
invalid_output_count: 0
json_report: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json
markdown_report: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.md

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

```bash
adapter: openai-compatible
split: data/generated/v3-hard-contrast-security-triage.jsonl
samples: 50
label_accuracy: 0.92
json_parse_success_rate: 1.0
schema_success_rate: 1.0
severity_accuracy: 0.92
is_suspicious_accuracy: 0.98
evidence_partial_match: 1.0
average_latency_ms: 6783.558132
invalid_output_count: 0
json_report: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json
markdown_report: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.md

```

## Result Summary

Training completed from the base `unsloth/Qwen3.5-0.8B` path with `1460` train records and `130` validation records. The captured training output reports `train_loss=0.26452613711357115`, `train_runtime=1709.8471` seconds, `train_samples_per_second=1.287`, and `train_steps_per_second=0.161` (source: ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml, source: docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md).

Runtime probe settings:

| Field | Value |
| --- | --- |
| Adapter | `openai-compatible` |
| Served alias | `qwen3.6-8B-triage-v3` |
| Base URL | `http://192.168.8.141:8080/v1` |
| Prompt | `triage-json-v2.1` |
| Structured-output mode | `structured_outputs_json` |
| Temperature | `0.0` |
| Max tokens | `512` |

Probe headline metrics:

| Probe | Samples | Label accuracy | Severity accuracy | Suspicious accuracy | Evidence partial | JSON/schema | Invalid | Avg latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v4.7 auth/SQLi/severity calibration | `30` | `0.366667` | `0.60` | `0.666667` | `1.0` | `1.0 / 1.0` | `0` | `6592.079815 ms` |
| v3 hard-contrast regression | `50` | `0.92` | `0.92` | `0.98` | `1.0` | `1.0 / 1.0` | `0` | `6783.558132 ms` |

Label breakdown:

| Probe | Expected label | Label correct | Severity correct | Main observation |
| --- | --- | ---: | ---: | --- |
| v4.7 calibration | `normal` | `0/15` | `15/15` | all normal-auth samples predicted `failed_login_bruteforce` |
| v4.7 calibration | `failed_login_bruteforce` | `7/7` | `0/7` | all medium brute-force samples predicted severity `high` |
| v4.7 calibration | `sql_injection_attempt` | `1/5` | `1/5` | four SQLi auth-context samples predicted `normal` with severity `low` |
| v4.7 calibration | `port_scan_or_recon` | `2/2` | `1/2` | one medium recon sample predicted severity `high` |
| v4.7 calibration | `directory_traversal_attempt` | `1/1` | `1/1` | traversal case passed label, severity, suspicious, and evidence checks |
| hard-contrast | `normal` | `7/10` | `10/10` | three benign auth samples still predicted `failed_login_bruteforce` |
| hard-contrast | `failed_login_bruteforce` | `10/10` | `7/10` | `v3-hard-000015`, `000016`, and `000018` still predicted severity `high` instead of `medium` |
| hard-contrast | `sql_injection_attempt` | `9/10` | `10/10` | `v3-hard-000025` still predicted `failed_login_bruteforce` |
| hard-contrast | `directory_traversal_attempt` | `10/10` | `10/10` | `v3-hard-000035` evidence partial match is corrected |
| hard-contrast | `port_scan_or_recon` | `10/10` | `9/10` | `v3-hard-000050` is corrected, but `v3-hard-000042` predicts severity `medium` instead of `high` |

HTML report:

```text
reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-report.html
```

## Gate Before Fixed Split

Open fixed split only if v4.7 clears these non-fixed checks. Actual result: fixed split remains closed.

| Gate | Target | Observed | Status |
| --- | ---: | ---: | --- |
| JSON/schema | `1.0 / 1.0` | calibration `1.0 / 1.0`; hard-contrast `1.0 / 1.0` | Pass |
| Invalid outputs | `0` | calibration `0`; hard-contrast `0` | Pass |
| Hard-contrast label accuracy | `>= 0.92` | `0.92` | Pass |
| Hard-contrast `normal` | `>= 8/10` | `7/10` | Hold |
| Hard-contrast SQLi | `>= 9/10` | `9/10` | Pass |
| Every suspicious hard-contrast label | `>= 9/10` | brute-force `10/10`, SQLi `9/10`, traversal `10/10`, recon `10/10` | Pass |
| Hard-contrast severity | `>= 0.90` | `0.92` | Pass |
| v4.7 calibration label/severity | `>= 0.90 / >= 0.90` | `0.366667 / 0.60` | Hold |
| v4.7 normal auth probe | `>= 14/15` | `0/15` label-correct; all predicted `failed_login_bruteforce` | Hold |
| v4.7 SQLi auth-context probe | `5/5` | `1/5` | Hold |
| v4.7 brute-force medium severity probe | `>= 5/5` | `0/7`; all predicted severity `high` | Hold |
| Specific repaired severity IDs | `v3-hard-000015`, `000016`, `000018`, `000050` corrected | `000015`, `000016`, `000018` still `medium -> high`; `000050` corrected | Hold |
| Specific repaired evidence ID | `v3-hard-000035` evidence partial match corrected | corrected | Pass |

Decision after v4.7: do not run mini semantic or fixed split comparison from this checkpoint. The hard-contrast headline improved, but the new calibration probe exposed a sharper regression on the exact auth/SQLi/severity cases v4.7 was created to repair.

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
| 2026-05-23 | User/Codex | Recorded v4.7 training completion, non-fixed probe metrics, gate read, and HTML report | `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json`, `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json`, `reports/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-report.html` | Probed; fixed split held |
| 2026-05-23 | Codex | Started v4.8 follow-up diagnostic audit from the v4.7 calibration failure shape | `docs/output-structure-fix/phase-8-v4-8-qwen35-auth-sqli-diagnostic-plan.md`, `reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json` | Diagnostic follow-up created |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Create v4.7 as narrow auth/SQLi/severity calibration | v4.6 already reaches overall hard-contrast label/severity `0.90`, so broad data expansion would blur the remaining failure causes | Add targeted normal-auth, SQLi-auth-context, medium brute-force, limited recon, and exact traversal evidence examples; keep fixed split closed |
| 2026-05-23 | Keep v4.7 training from base Qwen3.5, not the v4.6 adapter | Prior Qwen runs are recorded as separate LoRA experiments and should remain reproducible from the same base model | v4.7 config points directly to `unsloth/Qwen3.5-0.8B` and new train/validation splits |
| 2026-05-23 | Hold v4.7 before fixed split | Hard-contrast improves to label/severity `0.92`, but the new calibration probe fails label `0.366667`, normal-auth `0/15`, SQLi-auth `1/5`, and brute-force medium severity `0/7` | Do not open mini semantic or fixed split comparison from this checkpoint; treat v4.7 as evidence that the narrow supplement overcorrected key auth/SQLi boundaries |
| 2026-05-23 | Use v4.7 as v4.8 diagnostic input, not as a release checkpoint | Heuristic beats v4.7 by `0.30` label accuracy on the same calibration probe, and v4.6 direct comparator is not currently served | Keep fixed split closed; inspect paired boundaries before any v4.8 train supplement |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan]]
- [[output-structure-fix/phase-8-v4-8-qwen35-auth-sqli-diagnostic-plan]]
- [[fine-tuning-notes]]
- [[data-card]]
- [[openai-adapter-runtime-config]]

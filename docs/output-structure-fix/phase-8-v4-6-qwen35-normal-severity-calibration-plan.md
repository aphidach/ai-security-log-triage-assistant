# Phase 8 V4.6 Qwen3.5 Normal Severity Calibration Result

**Summary**

v4.6 เป็น calibration run ต่อจาก v4.5 trained-Qwen LoRA probe รอบนี้ train สำเร็จจาก Qwen3.5 base ใหม่ แล้วรันทั้ง non-fixed calibration probe และ hard-contrast probe เดิม ผลหลักคือ hard-contrast ดีขึ้นจาก v4.5: label accuracy `0.88` -> `0.90`, severity accuracy `0.72` -> `0.90`, JSON/schema ยัง `1.0`, invalid `0` แต่ fixed split ยังควรปิดต่อ เพราะ hard-contrast `normal` ยัง `7/10`, SQLi เหลือ `8/10`, calibration probe normal ได้ `11/15` และ brute-force severity ยังถูกยกเป็น `high` ครบ `4/4` เคส

**Sources**

- v4.5 trained-Qwen probe result (source: docs/output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe.md, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json)
- v4.6 calibration slice artifacts (source: scripts/create_v4_6_qwen35_normal_calibration_slice.py, source: reports/phase-8-v4-6-qwen35-normal-calibration-slice.json, source: reports/phase-8-v4-6-qwen35-normal-calibration-slice.md)
- v4.6 calibration dataset artifacts (source: scripts/create_v4_6_qwen35_normal_calibration_dataset.py, source: data/generated/v4-6-qwen35-normal-severity-calibration-security-triage.jsonl, source: data/splits/train-v4-6-qwen35-normal-severity-calibration.jsonl, source: data/splits/validation-v4-6-qwen35-normal-severity-calibration.jsonl, source: data/splits/v4-6-normal-severity-calibration-probe.jsonl)
- v4.6 Qwen training config (source: ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml)
- v4.6 Qwen training result capture (source: reports/phase-8-v4-6-qwen35-lora-training-result.json, source: reports/phase-8-v4-6-qwen35-lora-training-result.md)
- v4.6 calibration and hard-contrast evaluation reports (source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json)
- Stakeholder-readable v4.6 HTML report (source: reports/phase-8-v4-6-qwen35-normal-severity-calibration-report.html)
- v4.6 regression tests (source: tests/test_v4_6_qwen35_normal_calibration_workflow.py)

**Last updated**

2026-05-23

## Status

Trained and probed; still held before fixed split. v4.6 now has:

- failure slice report from v4.5 hard-contrast output
- 145-record calibration supplement
- 1340-record train split
- 100-record validation split
- 25-record non-fixed calibration probe split
- Qwen3.5 LoRA config
- training-complete capture
- non-fixed calibration probe result
- hard-contrast probe result
- HTML report for quick review
- regression tests for artifact determinism and split guardrails

No `data/splits/test.jsonl` run was opened or used in v4.6 tuning/evaluation.

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
| Max steps | `260` |
| Output dir | `ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration-lora` |

The learning rate is slightly lower than v4.5 (`0.00008` vs `0.0001`) because this is a calibration pass, not a broad class-learning pass.

## Training Result

The v4.6 training-complete capture is stored as:

```text
reports/phase-8-v4-6-qwen35-lora-training-result.json
reports/phase-8-v4-6-qwen35-lora-training-result.md
```

| Metric | Value |
| --- | ---: |
| Train records | `1340` |
| Validation records | `100` |
| Epoch | `1.5492537313432835` |
| Train loss | `0.2689869593255795` |
| Train runtime | `1419.9621` seconds |
| Train samples/sec | `1.465` |
| Train steps/sec | `0.183` |
| Total FLOPs | `4663705614868608.0` |

Compared with v4.5, v4.6 used more calibration data (`1220/75` -> `1340/100`) and ended with lower train loss (`0.4103` -> `0.2690`). The runtime is longer, so this is not a latency or training-efficiency win by itself; the useful signal is evaluation behavior.

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

```bash
{
  "status": "training_complete",
  "config_path": "ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml",
  "output_dir": "ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration-lora",
  "train_records": 1340,
  "validation_records": 100,
  "metrics": {
    "epoch": 1.5492537313432835,
    "total_flos": 4663705614868608.0,
    "train_loss": 0.2689869593255795,
    "train_runtime": 1419.9621,
    "train_samples_per_second": 1.465,
    "train_steps_per_second": 0.183
  }
}
```

After training, serve the adapter through vLLM. The recorded v4.6 probe used alias `qwen3.6-8B-triage-v2`, then ran:

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/v4-6-normal-severity-calibration-probe.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.md
```


```bash
adapter: openai-compatible
split: data/splits/v4-6-normal-severity-calibration-probe.jsonl
samples: 25
label_accuracy: 0.84
json_parse_success_rate: 1.0
schema_success_rate: 1.0
severity_accuracy: 0.8
is_suspicious_accuracy: 0.84
evidence_partial_match: 1.0
average_latency_ms: 6040.52215
invalid_output_count: 0
json_report: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json
markdown_report: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.md

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

```bash
adapter: openai-compatible
split: data/generated/v3-hard-contrast-security-triage.jsonl
samples: 50
label_accuracy: 0.9
json_parse_success_rate: 1.0
schema_success_rate: 1.0
severity_accuracy: 0.9
is_suspicious_accuracy: 0.96
evidence_partial_match: 0.98
average_latency_ms: 6613.680663
invalid_output_count: 0
json_report: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json
markdown_report: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.md
```

## Evaluation Result

Runtime metadata for both v4.6 probes:

| Field | Value |
| --- | --- |
| Adapter | `openai-compatible` |
| Base URL | `http://192.168.8.141:8080/v1` |
| Model alias | `qwen3.6-8B-triage-v2` |
| Prompt version | `triage-json-v2.1` |
| Response format | `structured_outputs_json` |
| Temperature | `0` |
| Max tokens | `512` |

Metric comparison:

| Probe | Samples | Label acc. | Severity acc. | Suspicious acc. | Evidence | JSON/schema | Invalid | Avg latency |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v4.5 hard-contrast | `50` | `0.88` | `0.72` | `0.88` | `0.98` | `1.0 / 1.0` | `0` | `5648.582491 ms` |
| v4.6 hard-contrast | `50` | `0.90` | `0.90` | `0.96` | `0.98` | `1.0 / 1.0` | `0` | `6613.680663 ms` |
| v4.6 calibration probe | `25` | `0.84` | `0.80` | `0.84` | `1.00` | `1.0 / 1.0` | `0` | `6040.52215 ms` |

v4.6 hard-contrast per-label read:

| Expected label | Label correct | Severity correct | Suspicious correct | Evidence match |
| --- | ---: | ---: | ---: | ---: |
| `normal` | `7/10` | `9/10` | `8/10` | `10/10` |
| `failed_login_bruteforce` | `10/10` | `7/10` | `10/10` | `10/10` |
| `sql_injection_attempt` | `8/10` | `10/10` | `10/10` | `10/10` |
| `directory_traversal_attempt` | `10/10` | `10/10` | `10/10` | `9/10` |
| `port_scan_or_recon` | `10/10` | `9/10` | `10/10` | `10/10` |

v4.6 calibration probe per-label read:

| Expected label | Label correct | Severity correct | Suspicious correct | Evidence match |
| --- | ---: | ---: | ---: | ---: |
| `normal` | `11/15` | `14/15` | `11/15` | `15/15` |
| `failed_login_bruteforce` | `4/4` | `0/4` | `4/4` | `4/4` |
| `sql_injection_attempt` | `1/1` | `1/1` | `1/1` | `1/1` |
| `directory_traversal_attempt` | `1/1` | `1/1` | `1/1` | `1/1` |
| `port_scan_or_recon` | `4/4` | `4/4` | `4/4` | `4/4` |

Hard-contrast failure shape moved in the right direction but is not clean:

| Failure family | Count | IDs |
| --- | ---: | --- |
| `normal` -> `failed_login_bruteforce` | `3` | `v3-hard-000001`, `v3-hard-000002`, `v3-hard-000003` |
| `sql_injection_attempt` -> `failed_login_bruteforce` | `2` | `v3-hard-000021`, `v3-hard-000025` |
| Brute-force severity `medium` -> `high` | `3` | `v3-hard-000015`, `v3-hard-000016`, `v3-hard-000018` |
| Port/recon severity `medium` -> `high` | `1` | `v3-hard-000050` |
| Evidence miss on traversal | `1` | `v3-hard-000035` |

Calibration-probe failure shape is narrower:

| Failure family | Count | IDs |
| --- | ---: | --- |
| `normal` -> `failed_login_bruteforce` | `4` | `v4-6-qwen35-cal-000121`, `000122`, `000123`, `000124` |
| Brute-force severity `medium` -> `high` | `4` | `v4-6-qwen35-cal-000136`, `000137`, `000138`, `000139` |

## Interpretation

v4.6 did what the calibration pass was supposed to test: it improved severity on the hard-contrast probe and restored some normal precision without breaking JSON/schema. The hard-contrast result now reaches the overall label gate at `0.90`, and severity rises to `0.90`.

But the remaining errors matter. Normal hard negatives are still over-alerted as brute force, SQLi drops from `10/10` in v4.5 to `8/10`, and the fresh calibration probe still misses the normal gate by one sample (`11/15` vs target `12/15`). Brute-force severity also remains too aggressive on medium cases. So v4.6 is a better Qwen checkpoint than v4.5, but it is still a held calibration result, not a fixed-split candidate.

HTML summary:

```text
reports/phase-8-v4-6-qwen35-normal-severity-calibration-report.html
```

## Gate Before Fixed Split

Open fixed split only if v4.6 clears these checks on non-fixed probes:

| Gate | Target | v4.6 result | Status |
| --- | ---: | ---: | --- |
| JSON/schema | `1.0 / 1.0` | `1.0 / 1.0` | Pass |
| Invalid outputs | `0` | `0` | Pass |
| Hard-contrast label accuracy | `>= 0.90` | `0.90` | Pass |
| Hard-contrast `normal` | `>= 8/10` | `7/10` | Hold |
| Suspicious hard-contrast labels | `>= 9/10` each | SQLi `8/10`, others `10/10` | Hold |
| Severity accuracy | `>= 0.85` | hard-contrast `0.90`, calibration `0.80` | Mixed |
| Calibration probe normal accuracy | `>= 12/15` | `11/15` | Hold |
| Calibration probe suspicious recall | no class collapses | labels `10/10`, brute-force severity `0/4` | Mixed |

Decision: keep fixed split closed. v4.6 improves the Qwen path enough to justify a narrower v4.7 calibration pass, but not enough to promote this adapter.

## Non-Goals

- No fixed split run
- No taxonomy expansion
- No prompt default change
- No production detection claim
- No merge/export decision until normal false positives and brute-force severity are repaired

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
| 2026-05-23 | User/Codex | Recorded v4.6 Qwen training completion, calibration probe, hard-contrast probe, and HTML summary | `reports/phase-8-v4-6-qwen35-lora-training-result.json`, `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-normal-severity-calibration-probe.json`, `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-temp-0-hard-contrast-memorization-probe.json`, `reports/phase-8-v4-6-qwen35-normal-severity-calibration-report.html` | Trained/probed; fixed split held |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Create v4.6 as calibration, not broad repair | v4.5 already catches suspicious labels but over-alerts normal and miscalibrates severity | Add normal-heavy and severity-boundary data while preserving suspicious recall guards; keep fixed split closed |
| 2026-05-23 | Hold v4.6 before fixed split | v4.6 improves hard-contrast label/severity metrics, but normal hard negatives, SQLi `8/10`, calibration normal `11/15`, and brute-force severity still miss gates | Keep fixed split closed; next work should target normal-vs-bruteforce hard negatives and medium brute-force severity |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe]]
- [[fine-tuning-notes]]
- [[data-card]]
- [[openai-adapter-runtime-config]]

# Phase 8 V4.5 Qwen3.5 LoRA Hard-Contrast Probe

**Summary**

v4.5 เป็นรอบแรกที่ Qwen3.5 ถูกบันทึกเป็น trained LoRA adapter ของโปรเจกต์ ไม่ใช่ base-model probe แบบ v4.3/v4.4 อีกต่อไป รอบนี้ train จาก config `ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml` สำเร็จ แล้ว serve ผ่าน vLLM + LoRA alias `qwen3.6-8B-triage-v1` เพื่อรัน hard-contrast probe เดิม ผลดีขึ้นชัดเจน: JSON/schema ผ่าน `1.0`, invalid `0`, label accuracy `0.88`, evidence partial match `0.98`, SQLi/traversal/bruteforce/port-recon ได้ label ถูกครบ `10/10` ทั้งหมด แต่ `normal` เหลือ `4/10` และ severity accuracy ยัง `0.72` ดังนั้น v4.5 เป็น promising trained-Qwen result แต่ยังไม่ควรเปิด fixed split หรือสรุปว่า gate ผ่านแล้ว

**Sources**

- Qwen3.5 LoRA pilot config (source: ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml)
- Qwen3.5 LoRA training result capture (source: reports/phase-8-v4-5-qwen35-lora-training-result.json, source: reports/phase-8-v4-5-qwen35-lora-training-result.md)
- OpenAI-compatible runtime config with `max_tokens: 512`, structured outputs, and model alias `qwen3.6-8B-triage-v1` (source: config-adapter.yml)
- v4.5 hard-contrast evaluation reports (source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v1-temp-0-hard-contrast-memorization-probe.md)
- Hard-contrast probe split used for diagnostic evaluation only (source: data/generated/v3-hard-contrast-security-triage.jsonl)
- Earlier Qwen3.5 base-model hold and boundary audit for contrast (source: docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md, source: docs/output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan.md)

**Last updated**

2026-05-23

## Status

Trained and probed; held for calibration. The adapter is useful evidence that Qwen3.5 can learn the suspicious hard-contrast classes from the project data, but the current run over-alerts on normal examples and under-calibrates severity.

No fixed split run should be opened from this result alone. The next gate should first repair or measure the normal false-positive problem and severity calibration on a non-fixed diagnostic split.

## Training Snapshot

| Field | Value |
| --- | --- |
| Status | `training_complete` |
| Config | `ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml` |
| Base model | `unsloth/Qwen3.5-0.8B` |
| Loader | `fast_vision_model` |
| Train split | `data/splits/train-v4-1-sqli-boundary-repair.jsonl` |
| Validation split | `data/splits/validation-v4-1-sqli-boundary-repair.jsonl` |
| Train records | `1220` |
| Validation records | `75` |
| Output directory | `ml/unsloth/outputs/qwen3-5-0-8b-security-triage-pilot-lora-smoke` |
| LoRA rank | `16` |
| Max sequence length | `1024` |
| Train loss | `0.41032123460123937` |
| Runtime | `597.8327` seconds |
| Train throughput | `1.606` samples/sec |

## Serving And Evaluation Setup

The adapter was served through vLLM with LoRA enabled and a 1024-token model context:

```bash
vllm serve "$BASE_MODEL" \
  --host 0.0.0.0 \
  --port 8080 \
  --enable-lora \
  --lora-modules qwen3.6-8B-triage-v1="$ADAPTER_DIR" \
  --max-lora-rank "$LORA_RANK" \
  --gpu-memory-utilization 0.6 \
  --max-model-len 1024 \
  --max-num-seqs 1 \
  --language-model-only \
  --enforce-eager
```

The first failed request shape used `max_tokens: 1023`, which left almost no room for the prompt under `--max-model-len 1024`. The successful evaluation uses `max_tokens: 512` in `config-adapter.yml`. If context validation appears again, lower `max_tokens` to `384` or `256`, or serve with `--max-model-len 2048` before rerunning the same report path.

Canonical hard-contrast command:

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v1-temp-0-hard-contrast-memorization-probe.md
```

Runtime metadata recorded by the evaluator:

| Field | Value |
| --- | --- |
| Adapter | `openai-compatible` |
| Base URL | `http://192.168.8.141:8080/v1` |
| Model alias | `qwen3.6-8B-triage-v1` |
| Prompt version | `triage-json-v2.1` |
| Response format | `structured_outputs` |
| Schema path | `data/schemas/triage-output.schema.json` |
| Temperature | `0` |
| Max tokens | `512` |
| Timeout | `120` seconds |

## Hard-Contrast Result

| Metric | Value |
| --- | ---: |
| Samples | `50` |
| Label accuracy | `0.88` |
| JSON parse success | `1.0` |
| Schema success | `1.0` |
| Invalid outputs | `0` |
| Severity accuracy | `0.72` |
| Suspicious accuracy | `0.88` |
| Evidence partial match | `0.98` |
| Average latency | `5648.582491 ms` |

Per-label read:

| Expected label | Label correct | Severity correct | Suspicious correct | Evidence match |
| --- | ---: | ---: | ---: | ---: |
| `normal` | `4/10` | `4/10` | `4/10` | `10/10` |
| `failed_login_bruteforce` | `10/10` | `7/10` | `10/10` | `10/10` |
| `sql_injection_attempt` | `10/10` | `10/10` | `10/10` | `10/10` |
| `directory_traversal_attempt` | `10/10` | `10/10` | `10/10` | `9/10` |
| `port_scan_or_recon` | `10/10` | `5/10` | `10/10` | `10/10` |

Prediction distribution:

| Label | Count |
| --- | ---: |
| `normal` | `4` |
| `failed_login_bruteforce` | `13` |
| `sql_injection_attempt` | `12` |
| `directory_traversal_attempt` | `11` |
| `port_scan_or_recon` | `10` |

The main label failure is normal false positives:

| Expected | Predicted | Count |
| --- | --- | ---: |
| `normal` | `failed_login_bruteforce` | `3` |
| `normal` | `sql_injection_attempt` | `2` |
| `normal` | `directory_traversal_attempt` | `1` |

## Interpretation

v4.5 flips the Qwen3.5 story. The base model in v4.3/v4.4 mostly collapsed suspicious classes into `normal`; the trained LoRA adapter now catches every suspicious hard-contrast label in this split. That is the strongest signal so far that Qwen3.5 can learn the project’s security-log triage schema from LoRA training.

But the result is not clean enough to unlock fixed-split comparison. The model now fails in the opposite direction: it over-labels normal hard negatives as suspicious. Severity is also not calibrated enough, especially brute force predicted too high in `3/10` cases and port scan/recon predicted too low in `5/10` cases.

Decision: keep v4.5 as a promising trained-Qwen probe, but hold fixed split. The next work should be either a normal-hard-negative calibration pass or a small non-fixed calibration split that checks whether the normal false-positive rate is specific to `v3-hard` examples.

## Next Work Options

| Option | When to choose | What it checks |
| --- | --- | --- |
| Normal false-positive repair | Default next step | Whether more normal hard negatives can restore `normal >= 8/10` without losing SQLi/traversal/recon recall |
| Severity calibration probe | Before any stakeholder-facing comparison | Whether severity errors are systematic, especially brute force high and recon medium |
| Mini semantic eval, clearly marked exploratory | If normal false positives improve on a fresh diagnostic split | Whether v4.5 generalizes beyond this hard-contrast probe |
| Fixed split comparison | Only after contract stays `1.0`, normal recovers, and severity improves | Whether trained Qwen beats or complements the heuristic baseline |

Follow-up status: v4.6 completed this normal/severity calibration path. It improved hard-contrast label accuracy to `0.90` and severity to `0.90`, but fixed split remains closed because normal, SQLi, calibration-normal, and brute-force severity gates still miss (source: docs/output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan.md).

## Non-Goals

- Do not treat v4.5 as production detection.
- Do not claim compromise; this remains triage of suspicious patterns.
- Do not open `data/splits/test.jsonl` from this result alone.
- Do not merge the Qwen LoRA adapter into a default model path until normal false positives and severity calibration are measured.

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-23 | User/Codex | Captured Qwen3.5 LoRA pilot training completion and hard-contrast evaluation result | `reports/phase-8-v4-5-qwen35-lora-training-result.json`, `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json` | Trained/probed; calibration held |
| 2026-05-23 | User/Codex | Linked v4.5 follow-up to the completed v4.6 calibration result | `docs/output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan.md` | Follow-up completed; fixed split still held |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Hold v4.5 before fixed split | Hard-contrast JSON/schema is perfect and suspicious labels are strong, but normal accuracy is only `4/10` and severity accuracy is `0.72` | Run normal/severity calibration before mini semantic or fixed split comparison |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan]]
- [[output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan]]
- [[fine-tuning-notes]]
- [[openai-adapter-runtime-config]]

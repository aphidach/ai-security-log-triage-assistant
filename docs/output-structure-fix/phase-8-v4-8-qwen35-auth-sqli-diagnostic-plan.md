# Phase 8 V4.8 Qwen3.5 Auth SQLi Diagnostic Plan

**Summary**

v4.8 เริ่มเป็น diagnostic-first follow-up จาก v4.7 ไม่ใช่ training run ทันที เพราะ v4.7 hard-contrast headline ดีขึ้นเป็น label/severity `0.92` แต่ calibration probe ที่ตั้งใจซ่อมกลับตกเหลือ label accuracy `0.366667`, normal-auth `0/15`, SQLi-auth-context `1/5`, และ brute-force medium severity `0/7` (source: docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json)

รอบนี้จึงสร้าง audit report บน probe เดิมเพื่อเทียบ v4.6, v4.7, heuristic baseline และ base Qwen3.5 ก่อนสร้าง v4.8 train data ใด ๆ ผลหลังเติม comparator ครบคือ heuristic ได้ label `0.666667`, v4.6 ได้ `0.433333`, v4.7 ได้ `0.366667`, และ base Qwen3.5 ได้ `0.366667`; v4.7 ดีขึ้นจาก v4.6 ด้าน severity/suspicious แต่ label accuracy ถอยลง และทั้งสอง trained adapters ยังแพ้ heuristic ชัดใน normal-auth/SQLi-auth buckets (source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.json, source: reports/heuristic-v4-7-auth-sqli-severity-calibration-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.json)

**Sources**

- v4.7 hold decision and probe result (source: docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json)
- v4.8 diagnostic audit script and reports (source: scripts/create_v4_8_qwen35_auth_sqli_diagnostic_audit.py, source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json, source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.md, source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html)
- Comparator reports on the same non-fixed probe (source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.json, source: reports/heuristic-v4-7-auth-sqli-severity-calibration-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.json)
- v4.8 regression tests (source: tests/test_v4_8_qwen35_auth_sqli_diagnostic_audit.py)

**Last updated**

2026-05-23

## Status

Diagnostic audit created. Fixed split remains closed. No v4.8 train split, generated supplement, or LoRA config exists yet.

Artifacts:

```text
scripts/create_v4_8_qwen35_auth_sqli_diagnostic_audit.py
reports/heuristic-v4-7-auth-sqli-severity-calibration-probe.json
reports/heuristic-v4-7-auth-sqli-severity-calibration-probe.md
reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.json
reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.md
reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.json
reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.md
reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json
reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.md
reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html
tests/test_v4_8_qwen35_auth_sqli_diagnostic_audit.py
```

## Comparator Status

v4.6-on-v4.7-probe comparison is now complete with alias `qwen3.6-8B-triage-v2`; it produced label accuracy `0.433333`, severity accuracy `0.40`, JSON/schema `1.0 / 1.0`, invalid `0`, and average latency `5957.112975 ms` (source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.json, source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json).

## Diagnostic Metrics

All rows use the same non-fixed split: `data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl`.

| Comparator | Label | Severity | Suspicious | Evidence | JSON/schema | Invalid | Avg latency ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v4.6 trained adapter | `0.433333` | `0.40` | `0.533333` | `1.0` | `1.0 / 1.0` | `0` | `5957.112975` |
| v4.7 trained adapter | `0.366667` | `0.60` | `0.666667` | `1.0` | `1.0 / 1.0` | `0` | `6592.079815` |
| heuristic baseline | `0.666667` | `0.666667` | `0.666667` | `1.0` | `1.0 / 1.0` | `0` | `0.058292` |
| base Qwen3.5 | `0.366667` | `0.20` | `0.433333` | `0.70` | `0.966667 / 0.966667` | `1` | `8768.592156` |

Read: v4.7 is `-0.066666` label accuracy behind v4.6 and `-0.30` behind the local heuristic on this exact probe. Compared with v4.6, v4.7 improves severity and suspicious boolean accuracy, but it overcorrects normal-auth label behavior even further. Compared with base Qwen3.5, both trained adapters fix output/schema and evidence reliability, but both keep the wrong auth/SQLi boundary shape (source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json).

## Bucket Summary

| Bucket | Samples | v4.6 label/severity | v4.7 label/severity | Heuristic label/severity | Base label/severity | v4.8 action |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `normal_auth_negative` | `15` | `2/15 / 9/15` | `0/15 / 15/15` | `13/15 / 13/15` | `3/15 / 3/15` | Keep paired benign auth contrasts; brute force must require repeated attempts, a rate/window, or blocking evidence. |
| `sqli_auth_context` | `5` | `1/5 / 1/5` | `1/5 / 1/5` | `3/5 / 3/5` | `0/5 / 2/5` | Make SQL payload tokens in username, email, or query fields own the label over generic auth route context. |
| `bruteforce_medium_severity` | `7` | `7/7 / 0/7` | `7/7 / 0/7` | `2/7 / 2/7` | `7/7 / 0/7` | Add a medium severity contract: high requires larger volume, spread, privileged target, lockout, or confirmed blocking impact. |
| `port_recon_severity` | `2` | `2/2 / 1/2` | `2/2 / 1/2` | `1/2 / 1/2` | `1/2 / 1/2` | Keep a small severity pair for recon; do not broaden the recon taxonomy. |
| `directory_traversal_guard` | `1` | `1/1 / 1/1` | `1/1 / 1/1` | `1/1 / 1/1` | `0/1 / 0/1` | Keep as regression guard, not a main v4.8 data target. |

## V4.8 Boundary Contract

Before creating v4.8 training data, lock the data intent to four narrow rules:

- `failed_login_bruteforce` requires repeated failed attempts, count/rate/window evidence, or blocked/lockout evidence. Login/auth vocabulary alone is not enough.
- `normal` can include login, failed retry, MFA, password reset, or account-status text when there is no repeated attack signal.
- SQL payload syntax in user-controlled fields should override route context such as `/login`, `username`, `email`, or `account`.
- Severity `high` should not be the default for brute force or recon. Escalation needs volume, spread, privileged target, lockout/blocking, or other impact signal.

## Recommended Gate

Do not open mini semantic or fixed split until a future v4.8 training run clears:

| Gate | Target |
| --- | ---: |
| v4.7 calibration probe label accuracy | `>= 0.85` |
| normal-auth label correct | `>= 13/15` |
| SQLi-auth-context label correct | `>= 4/5` |
| brute-force medium severity correct | `>= 5/7` |
| hard-contrast label accuracy | `>= 0.92` |
| JSON/schema | `1.0 / 1.0` |
| invalid output count | `0` |

## Command Runbook

Regenerate the heuristic comparator:

```bash
rtk python3 scripts/evaluate.py \
  --adapter heuristic \
  --split data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl \
  --out reports/heuristic-v4-7-auth-sqli-severity-calibration-probe.json \
  --comparison-out reports/heuristic-v4-7-auth-sqli-severity-calibration-probe.md \
  --no-progress
```

Regenerate the base Qwen3.5 comparator with the currently served base alias:

```bash
rtk env OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
  OPENAI_COMPATIBLE_MODEL=unsloth/Qwen3.5-0.8B \
  .venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.md \
  --no-progress
```

Regenerate the v4.6 comparator:

```bash
rtk env OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
  OPENAI_COMPATIBLE_MODEL=qwen3.6-8B-triage-v2 \
  .venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.md \
  --no-progress
```

Regenerate the diagnostic audit:

```bash
rtk python3 scripts/create_v4_8_qwen35_auth_sqli_diagnostic_audit.py
```

## Verification

```bash
rtk python3 -m unittest tests/test_v4_8_qwen35_auth_sqli_diagnostic_audit.py
```

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-23 | Codex | Created v4.8 diagnostic audit from v4.7 calibration probe comparators | `scripts/create_v4_8_qwen35_auth_sqli_diagnostic_audit.py`, `reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json`, `reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html` | Diagnostic complete |
| 2026-05-23 | User/Codex | Added v4.6-on-v4.7 comparator to the v4.8 diagnostic audit | `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.json`, `reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json`, `reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html` | Comparator complete |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Start v4.8 as diagnostic-first, not train-first | v4.7 failed the exact calibration probe it was created to fix, and heuristic beats it by `0.30` label accuracy on the same split | Keep fixed split closed; create only audit artifacts until the v4.8 boundary contract is reviewed |
| 2026-05-23 | Treat missing v4.6 comparator as runtime availability gap | The current endpoint did not expose `qwen3.6-8B-triage-v2` | Do not infer v4.6 quality from absence; rerun comparator when alias is served |
| 2026-05-23 | Keep v4.8 diagnostic-first after v4.6 comparator completed | v4.6 beats v4.7 on label accuracy (`0.433333` vs `0.366667`) but still trails heuristic (`0.666667`) and misses normal-auth, SQLi-auth, and medium-severity targets | Do not revert to v4.6 or open fixed split; design a narrow v4.8 paired-contrast supplement |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan]]
- [[openai-adapter-runtime-config]]
- [[fine-tuning-notes]]

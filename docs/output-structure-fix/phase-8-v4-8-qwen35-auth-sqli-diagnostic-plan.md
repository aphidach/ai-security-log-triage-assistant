# Phase 8 V4.8 Qwen3.5 Auth SQLi Diagnostic Plan

**Summary**

v4.8 เริ่มเป็น diagnostic-first follow-up จาก v4.7 ไม่ใช่ training run ทันที เพราะ v4.7 hard-contrast headline ดีขึ้นเป็น label/severity `0.92` แต่ calibration probe ที่ตั้งใจซ่อมกลับตกเหลือ label accuracy `0.366667`, normal-auth `0/15`, SQLi-auth-context `1/5`, และ brute-force medium severity `0/7` (source: docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json)

รอบนี้จึงสร้าง audit report บน probe เดิมเพื่อเทียบ v4.7 adapter กับ heuristic baseline และ base Qwen3.5 ที่ serve อยู่ตอนนี้ ก่อนสร้าง v4.8 train data ใด ๆ ผลเบื้องต้นคือ heuristic ได้ label `0.666667` บน probe เดียวกัน ขณะที่ v4.7 และ base Qwen3.5 ได้ label `0.366667`; v4.7 ยังเหนือ base ด้าน severity/schema/evidence แต่แพ้ heuristic ชัดใน normal-auth และ SQLi-auth buckets (source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json, source: reports/heuristic-v4-7-auth-sqli-severity-calibration-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.json)

**Sources**

- v4.7 hold decision and probe result (source: docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json)
- v4.8 diagnostic audit script and reports (source: scripts/create_v4_8_qwen35_auth_sqli_diagnostic_audit.py, source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json, source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.md, source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html)
- Comparator reports on the same non-fixed probe (source: reports/heuristic-v4-7-auth-sqli-severity-calibration-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.json)
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
reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.json
reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-base-temp-0-v4-7-auth-sqli-severity-calibration-probe.md
reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json
reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.md
reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html
tests/test_v4_8_qwen35_auth_sqli_diagnostic_audit.py
```

## Comparator Status

v4.6-on-v4.7-probe comparison is blocked for now because the endpoint inventory exposed only `unsloth/Qwen3.5-0.8B` and `qwen3.6-8B-triage-v3`; the v4.6 alias `qwen3.6-8B-triage-v2` was not served during this run (source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json).

Do not count the missing v4.6 comparison as model quality evidence. It is a runtime availability gap. If the v4.6 alias is served later, run it on the same probe and update this page append-only.

## Diagnostic Metrics

All rows use the same non-fixed split: `data/splits/v4-7-auth-sqli-severity-calibration-probe.jsonl`.

| Comparator | Label | Severity | Suspicious | Evidence | JSON/schema | Invalid | Avg latency ms |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v4.7 trained adapter | `0.366667` | `0.60` | `0.666667` | `1.0` | `1.0 / 1.0` | `0` | `6592.079815` |
| heuristic baseline | `0.666667` | `0.666667` | `0.666667` | `1.0` | `1.0 / 1.0` | `0` | `0.058292` |
| base Qwen3.5 | `0.366667` | `0.20` | `0.433333` | `0.70` | `0.966667 / 0.966667` | `1` | `8768.592156` |

Read: v4.7 is not just weak in absolute terms; it is `-0.30` label accuracy behind the local heuristic on this exact probe. Compared with base Qwen3.5, v4.7 fixes output/schema and several severity/evidence issues, but it still keeps the wrong auth/SQLi boundary learned during calibration (source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json).

## Bucket Summary

| Bucket | Samples | v4.7 label/severity | Heuristic label/severity | Base label/severity | v4.8 action |
| --- | ---: | ---: | ---: | ---: | --- |
| `normal_auth_negative` | `15` | `0/15 / 15/15` | `13/15 / 13/15` | `3/15 / 3/15` | Keep paired benign auth contrasts; brute force must require repeated attempts, a rate/window, or blocking evidence. |
| `sqli_auth_context` | `5` | `1/5 / 1/5` | `3/5 / 3/5` | `0/5 / 2/5` | Make SQL payload tokens in username, email, or query fields own the label over generic auth route context. |
| `bruteforce_medium_severity` | `7` | `7/7 / 0/7` | `2/7 / 2/7` | `7/7 / 0/7` | Add a medium severity contract: high requires larger volume, spread, privileged target, lockout, or confirmed blocking impact. |
| `port_recon_severity` | `2` | `2/2 / 1/2` | `1/2 / 1/2` | `1/2 / 1/2` | Keep a small severity pair for recon; do not broaden the recon taxonomy. |
| `directory_traversal_guard` | `1` | `1/1 / 1/1` | `1/1 / 1/1` | `0/1 / 0/1` | Keep as regression guard, not a main v4.8 data target. |

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

Regenerate the diagnostic audit:

```bash
rtk python3 scripts/create_v4_8_qwen35_auth_sqli_diagnostic_audit.py
```

If v4.6 alias is served again, run the missing comparator:

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

## Verification

```bash
rtk python3 -m unittest tests/test_v4_8_qwen35_auth_sqli_diagnostic_audit.py
```

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-23 | Codex | Created v4.8 diagnostic audit from v4.7 calibration probe comparators | `scripts/create_v4_8_qwen35_auth_sqli_diagnostic_audit.py`, `reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json`, `reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html` | Diagnostic complete |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-23 | Start v4.8 as diagnostic-first, not train-first | v4.7 failed the exact calibration probe it was created to fix, and heuristic beats it by `0.30` label accuracy on the same split | Keep fixed split closed; create only audit artifacts until the v4.8 boundary contract is reviewed |
| 2026-05-23 | Treat missing v4.6 comparator as runtime availability gap | The current endpoint did not expose `qwen3.6-8B-triage-v2` | Do not infer v4.6 quality from absence; rerun comparator when alias is served |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan]]
- [[openai-adapter-runtime-config]]
- [[fine-tuning-notes]]

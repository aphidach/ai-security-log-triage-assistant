# Phase 3 Runtime Capability Matrix

**Summary**

Phase 3 ทดสอบ runtime/mode candidate ด้วย smoke split และ schema เดียวกัน เพื่อหาว่ามี backend ใดบังคับ output contract ได้ 5/5 โดยไม่ต้อง JSON extraction

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ runtime matrix และ pass/fail condition (source: docs/structured-output-fix-plan.md)
- `reports/README.md` สำหรับ report path convention (source: reports/README.md)
- `data/splits/smoke-output-contract.jsonl` สำหรับ smoke split (source: data/splits/smoke-output-contract.jsonl)
- `data/schemas/triage-output.schema.json` สำหรับ output schema (source: data/schemas/triage-output.schema.json)
- `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json` สำหรับ vLLM `structured_outputs` smoke result (source: reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json)

**Last updated**

2026-05-20

## Status

Passed for the vLLM `structured_outputs` candidate. Phase 2 adversarial probe hardening is still useful later, but it is no longer blocking the first contract-passing runtime.

## Candidate Runs

| Candidate | Mode | Report path | Status |
| --- | --- | --- | --- |
| Current endpoint | `responses-parse` | `reports/structured-output/smoke/openai-compatible-current-responses-parse-smoke.json` | Pending |
| Current endpoint | `json-schema` | `reports/structured-output/smoke/openai-compatible-current-json-schema-smoke.json` | Pending |
| vLLM | `structured-outputs` | `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json` | Passed output contract; semantic accuracy still low |
| SGLang | `structured-outputs` or XGrammar equivalent | `reports/structured-output/smoke/openai-compatible-sglang-structured-outputs-smoke.json` | Optional |

The report-level matrix is preserved in `reports/structured-output/runtime/structured-output-capability-matrix.md`.

## vLLM Smoke Result

The successful smoke run used:

- base URL: `http://192.168.8.141:8080/v1`
- requested model: `lfm2-security-triage`
- response model: `lfm2-security-triage`
- adapter mode: `structured_outputs`
- provider request mode: `structured_outputs_json`
- split: `data/splits/smoke-output-contract.jsonl`
- schema: `data/schemas/triage-output.schema.json`

| Metric | Value |
| --- | ---: |
| `json_parse_success_rate` | `1.0` |
| `schema_success_rate` | `1.0` |
| `invalid_output_count` | `0` |
| `label_accuracy` | `0.2` |
| `severity_accuracy` | `0.6` |
| `is_suspicious_accuracy` | `0.8` |
| `evidence_partial_match` | `0.6` |
| `average_latency_ms` | `1204.060858` |

Interpretation:

- Runtime capability is good enough to continue with vLLM `structured_outputs`.
- The model still over-predicts or confuses labels on the smoke set, especially mapping normal, SQL injection, and directory traversal examples into `failed_login_bruteforce`.
- The next active step is mini semantic eval and error grouping, not final fixed-split comparison.

## Pass Condition

มีอย่างน้อยหนึ่ง runtime/mode ที่:

- `json_parse_success_rate = 1.0`
- `schema_success_rate = 1.0`
- `invalid_output_count = 0`
- raw output ไม่มี markdown fence หรือ prose wrapper

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 3 detail stub | `docs/output-structure-fix/phase-3-runtime-capability-matrix.md` | Drafted |
| 2026-05-20 | User/Codex | Added vLLM `structured_outputs` smoke result with 5/5 JSON and schema success | `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json`, `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.md` | Passed output contract |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-2-probe-hardening]]
- [[structured-output-fix-plan]]

# Phase 3 Runtime Capability Matrix

**Summary**

Phase 3 ทดสอบ runtime/mode candidate ด้วย smoke split และ schema เดียวกัน เพื่อหาว่ามี backend ใดบังคับ output contract ได้ 5/5 โดยไม่ต้อง JSON extraction

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ runtime matrix และ pass/fail condition (source: docs/structured-output-fix-plan.md)
- `reports/README.md` สำหรับ report path convention (source: reports/README.md)
- `data/splits/smoke-output-contract.jsonl` สำหรับ smoke split (source: data/splits/smoke-output-contract.jsonl)
- `data/schemas/triage-output.schema.json` สำหรับ output schema (source: data/schemas/triage-output.schema.json)

**Last updated**

2026-05-20

## Status

Draft. เริ่มหลัง Phase 2 probe แยก adversarial case และ per-sample evidence ได้

## Candidate Runs

| Candidate | Mode | Report path | Status |
| --- | --- | --- | --- |
| Current endpoint | `responses-parse` | `reports/openai-compatible-current-responses-parse-smoke.json` | Pending |
| Current endpoint | `json-schema` | `reports/openai-compatible-current-json-schema-smoke.json` | Pending |
| vLLM | `structured-outputs` | `reports/openai-compatible-vllm-structured-outputs-smoke.json` | Pending |
| SGLang | `structured-outputs` or XGrammar equivalent | `reports/openai-compatible-sglang-structured-outputs-smoke.json` | Optional |

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

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-2-probe-hardening]]
- [[structured-output-fix-plan]]

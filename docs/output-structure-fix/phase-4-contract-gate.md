# Phase 4 Contract Gate

**Summary**

Phase 4 เป็น gate ก่อนดู semantic quality ทุกครั้ง ต้องผ่าน output contract บน smoke split ก่อนถึงจะไป mini semantic eval หรือ fixed split

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ contract gate (source: docs/structured-output-fix-plan.md)
- `data/splits/smoke-output-contract.jsonl` สำหรับ smoke split (source: data/splits/smoke-output-contract.jsonl)
- `data/schemas/triage-output.schema.json` สำหรับ schema gate (source: data/schemas/triage-output.schema.json)
- `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json` สำหรับ passing contract gate result (source: reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json)

**Last updated**

2026-05-20

## Status

Passed for `openai-compatible` + vLLM + `structured_outputs` on 2026-05-20.

## Gate

- [x] `json_parse_success_rate = 1.0`
- [x] `schema_success_rate = 1.0`
- [x] `invalid_output_count = 0`
- [x] required fields ครบทุก sample
- [x] label และ severity อยู่ใน enum ทั้งหมด
- [x] raw output ไม่มี markdown fence หรือ prose wrapper

## Passing Run

```bash
OPENAI_COMPATIBLE_BASE_URL=http://192.168.8.141:8080/v1 \
OPENAI_COMPATIBLE_API_KEY=local \
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json \
  --comparison-out reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.md
```

Result:

- `json_parse_success_rate = 1.0`
- `schema_success_rate = 1.0`
- `invalid_output_count = 0`
- `label_accuracy = 0.2`
- `severity_accuracy = 0.6`
- `evidence_partial_match = 0.6`

The gate is about output contract only. The low label accuracy means the next phase should inspect semantic failures before any fixed-split comparison.

## Failure Handling

ถ้าไม่ผ่าน ให้หยุดก่อน fixed split และแยกว่า fail จาก:

- backend ไม่ enforce schema
- schema incompatibility
- missing required field
- invalid enum
- token truncation
- model hallucinating field/value แม้ schema ถูก enforce บางส่วน

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 4 detail stub | `docs/output-structure-fix/phase-4-contract-gate.md` | Drafted |
| 2026-05-20 | User/Codex | Recorded passing vLLM `structured_outputs` contract gate | `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json`, `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.md` | Passed |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-3-runtime-capability-matrix]]
- [[structured-output-fix-plan]]

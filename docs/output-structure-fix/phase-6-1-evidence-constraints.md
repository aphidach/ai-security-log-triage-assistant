# Phase 6.1 Evidence Constraints

**Summary**

Phase 6.1 เป็นรอบแก้เฉพาะปัญหา evidence loop หลัง Phase 6 case 1 พบว่า `json_object` และ vLLM `structured_outputs` วนเติม `evidence` จนชน token cap แม้ label เริ่มต้นจะถูกทาง

**Sources**

- `docs/output-structure-fix/phase-6-v3-or-runtime-decision.md` สำหรับข้อสรุป Phase 6 case 1 และ decision ที่ให้เริ่ม Phase 6.1 (source: docs/output-structure-fix/phase-6-v3-or-runtime-decision.md)
- `data/schemas/triage-output.schema.json` สำหรับ schema ปัจจุบันที่ `evidence` ยังเป็น array/string แบบเปิดกว้าง (source: data/schemas/triage-output.schema.json)
- `scripts/model_adapters/openai_compatible.py` สำหรับ provider schema sanitizer และ OpenAI-compatible request modes (source: scripts/model_adapters/openai_compatible.py)
- `reports/openai-compatible-vllm-structured-outputs-phase6-timeout-only-timeout120.json` สำหรับผล `structured_outputs` ที่ชน `finish_reason=length` หลัง `max_tokens=1024` (source: reports/openai-compatible-vllm-structured-outputs-phase6-timeout-only-timeout120.json)
- `reports/openai-compatible-vllm-json-object-phase6-timeout-only.json` สำหรับผล `json_object` ที่วนซ้ำใน `evidence` (source: reports/openai-compatible-vllm-json-object-phase6-timeout-only.json)
- `reports/openai-compatible-vllm-off-phase6-timeout-only.json` สำหรับผล `off` mode ที่ model หยุดเองและเริ่มด้วย label `port_scan_or_recon` (source: reports/openai-compatible-vllm-off-phase6-timeout-only.json)

**Last updated**

2026-05-20

## Status

Planned. เริ่มหลัง Phase 6 case 1 แยกได้ว่า timeout เดิมคือ generation loop ใน JSON-constrained modes ไม่ใช่ prompt processing หรือ queue ค้าง

## Problem

timeout-only diagnostic ใช้ 3 samples:

- `sample-000437`
- `sample-000458`
- `sample-000485`

ผลที่ต้องจำ:

- `structured_outputs` แบบไม่มี output cap timeout เพราะ client ตัดก่อน model จบ
- เมื่อใส่ `timeout=120`, `max_retries=0`, `max_tokens=1024` แล้วไม่ timeout แต่ทั้ง 3 samples ได้ `finish_reason=length`
- raw output เริ่มถูก label เป็น `port_scan_or_recon`
- output วนเติม `evidence` เช่น `port_scan_or_recon` หรือ `blocked` ซ้ำ ๆ จนถูกตัดกลาง JSON
- `off` mode หยุดเองและเข้าใจ broad label แต่ยังไม่ผ่าน contract เพราะใช้ markdown fence และขาด required field

ข้อสรุป: ปัญหาหลักของ case นี้คือ schema/runtime constrained generation เปิดทางให้ `evidence` ยาวไม่จำกัด จึงควรแก้ schema constraint และ sanitizer ก่อนตัดสินใจ retrain v3

## Current Schema Gap

`evidence` ปัจจุบัน:

```json
{
  "description": "Concrete substrings or facts from the log that support the label.",
  "type": "array",
  "items": {
    "type": "string",
    "minLength": 1
  }
}
```

ช่องว่าง:

- ไม่มี `minItems`
- ไม่มี `maxItems`
- ไม่มี `maxLength` ต่อ evidence item
- description ยังยอมให้เป็น `facts` ทำให้ model เลือกคำทั่วไปหรือ label name แทน substring จริงได้ง่าย
- provider schema sanitizer ยังไม่ได้ preserve constraint keywords อย่าง `minItems`, `maxItems`, `minLength`, `maxLength`

## Proposed Schema Direction

ไม่เปลี่ยน field shape ของ output contract ให้ยังเป็น:

```json
"evidence": ["..."]
```

แต่เพิ่ม constraint ให้แคบลง:

```json
{
  "description": "One to three short exact substrings copied from the input log. Do not use label names or invented facts.",
  "type": "array",
  "minItems": 1,
  "maxItems": 3,
  "items": {
    "type": "string",
    "minLength": 1,
    "maxLength": 160
  }
}
```

เหตุผลของค่าตั้งต้น:

- `minItems=1` ยังบังคับให้ model ให้หลักฐานอย่างน้อยหนึ่งชิ้น
- `maxItems=3` พอกับ log triage แบบ single-line และลดโอกาส loop ใน array
- `maxLength=160` ยาวพอสำหรับ substring สำคัญ เช่น query string หรือ port list แต่สั้นพอจะกัน explanation ยาว
- wording ใหม่บังคับว่า evidence ต้องเป็น substring จาก input log ไม่ใช่ label name เช่น `port_scan_or_recon`

## Required Code Changes

1. Update canonical schema

แก้ `data/schemas/triage-output.schema.json` เฉพาะ `evidence` constraints

2. Update provider schema sanitizer

แก้ `scripts/model_adapters/openai_compatible.py` ให้ preserve JSON Schema keywords เหล่านี้:

- `minItems`
- `maxItems`
- `minLength`
- `maxLength`

ถ้าไม่แก้ sanitizer ก่อน constraint เหล่านี้อาจถูกตัดออกก่อนส่งเข้า vLLM และ diagnostic จะไม่ทดสอบสิ่งที่ตั้งใจจริง

3. Validate existing splits

ตรวจว่า source dataset/splits ยังผ่าน constraint ใหม่:

```bash
rtk .venv/bin/python - <<'PY'
import json
from pathlib import Path

paths = [
    Path("data/splits/train.jsonl"),
    Path("data/splits/validation.jsonl"),
    Path("data/splits/smoke-output-contract.jsonl"),
    Path("data/splits/mini-semantic-eval.jsonl"),
    Path("data/splits/phase6-timeout-only.jsonl"),
]

for path in paths:
    if not path.exists():
        continue
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        item = json.loads(line)
        evidence = item["output"]["evidence"]
        if not 1 <= len(evidence) <= 3:
            raise SystemExit(f"{path}:{line_no}: evidence item count={len(evidence)}")
        for value in evidence:
            if not isinstance(value, str) or not value or len(value) > 160:
                raise SystemExit(f"{path}:{line_no}: invalid evidence item={value!r}")
print("evidence constraints preflight passed")
PY
```

## Diagnostic Rerun Plan

หลังแก้ schema และ sanitizer ให้รันตามลำดับนี้:

1. Phase 6 timeout-only split with vLLM `structured_outputs`

```bash
OPENAI_COMPATIBLE_BASE_URL=http://192.168.8.141:8080/v1 \
OPENAI_COMPATIBLE_API_KEY=local \
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TIMEOUT_SECONDS=120 \
OPENAI_COMPATIBLE_MAX_RETRIES=0 \
OPENAI_COMPATIBLE_MAX_TOKENS=512 \
rtk .venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/phase6-timeout-only.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-phase6-1-evidence-constraints.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-phase6-1-evidence-constraints.md
```

2. Smoke contract rerun

ถ้า timeout-only split ไม่ loop แล้ว ให้ rerun smoke split ก่อน mini eval:

```bash
OPENAI_COMPATIBLE_BASE_URL=http://192.168.8.141:8080/v1 \
OPENAI_COMPATIBLE_API_KEY=local \
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TIMEOUT_SECONDS=120 \
OPENAI_COMPATIBLE_MAX_RETRIES=0 \
OPENAI_COMPATIBLE_MAX_TOKENS=512 \
rtk .venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-phase6-1-smoke.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-phase6-1-smoke.md
```

3. Mini semantic eval rerun

รันเฉพาะเมื่อ smoke contract ผ่าน JSON/schema ครบ:

```bash
OPENAI_COMPATIBLE_BASE_URL=http://192.168.8.141:8080/v1 \
OPENAI_COMPATIBLE_API_KEY=local \
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TIMEOUT_SECONDS=120 \
OPENAI_COMPATIBLE_MAX_RETRIES=0 \
OPENAI_COMPATIBLE_MAX_TOKENS=512 \
rtk .venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/mini-semantic-eval.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-phase6-1-mini-semantic-eval.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-phase6-1-mini-semantic-eval.md
```

## Pass Criteria

Phase 6.1 ผ่านเมื่อ timeout-only split มีผลดังนี้:

- `json_parse_success_rate = 1.0`
- `schema_success_rate = 1.0`
- no `finish_reason=length`
- no repeated evidence loop pattern
- predicted `evidence` ทุกชิ้นเป็น substring ที่มีความหมายจาก input log

หลังจากนั้น smoke split ต้องกลับมาผ่าน output contract ก่อนจึงค่อย rerun mini semantic eval

## Fail Interpretation

ถ้ายัง loop หลังเพิ่ม evidence constraints:

- ลองลด `maxItems` เหลือ `2` และ `maxLength` เหลือ `80`
- ตรวจ stop/EOS และ chat template
- ทดลอง `guided_json` หรือ backend structured-output mode อื่น
- ตรวจ rendered training examples ว่า assistant JSON มี EOS/EOT หลังปิด object หรือไม่
- อย่าเพิ่ม timeout เป็นทางแก้หลัก เพราะจะซ่อน loop และทำให้ latency metric แย่ลง

ถ้า output contract ผ่านแต่ label/severity/evidence semantics ยังผิด:

- กลับไป Phase 6 path สำหรับ v3 training data และ hard cases
- อย่าใช้ fixed `data/splits/test.jsonl` เพื่อ tune schema/prompt

## Checklist

- [ ] Update `data/schemas/triage-output.schema.json` evidence constraints
- [ ] Update `PROVIDER_SCHEMA_ALLOWED_KEYS` in `scripts/model_adapters/openai_compatible.py`
- [ ] Run evidence constraint preflight on existing splits
- [ ] Run timeout-only diagnostic report
- [ ] Confirm `finish_reason` is not `length`
- [ ] Confirm raw evidence no longer loops
- [ ] Rerun smoke contract
- [ ] Rerun mini semantic eval only after smoke passes
- [ ] Record result back in Phase 6 and this page

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 6.1 evidence constraints plan | `docs/output-structure-fix/phase-6-v3-or-runtime-decision.md`, `data/schemas/triage-output.schema.json`, `scripts/model_adapters/openai_compatible.py` | Planned |

## Decision Log

| Date | Decision | Rationale | Consequence |
| --- | --- | --- | --- |
| 2026-05-20 | Tighten `evidence` before retraining v3 | Phase 6 case 1 shows JSON-constrained modes loop inside unbounded `evidence`, while `off` mode can stop and identify port scan | Next work should narrow schema and sanitizer behavior, then rerun timeout-only and smoke diagnostics |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[output-structure-fix/phase-5-mini-semantic-eval]]
- [[model-repetition-loop-diagnostics]]
- [[structured-output-fix-plan]]

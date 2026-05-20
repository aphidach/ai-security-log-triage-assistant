# Phase 5 Mini Semantic Eval

**Summary**

Phase 5 วัด semantic quality เฉพาะหลัง output contract ผ่านแล้ว จุดประสงค์คือดู error profile ก่อนแตะ fixed test split

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ mini semantic eval checklist (source: docs/structured-output-fix-plan.md)
- `docs/evaluation-metrics-rationale.md` สำหรับ metric rationale (source: docs/evaluation-metrics-rationale.md)
- `data/splits/test.jsonl` สำหรับ fixed split ที่ยังห้ามใช้ใน phase นี้ (source: data/splits/test.jsonl)
- `data/splits/mini-semantic-eval.jsonl` สำหรับ validation-derived mini split ของ Phase 5 (source: data/splits/mini-semantic-eval.jsonl)
- `scripts/create_mini_semantic_eval_split.py` สำหรับสร้าง mini split ซ้ำแบบ deterministic (source: scripts/create_mini_semantic_eval_split.py)
- `scripts/run_phase5_mini_semantic_eval.sh` สำหรับรัน Phase 5 eval ด้วย vLLM `structured_outputs` (source: scripts/run_phase5_mini_semantic_eval.sh)
- `reports/openai-compatible-vllm-structured-outputs-smoke.json` สำหรับ starting semantic error signals หลัง contract ผ่าน (source: reports/openai-compatible-vllm-structured-outputs-smoke.json)
- `reports/openai-compatible-vllm-structured-outputs-mini-semantic-eval.json` สำหรับ Phase 5 mini semantic eval result (source: reports/openai-compatible-vllm-structured-outputs-mini-semantic-eval.json)

**Last updated**

2026-05-20

## Status

Run complete. Phase 5 found that vLLM `structured_outputs` still needs follow-up before fixed-split comparison: mini eval JSON/schema success is `0.88` because 3 port-scan samples timed out, and semantic predictions over-concentrate on `failed_login_bruteforce`.

## Thai Summary

Phase 5 คือรอบ mini semantic eval เพื่อดูว่า หลังจาก vLLM บังคับ structured output ได้แล้ว โมเดลเข้าใจ log ถูกไหม ก่อนเอาไปวัดกับ fixed `test.jsonl`.

สิ่งที่ทำแล้ว:

- สร้าง `data/splits/mini-semantic-eval.jsonl` จำนวน 25 samples จาก validation split
- balance ครบ 5 labels label ละ 5 ตัวอย่าง
- ตรวจแล้วว่าไม่ overlap กับ `data/splits/test.jsonl`
- ตรวจแล้วว่าไม่ overlap กับ `data/splits/smoke-output-contract.jsonl`
- เพิ่มสคริปต์ `scripts/create_mini_semantic_eval_split.py`
- เพิ่มสคริปต์ `scripts/run_phase5_mini_semantic_eval.sh`
- รัน vLLM `structured_outputs` แล้ว
- อัปเดตเอกสาร Phase 5 พร้อม report path แล้ว

ผลรันหลัก:

- `label_accuracy = 0.24`
- `json_parse_success_rate = 0.88`
- `schema_success_rate = 0.88`
- `severity_accuracy = 0.68`
- `is_suspicious_accuracy = 0.68`
- `evidence_partial_match = 0.8`
- `invalid_output_count = 3`
- `average_latency_ms = 8337.805605`

ข้อค้นพบสำคัญ:

- JSON/schema ไม่ได้ค้างที่ `1.0` บน mini set เพราะ `port_scan_or_recon` timeout 3 ตัว
- timeout เป็น `APITimeoutError` ไม่ใช่ markdown fence หรือ malformed JSON
- โมเดลทาย `failed_login_bruteforce` มากเกินไปมาก: 20 จาก 25 predictions
- `sql_injection_attempt` ทั้ง 5 ตัวถูกทายเป็น `failed_login_bruteforce`
- `normal` 5 ตัวถูก escalate เป็น `high` ทั้งหมด
- evidence ที่ schema-valid ยังเป็น substring จาก log แต่บางตัวเลือก evidence แปลกหรือไม่ตรงจุดพอ

สรุปตัดสินใจ: ยังไม่ควรไป Phase 7 หรือ fixed `test.jsonl` ตอนนี้ควรเข้า Phase 6 เพื่อแยกว่า error มาจาก runtime timeout, training data/format, schema wording หรือ model capacity.

## Required Work

- [x] สร้าง mini eval split 20-25 samples ที่ไม่ใช่ `data/splits/test.jsonl`
- [x] รัน evaluator ด้วย runtime/mode ที่ผ่าน contract gate
- [x] ตรวจ confusion ราย label
- [x] ตรวจ severity drift
- [x] ตรวจ evidence ว่าเป็น substring จาก log
- [x] บันทึก latency และ timeout signal

## Scripts And Run Command

สร้าง mini split อย่างเดียว:

```bash
python3 scripts/create_mini_semantic_eval_split.py \
  --source data/splits/validation.jsonl \
  --out data/splits/mini-semantic-eval.jsonl \
  --per-label 5 \
  --exclude data/splits/test.jsonl \
  --exclude data/splits/smoke-output-contract.jsonl \
  --force
```

รัน Phase 5 ด้วย vLLM endpoint:

```bash
scripts/run_phase5_mini_semantic_eval.sh
```

ค่า default ใน runner:

- `OPENAI_COMPATIBLE_BASE_URL=http://192.168.8.141:8080/v1`
- `OPENAI_COMPATIBLE_API_KEY=local`
- `OPENAI_COMPATIBLE_MODEL=lfm2-security-triage`
- `OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs`
- `OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json`

ผลลัพธ์ถูกเขียนไปที่:

- `reports/openai-compatible-vllm-structured-outputs-mini-semantic-eval.json`
- `reports/openai-compatible-vllm-structured-outputs-mini-semantic-eval.md`

## Phase 5 Run Result

Run date: `2026-05-20`

Split:

- `data/splits/mini-semantic-eval.jsonl`
- 25 samples
- 5 samples per label
- no overlap with `data/splits/test.jsonl`
- no overlap with `data/splits/smoke-output-contract.jsonl`

Metrics:

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.24` |
| `json_parse_success_rate` | `0.88` |
| `schema_success_rate` | `0.88` |
| `severity_accuracy` | `0.68` |
| `is_suspicious_accuracy` | `0.68` |
| `evidence_partial_match` | `0.8` |
| `average_latency_ms` | `8337.805605` |
| `invalid_output_count` | `3` |

Important interpretation:

- Output contract did not remain at `1.0` on the mini split because 3 `port_scan_or_recon` samples timed out.
- The invalid outputs were timeouts, not markdown fences or malformed JSON.
- The model strongly over-predicts `failed_login_bruteforce`: predicted distribution is `failed_login_bruteforce=20`, `directory_traversal_attempt=1`, `sql_injection_attempt=1`, `<invalid>=3`.
- Correct labels came mostly from brute-force samples: all 5 `failed_login_bruteforce` samples were classified correctly, plus 1 directory traversal sample.
- All schema-valid predicted evidence strings were substrings of the source log, but semantic evidence quality still varies; `sample-000169` got the right brute-force label while choosing awkward evidence tokens such as `sshd[...]`.

Confusion summary:

| Expected | Predicted | Count |
| --- | --- | ---: |
| `directory_traversal_attempt` | `directory_traversal_attempt` | 1 |
| `directory_traversal_attempt` | `failed_login_bruteforce` | 4 |
| `failed_login_bruteforce` | `failed_login_bruteforce` | 5 |
| `normal` | `failed_login_bruteforce` | 4 |
| `normal` | `sql_injection_attempt` | 1 |
| `port_scan_or_recon` | `<invalid>` | 3 |
| `port_scan_or_recon` | `failed_login_bruteforce` | 2 |
| `sql_injection_attempt` | `failed_login_bruteforce` | 5 |

Timeout samples:

| Sample | Expected label | Latency ms | Error |
| --- | --- | ---: | --- |
| `sample-000437` | `port_scan_or_recon` | `60568.36425` | `APITimeoutError` |
| `sample-000458` | `port_scan_or_recon` | `60619.834583` | `APITimeoutError` |
| `sample-000485` | `port_scan_or_recon` | `60483.574292` | `APITimeoutError` |

Severity drift:

- All 5 `normal` samples were escalated from expected `low` to predicted `high`.
- Suspicious-class severity mostly stayed `high`, so the main severity issue is false escalation of normal traffic.

## Starting Evidence

The 5-sample smoke contract run already gives a small semantic warning:

- `label_accuracy = 0.2`
- `severity_accuracy = 0.6`
- `is_suspicious_accuracy = 0.8`
- `evidence_partial_match = 0.6`
- predicted labels over-concentrated on `failed_login_bruteforce`
- some evidence values are not clean substrings from the input log, such as invented log-file names

This is not enough to decide retraining by itself, but it is enough to justify a 20-25 sample mini semantic eval before touching `data/splits/test.jsonl`.

## Pass Condition

- output contract ยังผ่าน `1.0`
- semantic errors ถูกจัดกลุ่มได้พอจะตัดสินใจว่าแก้ dataset, schema wording, training format, runtime หรือ model capacity

Current result: failed first bullet, passed second bullet. Do not move to `data/splits/test.jsonl` yet.

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 5 detail stub | `docs/output-structure-fix/phase-5-mini-semantic-eval.md` | Drafted |
| 2026-05-20 | Codex | Marked Phase 5 ready after vLLM passed the contract gate and smoke exposed semantic drift | `reports/openai-compatible-vllm-structured-outputs-smoke.json` | Ready |
| 2026-05-20 | Codex | Created deterministic mini semantic eval split from validation data | `data/splits/mini-semantic-eval.jsonl` | 25 samples, 5 per label, no overlap with fixed test split or smoke split |
| 2026-05-20 | Codex | Added reusable Phase 5 scripts and ran vLLM mini semantic eval | `scripts/create_mini_semantic_eval_split.py`, `scripts/run_phase5_mini_semantic_eval.sh`, `reports/openai-compatible-vllm-structured-outputs-mini-semantic-eval.json` | JSON/schema `0.88`, label accuracy `0.24`, 3 timeout invalid outputs |
| 2026-05-20 | Codex | Added Thai quick summary for Phase 5 result and next decision | `docs/output-structure-fix/phase-5-mini-semantic-eval.md` | Summarizes mini split, metrics, timeout finding, over-prediction pattern, and decision not to move to fixed test split |

## Decision Log

| Date | Decision | Rationale | Consequence |
| --- | --- | --- | --- |
| 2026-05-20 | Do not run fixed `test.jsonl` comparison yet | Phase 5 mini eval did not preserve output contract at `1.0` and semantic predictions are concentrated on `failed_login_bruteforce` | Next work should diagnose port-scan timeout behavior and decide whether Phase 6 needs dataset/training-format changes, runtime settings, or model-capacity comparison |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-4-contract-gate]]
- [[structured-output-fix-plan]]

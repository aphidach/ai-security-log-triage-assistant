# Phase 5 Mini Semantic Eval

**Summary**

Phase 5 วัด semantic quality เฉพาะหลัง output contract ผ่านแล้ว จุดประสงค์คือดู error profile ก่อนแตะ fixed test split

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ mini semantic eval checklist (source: docs/structured-output-fix-plan.md)
- `docs/evaluation-metrics-rationale.md` สำหรับ metric rationale (source: docs/evaluation-metrics-rationale.md)
- `data/splits/test.jsonl` สำหรับ fixed split ที่ยังห้ามใช้ใน phase นี้ (source: data/splits/test.jsonl)
- `reports/openai-compatible-vllm-structured-outputs-smoke.json` สำหรับ starting semantic error signals หลัง contract ผ่าน (source: reports/openai-compatible-vllm-structured-outputs-smoke.json)

**Last updated**

2026-05-20

## Status

Ready. Phase 4 has passed for vLLM `structured_outputs`; the smoke result shows semantic errors that need grouping before fixed-split comparison.

## Required Work

- สร้าง mini eval split 20-25 samples ที่ไม่ใช่ `data/splits/test.jsonl`
- รัน evaluator ด้วย runtime/mode ที่ผ่าน contract gate
- ตรวจ confusion ราย label
- ตรวจ severity drift
- ตรวจ evidence ว่าเป็น substring จาก log
- บันทึก latency และ retry count ถ้ามี retry loop

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

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 5 detail stub | `docs/output-structure-fix/phase-5-mini-semantic-eval.md` | Drafted |
| 2026-05-20 | Codex | Marked Phase 5 ready after vLLM passed the contract gate and smoke exposed semantic drift | `reports/openai-compatible-vllm-structured-outputs-smoke.json` | Ready |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-4-contract-gate]]
- [[structured-output-fix-plan]]

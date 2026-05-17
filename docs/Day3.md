# Day 3: Heuristic Baseline And Evaluation Harness

**Summary**

วันที่สามทำ baseline ที่รันได้โดยไม่ต้องใช้ model key หรือ GPU แล้วสร้าง evaluator สำหรับวัดผลจาก fixed test split เป้าหมายคือให้ POC มีตัวเลขก่อน fine-tune ไม่ใช่มีแค่ demo ที่ตอบดูดี

**Sources**

- `docs/poc-plan.md` สำหรับ baseline plan และ evaluation metrics (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ evaluation rules และ schema stability (source: AGENTS.md)
- `docs/References.md` สำหรับแนวคิดจาก lm-evaluation-harness และ SigmaHQ (source: docs/References.md)
- `llm-wiki/SKILL.md` สำหรับ append-only log และ related pages (source: SKILL.md)

**Last updated**

2026-05-17

## Goal

มี heuristic baseline และ evaluation runner ที่รันซ้ำได้จาก command เดียว พร้อม report ที่อ่านได้ทั้งคนและเครื่อง

## Scope

- เขียน `scripts/baseline_heuristic.py`
- เขียน `scripts/evaluate.py`
- เขียน metric helpers ฝั่ง Python สำหรับ evaluation รอบแรก
- ใช้ schema validation จาก `data/schemas/triage-output.schema.json`
- ถ้าต้องโชว์ใน UI ค่อย mirror heuristic บางส่วนไปที่ `frontend/lib/` ภายหลัง
- export `reports/baseline-eval.json`
- export `reports/comparison.md` เวอร์ชันเริ่มต้น

## Checklist

- [x] เพิ่ม heuristic rule สำหรับ SQL injection
- [x] เพิ่ม heuristic rule สำหรับ directory traversal
- [x] เพิ่ม heuristic rule สำหรับ brute force
- [x] เพิ่ม heuristic rule สำหรับ port scan/recon
- [x] เพิ่ม fallback เป็น `normal`
- [x] วัด `label_accuracy`
- [x] วัด `json_parse_success_rate`
- [x] วัด `schema_success_rate`
- [x] วัด `severity_accuracy`
- [x] วัด `evidence_partial_match`
- [x] วัด `average_latency_ms`
- [x] วัด `invalid_output_count`
- [x] เขียน baseline report

## Acceptance Criteria

- `python3 scripts/evaluate.py --adapter heuristic --split data/splits/test.jsonl` หรือ command เทียบเท่ารันได้
- evaluator ใช้ `data/splits/test.jsonl` เท่านั้น
- report บอกจำนวน sample และ metric หลักครบ
- heuristic baseline คืน output schema เดียวกับ model adapter
- failure case ถูกนับ ไม่ถูกซ่อน

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 3 plan page | `docs/Day3.md` | Planned |
| 2026-05-16 | Codex | Switched baseline and evaluator plan to Python-first | `scripts/baseline_heuristic.py`, `scripts/evaluate.py` | Planned |
| 2026-05-17 | Codex | Added Python heuristic baseline module and CLI | `scripts/baseline_heuristic.py` | Done |
| 2026-05-17 | Codex | Added evaluator, baseline JSON report, and markdown comparison report | `scripts/evaluate.py`, `reports/baseline-eval.json`, `reports/comparison.md` | Done |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | heuristic baseline เป็น mandatory floor | ถ้า model ไม่ชนะ rule ง่าย ๆ ต้องรู้ตั้งแต่แรก | ทำให้ comparison หลัง fine-tune มีความหมาย |
| 2026-05-16 | evaluator ไม่ผูกกับ model implementation | ต้องรองรับ heuristic, base model และ fine-tuned model เหมือนกัน | adapter ทุกตัวต้องคืน schema เดียวกัน |
| 2026-05-16 | ใช้ Python เป็น evaluator หลัก | dataset, metric, report และ fine-tuning path อยู่ใน Python ecosystem เดียวกัน | frontend เป็น demo layer; evaluation result มาจาก `scripts/` และ `reports/` |
| 2026-05-17 | baseline เปิดทั้ง `analyze_log()` และ CLI | evaluator รอบต่อไป import logic เดียวกันได้ ส่วน CLI ใช้ตรวจด้วยมือได้เร็ว | `scripts/evaluate.py` สามารถเรียก baseline โดยไม่ต้อง spawn process |
| 2026-05-17 | report JSON เก็บ per-sample result | ต้อง debug ย้อนหลังได้ว่าแต่ละ record parse ผ่านไหม schema ผ่านไหม และ evidence match หรือไม่ | `reports/baseline-eval.json` มี `samples` และ `failures` ควบคู่กับ metric summary |

## Notes

baseline ที่ดีไม่จำเป็นต้องซับซ้อน แต่ต้องซื่อสัตย์ ถ้า rule-based จับ pattern ได้ดีมาก นั่นไม่ใช่ปัญหา มันช่วยบอกว่า fine-tune ควรชนะในเคสที่ ambiguous, noisy หรืออธิบาย evidence ได้ดีกว่า

## Related pages

- [[Day2]]
- [[Day4]]
- [[poc-plan]]
- [[References]]

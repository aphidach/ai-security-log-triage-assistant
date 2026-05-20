# Phase 7 Fixed Split Comparison

**Summary**

Phase 7 เป็นรอบสุดท้ายสำหรับ fixed test split comparison หลัง output contract ผ่านและ mini semantic eval มี error profile ที่เข้าใจได้แล้ว

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ Phase 7 prerequisites (source: docs/structured-output-fix-plan.md)
- `data/splits/test.jsonl` สำหรับ fixed holdout split (source: data/splits/test.jsonl)
- `reports/frozen-splits.sha256` สำหรับ checksum ของ fixed split (source: reports/frozen-splits.sha256)
- `reports/README.md` สำหรับ fixed split report path (source: reports/README.md)

**Last updated**

2026-05-20

## Status

Draft. ห้ามเริ่มจนกว่า Phase 4 และ Phase 5 จะผ่าน prerequisites

## Prerequisites

- [ ] Smoke contract ผ่าน 5/5
- [ ] Mini semantic eval มี error profile ที่เข้าใจได้
- [ ] ไม่มีการใช้ `data/splits/test.jsonl` ใน prompt/runtime tuning
- [ ] report path แยกชัดเจน

## Run Pattern

```bash
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/test.jsonl \
  --out reports/finetuned-eval.json \
  --comparison-out reports/comparison.md
```

## Pass Condition

- report บอกตรง ๆ ว่า fine-tuned model ชนะหรือแพ้ heuristic baseline ตรงไหน
- มีตัวอย่าง error 3-5 เคส
- ไม่มี overclaim ว่า model ยืนยัน compromise ได้

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 7 detail stub | `docs/output-structure-fix/phase-7-fixed-split-comparison.md` | Drafted |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[structured-output-fix-plan]]

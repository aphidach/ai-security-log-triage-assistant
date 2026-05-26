# Day 7: Demo UI, README, And Handoff

**Summary**

วันที่เจ็ดทำ demo ให้คนอื่นลองได้และจัดเอกสารส่งมอบให้ครบ เป้าหมายคือมี UI หรือ CLI ที่เล่า POC ได้ภายในไม่กี่นาที พร้อม README, report และ demo script ที่ไม่พูดเกินกว่าผล evaluation

**Sources**

- `docs/poc-plan.md` สำหรับ demo plan, definition of done และ timeline (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ UI guidance และ security/privacy rules (source: AGENTS.md)
- `docs/References.md` สำหรับ reference mapping ที่ใช้เล่า rationale ของ repo (source: docs/References.md)
- `frontend/app/page.tsx` สำหรับ Day 7 demo UI ที่ implement แล้ว (source: frontend/app/page.tsx)
- `frontend/app/api/triage/route.ts` สำหรับ server-side analyzer endpoint และ safe public model config metadata (source: frontend/app/api/triage/route.ts)
- `frontend/lib/demo-data.ts` สำหรับ sample logs และ comparison artifact snapshots (source: frontend/lib/demo-data.ts)
- `docs/demo-script.md` สำหรับ talk track ส่งมอบ demo (source: docs/demo-script.md)
- `reports/comparison.md` และ `reports/phase-7-fixed-split-summary.html` สำหรับ Phase 7 fixed split result หลังเปิด fixed split evaluation gate (source: reports/comparison.md, source: reports/phase-7-fixed-split-summary.html)
- `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json` สำหรับ latest fine-tuned v4.7 hard-contrast metric snapshot (source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json)
- `reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json` สำหรับ v4.8 diagnostic comparator หลัง v4.7 hold (source: reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json)
- `llm-wiki/SKILL.md` สำหรับ page shape, related pages และ append-only log (source: SKILL.md)

**Last updated**

2026-05-26

## Goal

ทำให้ POC พร้อม demo: paste log, analyze, เห็น evidence, เห็น structured result และดู comparison baseline vs fine-tuned ได้

## Scope

- ทำหน้า UI หลักสำหรับ paste log
- เพิ่ม sample log picker
- เพิ่ม analyzer selector
- แสดง structured result
- highlight evidence ใน log
- แสดง comparison metric
- update README ให้ครบ setup, dataset, evaluate, train, demo
- เขียน demo script สั้นสำหรับอัดวิดีโอ 2-3 นาที

## Checklist

- [x] สร้างหน้า analyze log
- [x] เพิ่ม sample logs ครบ 5 labels
- [x] เพิ่ม selector สำหรับ heuristic, base model, fine-tuned model
- [x] แสดง label, severity, evidence, reason, recommended action
- [x] แสดง raw JSON output
- [x] เพิ่ม comparison panel
- [x] update README
- [x] เพิ่ม demo script
- [x] run lint/typecheck/build
- [x] ตรวจว่า UI ไม่ fake fine-tuned result ถ้ายังไม่ได้ configure model

## Current Status

Day 7 demo UI พร้อมใช้งานบน `frontend/app/page.tsx`: หน้าแรกเป็น triage tool สำหรับ paste log, เลือก sample ครบ 5 labels, เลือก analyzer, แสดง structured result, highlight evidence ใน input log, แสดง raw JSON และมี comparison panel จาก artifact ปัจจุบัน (source: frontend/app/page.tsx, source: frontend/lib/demo-data.ts)

ตัว analyzer ที่รันได้ใน UI คือ heuristic baseline ฝั่ง TypeScript ซึ่ง mirror logic หลักจาก Python baseline และ validate output ด้วย `frontend/lib/triage-schema.ts`; ส่วน `Base model` และ `Fine-tuned` เรียกผ่าน `/api/triage` ด้วย server-side env config และจะแสดงสถานะ unconfigured โดยไม่สร้างผลลัพธ์ปลอมเมื่อ config ยังไม่ครบ (source: frontend/lib/heuristic-baseline.ts, source: frontend/app/api/triage/route.ts, source: frontend/lib/triage-schema.ts)

comparison panel ตอนนี้ใช้ v4.7 เป็น latest fine-tuned model snapshot: heuristic baseline ยังอ้าง Phase 7 fixed split จาก `reports/phase-7-heuristic-fixed-split-eval.json`, ส่วน Qwen3.5 v4.7 อ้าง hard-contrast probe ที่ได้ label/severity `0.92`, JSON/schema `1.0`, invalid `0`, แต่ยัง held เพราะ v4.7 calibration probe เหลือ label `0.366667`; card สุดท้ายอ่านชื่อ base model จาก `OPENAI_COMPATIBLE_MODEL` และ fine-tuned model จาก `OPENAI_FINETUNE_MODEL` ผ่าน `/api/triage` แบบไม่เปิดเผย API key หรือ base URL (source: frontend/lib/demo-data.ts, source: frontend/app/page.tsx, source: frontend/app/api/triage/route.ts, source: reports/phase-7-heuristic-fixed-split-eval.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json, source: reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json)

เพิ่ม `docs/demo-script.md` เป็น talk track 2-3 นาทีสำหรับ demo โดยย้ำว่า POC นี้ triage suspicious patterns และแนะนำ investigation เท่านั้น ไม่ใช่ระบบยืนยัน compromise (source: docs/demo-script.md, source: AGENTS.md)

หลังจากนั้น Phase 7 เปิด fixed `data/splits/test.jsonl` เป็น as-is evaluation gate แล้ว: heuristic baseline ได้ label accuracy `1.0`, v3.5 temp 0.3 2048 ได้ label accuracy `0.84`, JSON/schema `1.0 / 1.0`, invalid output `0` และ final decision คือ `hold` ไม่ใช่ promotion (source: reports/comparison.md, source: reports/phase-7-fixed-split-summary.html)

## Acceptance Criteria

- dev server รันได้
- sample log วิเคราะห์ได้อย่างน้อยด้วย heuristic baseline
- UI แสดงสถานะชัดเจนถ้า model adapter ยังไม่ได้ configure
- README อธิบาย workflow ทั้งหมดตั้งแต่ dataset ถึง evaluation
- demo script เล่าได้ว่า POC นี้วัดผลอย่างไร ไม่ใช่แค่โชว์ AI ตอบ log

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 7 plan page | `docs/Day7.md` | Planned |
| 2026-05-22 | Codex | Implemented Day 7 heuristic demo UI, README update, and demo script | `frontend/app/page.tsx`, `frontend/lib/heuristic-baseline.ts`, `frontend/lib/demo-data.ts`, `README.md`, `docs/demo-script.md` | Ready |
| 2026-05-22 | Codex | Linked Day 7 handoff to Phase 7 fixed split results | `reports/comparison.md`, `reports/phase-7-fixed-split-summary.html`, `docs/output-structure-fix/phase-7-fixed-split-comparison.md` | Phase 7 decision `hold` |
| 2026-05-26 | Codex | Updated demo comparison artifacts to show Qwen3.5 v4.7 as the latest fine-tuned model and v4.8 as diagnostic-only | `frontend/lib/demo-data.ts`, `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json`, `reports/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json` | Updated |
| 2026-05-26 | Codex | Updated the final comparison card to show configured base and fine-tuned model names from server-side env metadata | `frontend/app/page.tsx`, `frontend/app/api/triage/route.ts`, `frontend/lib/demo-data.ts` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | demo เป็น tool ไม่ใช่ landing page | stakeholder ต้องเห็น workflow วิเคราะห์ log จริง | UI โฟกัสที่ paste log, result และ comparison |
| 2026-05-16 | ไม่ fake fine-tuned result | ความน่าเชื่อถือของ POC อยู่ที่การวัดผลจริง | UI ต้องแสดง unconfigured state เมื่อยังไม่มี model |
| 2026-05-22 | Day 7 UI ใช้ heuristic baseline เป็น analyzer ที่ runnable ก่อน | fixed split comparison ยัง held หลัง Phase 6 และ live model endpoint ยังไม่ได้ wire เข้าหน้า UI | UI demo ได้โดยไม่ใช้ model key และไม่ปน exploratory v3.5 probe กับ final comparison |
| 2026-05-22 | Keep v3.5 as held after Phase 7 | Fixed split evaluation shows v3.5 has stable JSON/schema but lower label accuracy than the heuristic baseline | Demo narrative should present v3.5 as measured triage behavior, not as promoted model |
| 2026-05-26 | Use v4.7 as latest fine-tuned demo artifact | v4.8 is diagnostic-first and created no training artifact, while v4.7 is the latest trained Qwen3.5 checkpoint snapshot | UI comparison names v4.7 as latest fine-tuned and keeps v4.8 separate as diagnostic audit |
| 2026-05-26 | Expose only safe model config metadata to the browser | The UI needs to show which base and fine-tuned model names are configured, but secrets and endpoint URLs must stay server-side | `/api/triage` GET returns model env names, model values, and configured booleans only |

## Notes

วันสุดท้ายต้องทำให้เรื่องเล่าง่าย: เราสร้าง dataset, วัด baseline, fine-tune small model, evaluate ด้วย test split เดียวกัน แล้วโชว์ผลผ่าน demo ที่ตรวจ evidence ได้

## Related pages

- [[Day6]]
- [[poc-plan]]
- [[References]]
- [[demo-script]]
- [[output-structure-fix/phase-7-fixed-split-comparison]]
- [[output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan]]
- [[output-structure-fix/phase-8-v4-8-qwen35-auth-sqli-diagnostic-plan]]

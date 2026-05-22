# Demo Script

**Summary**

สคริปต์สั้นสำหรับ demo POC ภายใน 2-3 นาทีหลัง Phase 6 ปิดแล้ว โดยโชว์ Day 7 UI, heuristic baseline, evidence highlight และสถานะ fixed split ที่ยังไม่ถูกเปิด

**Sources**

- `docs/Day7.md` สำหรับ scope demo UI และ acceptance criteria (source: docs/Day7.md)
- `frontend/app/page.tsx` สำหรับหน้าจอ demo, analyzer selector, result view และ unconfigured model state (source: frontend/app/page.tsx)
- `frontend/lib/demo-data.ts` สำหรับ sample logs และ metric snapshots ที่ UI แสดง (source: frontend/lib/demo-data.ts)
- `reports/baseline-eval.json` สำหรับ heuristic baseline metric บน fixed test split (source: reports/baseline-eval.json)
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-2048-hard-contrast-memorization-probe.json` สำหรับ v3.5 exploratory probe metric ที่ยังไม่ใช่ fixed split comparison (source: reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-2048-hard-contrast-memorization-probe.json)
- `docs/Day6.md` สำหรับ Phase 6 closure และข้อจำกัดว่า fixed split ยัง held (source: docs/Day6.md)

**Last updated**

2026-05-22

## Talk Track

1. เปิด `http://localhost:3000` แล้วชี้ให้เห็นว่า demo เป็น triage tool ไม่ใช่ landing page
2. เลือก sample log ทีละ label: normal, failed login brute force, SQL injection, directory traversal และ port scan/recon
3. ใช้ analyzer `Heuristic` แล้วกด `Analyze`
4. อ่านผลลัพธ์แบบ structured output: label, severity, suspicious flag, evidence, reason และ recommended action
5. ชี้ evidence highlight ใน raw log เพื่อย้ำว่า output ต้องอ้าง substring จาก log ไม่ใช่ invent fact
6. เปิด raw JSON panel เพื่อย้ำ schema contract ที่ใช้ร่วมกันใน dataset, evaluator, adapter และ UI
7. เลือก `Fine-tuned` แล้วกด `Analyze` เพื่อโชว์ว่า UI ไม่ fake result เมื่อ live endpoint ยังไม่ได้ configure
8. ดู comparison panel: heuristic baseline พร้อมบน fixed test split, v3.5 เป็น exploratory hard-contrast probe, fixed split comparison ยัง held
9. ปิดด้วย limitation: POC นี้ triage suspicious patterns และแนะนำ investigation เท่านั้น ไม่ได้ยืนยัน compromise จาก log เส้นเดียว

## Commands

```bash
cd frontend
npm run dev -- --port 3000
```

Verification commands used for this handoff:

```bash
cd frontend
npx tsc --noEmit
npm run lint
npm run build
```

## Guardrails

- ห้ามพูดว่า fine-tuned model ชนะ fixed split เพราะ fixed `data/splits/test.jsonl` ยังไม่ได้เปิดสำหรับ Phase 7 comparison
- ห้าม claim ว่าระบบตรวจพบการถูก hack
- ถ้าจะ demo live model ต้อง configure endpoint จริงก่อน แล้วรัน evaluator/report แยก path ตาม convention
- ถ้าใช้ log จริง ต้อง sanitize IP, hostname, user, token, cookie และ session id ก่อน

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-22 | Codex | Created Day 7 demo script after UI implementation | `docs/demo-script.md`, `frontend/app/page.tsx` | Ready |

## Related pages

- [[Day7]]
- [[Day6]]
- [[structured-output-fix-plan]]
- [[output-structure-fix/phase-7-fixed-split-comparison]]

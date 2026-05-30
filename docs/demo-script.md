# Demo Script

**Summary**

สคริปต์สั้นสำหรับ demo POC ภายใน 2-3 นาทีหลัง Phase 6 ปิดแล้ว โดยโชว์ Day 7 UI, heuristic baseline, evidence highlight, live endpoint wiring และสถานะ fixed split ที่ยังไม่ถูกเปิด

**Sources**

- `docs/Day7.md` สำหรับ scope demo UI และ acceptance criteria (source: docs/Day7.md)
- `frontend/app/page.tsx` สำหรับหน้าจอ demo, analyzer selector, result view และ endpoint/error state (source: frontend/app/page.tsx)
- `frontend/app/api/triage/route.ts` สำหรับ API route ที่อ่าน OpenAI-compatible endpoint จาก env ฝั่ง server (source: frontend/app/api/triage/route.ts)
- `frontend/lib/demo-data.ts` สำหรับ sample logs และ metric snapshots ที่ UI แสดง (source: frontend/lib/demo-data.ts)
- `reports/baseline/baseline-eval.json` สำหรับ heuristic baseline metric บน fixed test split (source: reports/baseline/baseline-eval.json)
- `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-5-temp-03-2048-hard-contrast-memorization-probe.json` สำหรับ v3.5 exploratory probe metric ที่ยังไม่ใช่ fixed split comparison (source: reports/phase-6/openai-compatible-vllm-structured-outputs-v3-5-temp-03-2048-hard-contrast-memorization-probe.json)
- `docs/Day6.md` สำหรับ Phase 6 closure และข้อจำกัดว่า fixed split ยัง held (source: docs/Day6.md)

**Last updated**

2026-05-24

## Talk Track

1. เปิด `http://localhost:3000` แล้วชี้ให้เห็นว่า demo เป็น triage tool ไม่ใช่ landing page
2. เลือก sample log ทีละ label: normal, failed login brute force, SQL injection, directory traversal และ port scan/recon
3. ใช้ analyzer `Heuristic` แล้วกด `Analyze`
4. อ่านผลลัพธ์แบบ structured output: label, severity, suspicious flag, evidence, reason และ recommended action
5. ชี้ evidence highlight ใน raw log เพื่อย้ำว่า output ต้องอ้าง substring จาก log ไม่ใช่ invent fact
6. เปิด raw JSON panel เพื่อย้ำ schema contract ที่ใช้ร่วมกันใน dataset, evaluator, adapter และ UI
7. เลือก `Fine-tuned` แล้วกด `Analyze`; ถ้า endpoint พร้อม UI จะแสดงผล schema-valid จาก live model และถ้ายังไม่พร้อม UI จะแสดง endpoint-error/unconfigured โดยไม่ fake result
8. ดู comparison panel: heuristic baseline พร้อมบน fixed test split, v3.5 เป็น exploratory hard-contrast probe, fixed split comparison ยัง held
9. ปิดด้วย limitation: POC นี้ triage suspicious patterns และแนะนำ investigation เท่านั้น ไม่ได้ยืนยัน compromise จาก log เส้นเดียว

## Commands

```bash
cd frontend
cp .env.example .env.local
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
- ถ้าจะ demo live model ต้อง configure `frontend/.env.local` ให้ชี้ endpoint จริงก่อน และผล demo UI ยังไม่แทน evaluator/report ตาม convention
- ถ้าใช้ log จริง ต้อง sanitize IP, hostname, user, token, cookie และ session id ก่อน

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-22 | Codex | Created Day 7 demo script after UI implementation | `docs/demo-script.md`, `frontend/app/page.tsx` | Ready |
| 2026-05-24 | Codex | Updated demo script for frontend `/api/triage` endpoint and env-based live model configuration | `frontend/app/api/triage/route.ts`, `frontend/.env.example`, `docs/demo-script.md` | Ready |

## Related pages

- [[Day7]]
- [[Day6]]
- [[structured-output-fix-plan]]
- [[output-structure-fix/phase-7-fixed-split-comparison]]

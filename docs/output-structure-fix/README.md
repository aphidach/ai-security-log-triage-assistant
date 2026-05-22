# Output Structure Fix Phase Notes

**Summary**

โฟลเดอร์นี้เก็บ working notes แบบแยก phase สำหรับงานแก้ output contract หลัง smoke test ของ `unsloth_LFM2-350M_1779162226` เคยผ่าน JSON/schema เพียง 1/5 samples ตอนนี้ vLLM `structured_outputs` ผ่าน output contract แล้ว และงานถัดไปคือ semantic error analysis

หน้า `docs/structured-output-fix-plan.md` ยังเป็น master plan ส่วนโฟลเดอร์นี้ใช้เก็บรายละเอียดการทำงาน คำสั่งที่ต้องรัน หลักฐานที่ต้องเก็บ และ pass/fail condition ของแต่ละ phase ตั้งแต่ Phase 1 เป็นต้นไป

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ phase, gate และ deliverables หลัก (source: docs/structured-output-fix-plan.md)
- `reports/structured-output-run-artifacts.md` สำหรับ Phase 0 evidence register และ current smoke baseline (source: reports/structured-output-run-artifacts.md)
- `reports/README.md` สำหรับ report path convention ของ smoke และ mini semantic eval (source: reports/README.md)

**Last updated**

2026-05-22

## File Map

| Phase | Page | Status | Purpose |
| --- | --- | --- | --- |
| Phase 0 | `docs/structured-output-fix-plan.md` และ `reports/structured-output-run-artifacts.md` | Done | เก็บ evidence, checksums และ preserved smoke artifact แล้ว |
| Phase 1 | [[output-structure-fix/phase-1-backend-inventory]] | Passed for vLLM path | ระบุ backend, version, launch command, model alias, response model และ LoRA serving path |
| Phase 2 | [[output-structure-fix/phase-2-probe-hardening]] | Optional follow-up | เพิ่ม probe ให้แยก constrained decoding จริงจาก validation-after-generation |
| Phase 3 | [[output-structure-fix/phase-3-runtime-capability-matrix]] | Passed for vLLM path | ทดสอบ runtime/mode candidate ด้วย smoke split เดียวกัน |
| Phase 4 | [[output-structure-fix/phase-4-contract-gate]] | Passed | ตั้ง gate ที่ต้องผ่านก่อนดู semantic quality |
| Phase 5 | [[output-structure-fix/phase-5-mini-semantic-eval]] | Superseded by Phase 6.1 mini rerun | วัด semantic error profile หลัง contract ผ่าน |
| Phase 6 | [[output-structure-fix/phase-6-v3-or-runtime-decision]] | In progress | ตัดสินใจว่าจะ retrain v3, เปลี่ยน runtime หรือเปลี่ยน model candidate |
| Phase 6.1 | [[output-structure-fix/phase-6-1-evidence-constraints]] | Contract restored; semantics still blocked | แก้ evidence loop ด้วย schema constraints และ sanitizer update |
| Phase 6 v3 data | [[output-structure-fix/phase-6-v3-hard-contrast-dataset]] | Created | สร้าง hard contrast training supplement สำหรับแก้ prediction collapse |
| Phase 6 v3.1 eval | [[output-structure-fix/phase-6-v3-1-mini-semantic-eval]] | Failed semantic gate | บันทึกผล v3.1 mini semantic eval และ decision ให้ hold fixed test split |
| Phase 6 v3.2 probe | [[output-structure-fix/phase-6-v3-2-hard-contrast-probe]] | Failed canary, improved | บันทึกผล v3.2 hard-contrast memorization probe และ next target สำหรับ v3.3 |
| Phase 6 v3.3 probe | [[output-structure-fix/phase-6-v3-3-targeted-canary]] | Canary improved, still held | temp 0.3 runtime probe ขยับ hard-contrast label accuracy เป็น `0.64`, มี HTML infographic แล้ว แต่ SQLi ยัง `2/10` และยังไม่เปิด fixed test split |
| Phase 6 v3.4 plan | [[output-structure-fix/phase-6-v3-4-boundary-repair-plan]] | Temp 0 checked, still held | v3.4 temp 0.3 ขยับ label accuracy เป็น `0.72` แต่ temp 0 ได้ `0.68`; SQLi/invalid output/traversal/brute-force gravity ยัง block Phase 7 |
| Phase 6 v3.5 plan | [[output-structure-fix/phase-6-v3-5-boundary-repair-plan]] | Dataset/config prepared | v3.5 สร้าง failure slice จาก v3.4 temp 0 และเพิ่ม 200-record boundary repair supplement เพื่อซ่อม SQLi/traversal/port-recon กับลด brute-force gravity; fixed test ยัง held |
| Phase 7 | [[output-structure-fix/phase-7-fixed-split-comparison]] | Draft | รัน fixed split comparison หลังผ่าน prerequisites ทั้งหมด |

## Operating Rules

- ห้ามใช้ `data/splits/test.jsonl` ระหว่าง prompt/runtime tuning
- ทุก smoke run ต้องเขียนไปที่ `reports/{adapter}-{runtime}-{mode}-smoke.json` และ `.md`
- ทุก run ต้องเก็บ raw output ต่อ sample เพื่อดู failure mode ได้
- ห้ามเอา JSON extraction จาก markdown fence มานับเป็น metric หลัก
- ต้องระบุ backend และ mode ให้ชัดก่อนสรุปว่า model quality ดีหรือแย่

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created phase-detail directory for structured-output fix work | `docs/output-structure-fix/` | Drafted |
| 2026-05-20 | Codex | Updated phase map after vLLM `structured_outputs` passed the output-contract smoke gate | `reports/openai-compatible-vllm-structured-outputs-smoke.json` | Updated |
| 2026-05-20 | Codex | Added Phase 6.1 evidence constraints page to the phase map | `docs/output-structure-fix/phase-6-1-evidence-constraints.md` | Planned |
| 2026-05-21 | Codex | Marked Phase 6.1 local implementation complete in the phase map | `docs/output-structure-fix/phase-6-1-evidence-constraints.md`, `data/schemas/triage-output.schema.json` | Endpoint rerun pending |
| 2026-05-21 | Codex | Updated phase map after Phase 6.1 reruns restored the output contract | `reports/openai-compatible-vllm-structured-outputs-phase6-1-*.json` | Semantic quality remains blocked |
| 2026-05-21 | Codex | Added v3 hard contrast dataset page to the phase map | `docs/output-structure-fix/phase-6-v3-hard-contrast-dataset.md` | Created |
| 2026-05-21 | Codex | Added v3.1 mini semantic eval page to the phase map | `docs/output-structure-fix/phase-6-v3-1-mini-semantic-eval.md`, `reports/phase-6-v3-1-mini-semantic-eval-infographic.html` | Semantic gate failed |
| 2026-05-21 | Codex | Added v3.2 hard-contrast probe page to the phase map | `docs/output-structure-fix/phase-6-v3-2-hard-contrast-probe.md`, `reports/phase-6-v3-2-hard-contrast-memorization-probe-infographic.html` | Canary improved but still failed |
| 2026-05-21 | Codex | Added v3.3 targeted canary preparation page to the phase map | `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md`, `data/splits/train-v3-3-targeted-hard-contrast.jsonl` | Prepared |
| 2026-05-21 | Codex | Updated phase map after v3.3 temp 0.3 hard-contrast runtime probe | `reports/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json`, `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md` | Canary improved to `0.64`, fixed test still held |
| 2026-05-21 | Codex | Added v3.3 temp 0.3 hard-contrast infographic to phase map evidence | `reports/phase-6-v3-3-temp-03-hard-contrast-memorization-probe-infographic.html`, `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md` | Added |
| 2026-05-21 | Codex | Added v3.4 boundary repair plan to the phase map | `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md` | Planned |
| 2026-05-22 | Codex | Updated phase map after v3.4 boundary failure slice was generated | `reports/phase-6-v3-4-boundary-failure-slice.json`, `reports/phase-6-v3-4-boundary-failure-slice.md` | Failure slice complete |
| 2026-05-22 | Codex | Updated phase map after v3.4 boundary repair split/config preparation | `data/splits/train-v3-4-boundary-repair.jsonl`, `ml/unsloth/config.v3-4.yaml` | Dataset/config prepared |
| 2026-05-22 | Codex | Updated phase map after v3.4 temp 0.3 hard-contrast runtime probe and HTML report | `reports/openai-compatible-vllm-structured-outputs-v3-4-temp-03-hard-contrast-memorization-probe.json`, `reports/phase-6-v3-4-temp-03-hard-contrast-memorization-probe-infographic.html` | Improved to `0.72`, fixed test still held |
| 2026-05-22 | Codex | Updated phase map after v3.4 temp 0 hard-contrast probe and HTML report | `reports/openai-compatible-vllm-structured-outputs-v3-4-temp-0-hard-contrast-memorization-probe.json`, `reports/phase-6-v3-4-temp-0-hard-contrast-memorization-probe-infographic.html` | `label_accuracy=0.68`, fixed test still held |
| 2026-05-22 | Codex | Added v3.5 boundary repair plan, failure slice, dataset/config, and test coverage to the phase map | `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md`, `reports/phase-6-v3-5-boundary-failure-slice.json`, `data/splits/train-v3-5-boundary-repair.jsonl`, `ml/unsloth/config.v3-5.yaml`, `tests/test_v3_5_boundary_repair_workflow.py` | Dataset/config prepared, train pending |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-20 | แยก phase notes ออกจาก master plan | master plan ควรสั้นพอใช้ตัดสินใจ ส่วนรายละเอียดคำสั่งและหลักฐานของแต่ละ phase จะยาวขึ้นเรื่อย ๆ | งาน Phase 1 เป็นต้นไปมีหน้าเฉพาะสำหรับ update แบบ append-only |
| 2026-05-20 | ใช้ path `docs/output-structure-fix/` | normalize จากคำขอที่พิมพ์ว่า `sdocs/output-stuctur-fix/` ให้เข้ากับ repo docs และสะกด `structure` ให้ถูก | เอกสารใหม่อยู่ใต้ mini-wiki หลักและค้นหาได้จาก `docs/index.md` |
| 2026-05-20 | เลื่อนงาน active ไป Phase 5 mini semantic eval | vLLM `structured_outputs` ผ่าน JSON/schema gate แล้ว แต่ smoke label accuracy ยังอยู่ที่ `0.2` | ต่อไปควรวัด semantic error profile บน mini split ที่ไม่ใช่ fixed test split |
| 2026-05-20 | เพิ่ม Phase 6.1 สำหรับ evidence constraints | Phase 6 case 1 พบว่า JSON-constrained modes วนซ้ำใน `evidence` จนชน token cap | ก่อน retrain v3 ให้ลอง schema tightening และ sanitizer update |
| 2026-05-22 | เพิ่ม v3.5 เป็น failure-driven repair ก่อน Phase 7 | v3.4 temp 0 ยังมี label accuracy `0.68`, invalid output `1`, SQLi `3/10`, traversal `5/10` และ predicted brute force `19/50` | ต้อง train/probe v3.5 บน hard-contrast และ mini semantic eval ก่อนเปิด fixed test split |

## Related pages

- [[structured-output-fix-plan]]
- [[structured-output-reliability-research-2026]]
- [[output-contract-hardening]]
- [[model-output/v2-lfm2-350m-security-triage-responses-parse]]
- [[Day6]]

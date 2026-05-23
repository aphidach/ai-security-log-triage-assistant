# Output Structure Fix Phase Notes

**Summary**

โฟลเดอร์นี้เก็บ working notes แบบแยก phase สำหรับงานแก้ output contract หลัง smoke test ของ `unsloth_LFM2-350M_1779162226` เคยผ่าน JSON/schema เพียง 1/5 samples ตอนนี้ Phase 7 fixed split comparison ปิดด้วย decision `hold`, Phase 8/v4 train/probe แล้วแต่ยัง held เพราะ SQLi hard-contrast ยัง `4/10`, v4.1 train/probe แล้วแต่ยัง held เพราะ canonical temp 0 SQLi ยัง `6/10`, v4.2 prompt-priority diagnostic ก็ held เพราะ prompt v2.2 ทำให้ broader label boundary เสีย, v4.3 ทดสอบ base model `unsloth/Qwen3.5-0.8B` ครบ 3 run แล้วและ held, v4.4 audit ชี้ failure หลักว่า SQLi/traversal/recon ถูก classify เป็น `normal` ซ้ำ ๆ แม้ JSON/schema จะ `1.0`, v4.5 trained-Qwen LoRA พลิก suspicious labels ได้ครบแต่ยัง held เพราะ normal false positives และ severity calibration, และ v4.6 เตรียม normal/severity calibration workflow โดยยังไม่เปิด fixed split

หน้า `docs/structured-output-fix-plan.md` ยังเป็น master plan ส่วนโฟลเดอร์นี้ใช้เก็บรายละเอียดการทำงาน คำสั่งที่ต้องรัน หลักฐานที่ต้องเก็บ และ pass/fail condition ของแต่ละ phase ตั้งแต่ Phase 1 เป็นต้นไป

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ phase, gate และ deliverables หลัก (source: docs/structured-output-fix-plan.md)
- `reports/structured-output-run-artifacts.md` สำหรับ Phase 0 evidence register และ current smoke baseline (source: reports/structured-output-run-artifacts.md)
- `reports/README.md` สำหรับ report path convention ของ smoke และ mini semantic eval (source: reports/README.md)

**Last updated**

2026-05-23

## File Map

| Phase | Page | Status | Purpose |
| --- | --- | --- | --- |
| Phase 0 | `docs/structured-output-fix-plan.md` และ `reports/structured-output-run-artifacts.md` | Done | เก็บ evidence, checksums และ preserved smoke artifact แล้ว |
| Phase 1 | [[output-structure-fix/phase-1-backend-inventory]] | Passed for vLLM path | ระบุ backend, version, launch command, model alias, response model และ LoRA serving path |
| Phase 2 | [[output-structure-fix/phase-2-probe-hardening]] | Optional follow-up | เพิ่ม probe ให้แยก constrained decoding จริงจาก validation-after-generation |
| Phase 3 | [[output-structure-fix/phase-3-runtime-capability-matrix]] | Passed for vLLM path | ทดสอบ runtime/mode candidate ด้วย smoke split เดียวกัน |
| Phase 4 | [[output-structure-fix/phase-4-contract-gate]] | Passed | ตั้ง gate ที่ต้องผ่านก่อนดู semantic quality |
| Phase 5 | [[output-structure-fix/phase-5-mini-semantic-eval]] | Superseded by Phase 6.1 mini rerun | วัด semantic error profile หลัง contract ผ่าน |
| Phase 6 | [[output-structure-fix/phase-6-v3-or-runtime-decision]] | Closed with limitations | runtime/output-contract decision และ v3 repair path ปิดแล้วหลัง v3.5; fixed split ยัง held |
| Phase 6.1 | [[output-structure-fix/phase-6-1-evidence-constraints]] | Contract restored; semantics still blocked | แก้ evidence loop ด้วย schema constraints และ sanitizer update |
| Phase 6 v3 data | [[output-structure-fix/phase-6-v3-hard-contrast-dataset]] | Created | สร้าง hard contrast training supplement สำหรับแก้ prediction collapse |
| Phase 6 v3.1 eval | [[output-structure-fix/phase-6-v3-1-mini-semantic-eval]] | Failed semantic gate | บันทึกผล v3.1 mini semantic eval และ decision ให้ hold fixed test split |
| Phase 6 v3.2 probe | [[output-structure-fix/phase-6-v3-2-hard-contrast-probe]] | Failed canary, improved | บันทึกผล v3.2 hard-contrast memorization probe และ next target สำหรับ v3.3 |
| Phase 6 v3.3 probe | [[output-structure-fix/phase-6-v3-3-targeted-canary]] | Canary improved, still held | temp 0.3 runtime probe ขยับ hard-contrast label accuracy เป็น `0.64`, มี HTML infographic แล้ว แต่ SQLi ยัง `2/10` และยังไม่เปิด fixed test split |
| Phase 6 v3.4 plan | [[output-structure-fix/phase-6-v3-4-boundary-repair-plan]] | Temp 0 checked, still held | v3.4 temp 0.3 ขยับ label accuracy เป็น `0.72` แต่ temp 0 ได้ `0.68`; SQLi/invalid output/traversal/brute-force gravity ยัง block Phase 7 |
| Phase 6 v3.5 plan | [[output-structure-fix/phase-6-v3-5-boundary-repair-plan]] | Closed with limitations | 2048 temp 0.3 ขยับ hard-contrast label accuracy เป็น `0.88` และ JSON/schema เป็น `1.0`; canonical temp 0 และ SQLi ยัง held จึงปิดเป็น measured repair run ไม่ใช่ Phase 7 clearance |
| Phase 7 | [[output-structure-fix/phase-7-fixed-split-comparison]] | Executed; hold | fixed split comparison เสร็จแล้ว: heuristic label accuracy `1.0`, v3.5 label accuracy `0.84`, JSON/schema `1.0`, invalid `0`; final decision `hold` |
| Phase 8 v4 | [[output-structure-fix/phase-8-v4-sqli-boundary-repair-plan]] | Trained/probed; held | v4 SQLi-first repair train แล้วและ hard-contrast temp 0/temp 0.3 ได้ label accuracy `0.84`, JSON/schema `1.0`, invalid `0`, SQLi `4/10`; ยังไม่เปิด mini semantic หรือ fixed split |
| Phase 8 v4.1 | [[output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan]] | Trained/probed; held | v4.1 train แล้วและ hard-contrast temp 0 ได้ label accuracy `0.88`, SQLi `6/10`; temp 0.3 ได้ `0.90`, SQLi `7/10`; JSON/schema `1.0`, invalid `0`, fixed test ยัง held |
| Phase 8 v4.2 | [[output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan]] | Probed; held | prompt/architecture diagnostic บน v4.1 adapter เพิ่ม `triage-json-v2.2-sqli-priority` แบบ opt-in; temp 0 ได้ label accuracy `0.64`, SQLi `4/10`, traversal `4/10`; temp 0.3 ได้ JSON/schema `0.98` และ invalid `1` |
| Phase 8 v4.3 | [[output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan]] | Probed; held | capacity/architecture diagnostic ด้วย base model `unsloth/Qwen3.5-0.8B` ครบ smoke, hard-contrast temp 0, และ hard-contrast temp 0.3; JSON/schema `1.0`, invalid `0`, แต่ label accuracy `0.50`/`0.48` และ SQLi `3/10`/`2/10` ยังไม่ผ่าน gate |
| Phase 8 v4.4 | [[output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan]] | Audit complete; held | boundary audit จาก v4.3 Qwen3.5 base-model hard-contrast reports พบ union label failures `26`, persistent failures `25`, และ SQLi/traversal/recon -> `normal` `20/50` กับ `22/50`; fixed split และ train artifacts ยังปิด |
| Phase 8 v4.5 | [[output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe]] | Trained/probed; calibration held | Qwen3.5 LoRA pilot train สำเร็จและ hard-contrast temp 0 ได้ label accuracy `0.88`, JSON/schema `1.0`, invalid `0`, suspicious labels `10/10` ทุกกลุ่ม แต่ `normal` เหลือ `4/10` และ severity accuracy `0.72`; fixed split ยังปิด |
| Phase 8 v4.6 | [[output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan]] | Prepared; training pending | สร้าง v4.6 calibration slice, supplement `145` records, train `1340`, validation `100`, probe `25`, และ Qwen config ใหม่เพื่อแก้ normal false positives/severity โดยยังไม่ใช้ fixed split |

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
| 2026-05-22 | Codex | Updated phase map after v3.5 temp 0 and temp 0.3 hard-contrast probes and HTML reports | `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json`, `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json`, `reports/phase-6-v3-5-temp-0-hard-contrast-memorization-probe-infographic.html`, `reports/phase-6-v3-5-temp-03-hard-contrast-memorization-probe-infographic.html` | Improved to `0.84`, fixed test still held |
| 2026-05-22 | Codex | Updated phase map after v3.5 2048-token hard-contrast probes and HTML reports | `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-2048-hard-contrast-memorization-probe.json`, `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-2048-hard-contrast-memorization-probe.json`, `reports/phase-6-v3-5-temp-03-2048-hard-contrast-memorization-probe-infographic.html` | Temp 0.3 improved to `0.88` with contract `1.0`, fixed test still held |
| 2026-05-22 | User/Codex | Closed Phase 6 and v3.5 in the phase map | `docs/output-structure-fix/README.md`, `docs/output-structure-fix/phase-6-v3-or-runtime-decision.md`, `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md` | Closed with limitations |
| 2026-05-22 | Codex | Updated Phase 7 phase map status after adding copyable CLI runbook | `docs/output-structure-fix/phase-7-fixed-split-comparison.md`, `docs/output-structure-fix/README.md` | Runbook prepared |
| 2026-05-22 | Codex | Updated phase map after Phase 7 fixed split evaluation | `reports/comparison.md`, `reports/phase-7-fixed-split-summary.html`, `docs/output-structure-fix/phase-7-fixed-split-comparison.md` | Executed; decision `hold` |
| 2026-05-22 | Codex | Added Phase 8 v4 SQLi-first repair page to the phase map | `docs/output-structure-fix/phase-8-v4-sqli-boundary-repair-plan.md`, `data/splits/train-v4-sqli-boundary-repair.jsonl`, `ml/unsloth/config.v4.yaml` | Prepared |
| 2026-05-22 | User/Codex | Updated phase map after v4 training and hard-contrast probes | `reports/phase-8-v4-sqli-boundary-training-result.json`, `reports/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json`, `reports/openai-compatible-vllm-structured-outputs-v4-temp-03-2048-hard-contrast-memorization-probe.json` | Held |
| 2026-05-22 | Codex | Added Phase 8 v4.1 SQLi-boundary repair page to the phase map | `docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md`, `data/splits/train-v4-1-sqli-boundary-repair.jsonl`, `ml/unsloth/config.v4-1.yaml` | Prepared |
| 2026-05-22 | User/Codex | Updated phase map after v4.1 training and hard-contrast probes | `reports/phase-8-v4-1-sqli-boundary-training-result.json`, `reports/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json`, `reports/openai-compatible-vllm-structured-outputs-v4-1-temp-03-2048-hard-contrast-memorization-probe.json` | Held |
| 2026-05-22 | Codex | Added Phase 8 v4.2 SQLi-priority prompt diagnostic page to the phase map | `docs/output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan.md`, `reports/phase-8-v4-2-sqli-priority-diagnostic-slice.json`, `scripts/model_adapters/prompt_contract.py` | Prepared |
| 2026-05-22 | Codex | Updated phase map after v4.2 hard-contrast prompt probes | `reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json`, `reports/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.json` | Held |
| 2026-05-22 | Codex | Added v4.3 capacity/architecture diagnostic plan to the phase map | `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md`, `tests/test_v4_3_capacity_diagnostic_plan.py` | Planned |
| 2026-05-23 | Codex | Updated v4.3 phase map after selecting `unsloth/Qwen3.5-0.8B` as first base-model candidate intake | `docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md`, `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md` | Candidate intake |
| 2026-05-23 | User/Codex | Updated v4.3 phase map after all 3 Qwen3.5 base-model probes completed | `reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-smoke.json`, `reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-0-2048-capacity-diagnostic-hard-contrast.json`, `reports/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-temp-03-2048-capacity-diagnostic-hard-contrast.json` | Probed; held |
| 2026-05-23 | Codex | Added v4.4 hard-contrast boundary audit page after slicing v4.3 Qwen3.5 failures | `docs/output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan.md`, `reports/phase-8-v4-4-hard-contrast-boundary-audit.json` | Audit complete; held |
| 2026-05-23 | User/Codex | Clarified that v4.3/v4.4 Qwen3.5 evidence is from the Hub base model, not a trained Qwen model | `docs/output-structure-fix/README.md` | Clarified |
| 2026-05-23 | User/Codex | Added v4.5 trained-Qwen LoRA hard-contrast probe page to the phase map | `docs/output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe.md`, `reports/phase-8-v4-5-qwen35-lora-training-result.json`, `reports/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json` | Calibration held |
| 2026-05-23 | Codex | Added v4.6 Qwen normal/severity calibration workflow to the phase map | `docs/output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan.md`, `data/splits/train-v4-6-qwen35-normal-severity-calibration.jsonl`, `ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml` | Prepared; training pending |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-20 | แยก phase notes ออกจาก master plan | master plan ควรสั้นพอใช้ตัดสินใจ ส่วนรายละเอียดคำสั่งและหลักฐานของแต่ละ phase จะยาวขึ้นเรื่อย ๆ | งาน Phase 1 เป็นต้นไปมีหน้าเฉพาะสำหรับ update แบบ append-only |
| 2026-05-20 | ใช้ path `docs/output-structure-fix/` | normalize จากคำขอที่พิมพ์ว่า `sdocs/output-stuctur-fix/` ให้เข้ากับ repo docs และสะกด `structure` ให้ถูก | เอกสารใหม่อยู่ใต้ mini-wiki หลักและค้นหาได้จาก `docs/index.md` |
| 2026-05-20 | เลื่อนงาน active ไป Phase 5 mini semantic eval | vLLM `structured_outputs` ผ่าน JSON/schema gate แล้ว แต่ smoke label accuracy ยังอยู่ที่ `0.2` | ต่อไปควรวัด semantic error profile บน mini split ที่ไม่ใช่ fixed test split |
| 2026-05-20 | เพิ่ม Phase 6.1 สำหรับ evidence constraints | Phase 6 case 1 พบว่า JSON-constrained modes วนซ้ำใน `evidence` จนชน token cap | ก่อน retrain v3 ให้ลอง schema tightening และ sanitizer update |
| 2026-05-22 | เพิ่ม v3.5 เป็น failure-driven repair ก่อน Phase 7 | v3.4 temp 0 ยังมี label accuracy `0.68`, invalid output `1`, SQLi `3/10`, traversal `5/10` และ predicted brute force `19/50` | ต้อง train/probe v3.5 บน hard-contrast และ mini semantic eval ก่อนเปิด fixed test split |
| 2026-05-22 | Hold v3.5 before mini semantic eval | v3.5 temp 0 ผ่าน overall label gate แล้ว แต่ SQLi ยัง `4/10` และ output contract ยังไม่เต็ม | ทำ v3.5.1 SQLi/quote-output repair ก่อนรัน mini semantic หรือ fixed split |
| 2026-05-22 | Hold fixed split after 2048 runtime probe | 2048 temp 0.3 ผ่าน output contract แล้ว แต่ canonical temp 0 ยังไม่ผ่าน และ SQLi ยัง `6/10` ต่ำกว่า gate เดิม | mini semantic ถ้ารันต่อควร mark เป็น runtime-only exploratory; fixed test ยังไม่เปิด |
| 2026-05-22 | ปิด Phase 6 หลัง v3.5 | Phase 6 ให้คำตอบเชิง decision ครบแล้ว แม้ยังไม่ใช่ Phase 7 clearance | future SQLi repair หรือ model-capacity diagnostic ต้องเริ่มเป็นรอบใหม่; fixed test ยัง held |
| 2026-05-22 | Hold v3.5 after Phase 7 | Fixed split evaluation preserved output contract but did not beat the heuristic baseline | Any future model repair must be a new experiment; Phase 7 result remains historical evidence |
| 2026-05-22 | Start Phase 8 as v4 SQLi-first repair | Phase 7 and v3.5 hard-contrast failures point to SQLi/quote-heavy boundaries as the narrow blocker | v4 uses hard-contrast-derived repair data and must not reuse fixed split results for tuning |
| 2026-05-22 | Hold v4 after hard-contrast probes | v4 restores JSON/schema reliability but SQLi stays `4/10`, below the `8/10` gate | Stop before mini semantic eval; next work should either make a narrower SQLi-boundary repair or run a model-capacity diagnostic |
| 2026-05-22 | Prepare v4.1 as narrow SQLi-boundary repair | v4 failure slice shows the remaining issue is mostly SQLi predicted as traversal, not output contract failure | v4.1 appends focused SQLi contrast data to v4 train and holds mini semantic/fixed split until hard-contrast gates pass |
| 2026-05-22 | Hold v4.1 after hard-contrast probes | v4.1 improves SQLi but still misses SQLi `>=8/10`, with temp 0 at `6/10` and temp 0.3 at `7/10` | Do not run mini semantic eval; next work should be capacity/architecture diagnostic before any v4.2 |
| 2026-05-22 | Make v4.2 a prompt-priority diagnostic | v4.1 reached the data-only repair stop condition, so another broad supplement would make the cause harder to read | v4.2 adds an opt-in prompt profile and runs hard-contrast probes before any mini semantic eval |
| 2026-05-22 | Hold v4.2 after hard-contrast probes | SQLi-to-traversal went to `0/10`, but SQLi stayed `4/10`, traversal fell to `4/10`, and temp 0.3 lost JSON/schema `1.0` | Do not promote prompt v2.2; next work should be capacity pilot or deeper architecture diagnostic |
| 2026-05-22 | Plan v4.3 capacity/architecture diagnostic | v4.1 data repair and v4.2 prompt repair both failed the SQLi hard-contrast gate | Compare model/runtime capacity under prompt v2.1 before adding more SQLi synthetic data |
| 2026-05-23 | Start v4.3 with `unsloth/Qwen3.5-0.8B` base-model candidate intake | The model card is now downloaded locally and the user wants this small Qwen3.5 candidate tested next | Proceed to base-model serving/probe planning without creating v4.3 train data or config |
| 2026-05-23 | Hold v4.3 base Qwen3.5-0.8B after candidate probes | The 3 base-model runs preserve JSON/schema but hard-contrast semantics collapse many suspicious cases to `normal` | Keep fixed split closed; next step should be another capacity candidate, a boundary audit, or a separately named exploratory Qwen fine-tune |
| 2026-05-23 | Hold base Qwen3.5-0.8B after v4.4 boundary audit | The audit found `25` persistent failure IDs and a broad SQLi/traversal/recon -> `normal` collapse, not an output-contract problem | Do not create v4.4 train artifacts; choose another capacity candidate or a deliberately scoped boundary-repair experiment |
| 2026-05-23 | Hold v4.5 before fixed split | Trained Qwen LoRA fixes the suspicious-to-normal collapse on hard-contrast labels, but normal false positives rise to `6/10` and severity accuracy is `0.72` | Add normal/severity calibration before mini semantic eval or fixed split comparison |
| 2026-05-23 | Prepare v4.6 as normal/severity calibration | v4.5 no longer needs broad SQLi repair; its blocker is normal precision plus severity boundaries | Add normal-heavy and severity-boundary data with a non-fixed probe split; keep fixed split closed |

## Related pages

- [[structured-output-fix-plan]]
- [[structured-output-reliability-research-2026]]
- [[output-contract-hardening]]
- [[model-output/v2-lfm2-350m-security-triage-responses-parse]]
- [[Day6]]
- [[output-structure-fix/phase-8-v4-sqli-boundary-repair-plan]]
- [[output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan]]
- [[output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan]]
- [[output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan]]
- [[output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan]]
- [[output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe]]
- [[output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan]]

# Structured Output Fix Plan

**Summary**

แผนนี้แปลง `Recommended Next Plan` จาก research note ให้เป็นงานลงมือทำสำหรับแก้ปัญหา output contract หลัง smoke test ล่าสุดยังผ่าน JSON/schema ได้เพียง 1/5 samples

เป้าหมายของแผนนี้คือพิสูจน์ก่อนว่า serving backend บังคับ structured output แบบ constrained decoding ได้จริงหรือไม่ ถ้ายังทำไม่ได้ ห้ามใช้ fixed test split เป็น comparison หลัก และห้ามสรุปว่า fine-tuned model พร้อมใช้จากตัวอย่างที่ผ่านเพียง 1 sample

**Sources**

- `docs/structured-output-reliability-research-2026.md` สำหรับ recommended next plan, decision matrix และข้อมูล structured-output reliability ล่าสุด (source: docs/structured-output-reliability-research-2026.md)
- `docs/Day6.md` สำหรับสถานะ Day 6 ล่าสุดและ decision ว่าต้องพิสูจน์ constrained decoding ก่อน fixed split (source: docs/Day6.md)
- `docs/output-contract-hardening.md` สำหรับสิ่งที่แก้แล้วใน prompt `triage-json-v2`, OpenAI SDK adapter, schema sanitizer และ smoke split (source: docs/output-contract-hardening.md)
- `docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md` สำหรับ v2 smoke failure mode ที่ `responses_parse` ยังผ่านเพียง 1/5 (source: docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md)
- `reports/openai-compatible-unsloth-studio-json-schema-smoke.json` สำหรับ persisted smoke artifact ที่ถูก preserve ตาม report path convention: JSON/schema success `0.2`, invalid output `4` จาก 5 samples (source: reports/openai-compatible-unsloth-studio-json-schema-smoke.json)
- `reports/structured-output-run-artifacts.md` สำหรับ Phase 0 evidence register, artifact checksums, split checksums และ sample evidence summary (source: reports/structured-output-run-artifacts.md)
- `reports/frozen-splits.sha256` สำหรับ checksum ของ fixed test split และ smoke output-contract split (source: reports/frozen-splits.sha256)
- `scripts/probe_openai_structured_output.py` สำหรับ direct structured-output probe path ที่ต้องต่อยอด (source: scripts/probe_openai_structured_output.py)
- `scripts/model_adapters/openai_compatible.py` สำหรับ adapter modes ปัจจุบัน เช่น `responses_parse`, `json_schema`, `structured_outputs`, `guided_json`, `json_object` (source: scripts/model_adapters/openai_compatible.py)
- `scripts/evaluate.py` สำหรับ evaluator และ report output path ที่ต้องแยกตาม mode/runtime (source: scripts/evaluate.py)
- `reports/README.md` สำหรับ report path convention ของ smoke, mini semantic eval และ fixed split reports (source: reports/README.md)
- `docs/output-structure-fix/README.md` สำหรับ phase-detail notes ตั้งแต่ Phase 1 เป็นต้นไป (source: docs/output-structure-fix/README.md)
- `data/splits/smoke-output-contract.jsonl` สำหรับ 5-sample smoke gate (source: data/splits/smoke-output-contract.jsonl)
- `data/splits/test.jsonl` สำหรับ fixed test split ที่ต้อง freeze ไว้จนกว่า smoke contract ผ่าน (source: data/splits/test.jsonl)

**Last updated**

2026-05-20

## Goal

ทำให้ output contract ผ่านก่อนวัด model quality:

- `json_parse_success_rate = 1.0`
- `schema_success_rate = 1.0`
- `invalid_output_count = 0`

เกณฑ์นี้ต้องผ่านบน `data/splits/smoke-output-contract.jsonl` ก่อน จึงค่อยไป mini semantic eval หรือ fixed split หลัก

## Non-Goals

- ไม่แก้ evaluator ให้ดึง JSON จาก markdown fence ใน metric หลัก
- ไม่รัน `data/splits/test.jsonl` เป็น final comparison ระหว่างที่ smoke ยังไม่ผ่าน
- ไม่ broaden label taxonomy เกิน 5 labels เดิม
- ไม่ retrain v3 เพื่อกลบ runtime ที่ยังไม่ได้พิสูจน์ว่า constrained decoding ได้จริง
- ไม่ claim ว่า model ตรวจพบ compromise ได้จาก log เส้นเดียว

## Detailed Phase Pages

รายละเอียดการทำงานตั้งแต่ Phase 1 เป็นต้นไปอยู่ใน `docs/output-structure-fix/`:

| Phase | Page | Status |
| --- | --- | --- |
| Phase 1 | [[output-structure-fix/phase-1-backend-inventory]] | In progress |
| Phase 2 | [[output-structure-fix/phase-2-probe-hardening]] | Draft |
| Phase 3 | [[output-structure-fix/phase-3-runtime-capability-matrix]] | Draft |
| Phase 4 | [[output-structure-fix/phase-4-contract-gate]] | Draft |
| Phase 5 | [[output-structure-fix/phase-5-mini-semantic-eval]] | Draft |
| Phase 6 | [[output-structure-fix/phase-6-v3-or-runtime-decision]] | Draft |
| Phase 7 | [[output-structure-fix/phase-7-fixed-split-comparison]] | Draft |

## Phase 0: Freeze And Preserve Evidence

สถานะ: Done 2026-05-20

Checklist:

- [x] Freeze `data/splits/test.jsonl` และไม่ใช้กับ prompt/runtime tuning ระหว่างแก้ output contract
- [x] เก็บ smoke artifact ปัจจุบันจาก `reports/openai-compatible-eval-model-v2-output-v1.json` / `.md` เป็น mode-specific path ก่อนรันใหม่
- [x] ตั้ง convention report path เช่น `reports/openai-compatible-{runtime}-{mode}-smoke.json`
- [x] บันทึก raw output ของทั้ง 5 smoke samples ทุก run เพื่อดูว่า fail เพราะ markdown fence, prose, missing field หรือ invalid enum
- [x] ใส่ metadata ทุก report ให้มี backend, backend version, model alias, response model, adapter mode, schema mode และ launch note เท่าที่มี

### Report Path Convention

ให้ smoke report ใช้ path แบบนี้เสมอ:

```text
reports/{adapter}-{runtime}-{mode}-smoke.json
reports/{adapter}-{runtime}-{mode}-smoke.md
```

ให้ mini semantic eval ใช้ path แบบนี้:

```text
reports/{adapter}-{runtime}-{mode}-mini-semantic-eval.json
reports/{adapter}-{runtime}-{mode}-mini-semantic-eval.md
```

กติกาการตั้งชื่อ:

- `{adapter}` ใช้ชื่อ adapter จาก evaluator เช่น `openai-compatible`, `openai-finetune`, `heuristic`
- `{runtime}` ใช้ serving backend หรือ runtime profile เช่น `current`, `vllm`, `sglang`, `lmstudio`, `ollama`, `tgi`, `unsloth-studio`
- `{mode}` ใช้ structured-output mode แบบ kebab-case เช่น `responses-parse`, `json-schema`, `structured-outputs`, `guided-json`, `json-object`, `plain`
- ใช้ lowercase kebab-case เท่านั้น และเลี่ยงชื่อกลาง ๆ อย่าง `openai-compatible-eval.json` สำหรับ smoke รอบใหม่
- ถ้าต้องพูดถึง output ใน notes หรือ metadata ให้สะกด `output` ให้ถูก แต่ไม่ต้องใส่คำนี้ใน filename เว้นแต่เป็นส่วนของ model version label

Deliverables:

- `reports/openai-compatible-unsloth-studio-json-schema-smoke.json`
- `reports/openai-compatible-unsloth-studio-json-schema-smoke.md`
- `reports/README.md`
- `reports/frozen-splits.sha256`
- `reports/structured-output-run-artifacts.md`

Pass condition:

- ไม่มี report ใหม่เขียนทับ artifact เก่าโดยไม่ตั้งใจ

## Phase 1: Backend Inventory

สถานะ: In progress 2026-05-20

รายละเอียด: [[output-structure-fix/phase-1-backend-inventory]]

หมายเหตุ: สร้าง inventory report template แล้วที่ `reports/structured-output-backend-inventory.md` แต่ยังต้องเติม backend version, exact launch command และ `/v1/models` output จากเครื่องที่ serve Unsloth Studio adapter

Checklist:

- [ ] ระบุ serving backend จริง เช่น vLLM, SGLang, LM Studio, Ollama, TGI หรือ Unsloth Studio endpoint
- [ ] ระบุ backend version และ structured-output syntax ที่ backend นั้นรองรับ
- [ ] เก็บ launch command หรือ UI settings ที่ใช้ load `unsloth_LFM2-350M_1779162226`
- [ ] ระบุว่า LoRA serving path รองรับ server-side constrained decoding หรือเป็นแค่ client-side validation
- [ ] ระบุ model alias ที่ request เช่น `current` หรือ `lfm2-security-triage`
- [ ] ระบุ response model ที่ endpoint รายงานกลับมา เพื่อจับ alias drift

Deliverables:

- `reports/structured-output-backend-inventory.md`
- `docs/output-structure-fix/phase-1-backend-inventory.md`
- ส่วน `Runtime Metadata` ใน smoke report ทุกไฟล์

Pass condition:

- อ่าน report แล้วตอบได้ว่า run นี้ยิง backend อะไร รุ่นไหน ด้วย structured-output mode อะไร

## Phase 2: Probe Hardening

สถานะ: ต้องเพิ่ม probe ให้แยกว่า constrained decoding จริงหรือแค่ validation หลัง generate

Checklist:

- [ ] เพิ่ม option ใน `scripts/probe_openai_structured_output.py` เพื่อใส่ adversarial format instruction เช่นขอให้ตอบใน markdown fence
- [ ] เพิ่ม option ให้ probe หลาย sample จาก `data/splits/smoke-output-contract.jsonl` ในคำสั่งเดียว แต่ยังบันทึก per-sample raw output
- [ ] ให้ probe print `requested_model`, `response_model`, `mode`, `provider schema mode`, latency และ validation result
- [ ] เพิ่ม run mode ที่บังคับ output path แยก ไม่เขียนทับ `reports/openai-compatible-eval.json`
- [ ] เพิ่ม debug-only JSON extraction report ถ้าจำเป็น แต่ห้ามเอา extraction result ไปนับเป็น main metric

Deliverables:

- patch ใน `scripts/probe_openai_structured_output.py`
- smoke probe output เช่น `reports/structured-output-probe-current.md`

Pass condition:

- ถ้า adversarial prompt ขอ markdown fence แต่ backend เป็น constrained decoder จริง output ต้องยังเริ่มด้วย `{` และจบด้วย `}`

## Phase 3: Runtime Capability Matrix

สถานะ: เป็นแกนของรอบแก้ปัญหานี้

ให้ทดสอบด้วย smoke split เดียวกันและ schema เดียวกันทุก runtime/mode

| Candidate | What to test | Expected finding | Status |
| --- | --- | --- | --- |
| Current endpoint + `responses_parse` | ยืนยัน baseline 1/5 ด้วย output path แยก | validation-after-generation ยังไม่พอ | Pending |
| Current endpoint + `json_schema` | ดูว่า backend honor schema หรือ ignore/fallback | ถ้ายังมี markdown fence แปลว่าไม่ enforce จริง | Pending |
| vLLM `structured_outputs` | ใช้ syntax ปัจจุบันของ vLLM แทนพึ่ง `guided_json` | ควรบล็อก markdown/prose ได้ถ้า server รองรับจริง | Pending |
| SGLang XGrammar | ใช้ JSON schema ผ่าน structured output backend | candidate สำรองที่น่าทดสอบถ้า vLLM path ไม่ชัด | Pending |
| LM Studio/Ollama schema mode | local diagnostic เร็วถ้ามี model/runtime พร้อม | แยก model behavior จาก current endpoint behavior | Optional |
| Larger model diagnostic | model 7B/8B ที่ structured-output-friendly | แยก model capacity issue ออกจาก runtime issue | Optional |

Deliverables:

- `reports/structured-output-capability-matrix.md`
- mode-specific JSON/MD report อย่างน้อยสำหรับ current endpoint และหนึ่ง constrained-decoding candidate

Pass condition:

- มีอย่างน้อยหนึ่ง runtime/mode ที่ smoke contract ผ่าน 5/5 โดยไม่ต้อง JSON extraction

Fail condition:

- ทุก runtime ยังปล่อย markdown fence/prose หรือ schema fail จำนวนมาก แปลว่าต้องเลือกว่าจะเปลี่ยน serving stack, เพิ่ม validation-retry fallback หรือเปลี่ยน model candidate

## Phase 4: Contract Gate

สถานะ: gate นี้ต้องผ่านก่อนดู semantic quality

Smoke command pattern:

```bash
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_MODEL=current \
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-smoke.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-smoke.md \
  --no-progress
```

หมายเหตุ: คำสั่งนี้เป็น pattern ไม่ใช่คำสั่งรับประกันว่าจะใช้ได้กับทุก backend ต้องตั้ง env/mode ให้ตรงกับ runtime จริงก่อน

Gate:

- [ ] `json_parse_success_rate = 1.0`
- [ ] `schema_success_rate = 1.0`
- [ ] `invalid_output_count = 0`
- [ ] label อยู่ใน enum ทั้งหมด
- [ ] required fields ครบทุก sample
- [ ] raw output ไม่มี markdown fence หรือ prose wrapper

ถ้าไม่ผ่าน:

- หยุดก่อน fixed split
- อ่าน raw output per sample
- แยกว่า fail จาก runtime ไม่ enforce, schema incompatibility, missing field, invalid enum หรือ token truncation

ถ้าผ่าน:

- ไป Phase 5 mini semantic eval

## Phase 5: Mini Semantic Eval

สถานะ: ทำหลัง contract gate ผ่านเท่านั้น

Checklist:

- [ ] สร้าง mini eval split 20-25 samples จาก validation/dev data หรือ smoke-extension ที่ไม่ใช่ `data/splits/test.jsonl`
- [ ] รัน evaluator ด้วย runtime/mode ที่ผ่าน contract gate
- [ ] ตรวจ per-label confusion โดยเฉพาะ SQLi vs brute force, traversal vs failed login, port scan vs normal
- [ ] ตรวจ severity drift เช่น over-escalate เป็น `high`
- [ ] ตรวจ evidence ว่าเป็น substring จาก log ไม่ใช่ชื่อไฟล์หรือคำทั่วไป
- [ ] บันทึก latency และ retry count ถ้ามี retry loop

Pass condition:

- output contract ยังผ่าน `1.0`
- semantic errors ถูกจัดกลุ่มได้ชัดพอว่าต้องแก้ dataset, schema wording, model capacity หรือ training format

Deliverables:

- `reports/openai-compatible-{runtime}-{mode}-mini-semantic-eval.json`
- `reports/openai-compatible-{runtime}-{mode}-mini-semantic-eval.md`
- error taxonomy note ใน model-output page ใหม่หรือ report

## Phase 6: Decide V3 Training Or Runtime Change

สถานะ: decision point

ถ้า contract fail เพราะ runtime:

- เปลี่ยน serving runtime หรือ config ก่อน
- อย่า retrain เป็นคำตอบหลัก

ถ้า contract ผ่านแต่ semantics fail:

- เตรียม v3 training data
- assistant output ต้องเป็น raw JSON object เท่านั้น
- เพิ่ม hard cases ที่ v2 สับ label
- เพิ่ม examples ที่บังคับ field completeness
- ปรับ schema descriptions/key wording เพื่อช่วย semantics
- retrain ด้วย prompt/render format เดียวกับ evaluator

ถ้า LFM2-350M ยังอ่อนแม้ runtime ดี:

- เก็บ LFM2-350M เป็น resource-constrained baseline
- รัน diagnostic กับ model ใหญ่กว่า 7B/8B เพื่อดู model capacity
- ยังต้องใช้ smoke gate เดียวกัน

## Phase 7: Fixed Split Comparison

สถานะ: ทำท้ายสุดเท่านั้น

Prerequisites:

- [ ] Smoke contract ผ่าน 5/5
- [ ] Mini semantic eval มี error profile ที่เข้าใจได้
- [ ] ไม่มีการใช้ `data/splits/test.jsonl` ใน tuning/retry/prompt iteration
- [ ] report path แยกชัดเจน

Run:

```bash
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/test.jsonl \
  --out reports/finetuned-eval.json \
  --comparison-out reports/comparison.md
```

Deliverables:

- `reports/finetuned-eval.json`
- updated `reports/comparison.md`
- Day 6 error analysis ราย label

Pass condition:

- report บอกตรง ๆ ว่า fine-tuned model ชนะหรือแพ้ heuristic baseline ตรงไหน
- มีตัวอย่าง error 3-5 เคส
- ไม่มี overclaim ว่า model ยืนยัน compromise ได้

## Immediate Next Tasks

งานที่ควรเริ่มก่อนที่สุด:

1. ตั้งชื่อ report path แยกสำหรับ current `responses_parse` smoke และ rerun เพื่อ preserve metadata
2. เก็บ backend inventory: runtime, version, launch settings, model alias และ response model
3. เพิ่ม adversarial format option ใน `scripts/probe_openai_structured_output.py`
4. รัน current endpoint ด้วย adversarial probe เพื่อยืนยันว่า path ปัจจุบันเป็น validate-after-generation
5. เลือก constrained-decoding candidate แรก: vLLM `structured_outputs` ถ้า backend เป็น vLLM หรือ SGLang XGrammar ถ้าพร้อมกว่า

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created structured output fix plan from the recommended next plan | `docs/structured-output-fix-plan.md` | Done |
| 2026-05-20 | Codex | Set the report path convention for structured-output smoke and mini semantic eval runs | `reports/README.md`, `docs/structured-output-fix-plan.md` | Done |
| 2026-05-20 | Codex | Completed Phase 0 evidence preservation with canonical smoke artifacts, split checksums, and a run artifact register | `reports/openai-compatible-unsloth-studio-json-schema-smoke.json`, `reports/openai-compatible-unsloth-studio-json-schema-smoke.md`, `reports/frozen-splits.sha256`, `reports/structured-output-run-artifacts.md` | Done |
| 2026-05-20 | Codex | Started Phase 1 by creating phase-detail notes and backend inventory report template | `docs/output-structure-fix/`, `reports/structured-output-backend-inventory.md` | In progress |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-20 | ใช้ smoke contract gate เป็นประตูก่อน fixed split | ผลล่าสุดยัง JSON/schema success เพียง `0.2` ถ้าไป fixed split ตอนนี้จะปน output-contract failure กับ model-quality failure | Day 6 comparison ต้องรอให้ contract ผ่านก่อน |
| 2026-05-20 | แยก runtime capability matrix ออกจาก retrain v3 | ถ้า backend ยังไม่ได้ constrained decoding จริง retrain อาจยังหลุด markdown/prose อยู่ดี | งานถัดไปเริ่มจาก backend inventory และ constrained-decoding probe |
| 2026-05-20 | Validation/retry เป็น fallback ไม่ใช่ metric workaround | retry ช่วย production ได้ แต่ถ้าใช้กลบ invalid output จะทำให้ evaluator มองไม่เห็นปัญหาจริง | ต้องรายงาน retry count และ invalid count แยก |
| 2026-05-20 | ใช้ mode-specific report paths สำหรับ smoke รอบใหม่ | path กลางอย่าง `openai-compatible-eval.json` ถูก overwrite ง่ายและทำให้เทียบ mode ย้อนหลังยาก | smoke/mini eval รอบใหม่ต้องมี runtime และ mode อยู่ในชื่อไฟล์ |
| 2026-05-20 | แยก phase-detail docs ใต้ `docs/output-structure-fix/` | Phase 1 เป็นต้นไปต้องมีรายละเอียดคำสั่ง หลักฐาน และผลลัพธ์ต่อ phase มากกว่า master plan | master plan ใช้เป็น overview ส่วน execution detail ไปอยู่ในหน้า phase เฉพาะ |

## Related pages

- [[structured-output-reliability-research-2026]]
- [[output-structure-fix/README]]
- [[output-contract-hardening]]
- [[model-output/v2-lfm2-350m-security-triage-responses-parse]]
- [[Day6]]
- [[evaluation-metrics-rationale]]
- [[triage-output-schema]]

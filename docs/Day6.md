# Day 6: GPU Training, Fine-Tuned Evaluation And Comparison Report

**Summary**

วันที่หกเริ่มจากเติม GPU training implementation ใน `ml/unsloth/train_lora.py` ก่อน จากนั้นค่อยเอา fine-tuned adapter ที่ได้มาวัดกับ fixed test split เดียวกับ baseline แล้วเขียน comparison report แบบตรงไปตรงมา เป้าหมายคืออธิบายให้ได้ว่า fine-tune ช่วยตรงไหน ยังพลาดตรงไหน และควรปรับ dataset หรือ prompt อย่างไรต่อ

**Sources**

- `docs/poc-plan.md` สำหรับ evaluation plan และ report format (source: docs/poc-plan.md)
- `AGENTS.md` สำหรับ evaluation rules และคำเตือนเรื่อง overclaim (source: AGENTS.md)
- `docs/References.md` สำหรับ lm-evaluation-harness, SigmaHQ และ Unsloth mapping (source: docs/References.md)
- `docs/Day5.md` สำหรับ fine-tuning path ที่เตรียมไว้ก่อน Day 6 (source: docs/Day5.md)
- `docs/fine-tuning-notes.md` สำหรับ GPU/Colab notes, limitation และ Day 6 handoff (source: docs/fine-tuning-notes.md)
- `ml/unsloth/train_lora.py` สำหรับ GPU training body, split guard และ Unsloth-first training path (source: ml/unsloth/train_lora.py)
- `ml/unsloth/inference.py` สำหรับ local adapter inference และ raw-output debug flag (source: ml/unsloth/inference.py)
- `ml/unsloth/merge_adapter.py` สำหรับ merge/export path หลัง adapter พร้อม serve/export (source: ml/unsloth/merge_adapter.py)
- `ml/unsloth/config.example.yaml` สำหรับ model, LoRA, training และ output config (source: ml/unsloth/config.example.yaml)
- `reports/openai-finetune-eval.md` สำหรับ smoke/debug evaluation ล่าสุดของ OpenAI-compatible fine-tuned endpoint (source: reports/openai-finetune-eval.md)
- `docs/model-output/v1-lfm2-350m-security-triage.md` สำหรับบันทึก behavior, failure modes และ decision ของ model version 1 (source: docs/model-output/v1-lfm2-350m-security-triage.md)
- `docs/structured-output-reliability-research-2026.md` สำหรับ research note ล่าสุดหลัง smoke ยังผ่าน output contract เพียง 1/5 และแนวทาง constrained decoding ถัดไป (source: docs/structured-output-reliability-research-2026.md)
- `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md` สำหรับ v3.4 failure slice, boundary repair supplement, split/config และ gate ก่อน fixed split (source: docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md)
- `llm-wiki/SKILL.md` สำหรับ log append-only และ related pages (source: SKILL.md)

**Last updated**

2026-05-22

## Goal

ทำ GPU train รอบแรกให้ได้ LoRA adapter ก่อน แล้วสร้างผลเทียบ baseline vs fine-tuned model ที่มีตัวเลข, error analysis และข้อสรุปที่เอาไปคุยกับ stakeholder ได้

## Scope

- เติม GPU training implementation ใน `ml/unsloth/train_lora.py`
- รัน train ด้วย `ml/unsloth/config.example.yaml`
- smoke test LoRA adapter ด้วย `ml/unsloth/inference.py`
- รัน evaluator กับ fine-tuned adapter หรือ endpoint ที่ expose แบบ OpenAI-compatible
- เขียน `reports/finetuned-eval.json`
- update `reports/comparison.md`
- วิเคราะห์ false positive และ false negative
- ตรวจ evidence quality
- บันทึก limitation และ next experiment

## Checklist

- [x] เติม GPU training implementation ใน `ml/unsloth/train_lora.py`
- [x] รัน training short trial ด้วย config รอบแรก
- [x] save LoRA adapter ระหว่าง short trial ไปที่ `ml/unsloth/outputs/lfm2-350m-security-triage-lora`
- [x] smoke test adapter ด้วย `ml/unsloth/inference.py`
- [ ] รัน evaluation ด้วย fixed test split
- [x] เก็บ raw outputs เท่าที่จำเป็นสำหรับ debug
- [x] เขียน smoke/debug report ที่ `reports/openai-finetune-eval.json`
- [ ] update `reports/comparison.md`
- [ ] เพิ่มตาราง metric เทียบ heuristic, base model และ fine-tuned model
- [ ] เพิ่ม error analysis ราย label
- [x] เพิ่ม note ว่า dataset เป็น synthetic ใน fine-tuning notes
- [x] ระบุ next dataset/prompt improvements ใน fine-tuning notes

## Current Status

Day 6 ทำ wiring หลักของ training และ inference แล้ว: `train_lora.py` มี GPU training body, split guard, tokenizer chat-template formatting และ save path สำหรับ LoRA adapter ส่วน `inference.py` โหลด base model + LoRA adapter และ validate output กับ schema เดิมได้ (source: ml/unsloth/train_lora.py, ml/unsloth/inference.py)

มีการ validate short trial 30 steps แล้วและบันทึกใน fine-tuning notes ว่า training loop train และ save adapter ได้ แต่ output จาก inference ยังไม่เสถียรพอสำหรับ schema-valid JSON ทุกครั้ง (source: docs/fine-tuning-notes.md)

มี smoke/debug evaluation ของ `openai-finetune` แล้วที่ `reports/openai-finetune-eval.json` และ `reports/openai-finetune-eval.md`; historical run นั้นใช้ `data/raw/test.jsonl` จำนวน 5 samples และผลล่าสุดคือ JSON/schema validity ยังเป็น 0 กับ invalid output 5/5 เพราะ endpoint ตอบข้อความอธิบายแทน JSON object ที่ parse ได้ (source: reports/openai-finetune-eval.md)

บันทึก behavior ของ model version 1 ถูกแยกไว้ที่ `docs/model-output/v1-lfm2-350m-security-triage.md` เพื่อเก็บ config snapshot, API/local inference failure modes และ decision ว่า v1 ยังไม่ควร promote เพราะ output contract ไม่ผ่าน (source: docs/model-output/v1-lfm2-350m-security-triage.md)

เริ่มมี output-contract hardening path สำหรับรอบถัดไปแล้ว: prompt contract ถูกยกเป็น `triage-json-v2`, OpenAI-compatible adapter รองรับ strict `json_schema` พร้อม schema sanitizer/fallback แบบจำกัด, และมี deterministic smoke split ใหม่ที่ `data/splits/smoke-output-contract.jsonl` สำหรับเช็ก output contract ก่อนวิ่ง fixed split เต็ม (source: scripts/model_adapters/prompt_contract.py, scripts/model_adapters/openai_compatible.py, data/splits/smoke-output-contract.jsonl)

ยังไม่ถือว่า Day 6 comparison เสร็จ เพราะยังไม่ได้รัน fine-tuned evaluation บน fixed split หลัก `data/splits/test.jsonl` จำนวน 75 samples และยังไม่ได้อัปเดต `reports/comparison.md` ให้เทียบ heuristic/base/fine-tuned แบบครบชุด (source: docs/poc-plan.md, reports/comparison.md)

หลังแก้ prompt/adapter/SDK path และลอง smoke แล้ว ผลยังไม่ดีขึ้น: persisted smoke report ล่าสุดยังอยู่ที่ JSON/schema success `0.2` และ invalid output `4/5` จึงควรถือว่า bottleneck ตอนนี้คือ runtime enforcement มากกว่าการเขียน prompt เพิ่มอย่างเดียว งานถัดไปถูกย้ายไปพิสูจน์ server-side constrained decoding เช่น vLLM `structured_outputs` หรือ SGLang XGrammar ก่อน retrain หรือ fixed-split comparison (source: reports/openai-compatible-eval.json, source: docs/structured-output-reliability-research-2026.md)

อัปเดตล่าสุดของ Phase 6 หลัง vLLM constrained decoding และ evidence constraints ผ่านแล้วคือ semantic quality ยังเป็น blocker: v3.3 temp 0.3 hard-contrast probe ได้ `label_accuracy=0.64` แต่ SQLi ยังถูก `2/10` และ port scan `6/10` จึงสร้าง v3.4 failure slice และ v3.4 boundary repair training artifacts แล้ว ได้แก่ 160-record supplement, 710-record train split, 75-record validation split และ `ml/unsloth/config.v3-4.yaml`; fixed `data/splits/test.jsonl` ยังถูก hold ไว้ก่อน Phase 7 (source: docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md, source: data/splits/train-v3-4-boundary-repair.jsonl)

## Acceptance Criteria

- baseline และ fine-tuned ใช้ test split เดียวกัน
- training ไม่อ่าน `data/splits/test.jsonl`
- มี LoRA adapter output หรือบันทึกชัดเจนว่ารัน GPU ไม่สำเร็จเพราะอะไร
- local inference smoke test ผ่านอย่างน้อย 1 log หรือบันทึก error ชัดเจน
- report บอก metric ครบ
- ถ้า fine-tuned แพ้บาง metric ต้องเขียนไว้ตรง ๆ
- มีตัวอย่าง error อย่างน้อย 3-5 เคส
- ไม่มีการ claim ว่า model ยืนยันการถูก hack ได้จาก log เส้นเดียว

## Work Log

Append-only log สำหรับบันทึกว่าวันนี้ทำอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created Day 6 plan page | `docs/Day6.md` | Planned |
| 2026-05-17 | Codex | Moved GPU training implementation into the first Day 6 task | `docs/Day6.md`, `docs/fine-tuning-notes.md` | Planned |
| 2026-05-18 | Codex | Added and validated the repo-native Unsloth training body with a short trial run | `ml/unsloth/train_lora.py`, `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Added raw-output debugging to checkpoint inference | `ml/unsloth/inference.py`, `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Added merge and GGUF export path for the trained adapter | `ml/unsloth/merge_adapter.py`, `docs/fine-tuning-notes.md` | Done |
| 2026-05-18 | Codex | Ran a 5-sample OpenAI-compatible fine-tuned endpoint smoke evaluation and captured the invalid-JSON failure state | `reports/openai-finetune-eval.json`, `reports/openai-finetune-eval.md` | Debugged |
| 2026-05-18 | Codex | Split v1 model behavior notes into a dedicated model-output page | `docs/model-output/v1-lfm2-350m-security-triage.md` | Done |
| 2026-05-19 | Codex | Hardened the runtime output contract before retraining | `scripts/model_adapters/prompt_contract.py`, `scripts/model_adapters/openai_compatible.py`, `frontend/lib/prompts.ts`, `data/splits/smoke-output-contract.jsonl` | Done |
| 2026-05-20 | Codex | Researched current structured-output reliability options after smoke remained 1/5 | `docs/structured-output-reliability-research-2026.md`, `reports/openai-compatible-eval.json` | Done |
| 2026-05-22 | Codex | Prepared v3.4 boundary repair training artifacts after v3.3 canary remained below gate | `reports/phase-6-v3-4-boundary-failure-slice.json`, `scripts/create_v3_4_boundary_repair_dataset.py`, `data/splits/train-v3-4-boundary-repair.jsonl`, `ml/unsloth/config.v3-4.yaml` | Prepared |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | ใช้ fixed test split เท่านั้น | comparison ต้องแฟร์และรันซ้ำได้ | ห้ามแตะ test split ระหว่าง train |
| 2026-05-16 | report ต้องบอกข้อจำกัดชัดเจน | synthetic dataset อาจทำให้ผลดูดีเกินจริง | stakeholder จะเข้าใจว่า POC ยังไม่ใช่ production detector |
| 2026-05-17 | เริ่ม Day 6 ด้วย GPU training body ก่อน evaluation | Day 5 เตรียม config, split guard, training format และ inference path แล้ว แต่ยังไม่มี adapter output ถ้าไม่ train ก่อนก็ evaluate fine-tuned model ไม่ได้ | `ml/unsloth/train_lora.py` เป็นงานแรกของ Day 6; evaluation/report ทำหลังมี adapter หรือมีเหตุผลว่าทำไม train ไม่สำเร็จ |
| 2026-05-18 | แยก smoke/debug eval ออกจาก final fixed-split comparison | endpoint ล่าสุดยังไม่คืน schema-valid JSON และ smoke split มีแค่ 5 samples | `reports/openai-finetune-eval.*` ใช้เป็น debug artifact; final comparison ยังต้องรันกับ `data/splits/test.jsonl` |
| 2026-05-18 | merge/GGUF เป็น export step หลัง quality นิ่ง | merge checkpoint ไม่ได้แก้การตอบหลุด JSON schema | ต้องแก้ prompt/training/inference behavior ก่อนใช้ merged/GGUF เป็น evaluation artifact หลัก |
| 2026-05-18 | mark v1 เป็น debug baseline ไม่ใช่ promoted model | v1 train/serve ได้ แต่ API smoke evaluation ยังเป็น invalid output 5/5 | รอบถัดไปต้องโฟกัส JSON-only output, schema completeness และ reason grounding ก่อน metric ใหญ่ |
| 2026-05-19 | เลื่อน retrain ออกไปหลัง runtime contract stabilization | ถ้า output ยังไม่ parse/schema-valid ต่อให้ train ใหม่ก็ยังแยก semantic error ออกจาก contract error ได้ยาก | รอบถัดไปต้องรัน smoke split ใหม่ด้วย `triage-json-v2` และ structured output mode ให้ผ่านก่อนค่อยตัดสินใจ retrain |
| 2026-05-20 | พิสูจน์ constrained decoding จริงก่อนแก้ prompt/retrain เพิ่ม | smoke หลังแก้ SDK/adapter ยังผ่านเพียง 1/5 แปลว่า validate-after-generation ยังไม่พอ | Day 6 next step เปลี่ยนเป็น backend capability test และ mode-specific reports ก่อน fixed split |

## Notes

วันที่หกเป็นวันที่ POC เริ่มมีน้ำหนัก เพราะมีทั้ง adapter จากการ train และตัวเลขให้คุย ถ้า train ไม่สำเร็จหรือผลยังไม่สวย ให้เก็บเป็น insight ว่า environment, dataset หรือ schema ยังต้องปรับ ไม่ต้องกลบจุดอ่อน

งานถัดไปไม่ใช่ prompt hardening เพิ่มเฉย ๆ แล้ว แต่คือพิสูจน์ว่า backend บังคับ constrained decoding จริงหรือไม่ โดยทำ mode-specific smoke reports แยก path แล้วลอง vLLM `structured_outputs`, SGLang XGrammar หรือ runtime ที่มี token-level schema/grammar enforcement ก่อน ถ้า smoke ยังไม่ถึง JSON/schema success `1.0` ให้หยุดที่ output-contract gate และยังไม่รัน fixed split (source: docs/structured-output-reliability-research-2026.md)

## Related pages

- [[Day5]]
- [[Day7]]
- [[poc-plan]]
- [[References]]
- [[model-output/v1-lfm2-350m-security-triage]]
- [[structured-output-reliability-research-2026]]

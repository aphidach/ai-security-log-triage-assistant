# Phase 6 V3 Or Runtime Decision

**Summary**

Phase 6 เป็น decision point หลัง Phase 5 พบทั้ง runtime timeout และ semantic drift ต้องแยกให้ชัดก่อนว่าจะซ่อม runtime, ทำ v3 training data, ปรับ schema/prompt หรือเทียบ model capacity

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ Phase 6 decision rules (source: docs/structured-output-fix-plan.md)
- `docs/fine-tuning-notes.md` สำหรับ Unsloth training/export context (source: docs/fine-tuning-notes.md)
- `docs/data-formats-for-llm-training.md` สำหรับ training render format rationale (source: docs/data-formats-for-llm-training.md)
- `docs/label-imbalance-and-prediction-collapse.md` สำหรับกติกาแยก source data imbalance ออกจาก prediction collapse และ v3 mitigation options (source: docs/label-imbalance-and-prediction-collapse.md)

**Last updated**

2026-05-21

## Status

Planned. เริ่มจาก Phase 5 result ที่ vLLM mini semantic eval ได้ JSON/schema `0.88`, label accuracy `0.24`, มี 3 port-scan timeouts และ prediction เอนหนักไปทาง `failed_login_bruteforce` (source: docs/output-structure-fix/phase-5-mini-semantic-eval.md)

## Goal

Phase 6 ไม่ใช่รอบ fixed test comparison จุดประสงค์คือแยก root cause ให้พอชัดก่อน:

- ถ้า fail เพราะ runtime timeout ให้แก้ serving/evaluator config ก่อน
- ถ้า fail เพราะ semantic quality ให้เตรียม v3 training data และ training render format
- ถ้า LFM2-350M ยังไม่พอ ให้เก็บเป็น baseline แล้วเทียบ model ที่ใหญ่กว่า

เมื่อจบ Phase 6 ต้องมี decision ชัดเจนหนึ่งทางหรือมากกว่า:

- `runtime_change`
- `v3_training_data`
- `schema_or_prompt_wording`
- `model_capacity_comparison`
- `ready_for_phase_7`

## Inputs From Phase 5

ใช้ข้อมูลต่อไปนี้เป็น starting point ห้ามใช้ `data/splits/test.jsonl` เพื่อจูนหรือ retry:

- mini split: `data/splits/mini-semantic-eval.jsonl`
- report JSON: `reports/openai-compatible-vllm-structured-outputs-mini-semantic-eval.json`
- report markdown: `reports/openai-compatible-vllm-structured-outputs-mini-semantic-eval.md`
- timeout samples: `sample-000437`, `sample-000458`, `sample-000485`
- timeout-only diagnostic reports:
  - `reports/openai-compatible-vllm-structured-outputs-phase6-timeout-only-timeout120.json`
  - `reports/openai-compatible-vllm-off-phase6-timeout-only.json`
  - `reports/openai-compatible-vllm-json-object-phase6-timeout-only.json`
- main semantic drift: model ทาย `failed_login_bruteforce` มากเกินไป
- main severity drift: `normal` ถูกยกระดับเป็น `high`

## Work Plan

### 1. Runtime Timeout Diagnosis

รันเฉพาะ port-scan samples ที่ timeout เพื่อดูว่า timeout เกิดซ้ำแบบ deterministic หรือเป็น runtime noise:

- `sample-000437`
- `sample-000458`
- `sample-000485`

สิ่งที่ต้องบันทึก:

- runtime: vLLM `structured_outputs`
- endpoint และ model name
- output cap: `OPENAI_COMPATIBLE_MAX_TOKENS=512`
- timeout limit ของ evaluator/client
- latency ต่อ sample
- error type เช่น `APITimeoutError`
- output ที่ได้ ถ้ามี partial output ให้เก็บไว้ใน report แต่ห้ามเอาไปนับเป็น schema pass

การตัดสินใจ:

- ถ้า timeout เกิดซ้ำเฉพาะ `port_scan_or_recon` ให้ดู prompt/log pattern และ constrained decoding behavior
- ถ้าเพิ่ม timeout แล้วผ่าน schema ได้ ให้บันทึกว่าเป็น runtime/evaluator timeout issue
- ถ้ายัง timeout แม้เพิ่ม timeout ให้ถือเป็น serving/runtime compatibility risk

Token cap note:

หลังพบว่า Phase 6 timeout-only run แรกยังไม่มี output token cap จาก client ให้รัน diagnostic รอบถัดไปด้วย adapter default `max_tokens=512` ก่อน ถ้า `structured_outputs` ยัง timeout ทั้งที่มี cap แล้ว ปัญหาจะใกล้ runtime/constrained decoding หรือ model stop behavior มากกว่า “generate ยาวไม่จำกัด”

สิ่งที่ต้องทำมี 5 ขั้น:

1. สร้าง split ย่อยเฉพาะ 3 sample

ตอนนี้ `scripts/evaluate.py` ยังไม่มี flag เลือก `--sample-id` ดังนั้นวิธีง่ายสุดคือสร้างไฟล์ JSONL ย่อย:

```bash
rtk rg --no-filename '"id": "sample-000437"|"id": "sample-000458"|"id": "sample-000485"' \
  data/splits/mini-semantic-eval.jsonl \
  > data/splits/phase6-timeout-only.jsonl
```

2. รันซ้ำด้วย vLLM `structured_outputs` และ `max_tokens=512`

เป้าคือดูว่า timeout ยังเกิดซ้ำไหมเมื่อจำกัด output length แล้ว:

```bash
OPENAI_COMPATIBLE_BASE_URL=http://192.168.8.141:8080/v1 \
OPENAI_COMPATIBLE_API_KEY=local \
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_MAX_TOKENS=512 \
rtk .venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/phase6-timeout-only.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-phase6-timeout-only-max512.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-phase6-timeout-only-max512.md
```

3. รันแบบเพิ่ม timeout และปิด retry

อันนี้ช่วยแยกว่า “timeout limit สั้นไป” หรือ “model/runtime ติดจริง” เพราะก่อนหน้า latency ประมาณ 60 วิ อาจมาจาก retry ด้วย

```bash
OPENAI_COMPATIBLE_TIMEOUT_SECONDS=120 \
OPENAI_COMPATIBLE_MAX_RETRIES=0 \
OPENAI_COMPATIBLE_MAX_TOKENS=512 \
...
```

ถ้า 120 วิแล้วผ่าน แปลว่าเป็น runtime/evaluator timeout config issue มากกว่า semantic issue

4. รันเทียบ mode ที่ไม่บังคับ schema

ลอง `OPENAI_COMPATIBLE_RESPONSE_FORMAT=off` หรือ `json_object` กับ split เดิม ถ้า mode ปกติ generate ได้เร็ว แต่ `structured_outputs` timeout แปลว่าปัญหาอยู่ที่ vLLM constrained decoding / structured output path

ถ้าทุก mode timeout เหมือนกัน อาจเป็น prompt/log pattern หรือ model generate ไม่จบ

5. บันทึกผลเป็นตาราง decision

ดู 4 อย่างต่อ sample:

- timeout เกิดซ้ำไหม
- mode ไหน timeout
- latency เท่าไหร่
- ถ้าได้ output แล้ว JSON/schema ผ่านไหม

### Case 1 Result: Port-Scan Timeout Diagnosis

Conclusion: timeout เดิมไม่ได้เกิดจาก prompt processing หรือ vLLM queue ค้างเป็นหลัก แต่เกิดจาก generation ยาว/loop เมื่อเปิด JSON-constrained mode

ผลที่เห็นจาก timeout-only split:

| Mode | Result | Interpretation |
| --- | --- | --- |
| `structured_outputs`, no output cap | client timeout around 60s per sample | OpenAI client timeout 30s + retry 1; server still generating |
| `structured_outputs`, `timeout=120`, `max_retries=0`, `max_tokens=1024` | no timeout, but `finish_reason=length`, JSON parse `0/3` | model loops until token cap and JSON is cut mid-field |
| `json_object`, default max token cap | `finish_reason=length`, JSON parse `0/3` | JSON-constrained generation also loops without full schema |
| `off` | `finish_reason=stop`, raw output starts with correct `port_scan_or_recon` label | model understands the broad label, but output contract is still wrong because it uses markdown fence and misses required fields |

Raw-output pattern:

- `structured_outputs` and `json_object` start with the right label, then loop inside `evidence`
- repeated evidence tokens include `port_scan_or_recon` and `blocked`
- the current schema allows `evidence` as an unbounded array of strings, and the provider schema sanitizer currently strips some JSON Schema constraint keywords such as `minLength`

Decision:

- Do not move to Phase 7.
- Do not treat this as only a timeout setting issue.
- Start [[output-structure-fix/phase-6-1-evidence-constraints]] to tighten the `evidence` schema and preserve the new constraint keywords in the OpenAI-compatible adapter sanitizer before rerunning smoke/mini diagnostics.

### Case 1 Follow-Up: Phase 6.1 Result

Phase 6.1 fixed the runtime/output-contract side of the port-scan loop:

| Rerun | Split | JSON/schema | Invalid outputs | Main result |
| --- | --- | ---: | ---: | --- |
| Timeout-only | `data/splits/phase6-timeout-only.jsonl` | `1.0 / 1.0` | `0` | `label_accuracy = 1.0`, all `finish_reason=stop` |
| Smoke | `data/splits/smoke-output-contract.jsonl` | `1.0 / 1.0` | `0` | output contract gate restored, `label_accuracy = 0.2` |
| Mini semantic eval | `data/splits/mini-semantic-eval.jsonl` | `1.0 / 1.0` | `0` | `label_accuracy = 0.36`, predicted `failed_login_bruteforce` remains `20/25` |

Decision:

- Runtime/schema loop is no longer the blocker for these diagnostic splits.
- Semantic quality is now the blocker.
- Do not move to fixed `data/splits/test.jsonl` yet.
- Continue Phase 6 with semantic error taxonomy, hard contrast examples, v3 training data decision, and/or model-capacity diagnostic.




### 2. Semantic Error Profile

สรุป per-label confusion จาก Phase 5 ให้เป็น taxonomy ที่เอาไปแก้ dataset ได้:

- `normal` ถูกทายเป็น suspicious หรือ severity `high`
- `sql_injection_attempt` ถูกทายเป็น `failed_login_bruteforce`
- `directory_traversal_attempt` ถูกทายเป็น `failed_login_bruteforce`
- `port_scan_or_recon` timeout หรือถูกทายเป็น `failed_login_bruteforce`
- evidence เป็น substring แล้วหรือยัง แต่เลือก token ที่มีความหมายพอไหม

ผลลัพธ์ที่ต้องได้:

- ตาราง expected label → predicted label
- รายการ hard cases สำหรับ v3
- สรุปว่า error เกิดจาก label boundary, prompt wording, schema wording, training format หรือ model capacity
- ถ้า source split ยัง balanced แต่ predicted labels เอนหนักไป label เดียว ให้ถือเป็น prediction collapse และใช้ [[label-imbalance-and-prediction-collapse]] เป็น decision guide ก่อนลดจำนวน data ของ label นั้น

### Phase 6.1 Semantic Error Taxonomy Artifact

สร้าง HTML infographic report แล้วที่ `reports/phase-6-semantic-error-taxonomy-infographic.html` จาก `reports/openai-compatible-vllm-structured-outputs-phase6-1-mini-semantic-eval.json`

Key findings:

- mini eval ยังเป็น balanced split: expected label ละ 5 ตัวอย่าง
- predicted distribution เอนไป `failed_login_bruteforce` 20/25
- `label_accuracy = 0.36`, แต่ `json_parse_success_rate = 1.0`, `schema_success_rate = 1.0`, `invalid_output_count = 0`
- error หลักคือ label boundary และ data coverage; training format ยังเป็น low-risk แต่ต้อง verify rendered chat-template examples ก่อน retrain v3
- v3 backlog ควรเน้น hard contrast examples ไม่ใช่เพิ่ม synthetic data แบบสุ่ม

### V3 Model Mini Eval Result

รอบ v3 model ที่ train ด้วย `data/splits/train-v3-hard-contrast.jsonl` ยังไม่ผ่าน mini semantic eval:

| Metric | Value |
| --- | ---: |
| `label_accuracy` | `0.36` |
| `json_parse_success_rate` | `0.92` |
| `schema_success_rate` | `0.92` |
| `invalid_output_count` | `2` |
| predicted `failed_login_bruteforce` | `17/25` |

per-label result:

| Expected label | Correct | Main wrong prediction |
| --- | ---: | --- |
| `normal` | `0/5` | `failed_login_bruteforce` 3, `sql_injection_attempt` 1, invalid 1 |
| `failed_login_bruteforce` | `4/5` | invalid 1 |
| `sql_injection_attempt` | `1/5` | `failed_login_bruteforce` 4 |
| `directory_traversal_attempt` | `1/5` | `failed_login_bruteforce` 4 |
| `port_scan_or_recon` | `3/5` | `failed_login_bruteforce` 2 |

Decision: v3 ยังแก้ prediction collapse ไม่พอ และยังมี prompt mismatch ระหว่าง train config (`triage-json-v2`) กับ runtime/eval (`triage-json-v2.1`) จึงต้องทำ v3.1 recovery ก่อน fixed test split (source: reports/openai-compatible-vllm-structured-outputs-v3-model-mini-semantic-eval.json, ml/unsloth/config.example.yaml)

### V3.1 Recovery Step

v3.1 recovery ทำสองอย่างก่อน train ใหม่:

- align `format.prompt_version` ใน `ml/unsloth/config.example.yaml` ให้ตรงกับ runtime prompt contract `triage-json-v2.1`
- สร้าง weighted hard-contrast split ด้วย `scripts/create_v3_1_training_split.py`: canonical train 350 records + hard contrast weighted 150 records รวมเป็น 500 records หรือ label ละ 100 โดย validation ยังเป็น 75 records หรือ label ละ 15 และ fixed `data/splits/test.jsonl` ไม่ถูกอ่านหรือแก้

ตรวจ preflight ได้ด้วย:

```bash
rtk .venv/bin/python scripts/create_v3_1_training_split.py
rtk .venv/bin/python ml/unsloth/train_lora.py --preflight-only
```

### 3. Training Format Check

ตรวจว่า training/render format ตรงกับ evaluator ที่ใช้จริง:

- source record ยังเป็น `instruction/input/output`
- assistant message ตอน SFT ต้อง render เป็น raw JSON object เท่านั้น
- หลีกเลี่ยง markdown fence, prose ก่อน/หลัง JSON, หรือ key ที่ไม่อยู่ใน schema
- prompt ใน training ควรใกล้กับ prompt contract ของ evaluator

ถ้าพบว่า training output format ไม่ตรงกับ evaluator ให้แก้ format ก่อน retrain v3

### 4. V3 Training Data Plan

ถ้า semantic drift เป็นปัญหาหลัก ให้เตรียม v3 data แบบเจาะจุด:

- เพิ่ม normal hard negatives ที่คล้าย failed login แต่ไม่ใช่ brute force
- เพิ่ม SQLi examples ที่ evidence ชัด เช่น quote, tautology, union/select pattern
- เพิ่ม directory traversal examples ที่มี `../`, encoded traversal, path probing
- เพิ่ม port scan/recon examples ที่ evidence สั้นและชัด
- เพิ่ม paired contrast examples เช่น log คล้ายกันแต่ label ต่างกัน
- ตรวจทุก output ให้ครบ field ตาม schema

เป้าหมายไม่ใช่เพิ่ม data เยอะที่สุด แต่เพิ่ม case ที่ชนกับ confusion ของ Phase 5 โดยตรง

### Phase 6 V3 Hard Contrast Dataset Artifact

สร้าง v3 hard contrast training supplement แล้ว:

```text
scripts/create_v3_hard_contrast_dataset.py
data/generated/v3-hard-contrast-security-triage.jsonl
docs/output-structure-fix/phase-6-v3-hard-contrast-dataset.md
```

ชุดนี้มี 50 records แบบ balanced label ละ 10 records และเน้น:

- normal hard negatives เช่น single failed login, benign `select`/`union`/`sleep` search และ single connection
- brute-force positives ที่ทำ paired contrast กับ normal เช่น `failed_attempts=12`, `failures=18`, `count=16`
- SQLi payload ชัด เช่น quote, tautology, `UNION SELECT`, `SLEEP(`, `information_schema`
- traversal ทั้ง `../`, encoded traversal, Unix sensitive path และ Windows path
- port scan/recon signal เช่น `unique_ports`, `nmap fingerprint`, `SYN scan detected`

ใช้เป็น training supplement เท่านั้น ห้ามนำไปปน validation/test และยังไม่ควรใช้ `data/splits/test.jsonl` จนกว่า v3 จะผ่าน smoke + mini semantic eval ใหม่

### 5. Schema And Prompt Wording Check

ถ้า model สับ label เพราะคำอธิบายไม่ชัด ให้ปรับ wording โดยไม่เปลี่ยน schema shape:

- label definition ต้องแยก failed login, SQLi, traversal, port scan ให้คมขึ้น
- evidence instruction ต้องบอกให้เลือก substring ที่เป็น signal จริง
- severity instruction ต้องกันไม่ให้ `normal` ถูก escalate เป็น `high`

ถ้ามีการปรับ schema descriptions หรือ prompt ต้องกลับไปรัน smoke gate ก่อน mini eval อีกครั้ง

### 6. Model Capacity Diagnostic

ถ้า runtime ดีแล้ว format ถูกแล้ว แต่ LFM2-350M ยัง collapse ไปที่ `failed_login_bruteforce`:

- เก็บ LFM2-350M เป็น resource-constrained baseline
- เลือก model 7B/8B หนึ่งตัวสำหรับ diagnostic เท่านั้น
- ใช้ smoke split และ mini semantic eval เดิม
- ห้ามใช้ fixed `test.jsonl` จนกว่าจะผ่าน contract และเข้าใจ error profile

## Phase 6 Checklist

- [x] Rerun timeout-only diagnostic สำหรับ `sample-000437`, `sample-000458`, `sample-000485`
- [x] บันทึกว่า timeout เป็น runtime/config issue หรือ model behavior
- [x] ทำ semantic error taxonomy จาก Phase 5/Phase 6.1 mini eval reports
- [x] สรุป hard cases ที่ต้องเพิ่มใน v3
- [ ] ตรวจ training render format ว่า assistant output เป็น raw JSON object
- [ ] ตัดสินใจว่าต้องปรับ schema/prompt wording หรือไม่
- [ ] ตัดสินใจว่าจะ retrain v3 หรือเทียบ model capacity ก่อน
- [ ] บันทึก decision ก่อนเริ่ม Phase 7

## Exit Criteria

จะออกจาก Phase 6 ได้เมื่อมีอย่างน้อยหนึ่ง decision ที่ตรวจสอบได้:

- runtime/config fix พร้อม rerun plan
- v3 training data plan พร้อม hard-case list
- schema/prompt wording patch พร้อม smoke rerun plan
- model capacity diagnostic plan พร้อม candidate runtime

ยังไม่ควรเริ่ม Phase 7 จนกว่า:

- output contract กลับมาผ่าน `1.0` บน smoke และไม่เจอ timeout ที่อธิบายไม่ได้บน mini eval
- semantic error profile ถูกจัดกลุ่มแล้ว
- ไม่มีการใช้ `data/splits/test.jsonl` ระหว่าง tuning, retry หรือ prompt iteration

## Decision Rules

ถ้า contract fail เพราะ runtime:

- เปลี่ยน serving runtime หรือ config ก่อน
- ห้ามให้ retrain v3 เป็นคำตอบหลัก

ถ้า contract ผ่านแต่ semantics fail:

- เตรียม v3 training data
- assistant output ต้องเป็น raw JSON object เท่านั้น
- เพิ่ม hard cases ที่ v2 สับ label
- เพิ่ม examples ที่บังคับ field completeness
- ปรับ schema descriptions/key wording ถ้าช่วย semantics ได้
- retrain ด้วย prompt/render format เดียวกับ evaluator

ถ้า LFM2-350M ยังอ่อนแม้ runtime ดี:

- เก็บ LFM2-350M เป็น resource-constrained baseline
- รัน diagnostic กับ model ใหญ่กว่า 7B/8B
- ใช้ smoke gate เดียวกันกับทุก candidate

## Decision Log

| Date | Decision | Rationale | Consequence |
| --- | --- | --- | --- |
| 2026-05-20 | Do Phase 6 before fixed test comparison | Phase 5 mini eval found 3 runtime timeouts and strong semantic collapse toward `failed_login_bruteforce` | Next work must separate runtime/config issues from v3 data, schema/prompt wording, and model capacity before Phase 7 |
| 2026-05-20 | Start Phase 6.1 evidence constraints | Timeout-only diagnostics show `off` mode stops with the right broad label, while `json_object` and `structured_outputs` loop inside unbounded `evidence` until `finish_reason=length` | Tighten `evidence` constraints and adapter schema sanitizer before deciding whether to retrain v3 |
| 2026-05-21 | Treat current label skew as prediction collapse unless source distribution changes | Generated, train, validation, test, smoke, and mini semantic splits are label-balanced; the skew appears in predictions, especially toward `failed_login_bruteforce` | Do not downsample the existing balanced training split just to fight Phase 5 prediction skew; use confusion analysis, hard contrast examples, balanced sampling policy, and imbalance-aware metrics |
| 2026-05-21 | Move Phase 6 focus from runtime loop to semantic quality | Phase 6.1 timeout-only, smoke, and mini reruns all have JSON/schema `1.0`, invalid output `0`, and no `finish_reason=length`, but mini label accuracy is still `0.36` | Next work should build v3 hard cases or run a model-capacity diagnostic before fixed-split comparison |

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 6 detail stub | `docs/output-structure-fix/phase-6-v3-or-runtime-decision.md` | Drafted |
| 2026-05-20 | Codex | Added Phase 6 execution plan from Phase 5 findings | `docs/output-structure-fix/phase-5-mini-semantic-eval.md` | Planned |
| 2026-05-20 | Codex | Added OpenAI-compatible output token cap for Phase 6 timeout diagnosis | `scripts/model_adapters/openai_compatible.py`, `.env.example` | Adapter now sends `max_tokens=512` / `max_output_tokens=512` by default |
| 2026-05-20 | Codex | Recorded Phase 6 case 1 conclusion and linked Phase 6.1 | `reports/openai-compatible-vllm-structured-outputs-phase6-timeout-only-timeout120.json`, `reports/openai-compatible-vllm-off-phase6-timeout-only.json`, `reports/openai-compatible-vllm-json-object-phase6-timeout-only.json` | Evidence loop identified in JSON-constrained modes |
| 2026-05-21 | Codex | Linked Phase 6 semantic skew analysis to the label imbalance guidance page | `docs/label-imbalance-and-prediction-collapse.md` | Phase 6 now distinguishes source imbalance from prediction collapse |
| 2026-05-21 | User/Codex | Recorded Phase 6.1 rerun results and semantic blocker | `reports/openai-compatible-vllm-structured-outputs-phase6-1-evidence-constraints.json`, `reports/openai-compatible-vllm-structured-outputs-phase6-1-smoke.json`, `reports/openai-compatible-vllm-structured-outputs-phase6-1-mini-semantic-eval.json` | Output contract restored; semantic collapse remains |
| 2026-05-21 | Codex | Added Phase 6 semantic error taxonomy infographic report | `reports/phase-6-semantic-error-taxonomy-infographic.html`, `reports/openai-compatible-vllm-structured-outputs-phase6-1-mini-semantic-eval.json` | HTML report summarizes metrics, label distribution, confusion matrix, root-cause taxonomy, and v3 backlog |
| 2026-05-21 | Codex | Created v3 hard contrast training supplement | `scripts/create_v3_hard_contrast_dataset.py`, `data/generated/v3-hard-contrast-security-triage.jsonl`, `docs/output-structure-fix/phase-6-v3-hard-contrast-dataset.md` | Adds 50 balanced hard contrast records for v3 training without touching validation or fixed test split |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-5-mini-semantic-eval]]
- [[output-structure-fix/phase-6-1-evidence-constraints]]
- [[output-structure-fix/phase-6-v3-hard-contrast-dataset]]
- [[label-imbalance-and-prediction-collapse]]
- [[structured-output-fix-plan]]

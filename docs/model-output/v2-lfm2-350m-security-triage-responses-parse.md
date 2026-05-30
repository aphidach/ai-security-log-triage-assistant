# V2 LFM2-350M Security Triage Responses Parse Smoke

**Summary**

หน้านี้บันทึกผล output-contract smoke ของ artifact `unsloth_LFM2-350M_1779162226` หรือ `v2` หลังจากย้าย OpenAI-compatible adapter จาก LangChain runtime มาเป็น OpenAI Python SDK + Pydantic `responses_parse` path แล้ว ผลวันนี้ยังไม่ผ่านเกณฑ์ output contract: smoke 5 samples ผ่าน JSON/schema ได้เพียง 1 sample, อีก 4 samples ยังตอบเป็น markdown-fenced JSON ทำให้ Pydantic parse ตกตั้งแต่ตัวอักษรแรก

ข้อสรุปหลักคือ `responses_parse` ช่วยให้ failure ชัดขึ้นว่าเป็น invalid JSON หรือ validation error แต่ endpoint/backend นี้ยังไม่ได้บังคับ generation ให้เป็น JSON object ล้วนแบบ constrained decoding จริง จึงยังไม่ควรใช้ผลนี้เป็น fixed-split comparison หรือ claim ว่า model พร้อมใช้งาน

**Sources**

- `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json` สำหรับ persisted smoke report ล่าสุดที่เขียนทับ path มาตรฐานของ `openai-compatible` adapter (source: reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json)
- `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.md` สำหรับ markdown summary ของ smoke report ล่าสุด (source: reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.md)
- `scripts/model_adapters/openai_compatible.py` สำหรับ OpenAI SDK adapter, `responses_parse` mode และ Pydantic validation model (source: scripts/model_adapters/openai_compatible.py)
- `docs/output-contract-hardening.md` สำหรับ decision ที่ย้ายจาก LangChain parser path ไป OpenAI SDK + Pydantic runtime path (source: docs/output-contract-hardening.md)
- `data/splits/smoke-output-contract.jsonl` สำหรับ deterministic 5-sample output-contract smoke split (source: data/splits/smoke-output-contract.jsonl)
- `data/schemas/triage-output.schema.json` สำหรับ canonical output schema ของ repo (source: data/schemas/triage-output.schema.json)
- Unsloth Studio run note วันที่ 2026-05-19 สำหรับ artifact `unsloth_LFM2-350M_1779162226`, instruction tuning files และ LoRA 16-bit load profile (source: user-provided Codex thread note, 2026-05-19)
- Terminal run วันที่ 2026-05-19 ที่ใช้ `OPENAI_COMPATIBLE_RESPONSE_FORMAT=responses_parse` และ `OPENAI_COMPATIBLE_MODEL=current` (source: user-provided terminal output, 2026-05-19)

**Last updated**

2026-05-19

## Version Metadata

| Field | Value |
| --- | --- |
| Model version | `v2` |
| Trained artifact | `unsloth_LFM2-350M_1779162226` |
| Base model | `unsloth/LFM2-350M` |
| Training environment | Unsloth Studio |
| Training format | instruction tuning with `instruction`, `input`, `output` |
| Training files | `train.jsonl`, `validation.jsonl` |
| Output contract | `data/schemas/triage-output.schema.json` |
| Runtime adapter | `openai-compatible` |
| Runtime prompt | `triage-json-v2` |
| Primary runtime path tested today | OpenAI SDK `responses_parse` with Pydantic text format |
| Smoke split | `data/splits/smoke-output-contract.jsonl` |
| Report path | `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json`, `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.md` |
| Status | `rejected-for-output-contract` |

## Training Snapshot

รอบ v2 มาจาก Unsloth Studio โดยใช้ base model เดิมคือ `unsloth/LFM2-350M` และ load LoRA แบบ 16-bit ตอน serve รอบ smoke ไม่ใช่การเปลี่ยน base model ใหม่ ข้อมูล training ที่มีจาก operator note มีดังนี้ (source: user-provided Codex thread note, 2026-05-19)

| Setting | Value |
| --- | --- |
| Context length | `2048` |
| Max steps | `30` |
| Learning rate | `0.0002` |
| LoRA rank | `16` |
| LoRA alpha | `16` |
| LoRA dropout | `0.0` |
| Target modules | `q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj` |
| Optimizer | `AdamW 8-bit` |
| LR scheduler | `linear` |
| Batch size | `2` |
| Gradient accumulation | `4` |
| Warmup steps | `8` |
| Save steps | `30` |
| Eval steps | `0.1` |
| Seed | `3407` |

## Runtime And Report Notes

วันนี้มีจุดที่ต้องอ่าน report อย่างระวัง: path `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json` เป็น output path มาตรฐานของ adapter และอาจถูก overwrite ได้ง่ายถ้ารันหลาย mode ต่อกัน รอบ terminal ที่ผู้ใช้รายงานใช้ `responses_parse` จริงและได้ metric shape เดียวกันกับ persisted report ล่าสุด แต่ persisted JSON ที่อ่านจาก workspace ตอนจัดเอกสารนี้ยังแสดง metadata เป็น `json_schema_strict` (source: reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json; user-provided terminal output, 2026-05-19)

| Run source | Requested mode | Requested model | Samples | JSON parse | Schema success | Invalid outputs | Note |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| User terminal output | `responses_parse` | `current` | `5` | `0.2` | `0.2` | `4` | Pydantic path ถูกใช้จริงใน terminal run แต่ยัง fail เพราะ model ตอบ markdown fence |
| Persisted report file | `json_schema` / `json_schema_strict` | `lfm2-security-triage` | `5` | `0.2` | `0.2` | `4` | File ปัจจุบันยังบันทึก mode นี้และควรถูกอ่านเป็น report artifact ล่าสุดใน workspace |

เพื่อกันความสับสน รอบถัดไปควรเขียนแยก path เช่น:

```bash
OPENAI_COMPATIBLE_RESPONSE_FORMAT=responses_parse \
OPENAI_COMPATIBLE_MODEL=current \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/structured-output/smoke/openai-compatible-responses-parse-eval.json \
  --comparison-out reports/structured-output/smoke/openai-compatible-responses-parse-eval.md \
  --no-progress
```

## Latest Smoke Metrics

| Metric | Responses parse terminal run | Persisted report file |
| --- | ---: | ---: |
| Samples | `5` | `5` |
| Label accuracy | `0.2` | `0.2` |
| JSON parse success rate | `0.2` | `0.2` |
| Schema success rate | `0.2` | `0.2` |
| Severity accuracy | `0.0` | `0.0` |
| Is suspicious accuracy | `0.2` | `0.2` |
| Evidence partial match | `0.0` | `0.0` |
| Invalid output count | `4` | `4` |
| Average latency ms | `4498.824717` | `4483.430025` |

ตัวเลขนี้แปลตรง ๆ ว่า output contract ยังไม่ผ่าน smoke stage เพราะต้องการอย่างน้อย JSON/schema validity ที่นิ่งก่อน จึงค่อยไปดู fixed test split หรือ model quality เต็มรูปแบบ

## Sample-Level Result

| Sample | Expected | Observed | Contract result | Quality note |
| --- | --- | --- | --- | --- |
| `sample-000035` | `normal` | invalid output in report | parse/schema fail | normal traffic ถูกดันไปเป็น suspicious pattern ใน raw output รอบก่อนหน้า |
| `sample-000137` | `failed_login_bruteforce` | `failed_login_bruteforce` | parse/schema pass | label ถูก แต่ severity เป็น `high` แทน expected `medium` และ evidence ไม่ match |
| `sample-000248` | `sql_injection_attempt` | invalid output in report | parse/schema fail | model ยัง drift ไป SSH/bruteforce-style reasoning ใน raw output รอบก่อนหน้า |
| `sample-000331` | `directory_traversal_attempt` | invalid output in report | parse/schema fail | directory traversal ยังถูกสับกับ failed login/bruteforce ใน raw output รอบก่อนหน้า |
| `sample-000474` | `port_scan_or_recon` | invalid output in report | parse/schema fail | nmap/port scan ยังถูกสับกับ SSH brute force และเคยขาด `recommended_action` |

## Failure Modes

| Area | Current evidence | Impact |
| --- | --- | --- |
| JSON contract | 4/5 samples fail JSON parsing; terminal `responses_parse` run reports Pydantic invalid JSON on markdown-fenced output (source: user-provided terminal output, 2026-05-19) | adapter/evaluator rightly reject output before semantic comparison |
| Runtime enforcement | `responses_parse` validates after model response, but backend still allows markdown fence to be generated | ยังไม่ใช่ server-side constrained decoding สำหรับ endpoint นี้ |
| Required fields | Some historical raw outputs omit `recommended_action` (source: docs/output-contract-hardening.md) | schema contract breaks even when JSON body is visible inside markdown fence |
| Label taxonomy | Historical raw outputs invent labels such as `ssh_attempt_failed` and `ssh_bruteforce_attempt` (source: reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json, docs/output-contract-hardening.md) | downstream UI/evaluator cannot trust label enum |
| Severity | The only schema-valid sample predicts `high` while expected is `medium` (source: reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json) | model over-escalates priority |
| Evidence | The only schema-valid sample uses weak or hallucinated evidence such as `sshd.log`/`ssh2.log` rather than concrete substrings from the log (source: reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json) | analyst value is low even when shape passes |

## Decision

| Decision | Rationale | Impact |
| --- | --- | --- |
| Keep v2 rejected for output contract | Smoke validity is still 1/5, with 4 invalid outputs | Do not run fixed split as a model-comparison artifact yet |
| Keep `responses_parse` as strict validation path | It gives clearer Pydantic errors and returns dict output when successful | Good for evaluator path, but not sufficient as constrained decoding on this backend |
| Do not add a JSON extractor to the main evaluator path | Extracting JSON from markdown would hide production-facing contract failure | Keep extractor, if any, debug-only |
| Separate report output paths by mode | `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json` can be overwritten by multiple runs | Future docs should cite mode-specific report files |

## Next Experiment

1. Re-run `responses_parse` with explicit output paths so the report metadata and terminal command stay tied together.
2. If backend has server-side guided decoding or structured decoding beyond OpenAI SDK `responses.parse`, test that path next.
3. If runtime cannot enforce generation, prepare v3 data with hard negative examples where markdown fences are explicitly invalid and assistant outputs are JSON object only.
4. Keep `data/splits/smoke-output-contract.jsonl` as the gate. Do not move to `data/splits/test.jsonl` until JSON/schema success is near `1.0`.
5. After schema validity is fixed, inspect semantic drift separately: severity over-escalation, evidence hallucination, and confusion among SQLi, traversal, and port scan classes.

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-19 | Codex | Created v2 model-output page for OpenAI SDK + Pydantic `responses_parse` smoke results | `docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md`, `reports/structured-output/smoke/openai-compatible-eval-model-v2-output-v1.json`, user terminal output | Done |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-19 | Keep v2 in rejected state after `responses_parse` smoke | `responses_parse` still passes only 1/5 samples and fails 4/5 on invalid JSON/markdown fence behavior | Next work stays on runtime enforcement or v3 output-only training examples, not fixed split comparison |
| 2026-05-19 | Preserve mode-specific reports in future runs | The standard report path can be overwritten by `json_schema` and `responses_parse` runs with similar metrics | Future analysis should use `reports/structured-output/smoke/openai-compatible-responses-parse-eval.json` or equivalent |

## Related pages

- [[model-output/README]]
- [[model-output/v1-lfm2-350m-security-triage]]
- [[model-output/template]]
- [[output-contract-hardening]]
- [[Day6]]
- [[fine-tuning-notes]]
- [[triage-output-schema]]
- [[evaluation-metrics-rationale]]

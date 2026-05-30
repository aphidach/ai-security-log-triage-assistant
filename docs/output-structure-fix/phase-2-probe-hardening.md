# Phase 2 Probe Hardening

**Summary**

Phase 2 จะเพิ่ม probe ให้แยกได้ว่า backend บังคับ JSON/schema ตอน decode จริงหรือแค่ปล่อย model generate แล้วค่อย validate ภายหลัง

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ Phase 2 checklist (source: docs/structured-output-fix-plan.md)
- `scripts/probe_openai_structured_output.py` สำหรับ probe path ปัจจุบัน (source: scripts/probe_openai_structured_output.py)
- `data/splits/smoke-output-contract.jsonl` สำหรับ 5-sample smoke gate (source: data/splits/smoke-output-contract.jsonl)
- `reports/README.md` สำหรับ report path convention (source: reports/README.md)
- `reports/structured-output/probes/structured-output-probe-unsloth-studio-json-schema-smoke.json` สำหรับ Unsloth Studio baseline probe result (source: reports/structured-output/probes/structured-output-probe-unsloth-studio-json-schema-smoke.json)
- `reports/structured-output/probes/structured-output-probe-unsloth-studio-json-schema-adversarial.json` สำหรับ Unsloth Studio adversarial probe result (source: reports/structured-output/probes/structured-output-probe-unsloth-studio-json-schema-adversarial.json)
- `reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-smoke.json` สำหรับ vLLM baseline probe result (source: reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-smoke.json)
- `reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-adversarial.json` สำหรับ vLLM adversarial probe result (source: reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-adversarial.json)

**Last updated**

2026-05-20

## Status

Initial runtime comparison complete. Probe script has been hardened and four reports now compare Unsloth Studio against vLLM on baseline and adversarial format prompts.

## Required Changes

- [x] เพิ่ม flag สำหรับ adversarial format instruction เช่นขอให้ตอบใน markdown fence
- [x] เพิ่ม mode ที่รันหลาย sample จาก `data/splits/smoke-output-contract.jsonl` ในคำสั่งเดียว
- [x] บันทึก raw output, latency, requested model, response model, provider schema mode และ validation result ต่อ sample
- [x] เพิ่ม output path ที่บังคับไม่เขียนทับ report เก่า
- [x] ถ้าต้องทำ JSON extraction ให้แยกเป็น debug-only field และห้ามนับเป็น metric หลัก

## Why This Phase Exists

คำถามหลักคือทำไม smoke test ระหว่าง runtime ได้ผลไม่เหมือนกัน ทั้งที่ใช้ model artifact ใกล้กัน:

- Unsloth Studio endpoint: `http://192.168.8.141:8888/v1`
- vLLM endpoint: `http://192.168.8.141:8080/v1`

Phase 2 probe ต้องช่วยแยก 3 เรื่อง:

1. endpoint รับ structured-output request syntax แบบไหน
2. endpoint บังคับ schema ระหว่าง decode จริงไหม
3. output ที่ fail เป็นเพราะ runtime ไม่ enforce, request mode ไม่ตรง, auth/network error, หรือ model semantic drift

## Probe Script Capabilities

`scripts/probe_openai_structured_output.py` ตอนนี้รองรับ:

- `--all-smoke` เพื่อรันทุก record ใน `data/splits/smoke-output-contract.jsonl`
- `--limit N` เพื่อรันบางส่วนก่อน
- `--adversarial-format markdown_fence` เพื่อแกล้ง prompt ให้ขอ markdown fence
- `--out path.md` สำหรับ report อ่านง่าย
- `--json-out path.json` สำหรับ report แบบ machine-readable
- `--force` เพื่อยอม overwrite report เดิม

Per-sample report จะเก็บ:

- `id`
- `input`
- `mode`
- `provider_schema_mode`
- `requested_model`
- `response_model`
- `latency_ms`
- `error`
- `raw_content`
- `json_parse_success`
- `schema_success`
- `starts_with_object`
- `ends_with_object`
- `has_markdown_fence`
- debug-only extraction fields ถ้า raw output ไม่ parse เป็น JSON object ได้

## Manual Runbook

ให้รันจาก repo root:

```bash
cd /Volumes/Hiksemi/Code/ai-security-log-triage-assistant
```

ใช้ `.venv/bin/python` เพื่อให้เจอ `openai` และ `pydantic` dependency:

```bash
.venv/bin/python -c "import openai, pydantic; print(openai.__version__); print(pydantic.__version__)"
```

ถ้าคำสั่งนี้ fail ให้ติดตั้ง dependency ก่อน:

```bash
uv pip install -r requirements.txt
```

### 1. Unsloth Studio Baseline Probe

รันแบบไม่ adversarial ก่อน เพื่อดู behavior ปกติ:

```bash
.venv/bin/python scripts/probe_openai_structured_output.py \
  --base-url http://192.168.8.141:8888/v1 \
  --api-key local \
  --model lfm2-security-triage \
  --mode json_schema \
  --split data/splits/smoke-output-contract.jsonl \
  --all-smoke \
  --timeout-seconds 60 \
  --out reports/structured-output/probes/structured-output-probe-unsloth-studio-json-schema-smoke.md \
  --json-out reports/structured-output/probes/structured-output-probe-unsloth-studio-json-schema-smoke.json
```

ถ้า Unsloth Studio ตอบ `401 Invalid token payload` ให้เปลี่ยน `--api-key local` เป็น token/key เดียวกับที่ใช้รัน smoke สำเร็จก่อนหน้า หรือใช้ environment variable ที่ runtime นั้นต้องการ

### 2. vLLM Baseline Probe

รัน vLLM ด้วย `structured_outputs`:

```bash
.venv/bin/python scripts/probe_openai_structured_output.py \
  --base-url http://192.168.8.141:8080/v1 \
  --api-key local \
  --model lfm2-security-triage \
  --mode structured_outputs \
  --split data/splits/smoke-output-contract.jsonl \
  --all-smoke \
  --timeout-seconds 60 \
  --out reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-smoke.md \
  --json-out reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-smoke.json
```

### 3. Unsloth Studio Adversarial Probe

รันด้วย prompt ที่ตั้งใจขัดกับ output contract โดยขอ markdown fence:

```bash
.venv/bin/python scripts/probe_openai_structured_output.py \
  --base-url http://192.168.8.141:8888/v1 \
  --api-key local \
  --model lfm2-security-triage \
  --mode json_schema \
  --split data/splits/smoke-output-contract.jsonl \
  --all-smoke \
  --adversarial-format markdown_fence \
  --timeout-seconds 60 \
  --out reports/structured-output/probes/structured-output-probe-unsloth-studio-json-schema-adversarial.md \
  --json-out reports/structured-output/probes/structured-output-probe-unsloth-studio-json-schema-adversarial.json
```

### 4. vLLM Adversarial Probe

รัน adversarial probe เดียวกันกับ vLLM:

```bash
.venv/bin/python scripts/probe_openai_structured_output.py \
  --base-url http://192.168.8.141:8080/v1 \
  --api-key local \
  --model lfm2-security-triage \
  --mode structured_outputs \
  --split data/splits/smoke-output-contract.jsonl \
  --all-smoke \
  --adversarial-format markdown_fence \
  --timeout-seconds 60 \
  --out reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-adversarial.md \
  --json-out reports/structured-output/probes/structured-output-probe-vllm-structured-outputs-adversarial.json
```

## What To Compare

เปิด `.md` reports แล้วดู summary ก่อน:

| Field | Meaning |
| --- | --- |
| `json_parse_success_rate` | raw output parse เป็น JSON object ได้กี่สัดส่วน |
| `schema_success_rate` | JSON object ผ่าน schema กี่สัดส่วน |
| `error_count` | request fail ก่อนมี output กี่ sample |
| `markdown_fence_count` | output มี ``` fence กี่ sample |
| `plain_json_object_count` | output เริ่มด้วย `{` จบด้วย `}` และไม่มี fence กี่ sample |
| `average_latency_ms` | latency เฉลี่ยต่อ sample |

จากนั้นดู per-sample:

- `response_model` ตรงกับ `requested_model` ไหม
- fail เป็น `error` เช่น 401, timeout, connection error หรือเป็น output parse/schema fail
- `raw_content` เป็น JSON object ล้วนหรือมี prose/markdown fence
- adversarial run ยังได้ plain JSON object หรือไม่

## Expected Interpretation

ถ้า runtime enforce schema จริง:

- adversarial prompt ขอ markdown fence แต่ output ยังเป็น JSON object ล้วน
- `markdown_fence_count = 0`
- `plain_json_object_count = samples`
- `json_parse_success_rate = 1.0`
- `schema_success_rate = 1.0`

ถ้า runtime แค่รับ field แล้วไม่ enforce:

- adversarial prompt อาจชนะ และ output มี markdown fence/prose
- `markdown_fence_count > 0`
- JSON parse/schema อาจ fail

ถ้า report มี `error_count > 0`:

- อย่าสรุปว่า model หรือ schema fail ทันที
- แยกก่อนว่าเป็น auth, network, endpoint down, unsupported request shape หรือ timeout
- สำหรับ `401 Invalid token payload` ให้แก้ API key/token ก่อน rerun

## Result Summary Template

ผลจากรอบ Phase 2 แรก:

| Runtime | Mode | Adversarial | JSON parse | Schema | Errors | Fences | Plain objects | Notes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Unsloth Studio `:8888` | `json_schema` | no | `0.2` | `0.2` | `0` | `4` | `1` | Accepts request shape but does not reliably enforce plain JSON output |
| vLLM `:8080` | `structured_outputs` | no | `1.0` | `1.0` | `0` | `0` | `5` | Baseline output contract passes cleanly |
| Unsloth Studio `:8888` | `json_schema` | markdown fence | `0.0` | `0.0` | `1` | `4` | `0` | Prompt wins over schema mode in 4 completed samples; one sample timed out |
| vLLM `:8080` | `structured_outputs` | markdown fence | `0.6` | `0.6` | `2` | `0` | `3` | Completed samples still obey JSON/schema; two samples timed out under adversarial pressure |

## Phase 2 Findings

Phase 2 explains why smoke results differ:

- Unsloth Studio `:8888` appears to accept OpenAI-style `json_schema`, but the backend does not enforce the schema strongly during decoding. Baseline probe still produced markdown fences in 4/5 samples, so raw output parsing and schema validation passed only 1/5.
- vLLM `:8080` with `structured_outputs` enforces the output shape in the normal smoke probe: 5/5 samples were plain JSON objects, no markdown fences, and schema success was `1.0`.
- Under adversarial markdown-fence instruction, Unsloth Studio followed the conflicting format instruction in 4 completed samples, which is consistent with validation-after-generation or ignored schema enforcement.
- Under the same adversarial instruction, vLLM did not produce markdown fences in any completed sample. Its failure mode was timeout on 2/5 samples, not prose or fenced JSON. This suggests constrained decoding is resisting the adversarial format request, but the adversarial prompt can increase latency or cause timeout for some samples.
- The Unsloth Studio reports used requested model `current`; the endpoint response model was the Windows artifact path `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226`. vLLM reports used requested and response model `lfm2-security-triage`.

## Practical Conclusion

For output-contract work, vLLM `structured_outputs` is the reliable runtime. Unsloth Studio remains useful for serving/debugging the adapter, but not as the contract gate unless a different schema mode or server setting can remove markdown fences without post-processing.

For semantic-quality work, use vLLM baseline mode without adversarial formatting. The adversarial vLLM timeout behavior is useful runtime evidence, but it should not block Phase 5 mini semantic eval.

## Pass Condition

ถ้า prompt ขอ markdown fence แต่ backend เป็น constrained decoder จริง output ต้องยังเป็น JSON object เปล่า ๆ ที่เริ่มด้วย `{` และจบด้วย `}`

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 2 detail stub | `docs/output-structure-fix/phase-2-probe-hardening.md` | Drafted |
| 2026-05-20 | Codex | Added manual runbook for comparing Unsloth Studio and vLLM probes | `docs/output-structure-fix/phase-2-probe-hardening.md`, `scripts/probe_openai_structured_output.py` | Ready |
| 2026-05-20 | User/Codex | Recorded Phase 2 probe results for Unsloth Studio and vLLM baseline/adversarial runs | `reports/structured-output/probes/structured-output-probe-*.json`, `reports/structured-output/probes/structured-output-probe-*.md` | Complete |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-20 | Keep vLLM `structured_outputs` as the output-contract gate runtime | vLLM baseline probe passed JSON/schema 5/5 with no fences; Unsloth Studio baseline produced fences in 4/5 | Phase 5 should use vLLM for semantic evaluation |
| 2026-05-20 | Treat adversarial vLLM timeouts separately from output-format failure | vLLM adversarial completed samples were valid JSON with no fences, but 2/5 timed out | Timeout/latency tuning is a runtime robustness follow-up, not evidence that vLLM ignores schema |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-1-backend-inventory]]
- [[structured-output-fix-plan]]

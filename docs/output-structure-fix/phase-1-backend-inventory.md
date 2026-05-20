# Phase 1 Backend Inventory

**Summary**

Phase 1 ต้องตอบให้ได้ก่อนว่า smoke/probe แต่ละรอบกำลังยิง backend อะไร โหลดโมเดลแบบไหน และ structured-output request mode ที่ใช้เป็น server-side constrained decoding จริงหรือเป็นแค่ validation หลัง generate

รอบนี้ให้เก็บ inventory สองสาย: current Unsloth Studio endpoint ที่มี preserved smoke artifact แล้ว และ vLLM candidate ที่จะโหลด Unsloth Studio LoRA output จาก `unsloth_LFM2-350M_1779162226`

**Sources**

- `docs/structured-output-fix-plan.md` สำหรับ Phase 1 checklist และ pass condition (source: docs/structured-output-fix-plan.md)
- `reports/structured-output-run-artifacts.md` สำหรับ current endpoint metadata และ 1/5 smoke baseline (source: reports/structured-output-run-artifacts.md)
- `reports/openai-compatible-unsloth-studio-json-schema-smoke.json` สำหรับ per-sample adapter metadata และ raw output (source: reports/openai-compatible-unsloth-studio-json-schema-smoke.json)
- `scripts/model_adapters/openai_compatible.py` สำหรับ adapter modes `json_schema`, `structured_outputs`, `guided_json`, `responses_parse` (source: scripts/model_adapters/openai_compatible.py)
- `scripts/probe_openai_structured_output.py` สำหรับ direct probe path ที่จะต่อยอดใน Phase 2 (source: scripts/probe_openai_structured_output.py)
- vLLM supported models docs ระบุ `Lfm2ForCausalLM` และ `LiquidAI/LFM2-350M` (source: https://docs.vllm.ai/en/stable/models/supported_models/)
- vLLM LoRA docs ระบุการ serve LoRA ผ่าน OpenAI-compatible server ด้วย `--enable-lora --lora-modules` (source: https://docs.vllm.ai/en/stable/features/lora/)
- vLLM structured outputs docs ระบุ `structured_outputs` และ JSON schema support (source: https://docs.vllm.ai/en/latest/features/structured_outputs/)
- User-provided Unsloth Studio output path และ file listing จาก 2026-05-20 request (source: user request, 2026-05-20)

**Last updated**

2026-05-20

## Status

In progress.

สิ่งที่รู้แล้ว:

- current endpoint ยิงผ่าน `http://192.168.8.141:8888/v1`
- requested model คือ `lfm2-security-triage`
- response model ชี้ไปที่ `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226`
- current smoke ใช้ `json_schema_strict` แต่ยัง JSON/schema success เพียง `0.2`

สิ่งที่ยังต้องเก็บ:

- backend จริงของ endpoint `192.168.8.141:8888`
- backend version
- launch command หรือ UI settings ที่ใช้ load model
- vLLM version และ launch result
- `/v1/models` output จาก vLLM หลังโหลด LoRA
- response model จาก vLLM request จริง

## Phase 1 Question

Phase 1 ไม่ได้วัดว่า model เก่งขึ้นหรือยัง แต่ต้องตอบคำถาม inventory เหล่านี้:

- backend ที่รับ request คืออะไร: Unsloth Studio, vLLM, SGLang, LM Studio, Ollama, TGI หรืออย่างอื่น
- backend version คืออะไร
- model ถูก serve เป็น full merged model หรือ base model plus LoRA adapter
- model alias ที่เราส่งใน request ตรงกับ model ที่ backend ตอบกลับไหม
- structured-output syntax ที่ backend รองรับคืออะไร
- backend enforce schema ตอน decode จริงไหม หรือรับ field แล้ว ignore/fallback

## Current Endpoint Inventory

ข้อมูลนี้ดึงจาก Phase 0 artifact ที่ preserve ไว้แล้ว

| Field | Value |
| --- | --- |
| Adapter | `openai-compatible` |
| Runtime label | `unsloth-studio` |
| Base URL | `http://192.168.8.141:8888/v1` |
| Requested model | `lfm2-security-triage` |
| Response model | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` |
| Prompt version | `triage-json-v2` |
| Response format requested | `json_schema` |
| Request mode | `json_schema_strict` |
| Schema path | `data/schemas/triage-output.schema.json` |
| Split | `data/splits/smoke-output-contract.jsonl` |
| JSON/schema success | `0.2` |
| Invalid outputs | `4/5` |

Interpretation:

- current endpoint accepts the OpenAI-compatible request shape but does not appear to enforce the JSON schema strongly enough for the smoke gate
- raw outputs still include markdown-fenced JSON and invalid labels, so Phase 3 must compare against a runtime that clearly supports server-side constrained decoding
- response model points to a local Unsloth Studio output path, so alias drift is already visible: request alias is `lfm2-security-triage`, response model is a local artifact path

## User-Provided Unsloth Studio Output

Path:

```text
/mnt/c/Users/dargy/.unsloth/studio/outputs/unsloth_LFM2-350M_1779162226
```

Files shown by user:

```text
README.md
adapter_config.json
adapter_model.safetensors
chat_template.jinja
checkpoint-30
checkpoint-55
special_tokens_map.json
tokenizer.json
tokenizer_config.json
training_args.bin
```

Interpretation:

- this looks like a LoRA adapter output, not a fully merged model directory
- evidence: it has `adapter_config.json` and `adapter_model.safetensors`
- the listed files do not include `config.json` or full base-model weight shards
- vLLM should therefore load the base model separately and attach this directory as a LoRA adapter
- the exact base model must be confirmed from `adapter_config.json`

## vLLM Candidate Decision

Use vLLM as the first constrained-decoding candidate for Phase 1/3 if the machine can run it.

Rationale:

- vLLM docs list `Lfm2ForCausalLM` with `LiquidAI/LFM2-350M` and LoRA support
- vLLM can serve LoRA adapters through its OpenAI-compatible server using `--enable-lora --lora-modules`
- vLLM structured-output docs support JSON schema through current `structured_outputs` syntax
- `guided_json` is legacy/deprecated in newer vLLM docs, so the primary test should be `structured_outputs`

Risk:

- adapter target modules may not match vLLM LoRA support for this exact LFM2 checkpoint until tested
- LoRA rank may exceed vLLM default and require `--max-lora-rank`
- tokenizer/chat template from Unsloth Studio may need verification against the base model

## Commands To Collect Inventory On WSL

Run these on the machine that has the Unsloth Studio output path.

```bash
ADAPTER_DIR=/mnt/c/Users/dargy/.unsloth/studio/outputs/unsloth_LFM2-350M_1779162226
cd "$ADAPTER_DIR"

pwd
ls -la

jq '{
  base_model_name_or_path,
  peft_type,
  task_type,
  r,
  lora_alpha,
  target_modules,
  modules_to_save
}' adapter_config.json
```

Collect runtime version:

```bash
vllm --version
python -c "import vllm; print(vllm.__version__)"
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
```

Choose base model from adapter config:

```bash
BASE_MODEL="$(jq -r '.base_model_name_or_path // "LiquidAI/LFM2-350M"' adapter_config.json)"
LORA_RANK="$(jq -r '.r // 64' adapter_config.json)"

echo "$BASE_MODEL"
echo "$LORA_RANK"
```

Start vLLM:

```bash
vllm serve "$BASE_MODEL" \
  --host 0.0.0.0 \
  --port 8000 \
  --enable-lora \
  --lora-modules lfm2-security-triage="$ADAPTER_DIR" \
  --max-lora-rank "$LORA_RANK"
```

If the base model field is empty or points to an unavailable local path, try the expected base explicitly:

```bash
vllm serve LiquidAI/LFM2-350M \
  --host 0.0.0.0 \
  --port 8000 \
  --enable-lora \
  --lora-modules lfm2-security-triage="$ADAPTER_DIR" \
  --max-lora-rank "$LORA_RANK"
```

## Health Check

After vLLM starts:

```bash
curl -s http://127.0.0.1:8000/v1/models | jq .
```

Expected:

- one base model id
- one LoRA model id named `lfm2-security-triage`

Minimal non-gated chat request:

```bash
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local" \
  -d '{
    "model": "lfm2-security-triage",
    "messages": [
      {"role": "user", "content": "Return only the word ok."}
    ],
    "temperature": 0,
    "max_tokens": 16
  }' | jq .
```

This health check only proves the endpoint responds. It does not prove the output contract.

## Structured-Output Syntax To Record

For vLLM, record which syntax works on this installed version:

- preferred current syntax: `extra_body={"structured_outputs": {"json": provider_schema}}`
- OpenAI-style JSON schema syntax: `response_format={"type": "json_schema", "json_schema": {...}}`
- legacy syntax to avoid unless needed for compatibility: `guided_json`

Our adapter already has modes for these names:

| Adapter mode | Provider request shape | Use |
| --- | --- | --- |
| `structured_outputs` | `extra_body.structured_outputs.json` | primary vLLM candidate |
| `json_schema` | `response_format.type=json_schema` | OpenAI-style compatibility check |
| `guided_json` | `extra_body.guided_json` | legacy fallback only |
| `responses_parse` | OpenAI Responses parse | current validation-after-generation diagnostic |

## Inventory Report Template

Fill `reports/structured-output-backend-inventory.md` with:

| Field | Current Endpoint | vLLM Candidate |
| --- | --- | --- |
| Backend | inferred `unsloth-studio`; exact backend unknown | `vLLM` |
| Backend version | unknown | output of `vllm --version` |
| Base URL | `http://192.168.8.141:8888/v1` | `http://127.0.0.1:8000/v1` or LAN URL |
| Base model | unknown from report | output of `adapter_config.json.base_model_name_or_path` |
| Adapter path | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `/mnt/c/Users/dargy/.unsloth/studio/outputs/unsloth_LFM2-350M_1779162226` |
| Served alias | `lfm2-security-triage` | `lfm2-security-triage` |
| `/v1/models` output | not captured yet | pending |
| Structured-output syntax | `json_schema` accepted but not enforced enough | pending `structured_outputs` probe |
| Launch command/settings | not captured yet | pending |

## Phase 1 Pass Condition

Phase 1 passes only when `reports/structured-output-backend-inventory.md` lets us answer:

- exact backend and version
- exact base model and LoRA adapter path
- exact launch command or UI settings
- model alias requested by evaluator
- model id returned by endpoint
- supported structured-output request syntax to test in Phase 2/3

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created Phase 1 working note and seeded current endpoint inventory from preserved smoke artifact | `docs/output-structure-fix/phase-1-backend-inventory.md`, `reports/structured-output-run-artifacts.md` | In progress |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-20 | Treat Unsloth Studio output as a LoRA adapter until proven otherwise | User-provided listing has `adapter_config.json` and `adapter_model.safetensors`, not full model `config.json` or weight shards | vLLM launch should load the base model plus `--enable-lora --lora-modules`, not point `vllm serve` directly at the adapter directory as a full model |
| 2026-05-20 | Use vLLM `structured_outputs` as the first runtime candidate | vLLM documents LFM2 support, LoRA serving, and structured-output JSON schema support | Phase 2/3 should test `OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs` against vLLM after inventory is complete |

## Related pages

- [[output-structure-fix/README]]
- [[structured-output-fix-plan]]
- [[structured-output-reliability-research-2026]]
- [[output-contract-hardening]]
- [[model-output/v2-lfm2-350m-security-triage-responses-parse]]

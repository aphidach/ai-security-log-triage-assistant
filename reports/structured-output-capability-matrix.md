# Structured Output Capability Matrix

**Summary**

Runtime capability matrix for output-contract experiments. The first passing runtime is vLLM serving `unsloth/LFM2-350M` plus the `unsloth_LFM2-350M_1779162226` LoRA adapter through `structured_outputs`.

**Sources**

- `docs/structured-output-fix-plan.md` for phase goals, report naming, and pass/fail conditions (source: docs/structured-output-fix-plan.md)
- `reports/structured-output-backend-inventory.md` for backend version, base model, LoRA path, alias, and serving details (source: reports/structured-output-backend-inventory.md)
- `reports/openai-compatible-unsloth-studio-json-schema-smoke.json` for the preserved current-endpoint baseline (source: reports/openai-compatible-unsloth-studio-json-schema-smoke.json)
- `reports/openai-compatible-vllm-structured-outputs-smoke.json` for the passing vLLM smoke run (source: reports/openai-compatible-vllm-structured-outputs-smoke.json)

**Last updated**

2026-05-20

## Matrix

| Runtime | Mode | Base URL | Requested model | Response model | JSON parse | Schema | Invalid outputs | Label accuracy | Status |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| Current endpoint / Unsloth Studio-labeled baseline | `json_schema` | `http://192.168.8.141:8888/v1` | `lfm2-security-triage` | `C:\Users\dargy\.unsloth\studio\outputs\unsloth_LFM2-350M_1779162226` | `0.2` | `0.2` | `4/5` | not used as gate | Fails output contract |
| vLLM | `structured_outputs` | `http://192.168.8.141:8080/v1` | `lfm2-security-triage` | `lfm2-security-triage` | `1.0` | `1.0` | `0/5` | `0.2` | Passes output contract; semantics need analysis |

## Interpretation

vLLM `structured_outputs` is the active runtime/mode for the next phase because it passes the smoke output contract without JSON extraction. The model quality question remains open: smoke label accuracy is only `0.2`, with visible confusion toward `failed_login_bruteforce`.

Do not run final fixed-split comparison from this matrix alone. The next step is a 20-25 sample mini semantic evaluation outside `data/splits/test.jsonl`.

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-20 | Codex | Created capability matrix after vLLM passed the smoke output-contract gate | `reports/openai-compatible-vllm-structured-outputs-smoke.json` | Drafted |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-20 | Use vLLM `structured_outputs` as the active runtime for the next evaluation phase | It is the first observed mode with JSON parse success `1.0`, schema success `1.0`, and invalid output count `0` on the smoke split | Phase 5 can focus on semantic quality instead of output formatting |

## Related pages

- [[structured-output-fix-plan]]
- [[output-structure-fix/phase-3-runtime-capability-matrix]]
- [[output-structure-fix/phase-4-contract-gate]]

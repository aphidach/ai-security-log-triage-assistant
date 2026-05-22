# Phase 8 V4.2 SQLi Priority Prompt Diagnostic Plan

**Summary**

v4.2 เป็น runtime prompt/architecture diagnostic ต่อจาก v4.1 ที่ถูก hold เป้าหมายคือทดสอบว่า SQLi boundary ที่ยังเหลืออยู่แก้ได้ด้วย label-priority prompt หรือเป็นข้อจำกัดของ `LFM2-350M` เอง รอบนี้ไม่เพิ่ม dataset, ไม่ train LoRA ใหม่, ไม่เปลี่ยน schema/taxonomy/evaluator/UI API และไม่ใช้ `data/splits/test.jsonl` เป็น tuning feedback

**Sources**

- `reports/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json` และ temp 0.3 report สำหรับ v4.1 hard-contrast failure source (source: reports/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json, source: reports/openai-compatible-vllm-structured-outputs-v4-1-temp-03-2048-hard-contrast-memorization-probe.json)
- `scripts/create_v4_2_sqli_priority_diagnostic_slice.py`, `reports/phase-8-v4-2-sqli-priority-diagnostic-slice.json` และ `.md` สำหรับ v4.2 diagnostic slice (source: scripts/create_v4_2_sqli_priority_diagnostic_slice.py, source: reports/phase-8-v4-2-sqli-priority-diagnostic-slice.json)
- `scripts/model_adapters/prompt_contract.py` และ `scripts/model_adapters/openai_compatible.py` สำหรับ runtime-selectable prompt profile และ metadata (source: scripts/model_adapters/prompt_contract.py, source: scripts/model_adapters/openai_compatible.py)
- `tests/test_openai_adapter_config.py` และ `tests/test_v4_2_sqli_priority_prompt_workflow.py` สำหรับ regression checks (source: tests/test_openai_adapter_config.py, source: tests/test_v4_2_sqli_priority_prompt_workflow.py)
- `docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md` สำหรับ v4.1 hold decision และ gate context (source: docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md)
- `reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json` และ temp 0.3 report สำหรับ v4.2 hard-contrast probe results (source: reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json, source: reports/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.json)
- operator-provided `--no-write` fixed split sanity output for v4.1 default prompt, recorded as context only because no report artifact was written

**Last updated**

2026-05-22

## Status

Hard-contrast probed; held. v4.2 adds `triage-json-v2.2-sqli-priority` as an opt-in runtime prompt profile while keeping `triage-json-v2.1` as the default training/runtime prompt. The prompt profile reduced SQLi-to-traversal misses to `0/10`, but it damaged broader label boundaries: temp 0 label accuracy fell to `0.64`, temp 0.3 fell to `0.62`, and temp 0.3 also lost the output contract with JSON/schema `0.98`. No v4.2 train split, validation split, LoRA config, supplement generator, or train allowlist entry is created.

## Failure Slice

`scripts/create_v4_2_sqli_priority_diagnostic_slice.py` อ่านเฉพาะ v4.1 temp 0/temp 0.3 hard-contrast reports และ source hard-contrast split ไม่อ่าน fixed test split แล้วเขียน:

```text
reports/phase-8-v4-2-sqli-priority-diagnostic-slice.json
reports/phase-8-v4-2-sqli-priority-diagnostic-slice.md
```

union label failures มี `6` ids:

```text
v3-hard-000001
v3-hard-000003
v3-hard-000024
v3-hard-000025
v3-hard-000026
v3-hard-000029
```

temp 0 buckets:

| Bucket | Count | Prompt diagnostic intent |
| --- | ---: | --- |
| `normal_to_bruteforce` | `2` | single failed auth ต้องไม่เป็น brute force ถ้าไม่มี repeated/short-window volume |
| `sqli_to_port` | `1` | `SLEEP`/time-delay SQLi ต้องชนะ generic recon ถ้าไม่มี scan/port cue |
| `sqli_to_normal` | `1` | `information_schema` ใน request/search ต้องยังเป็น SQLi ไม่ใช่ benign search |
| `sqli_to_traversal` | `2` | SQL comments/destructive SQL verbs ต้องไม่ drift ไป traversal ถ้าไม่มี file/path cue |

temp 0.3 buckets:

| Bucket | Count | Prompt diagnostic intent |
| --- | ---: | --- |
| `normal_to_bruteforce` | `2` | single failed auth ต้องไม่เป็น brute force ถ้าไม่มี repeated/short-window volume |
| `sqli_to_port` | `1` | `SLEEP`/time-delay SQLi ต้องชนะ generic recon ถ้าไม่มี scan/port cue |
| `sqli_to_normal` | `1` | `information_schema` ใน request/search ต้องยังเป็น SQLi ไม่ใช่ benign search |
| `sqli_to_traversal` | `1` | SQL comments ต้องไม่ drift ไป traversal ถ้าไม่มี file/path cue |

## Prompt Profile

v4.2 เพิ่ม prompt profile ใหม่:

```text
triage-json-v2.2-sqli-priority
```

profile นี้เพิ่ม SQLi priority rules บน system prompt เดิม โดยเลือกผ่าน `OPENAI_COMPATIBLE_PROMPT_VERSION` หรือ YAML `prompt_version` ใน `config-adapter.yml` เฉพาะ runtime probe ที่ตั้งชื่อชัดเจน default ยังเป็น `triage-json-v2.1`

SQLi priority rules ให้ SQLi ชนะ context อื่นเมื่อ SQL tokens อยู่ใน request/query/body/login/search/API fields เช่น `OR 1=1`, quoted tautology, SQL comment, `SLEEP`, `pg_sleep`, `WAITFOR DELAY`, `information_schema`, `sqlite_master`, `pg_catalog`, `;DROP TABLE` และ `;SELECT`

guard ที่ต้องไม่หลุด:

| Guard | Rule |
| --- | --- |
| Traversal | ต้องมี file/path cue เช่น `../`, encoded traversal, `/etc/passwd`, `win.ini`, `.env`, `WEB-INF`, `php://filter` |
| Bruteforce | ต้องมี repeated failures, short window, many users หรือ many passwords |
| Recon | ต้องมี scan/probe/enumeration/host/service/port evidence เช่น `nmap`, `SYN scan`, multi-port |

## Commands

Pre-probe checks:

```bash
rtk .venv/bin/python scripts/create_v4_2_sqli_priority_diagnostic_slice.py
rtk .venv/bin/python -m unittest tests/test_openai_adapter_config.py tests/test_v4_2_sqli_priority_prompt_workflow.py
rtk .venv/bin/python -m py_compile scripts/create_v4_2_sqli_priority_diagnostic_slice.py scripts/model_adapters/prompt_contract.py scripts/model_adapters/openai_compatible.py
```

Hard-contrast temp 0 probe:

```bash
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v4-1 \
OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.2-sqli-priority \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TEMPERATURE=0 \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.md
```

Hard-contrast temp 0.3 probe:

```bash
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v4-1 \
OPENAI_COMPATIBLE_PROMPT_VERSION=triage-json-v2.2-sqli-priority \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TEMPERATURE=0.3 \
OPENAI_COMPATIBLE_TOP_P=0.9 \
OPENAI_COMPATIBLE_EXTRA_BODY='{"min_p":0.15,"repetition_penalty":1.05}' \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.md
```

## Gates

Both hard-contrast probes must hit JSON parse `1.0`, schema `1.0`, invalid outputs `0`, label accuracy `>=0.90`, SQLi `>=8/10`, SQLi predicted as traversal `<=2/10`, normal `>=8/10`, traversal `>=9/10`, port/recon `>=9/10`, and predicted brute-force `<=14/50`

If both pass, run mini semantic eval next and document v4.2 as a candidate runtime prompt repair. If either fails, mark v4.2 held and plan a capacity pilot next; do not add more synthetic SQLi data by default.

## Hard-Contrast Result

Both v4.2 probes used only `data/generated/v3-hard-contrast-security-triage.jsonl`; fixed `data/splits/test.jsonl` was not used. The fixed test hash stayed `b838f07b902890a8dc9159cd1d2a413e9d7c7ae4eeff5754d9c947a35e4cdb3b`.

| Probe | Label accuracy | JSON/schema | Invalid | SQLi | SQLi -> traversal | Normal | Traversal | Port/recon | Predicted brute-force | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| temp 0 | `0.64` | `1.0 / 1.0` | `0` | `4/10` | `0/10` | `7/10` | `4/10` | `7/10` | `16/50` | Held |
| temp 0.3 | `0.62` | `0.98 / 0.98` | `1` | `4/10` | `0/10` | `6/10` | `4/10` | `7/10` | `16/50` | Held |

The prompt priority rule moved the failure mode away from SQLi-to-traversal, but not toward the correct SQLi label. Remaining SQLi misses shifted mostly to brute-force, port/recon, and normal, while true traversal and port/recon recall regressed. Mini semantic eval stays blocked.

## Post-Hoc Fixed Split Sanity Check

After v4.2 was held, the operator ran a manual `--no-write` fixed split check against served alias `lfm2-security-triage-v4-1` with `OPENAI_COMPATIBLE_TEMPERATURE=0.3`, `OPENAI_COMPATIBLE_TOP_P=0.9`, `OPENAI_COMPATIBLE_EXTRA_BODY='{"min_p":0.15,"repetition_penalty":1.05}'`, and no explicit `OPENAI_COMPATIBLE_PROMPT_VERSION`. Because `config-adapter.yml` does not set `prompt_version`, this means the run used the default `triage-json-v2.1` prompt, not v4.2's opt-in prompt.

| Split | Model alias | Prompt | Label accuracy | JSON/schema | Invalid | Notes |
| --- | --- | --- | ---: | ---: | ---: | --- |
| `data/splits/test.jsonl` | `lfm2-security-triage-v4-1` | `triage-json-v2.1` | `0.893333` | `1.0 / 1.0` | `0` | Post-hoc sanity only; not a Phase 8 gate and not tuning feedback |

This result is useful as evidence that v4.1 did not collapse on the older fixed split distribution, but it does not reverse the v4.2 hold decision. The fixed split is easier and more historically exposed than the hard-contrast boundary probe; Phase 8 decisions still depend on hard-contrast or a newly frozen holdout.

## Hold Fixed Test

`data/splits/test.jsonl` must not be used again in Phase 8. v4.2 may use v4.1 hard-contrast reports and `data/generated/v3-hard-contrast-security-triage.jsonl` only.

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-22 | Codex | Added v4.2 prompt-priority diagnostic slice, runtime prompt profile, adapter config support, tests, and docs | `scripts/create_v4_2_sqli_priority_diagnostic_slice.py`, `scripts/model_adapters/prompt_contract.py`, `scripts/model_adapters/openai_compatible.py`, `tests/test_v4_2_sqli_priority_prompt_workflow.py` | Prepared |
| 2026-05-22 | Codex | Ran v4.2 hard-contrast temp 0/temp 0.3 prompt probes | `reports/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json`, `reports/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.json` | Held |
| 2026-05-22 | User/Codex | Recorded manual v4.1 fixed split sanity check as non-gate context | operator `--no-write` command output, `config-adapter.yml` default prompt behavior | Context only |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-22 | Make v4.2 a prompt/architecture diagnostic instead of data-only repair | v4.1 hit the stop condition: canonical temp 0 SQLi stayed at `6/10` after a narrow data supplement | v4.2 creates no train artifacts and tests SQLi priority through an opt-in prompt profile |
| 2026-05-22 | Keep `triage-json-v2.1` as default | Existing v3/v4/v4.1 training configs and UI runtime must remain comparable | `triage-json-v2.2-sqli-priority` is selected only by env/YAML for named v4.2 probes |
| 2026-05-22 | Hold v4.2 and do not promote prompt v2.2 | v2.2 reduced SQLi-to-traversal to `0/10` but lowered overall accuracy, SQLi recall, traversal recall, and temp 0.3 JSON/schema | Next work should be capacity pilot or architecture diagnostic, not more prompt wording or broad synthetic data by default |
| 2026-05-22 | Treat the v4.1 fixed split improvement as sanity evidence only | The run used `--no-write` and the historical fixed split after several repair rounds | It may inform confidence that v4.1 is not broadly broken, but it must not tune Phase 8 or unblock v4.2 gates |

## Related pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan]]
- [[output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan]]
- [[openai-adapter-runtime-config]]
- [[fine-tuning-notes]]
- [[data-card]]

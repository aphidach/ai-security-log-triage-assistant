# Phase 6 V3.5 Boundary Repair Plan

**Summary**

v3.5 เป็น repair run ที่เริ่มจากหลักฐาน v3.4 `temperature=0` โดยตรง: สร้าง failure slice จาก hard-contrast report, เพิ่ม deterministic supplement 200 records เพื่อซ่อม SQLi/traversal/port-recon boundary และลดแรงดึงของ `failed_login_bruteforce`, แล้ว train adapter ใหม่จาก base `unsloth/LFM2-350M` โดยยังไม่แตะ fixed `data/splits/test.jsonl`

**Sources**

- `reports/openai-compatible-vllm-structured-outputs-v3-4-temp-0-hard-contrast-memorization-probe.json` และ `.md` สำหรับ metrics, raw outputs และ confusion ที่เป็นต้นทางของ v3.5 (source: reports/openai-compatible-vllm-structured-outputs-v3-4-temp-0-hard-contrast-memorization-probe.json)
- `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md` สำหรับบริบท v3.4, gate ที่พลาด และ decision ให้ hold fixed test split (source: docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md)
- `scripts/create_v3_5_failure_slice.py`, `reports/phase-6-v3-5-boundary-failure-slice.json` และ `.md` สำหรับ v3.5 failure buckets (source: scripts/create_v3_5_failure_slice.py, source: reports/phase-6-v3-5-boundary-failure-slice.json)
- `scripts/create_v3_5_boundary_repair_dataset.py`, `data/generated/v3-5-boundary-repair-security-triage.jsonl`, `data/splits/train-v3-5-boundary-repair.jsonl` และ `data/splits/validation-v3-5-boundary-repair.jsonl` สำหรับ deterministic supplement และ split artifacts (source: scripts/create_v3_5_boundary_repair_dataset.py)
- `ml/unsloth/config.v3-5.yaml` สำหรับ base model, LoRA config, output directory และ prompt version (source: ml/unsloth/config.v3-5.yaml)
- `reports/phase-6-v3-5-boundary-training-result.json` และ `.md` สำหรับ training metrics และ post-training gate summary (source: reports/phase-6-v3-5-boundary-training-result.json)
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json`, `.md` และ `reports/phase-6-v3-5-temp-0-hard-contrast-memorization-probe-infographic.html` สำหรับ canonical temp 0 hard-contrast probe (source: reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json)
- `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json`, `.md` และ `reports/phase-6-v3-5-temp-03-hard-contrast-memorization-probe-infographic.html` สำหรับ temp 0.3 runtime probe (source: reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json)
- `scripts/model_adapters/openai_compatible.py` สำหรับ runtime env overrides เช่น `OPENAI_COMPATIBLE_MODEL`, `OPENAI_COMPATIBLE_TEMPERATURE`, `OPENAI_COMPATIBLE_TOP_P` และ `OPENAI_COMPATIBLE_EXTRA_BODY` ที่ใช้กัน report path ชี้ผิด model/temp (source: scripts/model_adapters/openai_compatible.py)
- `tests/test_v3_5_boundary_repair_workflow.py` สำหรับ regression checks ก่อน train (source: tests/test_v3_5_boundary_repair_workflow.py)
- `docs/References.md` และ `docs/structured-output-reliability-research-2026.md` สำหรับ OWASP, SigmaHQ, OpenAI Structured Outputs, vLLM structured outputs, TRL และ Unsloth reference notes (source: docs/References.md, source: docs/structured-output-reliability-research-2026.md)

**Last updated**

2026-05-22

## Status

v3.5 trained and was probed on hard-contrast at temp 0 and temp 0.3. The broad boundary repair worked: label accuracy reached `0.84`, traversal/brute-force/port-recon hit `10/10`, normal held at `8/10`, and predicted brute force dropped to `12/50`.

แต่ v3.5 ยังไม่ผ่าน exit criteria ทั้งชุด เพราะ JSON/schema ยังเป็น `0.98 / 0.98`, invalid output ยังมี `1`, และ SQLi ยังได้เพียง `4/10` ทั้ง temp 0 และ temp 0.3 ดังนั้น fixed `data/splits/test.jsonl` ยังต้อง hold ไว้ และ mini semantic eval ยังไม่ควรเป็น step ถัดไป

## Problem Statement

v3.4 temp 0 บน `data/generated/v3-hard-contrast-security-triage.jsonl` ยังไม่ผ่าน gate: `label_accuracy=0.68`, JSON/schema `0.98`, invalid output `1`, SQLi ถูกเพียง `3/10`, traversal `5/10`, port/recon `8/10`, และ prediction ถูกดูดไป `failed_login_bruteforce=19/50`

ปัญหาไม่ได้อยู่ที่ taxonomy ใหม่ แต่เป็น boundary เดิมที่ยังเบลอ:

| Boundary | Failure mode | Repair intent |
| --- | --- | --- |
| SQLi vs brute force | login/API/status cue ชนะ SQL payload | เพิ่ม SQLi positives ใน login/API/search/reset contexts พร้อม status `401/403/400/500` |
| SQLi vs invalid JSON | quote-heavy evidence ทำ raw output แตก | เพิ่ม quote-heavy evidence ที่ต้อง escape ให้ถูกใน structured output |
| SQLi vs traversal/normal | SQL comment/schema-discovery cue ยังไม่นิ่ง | เพิ่ม contrast ระหว่าง SQL payload กับ benign SQL terms และ traversal paths |
| Traversal vs normal/port/brute force | status/user-agent/scanner cue กลบ path token | เพิ่ม traversal positives ที่มี `../`, encoded traversal, sensitive files และ distracting cues |
| Port/recon vs brute force | คำว่า blocked/attempt ถูกอ่านเป็น auth burst | เพิ่ม recon positives ที่มี nmap, service enumeration, horizontal scan และ unique threshold |
| Normal vs brute force | single failed login/isolated `4625` ยังถูก over-escalate | เพิ่ม normal hard negatives ที่มี failure words แต่ไม่มี burst/correlation |

## Failure Slice

`scripts/create_v3_5_failure_slice.py` อ่านเฉพาะ v3.4 temp 0 hard-contrast report และ source hard-contrast split ไม่อ่าน fixed test split แล้วเขียน report ไปที่:

```text
reports/phase-6-v3-5-boundary-failure-slice.json
reports/phase-6-v3-5-boundary-failure-slice.md
```

ผล slice มี label failures `16/50` และ buckets ดังนี้:

| Bucket | Count | Why it matters |
| --- | ---: | --- |
| `normal_to_bruteforce` | `2` | ลด false positive จาก single failed login และ isolated Windows `4625` |
| `sqli_to_bruteforce` | `4` | SQL payload ยังแพ้ login/auth/status context |
| `sqli_to_invalid` | `1` | quote-heavy SQLi evidence ยังเสี่ยงทำ output contract แตก |
| `sqli_to_normal` | `1` | schema-discovery SQLi ยังถูกมอง benign |
| `sqli_to_traversal` | `1` | SQL comment/quote cue ยังสับสนกับ path/file injection |
| `traversal_to_normal` | `2` | sensitive path traversal token ยัง underweighted |
| `traversal_to_port` | `2` | curl/scanner/status cue ดึง traversal ไปเป็น recon |
| `traversal_to_bruteforce` | `1` | blocked/status cue ดึง traversal ไปเป็น brute force |
| `port_to_bruteforce` | `2` | recon wording แบบ blocked/attempt ยังถูกอ่านเป็น auth burst |

## Dataset Recipe

`scripts/create_v3_5_boundary_repair_dataset.py` สร้าง supplement แบบ deterministic จำนวน `200` records และ append เข้ากับ v3.4 train split โดยยังใช้ validation balanced 75 records เดิม

Supplement labels:

| Label | Count |
| --- | ---: |
| `normal` | `45` |
| `failed_login_bruteforce` | `0` |
| `sql_injection_attempt` | `75` |
| `directory_traversal_attempt` | `55` |
| `port_scan_or_recon` | `25` |

Train labels after appending to v3.4 train:

| Label | Count |
| --- | ---: |
| `normal` | `215` |
| `failed_login_bruteforce` | `120` |
| `sql_injection_attempt` | `235` |
| `directory_traversal_attempt` | `155` |
| `port_scan_or_recon` | `185` |

Content rules:

- SQLi positives cover quoted tautology, `UNION SELECT`, `SLEEP`, `WAITFOR`, stacked query, comment marker, encoded payload, schema discovery, and quote-heavy evidence.
- Traversal positives cover `../`, encoded `%2e%2e`, `/etc/passwd`, `/etc/shadow`, `win.ini`, `secrets.yml`, `%00`, `php://filter`, and distracting status/user-agent cues.
- Normal hard negatives cover single auth failures, isolated `4625`, benign SQL documentation/search terms, benign relative paths, allowlisted inventory, and monitoring.
- Port/recon positives cover nmap fingerprint, service enumeration, horizontal scan, unique hosts/ports, and blocked/attempt wording that must not become brute force.
- No new brute-force positives are added because v3.4 already has strong brute-force recall; v3.5 is meant to reduce brute-force gravity.

Persisted supplement records strip internal `metadata`, while tests still verify the generator bucket mix before persistence.

## Training Plan

Use `ml/unsloth/config.v3-5.yaml` and train from the base model, not by continuing the v3.4 adapter:

```text
base_model: unsloth/LFM2-350M
train_path: data/splits/train-v3-5-boundary-repair.jsonl
validation_path: data/splits/validation-v3-5-boundary-repair.jsonl
prompt_version: triage-json-v2.1
output_dir: ml/unsloth/outputs/lfm2-350m-v3-5-boundary-repair-security-triage-lora
adapter_name: lfm2-350m-v3-5-boundary-repair-security-triage-lora
serve_alias: lfm2-security-triage-v3-5
```

เหตุผลที่เริ่มจาก base คือ v3.5 ต้องวัดผลของ dataset repair โดยตรง ถ้า continue จาก v3.4 adapter จะปนผลของ previous adapter drift กับข้อมูล supplement ใหม่

## Evaluation Commands

Pre-train artifact checks:

```bash
rtk .venv/bin/python scripts/create_v3_5_failure_slice.py
rtk .venv/bin/python scripts/create_v3_5_boundary_repair_dataset.py
rtk .venv/bin/python -m unittest tests/test_v3_5_boundary_repair_workflow.py
rtk .venv/bin/python ml/unsloth/inference.py --preflight-only --config ml/unsloth/config.v3-5.yaml
```

Train command:

```bash
rtk .venv/bin/python ml/unsloth/train_lora.py --config ml/unsloth/config.v3-5.yaml
```

Canonical hard-contrast probe after serving alias `lfm2-security-triage-v3-5`:

```bash
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v3-5 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TEMPERATURE=0 \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.md
```

Runtime probe second. Force the v3.5 alias and temp 0.3 runtime parameters in env so a stale `config-adapter.yml` cannot silently produce a v3.4 or temp 0 report:

```bash
OPENAI_COMPATIBLE_CONFIG_PATH=config-adapter.yml \
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v3-5 \
OPENAI_COMPATIBLE_TEMPERATURE=0.3 \
OPENAI_COMPATIBLE_TOP_P=0.9 \
OPENAI_COMPATIBLE_EXTRA_BODY='{"min_p":0.15,"repetition_penalty":1.05}' \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/generated/v3-hard-contrast-security-triage.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.md
```

Mini semantic eval only if hard-contrast gates pass:

```bash
OPENAI_COMPATIBLE_MODEL=lfm2-security-triage-v3-5 \
OPENAI_COMPATIBLE_RESPONSE_FORMAT=structured_outputs \
OPENAI_COMPATIBLE_SCHEMA_PATH=data/schemas/triage-output.schema.json \
OPENAI_COMPATIBLE_TEMPERATURE=0 \
.venv/bin/python scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/mini-semantic-eval.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-v3-5-mini-semantic-eval.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-v3-5-mini-semantic-eval.md
```

## Training Result

ผู้ใช้รัน v3.5 training จาก `ml/unsloth/config.v3-5.yaml` แล้วรายงาน `status=training_complete`, `train_records=910`, `validation_records=75`, final `train_loss=0.6392523148461529`, runtime `347.5661s`, throughput `10.588 train_samples_per_second` และ `1.323 train_steps_per_second` (source: reports/phase-6-v3-5-boundary-training-result.json)

training result ถูกบันทึกไว้ที่:

```text
reports/phase-6-v3-5-boundary-training-result.json
reports/phase-6-v3-5-boundary-training-result.md
```

## V3.5 Temp 0 Hard-Contrast Probe Result

canonical temp 0 run ใช้ alias `lfm2-security-triage-v3-5`, `structured_outputs`, split `data/generated/v3-hard-contrast-security-triage.jsonl` จำนวน 50 records แล้วบันทึก report JSON/MD และ HTML infographic (source: reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json, source: reports/phase-6-v3-5-temp-0-hard-contrast-memorization-probe-infographic.html)

| Metric | Result | Read |
| --- | ---: | --- |
| Label accuracy | `0.84` | ผ่าน overall gate และดีขึ้นจาก v3.4 temp 0 ที่ `0.68` |
| JSON parse / schema success | `0.98 / 0.98` | ยังไม่เต็ม; invalid output `1` |
| Severity accuracy | `0.78` | ดีขึ้นจาก v3.4 temp 0 ที่ `0.72` |
| Suspicious accuracy | `0.92` | ดีขึ้นจาก v3.4 temp 0 ที่ `0.88` |
| Evidence partial match | `0.98` | ดีมาก แต่ยังมี invalid SQLi หนึ่งเคส |
| Average latency | `490.6283 ms` | เร็วกว่ารอบ temp 0.3 |

Per-label canary: `normal=8/10`, `failed_login_bruteforce=10/10`, `sql_injection_attempt=4/10`, `directory_traversal_attempt=10/10`, `port_scan_or_recon=10/10` โดย predicted `failed_login_bruteforce=12/50` ผ่าน gravity ceiling แล้ว แต่ SQLi ยังต่ำกว่า target `>=7/10` (source: reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json)

label mismatches เหลือ 8 เคส: normal -> brute force `2`, SQLi -> traversal `4`, SQLi -> normal `1`, และ SQLi -> invalid `1` โดย invalid ยังคือ `v3-hard-000030` ซึ่งเป็น quote-heavy SQLi payload (source: reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json)

## V3.5 Temp 0.3 Runtime Probe Result

temp 0.3 runtime probe ใช้ alias `lfm2-security-triage-v3-5`, `temperature=0.3`, `top_p=0.9`, `min_p=0.15`, `repetition_penalty=1.05` บน hard-contrast split เดียวกัน แล้วบันทึก report JSON/MD และ HTML infographic (source: reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json, source: reports/phase-6-v3-5-temp-03-hard-contrast-memorization-probe-infographic.html)

| Metric | Result | Read |
| --- | ---: | --- |
| Label accuracy | `0.84` | เท่า temp 0 และผ่าน overall gate |
| JSON parse / schema success | `0.98 / 0.98` | ยังติด invalid output `1` เหมือน temp 0 |
| Severity accuracy | `0.74` | ต่ำกว่า temp 0 |
| Suspicious accuracy | `0.92` | เท่า temp 0 |
| Evidence partial match | `0.96` | ต่ำกว่า temp 0 เล็กน้อย |
| Average latency | `629.195529 ms` | ช้ากว่า temp 0 |

Per-label canary ยังเป็นภาพเดียวกับ temp 0: `normal=8/10`, `failed_login_bruteforce=10/10`, `sql_injection_attempt=4/10`, `directory_traversal_attempt=10/10`, `port_scan_or_recon=10/10` และ predicted `failed_login_bruteforce=12/50`; runtime sampling ไม่ได้แก้ SQLi/invalid JSON จึงไม่ควรใช้เป็นทางผ่านไป Phase 7 (source: reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json)

## Exit Criteria

v3.5 เปิดทางไป mini semantic eval หรือ Phase 7 ได้ต่อเมื่อ hard-contrast temp 0 ผ่าน gate เหล่านี้:

| Gate | Target |
| --- | ---: |
| JSON parse success | `1.0` |
| Schema success | `1.0` |
| Invalid outputs | `0` |
| Label accuracy | `>=0.80` |
| SQLi correct | `>=7/10` |
| Traversal correct | `>=7/10` |
| Port/recon correct | `>=8/10` |
| Normal correct | `>=8/10` |
| Predicted brute force | `<=14/50` |

ถ้า temp 0 ยังไม่ผ่าน ให้ slice failure ต่อจาก v3.5 hard-contrast report ก่อน ไม่ข้ามไป fixed test

Current read: temp 0 ผ่าน overall label accuracy, traversal, port/recon, normal และ brute-force gravity แล้ว แต่ยัง fail JSON/schema, invalid output และ SQLi canary ดังนั้น next repair ควรเป็น v3.5.1 ที่แคบมาก: SQLi-vs-traversal contrast และ quote-heavy structured-output validity

## Hold Fixed Test

`data/splits/test.jsonl` ยังเป็น held-out comparison split สำหรับ Phase 7 เท่านั้น v3.5 generator, failure slice, config preflight และ unit test ต้องไม่ใช้ split นี้เป็นแหล่งเลือกตัวอย่างหรือจูน decision ใด ๆ

## Work Log

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-22 | Codex | Created v3.5 failure slice from v3.4 temp 0 hard-contrast report | `scripts/create_v3_5_failure_slice.py`, `reports/phase-6-v3-5-boundary-failure-slice.json`, `reports/phase-6-v3-5-boundary-failure-slice.md` | Complete |
| 2026-05-22 | Codex | Created deterministic 200-record boundary repair supplement and v3.5 train/validation splits | `scripts/create_v3_5_boundary_repair_dataset.py`, `data/generated/v3-5-boundary-repair-security-triage.jsonl`, `data/splits/train-v3-5-boundary-repair.jsonl`, `data/splits/validation-v3-5-boundary-repair.jsonl` | Complete |
| 2026-05-22 | Codex | Added v3.5 Unsloth config and allowed v3.5 split paths in preflight | `ml/unsloth/config.v3-5.yaml`, `ml/unsloth/train_lora.py` | Complete |
| 2026-05-22 | Codex | Added regression test coverage for failure slice, data generation, split counts, metadata stripping, fixed-test hash, formatting, and preflight | `tests/test_v3_5_boundary_repair_workflow.py` | Passing |
| 2026-05-22 | Codex | Updated inference preflight so the documented v3.5 preflight command can run without a log input | `ml/unsloth/inference.py` | Complete |
| 2026-05-22 | Codex | Fixed v3.5 eval commands to force model/temp runtime overrides and wired LoRA `target_modules` from YAML | `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md`, `scripts/model_adapters/openai_compatible.py`, `ml/unsloth/train_lora.py`, `tests/test_openai_adapter_config.py` | Complete |
| 2026-05-22 | Codex | Removed over-strict pre-LoRA target-module introspection after LFM2/Unsloth wrapper hid valid target names from `named_modules()` | `ml/unsloth/train_lora.py` | Fixed training blocker |
| 2026-05-22 | User/Codex | Recorded v3.5 training completion and hard-contrast temp 0/temp 0.3 probes with HTML reports | `reports/phase-6-v3-5-boundary-training-result.json`, `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json`, `reports/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json`, `reports/phase-6-v3-5-temp-0-hard-contrast-memorization-probe-infographic.html`, `reports/phase-6-v3-5-temp-03-hard-contrast-memorization-probe-infographic.html` | Improved to `0.84`, still held |

## Decision Log

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-22 | Make v3.5 a repair run, not Phase 7 | v3.4 temp 0 still misses contract and semantic gates | Hard-contrast and mini semantic eval must improve before fixed split comparison |
| 2026-05-22 | Build failure slice from v3.4 temp 0, not temp 0.3 | temp 0 is the canonical deterministic check and exposed invalid quoted SQLi output | Dataset repair targets the stricter failure profile |
| 2026-05-22 | Add no brute-force positives in v3.5 | Brute-force recall is already strong and over-predicted | Supplement shifts probability mass back to SQLi, traversal, port/recon, and normal |
| 2026-05-22 | Train from `unsloth/LFM2-350M` base | Need a clean read on dataset repair rather than incremental adapter drift | Output directory and alias are versioned as v3.5 |
| 2026-05-22 | Use internet sources only as design references | OWASP/Sigma/structured-output/TRL/Unsloth docs inform synthetic pattern design and workflow, not copied raw data | Dataset remains deterministic and repo-owned |
| 2026-05-22 | Force runtime request overrides in v3.5 eval commands | `config-adapter.yml` can lag behind the report name and still point at v3.4 or temp 0 | v3.5 temp 0.3 commands now set model, temperature, top_p, and extra_body explicitly through adapter env vars |
| 2026-05-22 | Let Unsloth/PEFT validate LoRA target modules | LFM2 through Unsloth may not expose every valid adapter target through plain `model.named_modules()` before `get_peft_model` runs | Training no longer fails early on `down_proj`, `gate_proj`, `o_proj`, or `up_proj` being absent from pre-LoRA introspection |
| 2026-05-22 | Hold mini semantic eval and fixed split after v3.5 probes | v3.5 hits `label_accuracy=0.84`, but SQLi remains `4/10` and JSON/schema remains `0.98` with invalid output `1` | Next work should be a narrow v3.5.1 SQLi/quote-output repair slice before any broader evaluation |

## Related Pages

- [[output-structure-fix/README]]
- [[output-structure-fix/phase-6-v3-4-boundary-repair-plan]]
- [[output-structure-fix/phase-7-fixed-split-comparison]]
- [[label-imbalance-and-prediction-collapse]]
- [[openai-adapter-runtime-config]]
- [[structured-output-reliability-research-2026]]
- [[Day6]]

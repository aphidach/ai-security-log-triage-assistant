# Phase 6 V3.2 Hard Contrast Memorization Probe

**Summary**

หน้าเอกสารนี้บันทึกผล v3.2 hard-contrast memorization probe หลัง train adapter ใหม่ด้วย `ml/unsloth/config.v3-2.yaml` ผลรวมดีขึ้นจาก v3.1 ชัดเจน: `label_accuracy` เพิ่มจาก `0.34` เป็น `0.56`, JSON/schema ยังนิ่งที่ `1.0`, และ prediction collapse ไป `failed_login_bruteforce` ลดจาก 36/50 เหลือ 21/50 แต่ probe นี้ยังไม่ผ่าน canary เพราะ SQLi เหลือถูกแค่ 1/10 และ port scan ถูกแค่ 2/10 (source: reports/openai-compatible-vllm-structured-outputs-v3-2-hard-contrast-memorization-probe.json)

**Sources**

- `reports/openai-compatible-vllm-structured-outputs-v3-2-hard-contrast-memorization-probe.json` สำหรับ metric, adapter metadata, predicted distribution และ per-sample result ของ v3.2 probe (source: reports/openai-compatible-vllm-structured-outputs-v3-2-hard-contrast-memorization-probe.json)
- `reports/openai-compatible-vllm-structured-outputs-v3-2-hard-contrast-memorization-probe.md` สำหรับ markdown evaluator summary (source: reports/openai-compatible-vllm-structured-outputs-v3-2-hard-contrast-memorization-probe.md)
- `reports/phase-6-v3-2-hard-contrast-memorization-probe-infographic.html` สำหรับ stakeholder-readable HTML infographic (source: reports/phase-6-v3-2-hard-contrast-memorization-probe-infographic.html)
- `reports/openai-compatible-vllm-structured-outputs-v3-1-2-hard-contrast-memorization-probe.json` สำหรับ baseline comparison ของ v3.1 hard-contrast probe (source: reports/openai-compatible-vllm-structured-outputs-v3-1-2-hard-contrast-memorization-probe.json)
- `ml/unsloth/config.v3-2.yaml` สำหรับ training recipe ของ v3.2 เช่น `max_steps = 180`, prompt version และ output directory (source: ml/unsloth/config.v3-2.yaml)
- `data/generated/v3-hard-contrast-security-triage.jsonl` สำหรับ hard-contrast probe split 50 records ที่ใช้เป็น memorization diagnostic ไม่ใช่ fixed eval split (source: data/generated/v3-hard-contrast-security-triage.jsonl)
- user training summary วันที่ 2026-05-21 สำหรับ train completion metadata: train 500 records, validation 75 records, epoch `2.864`, train loss `1.3138311010268`, runtime `155.398s` (source: user-provided terminal output, 2026-05-21)

**Last updated**

2026-05-21

## Status

Improved but failed canary. v3.2 พิสูจน์ว่า training recipe ที่แรงขึ้นช่วยให้ model ขยับออกจาก brute-force collapse ได้ แต่ยังจำ hard-contrast training supplement ไม่พอ จึงยังไม่ควรใช้ fixed `data/splits/test.jsonl`

HTML infographic:

```text
reports/phase-6-v3-2-hard-contrast-memorization-probe-infographic.html
```

## Run Identity

| Field | Value |
| --- | --- |
| Adapter | `openai-compatible` |
| Runtime/mode | vLLM `structured_outputs` |
| Served model name | `lfm2-security-triage-v3-2` |
| Split | `data/generated/v3-hard-contrast-security-triage.jsonl` |
| Samples | 50 |
| Prompt version | `triage-json-v2.1` |
| JSON report | `reports/openai-compatible-vllm-structured-outputs-v3-2-hard-contrast-memorization-probe.json` |
| Markdown report | `reports/openai-compatible-vllm-structured-outputs-v3-2-hard-contrast-memorization-probe.md` |

## Training Snapshot

| Field | Value |
| --- | ---: |
| Config path | `ml/unsloth/config.v3-2.yaml` |
| Output dir | `ml/unsloth/outputs/lfm2-350m-v3-2-hard-contrast-security-triage-lora` |
| Base model | `unsloth/LFM2-350M` |
| Train records | `500` |
| Validation records | `75` |
| Max steps | `180` |
| Reported epoch | `2.864` |
| Train loss | `1.3138311010268` |
| Train runtime seconds | `155.398` |
| Train samples/sec | `9.267` |
| Train steps/sec | `1.158` |

## Metrics

| Metric | Value | Note |
| --- | ---: | --- |
| `label_accuracy` | `0.56` | improved from v3.1 hard probe `0.34`, but below canary target |
| `json_parse_success_rate` | `1.0` | output contract is stable |
| `schema_success_rate` | `1.0` | all outputs match schema |
| `severity_accuracy` | `0.78` | improved from `0.64` |
| `is_suspicious_accuracy` | `0.9` | improved from `0.8` |
| `evidence_partial_match` | `0.92` | evidence extraction remains strong |
| `average_latency_ms` | `487.630723` | lower than v3.1 hard probe `726.040956` |
| `invalid_output_count` | `0` | no invalid outputs |

## V3.1 To V3.2 Comparison

| Signal | V3.1 hard probe | V3.2 hard probe | Interpretation |
| --- | ---: | ---: | --- |
| `label_accuracy` | `0.34` | `0.56` | training recipe helped, but canary still fails |
| `severity_accuracy` | `0.64` | `0.78` | priority mapping improved |
| `is_suspicious_accuracy` | `0.8` | `0.9` | normal/suspicious boundary improved |
| `evidence_partial_match` | `0.9` | `0.92` | evidence remains usable |
| `average_latency_ms` | `726.040956` | `487.630723` | runtime was faster on this run |
| predicted `failed_login_bruteforce` | `36/50` | `21/50` | brute-force collapse reduced |
| predicted `normal` | `0/50` | `11/50` | v3.2 learned normal hard negatives better |
| predicted `sql_injection_attempt` | `9/50` | `2/50` | SQLi is now under-predicted |
| predicted `port_scan_or_recon` | `3/50` | `2/50` | port scan is still under-predicted |

## Per-Label Accuracy

| Expected label | Correct | Main failure pattern |
| --- | ---: | --- |
| `normal` | `8/10` | 2 records still over-escalate to `failed_login_bruteforce` |
| `failed_login_bruteforce` | `10/10` | stable |
| `sql_injection_attempt` | `1/10` | split across `normal`, `failed_login_bruteforce`, and `directory_traversal_attempt` |
| `directory_traversal_attempt` | `7/10` | mostly improved, with residual confusion to brute force |
| `port_scan_or_recon` | `2/10` | split between `failed_login_bruteforce` and `directory_traversal_attempt` |

## Confusion Matrix

| Expected \ Predicted | `normal` | `failed_login_bruteforce` | `sql_injection_attempt` | `directory_traversal_attempt` | `port_scan_or_recon` |
| --- | ---: | ---: | ---: | ---: | ---: |
| `normal` | 8 | 2 | 0 | 0 | 0 |
| `failed_login_bruteforce` | 0 | 10 | 0 | 0 | 0 |
| `sql_injection_attempt` | 3 | 3 | 1 | 3 | 0 |
| `directory_traversal_attempt` | 0 | 2 | 1 | 7 | 0 |
| `port_scan_or_recon` | 0 | 4 | 0 | 4 | 2 |

อ่านตามแถว: label จริงอยู่ซ้าย, label ที่ model ทายอยู่ด้านบน

## Interpretation

v3.2 เป็นสัญญาณดีว่าปัญหาไม่ได้ตันที่ JSON/schema แล้ว และไม่ได้ตันทั้งหมดที่ model capacity ด้วย เพราะ normal hard negatives และ traversal ดีขึ้นมากหลังเพิ่ม training strength

แต่ v3.2 ยังไม่ผ่าน hard-contrast memorization canary ด้วยเหตุผลหลักสองข้อ:

- `sql_injection_attempt` ถูกเพียง 1/10 และไม่ใช่ collapse แบบเดียวแล้ว แต่กระจายผิดไป `normal`, `failed_login_bruteforce`, และ `directory_traversal_attempt`
- `port_scan_or_recon` ถูกเพียง 2/10 และถูกดูดไป `failed_login_bruteforce` กับ `directory_traversal_attempt` เท่ากัน

ดังนั้นรอบถัดไปไม่ควรเพิ่มทุก label เท่า ๆ กันแบบกว้าง ๆ จุดที่ควรแก้คือ SQLi และ port-scan boundary โดยตรง โดยเฉพาะตัวอย่างคู่ที่แยกคำว่า `select`, `union`, path-like tokens และหลายพอร์ตออกจาก label ที่ไม่เกี่ยวข้อง

## Decision

Do not move to fixed split comparison.

v3.2 ยังเป็น diagnostic run ไม่ใช่ candidate สำหรับ Phase 7 เพราะ hard-contrast training supplement เองยังได้แค่ `0.56` ถ้ารัน `data/splits/test.jsonl` ตอนนี้จะเอา fixed test มาใช้เร็วเกินไปและเสี่ยงทำให้รอบ tuning ถัดไปปนกับ final comparison

งานถัดไปควรเป็น v3.3 targeted canary:

1. เพิ่ม weight หรือ duplicate เฉพาะ `sql_injection_attempt` และ `port_scan_or_recon` hard cases
2. เพิ่ม paired examples ที่ SQLi จริงชนกับ normal query ที่มีคำว่า `select`/`union`
3. เพิ่ม paired examples ที่ port scan ชนกับ traversal และ brute force โดยใช้ `unique_ports`, `nmap fingerprint`, `SYN scan detected`, horizontal scan และ service enumeration
4. รัน hard-contrast probe ซ้ำก่อน mini semantic eval
5. ใช้ mini semantic eval เฉพาะเมื่อ hard-contrast canary ขยับใกล้ `0.80+`

v3.3 preparation now implements this next move as a targeted training-time weighting layer: SQLi and port-scan positives are weighted higher, normal pairs with similar SQLi/port-scan language are included at lighter weight, and the original hard-contrast file remains the first rerun probe before mini semantic eval (source: docs/output-structure-fix/phase-6-v3-3-targeted-canary.md, scripts/create_v3_3_training_split.py)

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Created v3.2 hard-contrast memorization probe doc and linked HTML infographic | `reports/phase-6-v3-2-hard-contrast-memorization-probe-infographic.html`, `reports/openai-compatible-vllm-structured-outputs-v3-2-hard-contrast-memorization-probe.json` | Created |
| 2026-05-21 | Codex | Prepared v3.3 targeted canary follow-up from v3.2 decision | `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md`, `scripts/create_v3_3_training_split.py`, `ml/unsloth/config.v3-3.yaml` | Prepared |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Hold fixed test split after v3.2 hard-contrast probe | v3.2 improves label accuracy to `0.56` but hard-contrast canary still fails, especially SQLi `1/10` and port scan `2/10` | Next work becomes v3.3 targeted canary before mini semantic eval or fixed split comparison |
| 2026-05-21 | Weight SQLi and port scan in v3.3 before any mini/fixed eval | The canary failure is concentrated in SQLi and port scan, while brute force is already stable | v3.3 adds targeted SQLi/port-scan examples and normal pairs, then reruns the hard-contrast probe first |

## Related pages

- [[output-structure-fix/phase-6-v3-1-mini-semantic-eval]]
- [[output-structure-fix/phase-6-v3-hard-contrast-dataset]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[output-structure-fix/phase-6-v3-3-targeted-canary]]
- [[label-imbalance-and-prediction-collapse]]
- [[fine-tuning-notes]]

# Phase 6 V3.1 Mini Semantic Eval

**Summary**

หน้าเอกสารนี้บันทึกผล mini semantic eval ของ v3.1 model หลังเพิ่ม weighted hard contrast split และ align prompt เป็น `triage-json-v2.1` แล้ว ผลสรุปคือ output contract ดีขึ้นเล็กน้อย แต่ semantic label ยังไม่ฟื้น: `label_accuracy = 0.36` เท่า v3, predicted `failed_login_bruteforce` เพิ่มเป็น 18/25 และ `normal` ยังถูกทายผิดทั้งหมด (source: reports/phase-6/openai-compatible-vllm-structured-outputs-v3-1-model-mini-semantic-eval.json)

**Sources**

- `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-1-model-mini-semantic-eval.json` สำหรับ metric, predicted distribution, confusion matrix และ adapter metadata (source: reports/phase-6/openai-compatible-vllm-structured-outputs-v3-1-model-mini-semantic-eval.json)
- `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-1-model-mini-semantic-eval.md` สำหรับ markdown evaluator summary (source: reports/phase-6/openai-compatible-vllm-structured-outputs-v3-1-model-mini-semantic-eval.md)
- `reports/phase-6/phase-6-v3-1-mini-semantic-eval-infographic.html` สำหรับ stakeholder-readable HTML infographic (source: reports/phase-6/phase-6-v3-1-mini-semantic-eval-infographic.html)
- `ml/unsloth/config.example.yaml` สำหรับ v3.1 train/validation path, prompt version และ output adapter directory (source: ml/unsloth/config.example.yaml)
- `docs/output-structure-fix/phase-6-v3-hard-contrast-dataset.md` สำหรับ v3.1 weighted split rationale (source: docs/output-structure-fix/phase-6-v3-hard-contrast-dataset.md)

**Last updated**

2026-05-21

## Status

Failed semantic gate. ยังไม่ควรใช้ fixed `data/splits/test.jsonl` เพราะ mini semantic eval ยังไม่ผ่าน และยังมี prediction collapse ไปทาง `failed_login_bruteforce`

HTML infographic:

```text
reports/phase-6/phase-6-v3-1-mini-semantic-eval-infographic.html
```

## Run Identity

| Field | Value |
| --- | --- |
| Adapter | `openai-compatible` |
| Runtime/mode | vLLM `structured_outputs` |
| Served model name | `lfm2-security-triage` |
| Split | `data/splits/mini-semantic-eval.jsonl` |
| Samples | 25 |
| Prompt version | `triage-json-v2.1` |
| JSON report | `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-1-model-mini-semantic-eval.json` |
| Markdown report | `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-1-model-mini-semantic-eval.md` |

## Metrics

| Metric | Value | Note |
| --- | ---: | --- |
| `label_accuracy` | `0.36` | unchanged from v3 |
| `json_parse_success_rate` | `0.96` | improved from v3 `0.92` |
| `schema_success_rate` | `0.96` | improved from v3 `0.92` |
| `severity_accuracy` | `0.64` | unchanged from v3 |
| `is_suspicious_accuracy` | `0.76` | unchanged from v3 |
| `evidence_partial_match` | `0.64` | down from v3 `0.68` |
| `average_latency_ms` | `811.942363` | lower than v3 `842.189018` |
| `invalid_output_count` | `1` | improved from v3 `2` |

## V3 To V3.1 Comparison

| Signal | V3 | V3.1 | Interpretation |
| --- | ---: | ---: | --- |
| `label_accuracy` | `0.36` | `0.36` | semantic quality ไม่ดีขึ้น |
| `json_parse_success_rate` | `0.92` | `0.96` | contract ดีขึ้นเล็กน้อย |
| `schema_success_rate` | `0.92` | `0.96` | schema-valid เพิ่มขึ้น 1 sample |
| `evidence_partial_match` | `0.68` | `0.64` | evidence selection ถอยลงเล็กน้อย |
| predicted `failed_login_bruteforce` | `17/25` | `18/25` | prediction collapse ยังหนักมาก |

## Confusion Matrix

| Expected \ Predicted | `normal` | `failed_login_bruteforce` | `sql_injection_attempt` | `directory_traversal_attempt` | `port_scan_or_recon` | `<invalid>` |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `normal` | 0 | 4 | 1 | 0 | 0 | 0 |
| `failed_login_bruteforce` | 0 | 4 | 0 | 0 | 0 | 1 |
| `sql_injection_attempt` | 0 | 4 | 1 | 0 | 0 | 0 |
| `directory_traversal_attempt` | 0 | 4 | 0 | 1 | 0 | 0 |
| `port_scan_or_recon` | 0 | 2 | 0 | 0 | 3 | 0 |

อ่านตามแถว: label จริงอยู่ซ้าย, label ที่ model ทายอยู่ด้านบน

## Interpretation

v3.1 ทำให้ output contract ดีขึ้นเล็กน้อย แต่ไม่แก้ root cause หลัก ตอนนี้ปัญหาไม่ใช่ JSON/schema เป็นหลักแล้ว แต่เป็น semantic mapping จาก evidence ไป label:

- `normal` ยังได้ 0/5 เพราะ single failed login และ health check ถูกตีเป็น suspicious/high
- `sql_injection_attempt` ได้ 1/5 เพราะ SQLi payload ใน login/query ถูกลากไป `failed_login_bruteforce`
- `directory_traversal_attempt` ได้ 1/5 เพราะ traversal path ถูกลากไป `failed_login_bruteforce`
- `port_scan_or_recon` ดีที่สุดที่ 3/5 แต่ยังถูกทายเป็น brute force 2 cases

มีอีก caveat สำคัญ: adapter metadata ยังใช้ served model name เดิม `lfm2-security-triage` เหมือน v3 จึงต้อง verify ว่า endpoint โหลด adapter v3.1 จริงก่อนสรุปว่า v3.1 training recipe ล้มเหลวเต็มที่ (source: reports/phase-6/openai-compatible-vllm-structured-outputs-v3-1-model-mini-semantic-eval.json)

## Decision

Do not move to Phase 7 fixed split comparison.

งานถัดไปควรเป็น diagnostic ไม่ใช่ train เพิ่มแบบเดิมทันที:

1. ยืนยัน vLLM launch command, adapter path และ served model name ให้แยก v3.1 ชัดเจน เช่น `lfm2-security-triage-v3-1`
2. รัน hard-contrast memorization probe กับ `data/generated/v3-hard-contrast-security-triage.jsonl`
3. ถ้า model ยังทาย hard contrast training examples ผิด ให้ตรวจ adapter loading หรือขยับ training recipe เช่น steps/epochs/LoRA rank
4. ถ้า model จำ hard contrast ได้ แต่ mini ยังพัง ให้เพิ่ม coverage ตาม mini failure แทนการ weight ซ้ำอย่างเดียว
5. ถือ fixed `data/splits/test.jsonl` ไว้จนกว่า mini semantic eval จะผ่าน gate ขั้นต่ำ

## Work Log

Append-only log สำหรับบันทึกว่าเอกสารนี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-21 | Codex | Created v3.1 mini semantic eval doc and linked HTML infographic | `reports/phase-6/phase-6-v3-1-mini-semantic-eval-infographic.html`, `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-1-model-mini-semantic-eval.json` | Created |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-21 | Hold fixed test split after v3.1 mini eval | v3.1 remains at `label_accuracy = 0.36` and predicts `failed_login_bruteforce` 18/25 despite better JSON/schema success | Next work shifts to adapter-loading verification and hard-contrast memorization probe before another training run |

## Related pages

- [[output-structure-fix/phase-6-v3-hard-contrast-dataset]]
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]
- [[output-structure-fix/phase-6-1-evidence-constraints]]
- [[label-imbalance-and-prediction-collapse]]
- [[fine-tuning-notes]]

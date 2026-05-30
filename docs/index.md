# Docs Index

**Summary**

สารบัญเอกสารของ `AI Security Log Triage Assistant` สำหรับนำทางแผน POC, day plan, rationale และ documentation log

**Sources**

- `AGENTS.md` สำหรับ mission และ repo scope (source: AGENTS.md)
- `docs/poc-plan.md` สำหรับ milestone และ repo structure (source: docs/poc-plan.md)
- `docs/project-structure-rationale.md` สำหรับเหตุผลของ directory structure (source: docs/project-structure-rationale.md)
- `reports/README.md` สำหรับโครงสร้าง report artifacts แบบ public-facing (source: reports/README.md)
- `docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md` และ v4.7 report artifacts สำหรับสถานะ Qwen3.5 calibration ล่าสุด (source: docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md, source: reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-auth-sqli-severity-calibration-probe.json, source: reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-7-temp-0-hard-contrast-memorization-probe.json)
- `docs/output-structure-fix/phase-8-v4-8-qwen35-auth-sqli-diagnostic-plan.md` และ v4.8 diagnostic audit artifacts สำหรับ next-step หลัง v4.7 hold (source: docs/output-structure-fix/phase-8-v4-8-qwen35-auth-sqli-diagnostic-plan.md, source: reports/phase-8/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json)

**Last updated**

2026-05-30

## Core Pages

- [[poc-plan]]: แผน POC หลัก ตั้งแต่ scope, success criteria, dataset, baseline, fine-tuning และ evaluation
- [[project-structure-rationale]]: เหตุผลที่ต้องแยก `data/`, `scripts/`, `ml/`, `reports/` และ `frontend/`
- [[scripts]]: runbook กลางสำหรับคำสั่ง setup, generate dataset, baseline, evaluate, probe endpoint, frontend และ optional Unsloth/GPU workflow
- [[triage-output-schema]]: อธิบาย `data/schemas/triage-output.schema.json` ซึ่งเป็น output contract กลางของ dataset, evaluator, model adapter และ UI
- [[label-taxonomy]]: ความหมาย วิธีใช้ evidence และ caveat ของ label รอบแรกทั้ง 5 ตัว
- [[dataset-input-output-format]]: รูปแบบ JSONL ของ `instruction`, `input`, `output`, ขนาด dataset รอบแรก และ validation rules
- [[data-formats-for-llm-training]]: สรุปรูปแบบข้อมูลสำหรับ LLM training และเหตุผลที่โปรเจกต์นี้ควรใช้ `instruction/input/output` เป็น source format แล้ว render เป็น `messages`
- [[data-card]]: data card ของ synthetic dataset รอบแรก รวมที่มา วิธี generate split ข้อจำกัด และ privacy note
- [[log-type-examples]]: คำอธิบาย log format ที่ dataset จำลองไว้ เช่น web access, SSH auth, WAF, IDS และ netflow-style log พร้อมตัวอย่าง
- [[evaluation-metrics-rationale]]: เหตุผลที่ต้องวัด metric รอบแรก เช่น label accuracy, JSON/schema validity, evidence match และ latency
- [[label-imbalance-and-prediction-collapse]]: แนวทางแยก data imbalance ออกจาก prediction collapse ใน Phase 6 พร้อม research-backed mitigation เช่น balanced sampling, focal/class-balanced loss, hard contrast examples และ macro metrics
- [[fine-tuning-notes]]: notes สำหรับ Unsloth fine-tuning path, Colab/GPU setup, limitation, Day 6 handoff, Qwen3.5 exploratory LoRA smoke pilot ด้วย `FastVisionModel` และ v4.5 trained-Qwen hard-contrast result
- [[lfm2-350m-model-card-notes]]: สรุปคำแนะนำจาก Hugging Face model card ของ `unsloth/LFM2-350M` และผลต่อ config v3.3, chat template, generation params และ runtime probe
- [[small-model-fine-tuning-candidates-6gb]]: shortlist ของ small model ไม่เกิน `4B` สำหรับ GPU `6GB`, รวม LFM2.5, Qwen3.5, Granite 4.1, SmolLM3, QLoRA memory guardrails และ caveat ก่อนเปิด fixed split
- [[model-candidates/unsloth-qwen3.5-0.8b/model-card]]: downloaded Hugging Face model card ของ `unsloth/Qwen3.5-0.8B` สำหรับ Phase 8 v4.3 capacity/architecture diagnostic
- [[openai-adapter-runtime-config]]: วิธีใช้ `config-adapter.yml` เพื่อปรับ OpenAI-compatible adapter runtime เช่น `temperature`, `top_p`, structured output mode และ backend `extra_body`
- [[demo-script]]: talk track สำหรับ demo Day 7 แบบ 2-3 นาที พร้อม guardrails ไม่ overclaim และไม่เปิด fixed split โดยไม่ผ่าน gate
- [[model-repetition-loop-diagnostics]]: runbook สำหรับแยกสาเหตุ model loop token ซ้ำ ๆ จาก decoding, EOS/chat template, structured outputs, runtime, quantization และ fine-tuning format
- [[output-contract-hardening]]: สรุปรอบแก้ prompt `v2`, structured output adapter, schema sanitizer, smoke split ใหม่ และ decision ว่ายังไม่ retrain ทันที
- [[structured-output-reliability-research-2026]]: สรุปข้อมูลปี 2026 เรื่อง structured output reliability, constrained decoding, validation/retry และแผนตัดสินใจต่อหลัง smoke ยังผ่าน JSON/schema เพียง 1/5
- [[structured-output-fix-plan]]: แผนลงมือแก้ output contract ตั้งแต่ freeze evidence, backend inventory, probe hardening, runtime capability matrix, contract gate, mini semantic eval ไปจนถึง fixed split
- [[output-structure-fix/README]]: working notes แยก phase สำหรับงาน output contract fix ตั้งแต่ Phase 1 เป็นต้นไป
- [[model-output/README]]: บันทึก versioned model output notes, template และ behavior ของ model แต่ละรอบ
- [[model-output/v1-lfm2-350m-security-triage]]: สรุปว่า v1 train/serve ได้ แต่ออก API เป็น prose/prose+JSON จึงยังไม่ผ่าน output contract
- [[model-output/v2-lfm2-350m-security-triage-responses-parse]]: สรุป v2 artifact `unsloth_LFM2-350M_1779162226` หลังย้าย adapter มา OpenAI SDK + Pydantic `responses_parse`; smoke ยังผ่าน schema เพียง 1/5
- [[dataset-source-strategy]]: กลยุทธ์เลือกและจัดลำดับแหล่ง dataset ภายนอก เช่น Loghub, OTRF/Mordor, BOTS, SigmaHQ, Splunk Attack Data และ Kaggle synthetic candidate
- [[slm-fine-tuning-model-choice]]: สรุป benchmark SLM และเหตุผลที่ POC รอบแรกเริ่มจาก LFM2-350M
- [[slm-rag-fine-tuning-hallucination]]: บทเรียนจาก industrial RAG fine-tuning เรื่อง cost-aware evaluation, factuality และ hallucination taxonomy
- [[tinylora-reasoning-13-parameters]]: สรุป TinyLoRA และบทเรียนเรื่อง RL-based ultra-low-parameter tuning สำหรับ future work

## Day Plans

- [[Day1]]: project foundation, schema, label taxonomy และ repo structure
- [[Day2]]: dataset และ data card
- [[Day3]]: heuristic baseline
- [[Day4]]: model adapters และ evaluator integration
- [[Day5]]: fine-tuning path ด้วย Unsloth, config, training format และ inference wiring
- [[Day6]]: GPU training, fine-tuned evaluation และ comparison report
- [[Day7]]: demo UI และ integration รอบถัดไป

## External References

- [[References]]: แหล่งอ้างอิงและเหตุผลการยืมแนวคิดจาก Unsloth, Axolotl, TRL, lm-evaluation-harness, Loghub, Splunk BOTS, OTRF, SigmaHQ และ OWASP

## Structured Output Fix Phase Notes

- [[output-structure-fix/phase-1-backend-inventory]]: Phase 1 backend inventory, current endpoint metadata, vLLM + Unsloth LoRA serving evidence และ report template
- [[output-structure-fix/phase-2-probe-hardening]]: Phase 2 probe hardening stub สำหรับ adversarial format instruction และ per-sample raw output
- [[output-structure-fix/phase-3-runtime-capability-matrix]]: Phase 3 runtime/mode matrix พร้อมผล vLLM `structured_outputs` ที่ผ่าน output contract
- [[output-structure-fix/phase-4-contract-gate]]: Phase 4 contract gate ที่ผ่านแล้วสำหรับ vLLM `structured_outputs`
- [[output-structure-fix/phase-5-mini-semantic-eval]]: Phase 5 mini semantic eval ที่พร้อมเริ่มหลัง contract ผ่าน
- [[output-structure-fix/phase-6-v3-or-runtime-decision]]: Phase 6 decision and repair note; ปิดแล้วหลัง v3.5 โดย fixed split ยัง held
- [[output-structure-fix/phase-6-1-evidence-constraints]]: Phase 6.1 implementation สำหรับแก้ evidence loop ด้วย schema constraints, adapter sanitizer update และ validator alignment
- [[output-structure-fix/phase-6-v3-hard-contrast-dataset]]: Phase 6 v3 hard-contrast dataset supplement สำหรับแก้ prediction collapse ด้วย paired examples และ hard negatives
- [[output-structure-fix/phase-6-v3-1-mini-semantic-eval]]: ผล v3.1 mini semantic eval, HTML infographic, confusion matrix และ decision ให้ hold fixed test split
- [[output-structure-fix/phase-6-v3-2-hard-contrast-probe]]: ผล v3.2 hard-contrast memorization probe, HTML infographic, confusion matrix และ decision ให้ทำ v3.3 targeted canary ก่อน fixed split
- [[output-structure-fix/phase-6-v3-3-targeted-canary]]: preparation, HTML infographic และผล hard-contrast runtime probe ของ v3.3 targeted weighted split; temp 0.3 ขยับ label accuracy เป็น `0.64` แต่ fixed test ยัง held
- [[output-structure-fix/phase-6-v3-4-boundary-repair-plan]]: แผนและสถานะ v3.4 boundary repair; temp 0.3 ขยับ label accuracy เป็น `0.72` แต่ temp 0 ได้ `0.68` พร้อม HTML infographic แล้ว และ fixed test ยัง held
- [[output-structure-fix/phase-6-v3-5-boundary-repair-plan]]: แผนและผล v3.5 จาก failure slice v3.4 temp 0; ปิดเป็น final Phase 6 repair run หลัง 2048 temp 0.3 ได้ label accuracy `0.88`, JSON/schema `1.0`, invalid `0` แต่ไม่ใช่ Phase 7 clearance
- [[output-structure-fix/phase-7-fixed-split-comparison]]: Phase 7 fixed split comparison result; heuristic label accuracy `1.0`, v3.5 as-is label accuracy `0.84`, JSON/schema `1.0`, final decision `hold`
- [[output-structure-fix/phase-8-v4-sqli-boundary-repair-plan]]: Phase 8 v4 SQLi-first repair trained and probed; hard-contrast JSON/schema `1.0`, invalid `0`, but label accuracy `0.84` and SQLi `4/10` keep mini semantic and fixed comparison held
- [[output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan]]: Phase 8 v4.1 narrow SQLi-boundary repair trained/probed; JSON/schema `1.0`, invalid `0`, but temp 0 SQLi `6/10` and temp 0.3 SQLi `7/10` keep mini semantic and fixed comparison held
- [[output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan]]: Phase 8 v4.2 SQLi-priority prompt diagnostic probed/held; prompt v2.2 reduced SQLi-to-traversal to `0/10` but temp 0 label accuracy fell to `0.64`, SQLi stayed `4/10`, and temp 0.3 lost JSON/schema `1.0`
- [[output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan]]: Phase 8 v4.3 capacity/architecture diagnostic result; base model `unsloth/Qwen3.5-0.8B` passed JSON/schema on smoke and hard-contrast probes, but hard-contrast label accuracy stayed `0.50`/`0.48` with SQLi `3/10`/`2/10`, so the candidate is held and fixed test remains closed
- [[output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan]]: Phase 8 v4.4 boundary audit result; v4.3 Qwen3.5 base-model failures have `26` union IDs and `25` persistent IDs, with SQLi/traversal/recon -> `normal` as the main failure family, so fixed test and v4.4 train artifacts remain closed
- [[output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe]]: Phase 8 v4.5 trained-Qwen LoRA probe; hard-contrast JSON/schema `1.0`, invalid `0`, label accuracy `0.88`, evidence `0.98`, and all suspicious labels `10/10`, but normal is only `4/10` and severity `0.72`, so fixed split remains closed
- [[output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan]]: Phase 8 v4.6 Qwen normal/severity calibration result; train/probe แล้วได้ hard-contrast label `0.90`, severity `0.90`, JSON/schema `1.0`, invalid `0`, แต่ยัง held เพราะ normal `7/10`, SQLi `8/10`, calibration normal `11/15`, และ brute-force severity ยังสูงเกิน
- [[output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan]]: Phase 8 v4.7 Qwen auth/SQLi/severity calibration result; train/probe แล้วได้ hard-contrast label/severity `0.92`, JSON/schema `1.0`, invalid `0`, แต่ยัง held เพราะ v4.7 calibration label `0.366667`, severity `0.60`, normal-auth `0/15`, SQLi-auth `1/5`, และ brute-force medium severity `0/7`
- [[output-structure-fix/phase-8-v4-8-qwen35-auth-sqli-diagnostic-plan]]: Phase 8 v4.8 diagnostic audit; เทียบ v4.6, v4.7, heuristic และ base Qwen3.5 บน v4.7 calibration probe เดิม, heuristic label `0.666667` ชนะ v4.6 `0.433333` และ v4.7 `0.366667`, fixed split ยังปิด
- `reports/phase-8/phase-8-lfm2-350m-vs-qwen35-0-8b-comparison.html`: HTML comparison report for LFM2-350M v4.1 and Qwen3.5-0.8B v4.5 on the same hard-contrast temp 0 probe
- `reports/phase-8/phase-8-v4-6-qwen35-normal-severity-calibration-report.html`: HTML report for Qwen3.5 v4.6 training, calibration probe, hard-contrast probe, gate read, and fixed-split hold decision
- `reports/phase-8/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-report.html`: HTML report for Qwen3.5 v4.7 training summary, calibration probe, hard-contrast probe, gate read, and fixed-split hold decision
- `reports/phase-8/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html`: HTML report for v4.8 diagnostic audit and comparator bucket summary

## Documentation Maintenance

- [[log]]: append-only documentation change log

## Work Log

Append-only log สำหรับบันทึกว่า index นี้เปลี่ยนอะไรไปแล้ว ให้เพิ่ม row ใหม่ด้านล่างเสมอ

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created docs index and linked current planning pages | `docs/index.md` | Drafted |
| 2026-05-16 | Codex | Added SLM model-choice page to core docs | `docs/slm-fine-tuning-model-choice.md` | Updated |
| 2026-05-16 | Codex | Added industrial SLM RAG fine-tuning page to core docs | `docs/slm-rag-fine-tuning-hallucination.md` | Updated |
| 2026-05-16 | Codex | Added TinyLoRA page to core docs | `docs/tinylora-reasoning-13-parameters.md` | Updated |
| 2026-05-16 | Codex | Added evaluation metrics rationale page to core docs | `docs/evaluation-metrics-rationale.md` | Updated |
| 2026-05-16 | Codex | Added dataset source strategy page to core docs | `docs/dataset-source-strategy.md` | Updated |
| 2026-05-16 | Codex | Moved References into the docs wiki directory | `docs/References.md` | Updated |
| 2026-05-16 | Codex | Added triage output schema explanation page | `docs/triage-output-schema.md` | Updated |
| 2026-05-16 | Codex | Added first-pass label taxonomy page to core docs | `docs/label-taxonomy.md` | Updated |
| 2026-05-16 | Codex | Added dataset input/output format page to core docs | `docs/dataset-input-output-format.md` | Updated |
| 2026-05-17 | Codex | Added first synthetic dataset data card to core docs | `docs/data-card.md` | Updated |
| 2026-05-17 | Codex | Added log type examples page to core docs | `docs/log-type-examples.md` | Updated |
| 2026-05-17 | Codex | Added fine-tuning notes page and refreshed day plan labels | `docs/fine-tuning-notes.md`, `docs/index.md` | Updated |
| 2026-05-18 | Codex | Added model-output notes and linked v1 output-contract failure page | `docs/model-output/README.md`, `docs/model-output/v1-lfm2-350m-security-triage.md` | Updated |
| 2026-05-19 | Codex | Added LLM training data format guide to core docs | `docs/data-formats-for-llm-training.md` | Updated |
| 2026-05-19 | Codex | Added output-contract hardening page to the core docs index | `docs/output-contract-hardening.md`, `docs/index.md` | Updated |
| 2026-05-19 | Codex | Added v2 model-output page for OpenAI SDK + Pydantic `responses_parse` smoke results | `docs/model-output/v2-lfm2-350m-security-triage-responses-parse.md`, `docs/index.md` | Updated |
| 2026-05-20 | Codex | Added 2026 structured-output reliability research note to the core docs index | `docs/structured-output-reliability-research-2026.md`, `docs/index.md` | Updated |
| 2026-05-20 | Codex | Added structured output fix plan to the core docs index | `docs/structured-output-fix-plan.md`, `docs/index.md` | Updated |
| 2026-05-20 | Codex | Added structured-output fix phase-detail pages to the docs index | `docs/output-structure-fix/`, `docs/index.md` | Updated |
| 2026-05-20 | Codex | Refreshed structured-output phase descriptions after vLLM passed the contract gate | `docs/output-structure-fix/`, `reports/structured-output/smoke/openai-compatible-vllm-structured-outputs-smoke.json` | Updated |
| 2026-05-20 | Codex | Added model repetition-loop diagnostics page to core docs | `docs/model-repetition-loop-diagnostics.md`, `docs/index.md` | Updated |
| 2026-05-20 | Codex | Added Phase 6.1 evidence constraints plan to the structured-output phase notes | `docs/output-structure-fix/phase-6-1-evidence-constraints.md`, `docs/index.md` | Updated |
| 2026-05-21 | Codex | Updated Phase 6.1 index status after local implementation | `docs/output-structure-fix/phase-6-1-evidence-constraints.md`, `docs/index.md` | Endpoint rerun pending |
| 2026-05-21 | Codex | Added label imbalance and prediction collapse guidance to core docs | `docs/label-imbalance-and-prediction-collapse.md`, `docs/index.md` | Updated |
| 2026-05-21 | Codex | Added Phase 6 v3 hard contrast dataset page to the structured-output phase notes | `docs/output-structure-fix/phase-6-v3-hard-contrast-dataset.md`, `docs/index.md` | Updated |
| 2026-05-21 | Codex | Added script runbook to core docs | `docs/script.md`, `docs/index.md` | Updated |
| 2026-05-21 | Codex | Added Phase 6 v3.1 mini semantic eval page to the structured-output phase notes | `docs/output-structure-fix/phase-6-v3-1-mini-semantic-eval.md`, `reports/phase-6/phase-6-v3-1-mini-semantic-eval-infographic.html` | Updated |
| 2026-05-21 | Codex | Added Phase 6 v3.2 hard-contrast probe page to the structured-output phase notes | `docs/output-structure-fix/phase-6-v3-2-hard-contrast-probe.md`, `reports/phase-6/phase-6-v3-2-hard-contrast-memorization-probe-infographic.html` | Updated |
| 2026-05-21 | Codex | Added Phase 6 v3.3 targeted canary preparation page to the structured-output phase notes | `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md`, `scripts/create_v3_3_training_split.py` | Updated |
| 2026-05-21 | Codex | Added LFM2-350M model-card note to the core docs index | `docs/lfm2-350m-model-card-notes.md`, `docs/index.md` | Updated |
| 2026-05-21 | Codex | Added OpenAI adapter runtime config page to the core docs index | `docs/openai-adapter-runtime-config.md`, `config-adapter.example.yml` | Updated |
| 2026-05-21 | Codex | Updated v3.3 index entry after temp 0.3 hard-contrast runtime probe | `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md`, `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-3-temp-03-hard-contrast-memorization-probe.json` | Updated |
| 2026-05-21 | Codex | Added v3.3 temp 0.3 infographic link to index context | `reports/phase-6/phase-6-v3-3-temp-03-hard-contrast-memorization-probe-infographic.html`, `docs/output-structure-fix/phase-6-v3-3-targeted-canary.md` | Updated |
| 2026-05-21 | Codex | Added v3.4 boundary repair plan to the structured-output phase notes | `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md`, `docs/index.md` | Planned |
| 2026-05-22 | Codex | Updated v3.4 index entry after boundary repair split/config preparation | `docs/output-structure-fix/phase-6-v3-4-boundary-repair-plan.md`, `data/splits/train-v3-4-boundary-repair.jsonl`, `ml/unsloth/config.v3-4.yaml` | Prepared |
| 2026-05-22 | Codex | Updated v3.4 index entry after temp 0.3 hard-contrast runtime probe and HTML infographic | `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-4-temp-03-hard-contrast-memorization-probe.json`, `reports/phase-6/phase-6-v3-4-temp-03-hard-contrast-memorization-probe-infographic.html` | Improved but held |
| 2026-05-22 | Codex | Updated v3.4 index entry after temp 0 hard-contrast probe and HTML infographic | `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-4-temp-0-hard-contrast-memorization-probe.json`, `reports/phase-6/phase-6-v3-4-temp-0-hard-contrast-memorization-probe-infographic.html` | Canonical check held |
| 2026-05-22 | Codex | Added v3.5 boundary repair page to the structured-output phase notes | `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md`, `reports/phase-6/phase-6-v3-5-boundary-failure-slice.json`, `data/splits/train-v3-5-boundary-repair.jsonl`, `ml/unsloth/config.v3-5.yaml`, `tests/test_v3_5_boundary_repair_workflow.py` | Dataset/config prepared |
| 2026-05-22 | Codex | Updated v3.5 index entry after hard-contrast temp 0 and temp 0.3 probes | `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-5-temp-0-hard-contrast-memorization-probe.json`, `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-5-temp-03-hard-contrast-memorization-probe.json`, `reports/phase-6/phase-6-v3-5-temp-0-hard-contrast-memorization-probe-infographic.html` | Improved but held |
| 2026-05-22 | Codex | Updated v3.5 index entry after 2048-token hard-contrast probes | `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-5-temp-0-2048-hard-contrast-memorization-probe.json`, `reports/phase-6/openai-compatible-vllm-structured-outputs-v3-5-temp-03-2048-hard-contrast-memorization-probe.json`, `reports/phase-6/phase-6-v3-5-temp-03-2048-hard-contrast-memorization-probe-infographic.html` | Runtime improved but held |
| 2026-05-22 | User/Codex | Marked Phase 6 and v3.5 closed in the docs index | `docs/Day6.md`, `docs/output-structure-fix/phase-6-v3-or-runtime-decision.md`, `docs/output-structure-fix/phase-6-v3-5-boundary-repair-plan.md` | Closed with limitations |
| 2026-05-22 | Codex | Updated Phase 7 index entry after adding copyable CLI runbook | `docs/output-structure-fix/phase-7-fixed-split-comparison.md`, `docs/index.md` | Runbook prepared |
| 2026-05-22 | Codex | Added Day 7 demo script to the docs index | `docs/demo-script.md`, `docs/Day7.md`, `README.md` | Ready |
| 2026-05-22 | Codex | Updated index after Phase 7 fixed split evaluation | `docs/output-structure-fix/phase-7-fixed-split-comparison.md`, `reports/phase-7/comparison.md`, `reports/phase-7/phase-7-fixed-split-summary.html` | Decision `hold` |
| 2026-05-22 | Codex | Added Phase 8 v4 SQLi-first repair page to the docs index | `docs/output-structure-fix/phase-8-v4-sqli-boundary-repair-plan.md`, `data/splits/train-v4-sqli-boundary-repair.jsonl`, `ml/unsloth/config.v4.yaml` | Prepared |
| 2026-05-22 | User/Codex | Updated Phase 8 index entry after v4 training and hard-contrast probes | `reports/phase-8/phase-8-v4-sqli-boundary-training-result.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-temp-0-2048-hard-contrast-memorization-probe.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-temp-03-2048-hard-contrast-memorization-probe.json` | Held |
| 2026-05-22 | Codex | Added Phase 8 v4.1 SQLi-boundary repair page to the docs index | `docs/output-structure-fix/phase-8-v4-1-sqli-boundary-repair-plan.md`, `data/splits/train-v4-1-sqli-boundary-repair.jsonl`, `ml/unsloth/config.v4-1.yaml` | Prepared |
| 2026-05-22 | User/Codex | Updated Phase 8 v4.1 index entry after training and hard-contrast probes | `reports/phase-8/phase-8-v4-1-sqli-boundary-training-result.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-1-temp-0-2048-hard-contrast-memorization-probe.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-1-temp-03-2048-hard-contrast-memorization-probe.json` | Held |
| 2026-05-22 | Codex | Added Phase 8 v4.2 SQLi-priority prompt diagnostic page to the docs index | `docs/output-structure-fix/phase-8-v4-2-sqli-priority-diagnostic-plan.md`, `reports/phase-8/phase-8-v4-2-sqli-priority-diagnostic-slice.json`, `scripts/model_adapters/prompt_contract.py` | Prepared |
| 2026-05-22 | Codex | Updated Phase 8 v4.2 index entry after hard-contrast prompt probes | `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-2-temp-0-2048-sqli-priority-prompt-probe.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-2-temp-03-2048-sqli-priority-prompt-probe.json` | Held |
| 2026-05-22 | Codex | Added Phase 8 v4.3 capacity/architecture diagnostic plan to the docs index | `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md`, `tests/test_v4_3_capacity_diagnostic_plan.py` | Planned |
| 2026-05-23 | Codex | Added the `unsloth/Qwen3.5-0.8B` downloaded model card and linked it to Phase 8 v4.3 | `docs/model-candidates/unsloth-qwen3.5-0.8b/model-card.md`, `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md`, `docs/References.md` | Candidate intake |
| 2026-05-23 | User/Codex | Updated the index after all 3 Phase 8 v4.3 Qwen3.5 probes completed | `docs/output-structure-fix/phase-8-v4-3-capacity-architecture-diagnostic-plan.md`, `reports/phase-8/openai-compatible-vllm-structured-outputs-v4-3-qwen3-5-0-8b-*.json` | Probed; held |
| 2026-05-23 | Codex | Added Phase 8 v4.4 boundary audit page to the docs index | `docs/output-structure-fix/phase-8-v4-4-hard-contrast-boundary-audit-plan.md`, `reports/phase-8/phase-8-v4-4-hard-contrast-boundary-audit.json` | Audit complete; held |
| 2026-05-23 | User/Codex | Clarified index wording so v4.3/v4.4 Qwen3.5 reports are described as base-model probes, not trained-model results | `docs/index.md` | Clarified |
| 2026-05-23 | Codex | Linked the Qwen3.5 exploratory LoRA smoke pilot from the docs index | `docs/fine-tuning-notes.md`, `ml/unsloth/qwen3-5-0-8b-security-triage-pilot.yaml` | Pilot wiring prepared |
| 2026-05-23 | Codex | Added 6GB small-model fine-tuning candidate page to core docs | `docs/small-model-fine-tuning-candidates-6gb.md`, `docs/index.md`, `docs/References.md` | Updated |
| 2026-05-23 | Codex | Refreshed 6GB small-model candidate docs with newer Qwen3.5, Granite 4.1, LFM2.5, and SmolLM3 options | `docs/small-model-fine-tuning-candidates-6gb.md`, `docs/index.md`, `docs/References.md` | Updated |
| 2026-05-23 | User/Codex | Added Phase 8 v4.5 trained-Qwen LoRA hard-contrast probe to the docs index | `docs/output-structure-fix/phase-8-v4-5-qwen35-lora-hard-contrast-probe.md`, `reports/phase-8/phase-8-v4-5-qwen35-lora-training-result.json`, `reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B—v1temp-0-hard-contrast-memorization-probe.json` | Trained/probed; calibration held |
| 2026-05-23 | Codex | Added Phase 8 v4.6 Qwen normal/severity calibration workflow to the docs index | `docs/output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan.md`, `scripts/create_v4_6_qwen35_normal_calibration_dataset.py`, `ml/unsloth/qwen3-5-0-8b-security-triage-v4-6-normal-severity-calibration.yaml` | Prepared; training pending |
| 2026-05-23 | Codex | Added Phase 8 LFM2 vs Qwen HTML comparison report to the index | `reports/phase-8/phase-8-lfm2-350m-vs-qwen35-0-8b-comparison.html`, `docs/index.md` | Comparison report ready |
| 2026-05-23 | User/Codex | Updated the index after v4.6 Qwen training, non-fixed probes, and HTML report | `docs/output-structure-fix/phase-8-v4-6-qwen35-normal-severity-calibration-plan.md`, `reports/phase-8/phase-8-v4-6-qwen35-normal-severity-calibration-report.html` | Improved but held |
| 2026-05-23 | Codex | Added Phase 8 v4.7 Qwen auth/SQLi/severity calibration workflow to the docs index | `docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md`, `data/splits/train-v4-7-qwen35-auth-sqli-severity-calibration.jsonl`, `ml/unsloth/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration.yaml` | Prepared; training pending |
| 2026-05-23 | User/Codex | Updated the index after v4.7 Qwen training, non-fixed probes, gate read, and HTML report | `docs/output-structure-fix/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-plan.md`, `reports/phase-8/phase-8-v4-7-qwen35-auth-sqli-severity-calibration-report.html` | Hard-contrast improved but calibration held |
| 2026-05-23 | Codex | Added Phase 8 v4.8 diagnostic audit to the docs index | `docs/output-structure-fix/phase-8-v4-8-qwen35-auth-sqli-diagnostic-plan.md`, `reports/phase-8/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit.json`, `reports/phase-8/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html` | Diagnostic audit complete |
| 2026-05-23 | User/Codex | Updated the index after v4.6-on-v4.7 comparator was added to v4.8 audit | `reports/phase-8/openai-compatible-vllm-structured-outputs-qwen3.5-8B-v4-6-on-v4-7-auth-sqli-severity-calibration-probe.json`, `docs/output-structure-fix/phase-8-v4-8-qwen35-auth-sqli-diagnostic-plan.md`, `reports/phase-8/phase-8-v4-8-qwen35-auth-sqli-diagnostic-audit-report.html` | Comparator complete |
| 2026-05-30 | Codex | Updated docs index after reorganizing `reports/` into public-facing workflow folders | `reports/README.md`, `docs/index.md`, `docs/project-structure-rationale.md` | Updated |

## Decision Log

Append-only log สำหรับบันทึกว่าตัดสินใจอะไร เพราะอะไร และกระทบส่วนไหน

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| 2026-05-16 | เพิ่ม docs index | docs มีหลายหน้าแล้วและต้องค้นหา rationale ได้ง่าย | เอกสารใหม่ถูกผูกเข้ากับ mini-wiki แทนที่จะเป็น markdown โดด ๆ |
| 2026-05-16 | ย้าย References เข้า `docs/` | ให้ reference อยู่ใน mini-wiki เดียวกับ day plan, rationale และ dataset strategy | path อ้างอิงหลักเปลี่ยนจาก `References.md` เป็น `docs/References.md` |
| 2026-05-18 | เพิ่มหมวด `docs/model-output/` | ต้องแยกพฤติกรรม model แต่ละ version ออกจาก day plan เพื่อเทียบ run ได้ตรงไปตรงมา | model version ถัดไปควรมีหน้า output note ตาม template เดียวกัน |
| 2026-05-19 | เพิ่ม data format guide สำหรับ LLM training | ต้องมีหน้าอธิบายความต่างระหว่าง source dataset format กับ training render format ก่อนแก้ output model รอบถัดไป | Day 6 output-fix discussion มี reference กลางสำหรับเลือก instruction tuning และ chat-message rendering |
| 2026-05-19 | เพิ่มหน้าเฉพาะสำหรับ output-contract hardening | prompt, adapter, schema sanitizer, smoke split และ retrain decision เป็นงานชุดเดียวที่มี tradeoff ของตัวเอง | การแก้ runtime contract รอบถัดไปไม่ต้องไปไล่อ่าน Day4/Day6 กระจัดกระจาย |
| 2026-05-19 | เพิ่มหน้า v2 model-output แยกจาก v1 | v2 มีผล `responses_parse` และ failure mode คนละชั้นกับ v1 baseline แล้ว | การเทียบ run ถัดไปจะไม่ปน historical v1 failure กับ v2 output-contract investigation |
| 2026-05-20 | เพิ่มหน้า research note สำหรับ structured output reliability | smoke หลังแก้ SDK/adapter ยังไม่ดีขึ้น จึงต้องตัดสินใจจาก runtime constrained decoding, validation/retry และ research ล่าสุด | Day 6 next step ถูกดันไปทางพิสูจน์ server-side constrained decoding ก่อน retrain/fixed split |
| 2026-05-20 | เพิ่มหน้า fix plan แยกจาก research note | research note ตอบว่าควรไปทางไหน แต่ทีมยังต้องมี checklist และ gate สำหรับลงมือทำ | งานถัดไปมี phase, deliverable และ pass/fail condition ชัดเจน |
| 2026-05-20 | เพิ่ม section สำหรับ phase-detail notes | Phase 1 เป็นต้นไปต้องมีรายละเอียด command/evidence ต่อ phase โดยไม่ทำให้ core index อ่านยาก | docs index มีทางเข้าทั้ง master plan และ phase execution notes |
| 2026-05-20 | เพิ่ม runbook สำหรับ repeated-token loops | Phase 5/6 ต้องแยกว่า timeout หรือ token loop มาจาก decoding, stop token, structured outputs, runtime หรือ training format ก่อนตัดสินใจ retrain | งาน diagnosis ถัดไปมี checklist กลางและไม่ใช้ fixed test split เพื่อจูน |
| 2026-05-20 | เพิ่ม Phase 6.1 เป็น evidence-constraint fix path | Phase 6 case 1 แยกได้ว่า JSON-constrained modes loop ใน `evidence` แม้ broad label ถูกทาง | งานถัดไปควร tighten schema/sanitizer ก่อนตัดสินใจ retrain v3 |
| 2026-05-21 | เพิ่มหน้า label imbalance แยกจาก runtime/output loop | Phase 6 มีทั้ง evidence loop และ prediction skew จึงต้องมีหน้าแยกว่า source data imbalance ต่างจาก model prediction collapse อย่างไร | การทำ v3 data/report metrics จะไม่รีบ downsample label ที่ source split ยัง balanced อยู่ |
| 2026-05-21 | เพิ่ม `docs/script.md` เป็น runbook คำสั่งกลาง | คำสั่งรันโปรเจกต์กระจายอยู่ใน README, day plans และ phase notes จึงต้องมี entrypoint เดียวสำหรับ setup, evaluation, endpoint probe และ optional GPU workflow | ผู้ใช้เริ่มจาก `[[script]]` ได้โดยไม่ต้องไล่เปิดหลายหน้า |
| 2026-05-23 | Hold base Qwen3.5-0.8B after v4.4 boundary audit | v4.4 found persistent suspicious-to-normal collapse across both base-model hard-contrast probes, not an output-contract failure | Keep fixed split closed; the next experiment should be another capacity candidate or a scoped boundary repair, not a default Qwen train run |
| 2026-05-23 | Treat `Qwen/Qwen3-1.7B` as the first <=4B candidate for a 6GB GPU | 4B models remain interesting but are memory-risky for QLoRA training on 6GB; 1.7B is a better next capacity step after LFM2-350M | Future candidate configs should start below 2B before spending time on 3B/4B stretch targets |
| 2026-05-23 | Refresh first-choice 6GB candidates to `LiquidAI/LFM2.5-1.2B-Instruct` or `Qwen/Qwen3.5-2B` | Newer model check found 1.2B-2B options that are fresher than the old shortlist while staying safer than 3B/4B on 6GB | Try LFM2.5/Qwen3.5-2B before Granite 4.1 3B, SmolLM3 3B, or Qwen3.5 4B stretch runs |
| 2026-05-23 | Hold v4.5 before fixed split | Trained Qwen LoRA reaches hard-contrast label accuracy `0.88` with JSON/schema `1.0`, but normal accuracy is only `4/10` and severity accuracy is `0.72` | Calibrate normal false positives and severity before mini semantic or fixed split comparison |
| 2026-05-23 | Prepare v4.6 as normal/severity calibration | v4.5 failure shape moved from suspicious recall to normal precision and severity calibration | Train and probe v4.6 on non-fixed calibration artifacts before any fixed split comparison |
| 2026-05-23 | Hold v4.6 before fixed split | v4.6 improves hard-contrast overall metrics but still misses normal, SQLi, calibration-normal, and brute-force severity gates | Keep `data/splits/test.jsonl` closed; use v4.6 as evidence for a narrower v4.7 calibration pass |
| 2026-05-23 | Prepare v4.7 as narrow auth/SQLi/severity calibration | v4.6 misses are concentrated in benign auth false positives, SQLi auth-context confusion, medium severity boundaries, and one traversal evidence miss | Add v4.7 train/probe artifacts and config while keeping `data/splits/test.jsonl` closed |
| 2026-05-23 | Hold v4.7 before fixed split | v4.7 reaches hard-contrast label/severity `0.92`, but the new calibration probe fails on the exact normal-auth, SQLi-auth, and medium-severity cases it targeted | Keep `data/splits/test.jsonl` closed and use the v4.7 result as failure-analysis input, not a release candidate |
| 2026-05-23 | Start v4.8 as diagnostic-first | v4.7 underperforms heuristic on the same calibration probe and v4.6 alias is not currently served for direct comparison | Keep fixed split and v4.8 training closed until comparator audit and boundary contract are reviewed |
| 2026-05-23 | Keep v4.8 diagnostic-first after v4.6 comparator completed | v4.6 label accuracy `0.433333` is above v4.7 `0.366667` but below heuristic `0.666667` on the same probe | Do not revert to v4.6 or open fixed split; prepare narrow v4.8 repair only after reviewing bucket-level failures |
| 2026-05-30 | Keep report artifacts grouped by workflow ownership | Flat `reports/` root had too many mixed JSON/MD/HTML artifacts for a public repo | New report paths live under `baseline/`, `structured-output/`, `phase-6/`, `phase-7/`, `phase-8/`, and `checksums/` |

## Related pages

- [[poc-plan]]
- [[project-structure-rationale]]
- [[log]]

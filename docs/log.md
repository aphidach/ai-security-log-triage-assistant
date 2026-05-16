# Documentation Log

**Summary**

append-only log สำหรับบันทึกการเปลี่ยนแปลงเอกสารใน `docs/`

**Sources**

- `AGENTS.md` สำหรับกติกา repo และการอัปเดต docs เมื่อ schema/workflow เปลี่ยน (source: AGENTS.md)
- `.codex/skills/llm-docs/SKILL.md` สำหรับกติกา docs index, docs log, source citation และ append-only logging (source: .codex/skills/llm-docs/SKILL.md)

**Last updated**

2026-05-16

## Log

| Date | Actor | Change | Files | Notes |
| --- | --- | --- | --- | --- |
| 2026-05-16 | Codex | Created project structure rationale and initialized docs index/log | `docs/project-structure-rationale.md`, `docs/index.md`, `docs/log.md` | Documentation-only change; no implementation files or repo structure folders were created |
| 2026-05-16 | Codex | Updated fine-tuning model direction to start with LFM2-350M due to limited resources | `docs/poc-plan.md`, `docs/Day5.md`, `References.md` | Qwen 1.5B/3B/4B kept as later comparison candidates, not the first default |
| 2026-05-16 | Codex | Aligned agent and README guidance with LFM2-350M-first fine-tuning direction | `AGENTS.md`, `README.md` | Project-level instructions now match the POC plan and Day 5 docs |
| 2026-05-16 | Codex | Created curated SLM fine-tuning model choice doc from Distil Labs clipping | `docs/slm-fine-tuning-model-choice.md`, `docs/index.md` | Captures LFM2-350M-first decision, Qwen comparison path, and benchmark limitations |
| 2026-05-16 | Codex | Removed later-comparison model-size references from the main agent and README docs | `AGENTS.md`, `README.md` | Main docs now present only the LFM2-350M-first direction |
| 2026-05-16 | Codex | Added industrial SLM RAG fine-tuning paper to the wiki | `docs/slm-rag-fine-tuning-hallucination.md`, `docs/index.md`, `References.md` | Captures cost-aware evaluation, hallucination taxonomy, and scope limits for security log triage |
| 2026-05-16 | Codex | Added TinyLoRA paper summary to the wiki | `docs/tinylora-reasoning-13-parameters.md`, `docs/index.md`, `References.md` | Captures TinyLoRA as future RL-based ultra-low-parameter tuning reference, not the first POC path |
| 2026-05-16 | Codex | Added rationale for first-pass evaluation metrics | `docs/evaluation-metrics-rationale.md`, `docs/index.md` | Explains why correctness, JSON/schema validity, evidence match, latency, and invalid output counts are all needed |
| 2026-05-16 | Codex | Added first-pass dataset size and split plan | `docs/poc-plan.md`, `docs/Day2.md` | Sets round-one dataset to 500 records, label-balanced at 100 each, split `350/75/75` |
| 2026-05-16 | Codex | Created initial tracked repo directory structure for Day 1 | `data/`, `scripts/`, `ml/`, `reports/`, `docs/Day1.md` | Adds placeholders only; schema, labels, and scripts remain next Day 1 tasks |

## Related pages

- [[index]]
- [[project-structure-rationale]]
- [[Day1]]

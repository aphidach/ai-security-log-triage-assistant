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
| 2026-05-16 | Codex | Marked Day 1 Next.js/TypeScript scaffold as verified | `docs/Day1.md`, `frontend/` | Scaffold exists with app router, TypeScript config, ESLint config, and package scripts |
| 2026-05-16 | Codex | Added Day 1 triage output schema | `data/schemas/triage-output.schema.json`, `docs/Day1.md` | Defines required triage output fields, five-label enum, severity enum, and no extra properties |
| 2026-05-16 | Codex | Added triage output schema explanation page | `docs/triage-output-schema.md`, `docs/index.md`, `docs/Day1.md` | Documents the schema as the shared contract for dataset, evaluator, adapters, UI, and fine-tuning output |
| 2026-05-16 | Codex | Added dataset source strategy note to the wiki | `docs/dataset-source-strategy.md`, `docs/index.md`, `References.md` | Stores Loghub, BOTS, OTRF/Mordor, SigmaHQ, Splunk Attack Data, and Kaggle synthetic candidates as future dataset backlog |
| 2026-05-16 | Codex | Moved References into the docs wiki directory | `docs/References.md`, `README.md`, `docs/index.md` | Updated active source citations to use `docs/References.md`; old log rows remain append-only history |
| 2026-05-16 | Codex | Added first-pass label taxonomy definitions | `docs/label-taxonomy.md`, `docs/triage-output-schema.md`, `docs/index.md`, `docs/Day1.md` | Defines the five initial labels, evidence expectations, severity defaults, and false-positive caveats |
| 2026-05-16 | Codex | Added frontend label taxonomy constants | `frontend/lib/labels.ts`, `docs/Day1.md` | Provides the canonical TypeScript label list, metadata, and `isTriageLabel` guard for UI, adapters, and evaluator code |
| 2026-05-16 | Codex | Added frontend triage output runtime schema | `frontend/lib/triage-schema.ts`, `docs/Day1.md` | Mirrors the JSON Schema in TypeScript with severity constants, output type, field-level parse errors, and a type guard |
| 2026-05-16 | Codex | Ran frontend Day 1 verification commands | `docs/Day1.md` | `npx tsc --noEmit` and `npm run lint` passed in `frontend/` |
| 2026-05-16 | Codex | Added README quickstart for Day 1 frontend workflow | `README.md`, `docs/Day1.md` | Documents install, typecheck, lint, dev server, and current shared triage contract files; verification commands passed |
| 2026-05-16 | Codex | Added dataset input/output format page | `docs/dataset-input-output-format.md`, `docs/index.md`, `docs/Day2.md` | Documents JSONL record shape, input/output rules, 500-record split, examples, validation checks, and generator guidelines |

## Related pages

- [[index]]
- [[project-structure-rationale]]
- [[Day1]]

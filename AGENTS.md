# AGENTS.md

Guidance for coding agents working in this repository.

## Project Mission

Build a measurable proof of concept named **AI Security Log Triage Assistant**.

The POC should accept one or more security log lines and return a structured triage result:

- whether the event is normal or suspicious
- the most likely attack or activity pattern
- concrete evidence found in the log
- severity
- a short reason
- recommended next investigation action

This project is about **fine-tuning and evaluation for security log triage**, not general document RAG.

## POC Scope

Start small. The first version should cover only these labels:

- `normal`
- `failed_login_bruteforce`
- `sql_injection_attempt`
- `directory_traversal_attempt`
- `port_scan_or_recon`

Do not broaden the taxonomy until the dataset, evaluator, and baseline comparison are working.

## Expected Output Schema

All model and baseline outputs should conform to this shape:

```json
{
  "label": "sql_injection_attempt",
  "severity": "high",
  "is_suspicious": true,
  "evidence": ["' OR '1'='1"],
  "reason": "The request contains a common SQL injection pattern.",
  "recommended_action": "Review web application logs and block or rate-limit the source IP."
}
```

Keep the schema stable. If the schema changes, update the dataset generator, evaluator, API, UI, and documentation together.

## Repository Shape

The intended structure is:

```text
data/
  raw/
  generated/
  splits/
  schemas/
docs/
  poc-plan.md
  data-card.md
  evaluation-method.md
  fine-tuning-notes.md
ml/
  unsloth/
  notebooks/
reports/
scripts/
frontend/
  app/
  components/
  lib/
```

Prefer keeping shared triage logic under `frontend/lib/` and model training assets under `ml/`.

## Implementation Priorities

Build in this order:

1. Output schema and label taxonomy.
2. Synthetic JSONL dataset generator.
3. Train, validation, and test splits.
4. Rule-based heuristic baseline that runs locally without model keys.
5. Evaluation runner with repeatable metrics.
6. Model adapters for OpenAI-compatible APIs, local Ollama or LM Studio, and fine-tuned models.
7. Next.js demo UI.
8. Unsloth LoRA or QLoRA fine-tuning script.
9. Evaluation report comparing baseline and fine-tuned model.

The project should always have a path that runs without GPU access. GPU-dependent fine-tuning should be optional and documented separately.

## Evaluation Rules

Evaluation matters more than presentation polish.

Track at least:

- label accuracy
- JSON parse success rate
- severity accuracy
- evidence match or partial match
- average latency
- invalid or missing required fields

Use a fixed test split for comparisons. Do not evaluate on training examples.

## Dataset Rules

Use JSONL for training and evaluation examples.

Each record should include:

```json
{
  "id": "sample-000001",
  "instruction": "Analyze this security log and classify whether it is suspicious.",
  "input": "192.168.1.20 - - [10/May/2026] \"GET /login?user=admin' OR '1'='1 HTTP/1.1\" 200",
  "output": {
    "label": "sql_injection_attempt",
    "severity": "high",
    "is_suspicious": true,
    "evidence": ["admin' OR '1'='1"],
    "reason": "The request contains a common SQL injection pattern.",
    "recommended_action": "Review web application logs and block or rate-limit the source IP."
  }
}
```

Synthetic data is acceptable for the first POC, but document its limits clearly. Public log datasets may be referenced later, especially Loghub, Splunk BOTS, OTRF Security Datasets, SigmaHQ rules, and OWASP attack taxonomy.

## Fine-Tuning Guidance

The first fine-tuning path should target **LFM2-350M** because the current POC is resource constrained and should prove the end-to-end workflow before spending compute on larger models.

- Use LFM2-350M as the first base model candidate.
- Treat Qwen 1.5B/3B/4B class models as later comparison candidates, not the first default.
- Keep Phi small models and small Llama-family instruct models as optional future references only.

Use LoRA or QLoRA first. Avoid full fine-tuning unless there is a clear reason and enough compute.

Keep training scripts separate from the frontend. The frontend should consume adapters or exported model endpoints, not import training code.

## UI Guidance

The demo UI should be a working triage tool, not a marketing landing page.

Core screens:

- paste log and analyze
- structured result view
- evidence highlighting
- baseline vs fine-tuned comparison
- small sample log picker

Do not add broad dashboard features until the triage and evaluation flow works.

## Security And Privacy

Do not commit real production logs, secrets, credentials, tokens, private IP inventories, or customer data.

If using real logs later:

- sanitize IPs, hostnames, users, cookies, authorization headers, and session IDs
- keep raw private logs out of git
- document the anonymization process

## References To Study

Useful reference projects and sources:

- Unsloth: efficient LoRA and QLoRA fine-tuning
- Axolotl: YAML-driven fine-tuning workflow
- Hugging Face TRL: SFTTrainer and post-training patterns
- Distil Labs SLM fine-tuning benchmark: rationale for starting with LFM2-350M under limited resources
- EleutherAI lm-evaluation-harness: evaluation architecture
- Loghub: log analytics datasets
- Splunk BOTS: SOC training datasets
- OTRF Security Datasets: adversary-emulation log datasets
- SigmaHQ: detection rule structure and metadata
- OWASP Attacks: attack taxonomy

Use these as design references, not as code to copy blindly.

## Agent Working Style

- Read existing files before editing.
- Prefer small, focused changes.
- Keep generated data deterministic where possible.
- Update docs when changing workflow or schema.
- Run available checks before finishing.
- Never hide evaluation limitations.
- Never overclaim that the model detects compromise. Say it triages suspicious patterns and recommends investigation.

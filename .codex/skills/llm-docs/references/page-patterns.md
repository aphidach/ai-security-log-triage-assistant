# LLM Docs Page Patterns

Use these templates only when creating or restructuring this project's documentation.

## Curated Page Template

```markdown
# Title

**Summary**

One short paragraph explaining what this page is for and how it fits the project.

**Sources**

- `AGENTS.md` for project mission and guardrails (source: AGENTS.md)
- `docs/poc-plan.md` for project plan and milestone context (source: docs/poc-plan.md)

**Last updated**

YYYY-MM-DD

## Body Section

Write the useful content here.

## Work Log

Append-only log for what changed or what was done.

| Date | Actor | Work | Evidence | Status |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | Codex | Created page | `docs/example.md` | Planned |

## Decision Log

Append-only log for decisions, tradeoffs, and rationale.

| Date | Decision | Rationale | Impact |
| --- | --- | --- | --- |
| YYYY-MM-DD | Decision text | Why this choice was made | What changes downstream |

## Related pages

- [[poc-plan]]
- [[References]]
```

## docs/index.md Template

```markdown
# Documentation Index

**Summary**

Entry point for project documentation.

**Sources**

- `AGENTS.md` for repository mission and working rules (source: AGENTS.md)
- `docs/poc-plan.md` for project milestones (source: docs/poc-plan.md)

**Last updated**

YYYY-MM-DD

## Core Pages

- [[poc-plan]] - project plan and timeline
- [[References]] - external references and design rationale

## Daily Plan Pages

- [[Day1]] - project foundation
- [[Day2]] - dataset and data-card
- [[Day3]] - heuristic baseline and evaluation
- [[Day4]] - model adapters and prompt contract
- [[Day5]] - fine-tuning path
- [[Day6]] - fine-tuned evaluation and comparison
- [[Day7]] - demo and handoff

## Related pages

- [[poc-plan]]
- [[References]]
```

## docs/log.md Template

```markdown
# Documentation Log

**Summary**

Append-only log of documentation changes.

**Sources**

- `AGENTS.md` for documentation and working rules (source: AGENTS.md)

**Last updated**

YYYY-MM-DD

## Log

| Date | Actor | Pages | Change | Reason |
| --- | --- | --- | --- | --- |
| YYYY-MM-DD | Codex | `docs/example.md` | Created page | New documentation area |

## Related pages

- [[poc-plan]]
- [[References]]
```

## Log Row Guidance

- `Date`: use `YYYY-MM-DD`.
- `Actor`: use `Codex` unless the user provides another actor.
- `Work`: describe the actual change, not the intention.
- `Evidence`: cite files or commands that prove the work happened.
- `Status`: use `Planned`, `In progress`, `Done`, `Blocked`, or `Deferred`.
- `Decision`: write the choice in plain language.
- `Rationale`: explain why the choice was made.
- `Impact`: note which files or workflows are affected.

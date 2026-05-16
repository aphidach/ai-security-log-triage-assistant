---
name: llm-docs
description: Maintain this project's documentation as a small LLM-Wiki-style knowledge base. Use when Codex needs to create, update, audit, or reorganize docs in ai-security-log-triage-assistant; manage docs/Day1.md through docs/Day7.md, docs/poc-plan.md, References.md, README-like docs, docs/index.md, docs/log.md, Work Log, Decision Log, Sources, Last updated, and Related pages; preserve append-only documentation logs and cite source files.
---

# LLM Docs

Use this skill to manage this repository's documentation as a maintained mini-wiki, not as loose markdown files.

Project root: `/Volumes/Hiksemi/Code/ai-security-log-triage-assistant`.

## Core Model

- Treat `docs/` as curated project pages.
- Treat `data/raw/` and other raw source folders as immutable unless the user explicitly asks otherwise.
- Keep `docs/index.md` as the table of contents when it exists; create it when the docs set grows beyond a few pages.
- Keep `docs/log.md` as the global append-only documentation change log when it exists; create it before larger doc maintenance work.
- Preserve existing user-requested file names such as `docs/Day1.md` through `docs/Day7.md`; use lowercase hyphen-case for new free-form docs unless the user names a file.

## First Reads

Before editing docs, read only the relevant context:

1. `AGENTS.md` for repo mission and working rules.
2. `docs/poc-plan.md` for project plan and milestones.
3. `References.md` for external source rationale.
4. Target doc pages being edited.
5. `docs/index.md` and `docs/log.md` if present.

If QMD is available and the docs are indexed, use QMD search for discovery. Otherwise use `rg --files`, `rg`, and direct file reads.

## Page Shape

For curated docs, use this shape unless the existing page has a stronger local convention:

- `# Title`
- `**Summary**`
- `**Sources**`
- `**Last updated**`
- body content
- `## Work Log` for execution/status pages
- `## Decision Log` for planning or architecture pages
- `## Related pages`

For exact table templates, read `references/page-patterns.md` only when creating or restructuring docs.

## Source And Link Rules

- Cite factual project claims with `(source: filename)` or `(source: path/to/file)`.
- Mark uncertain claims with `(needs verification)`.
- Add wiki-style links between related pages, for example `[[Day2]]`, `[[poc-plan]]`, or `[[References]]`.
- Keep links useful for navigation; do not link every repeated term.
- Preserve the language of the existing page. For this project, Thai prose is acceptable and often preferred for planning docs.

## Logging Rules

For every meaningful documentation change:

- Append a row to the target page `## Work Log` when that page has one.
- Append a row to `## Decision Log` when the change records a decision, tradeoff, scope change, or rationale.
- Append one global entry to `docs/log.md` when it exists, or create it for documentation-wide changes.
- Never rewrite old log rows except to fix a typo in the same turn.

Use absolute dates in `YYYY-MM-DD` format.

## Common Workflows

### Create A New Doc Page

1. Read `AGENTS.md`, `docs/poc-plan.md`, `References.md`, and nearby related pages.
2. Choose the file name: preserve the user's requested name; otherwise use lowercase hyphen-case.
3. Create the page using the standard page shape.
4. Add Sources, Last updated, Related pages, and initial Work/Decision Log rows when relevant.
5. Update `docs/index.md` if present or if this is a major new page.
6. Append `docs/log.md` if present or if the user asked for maintained docs.

### Update A Day Plan

1. Read the target `docs/DayN.md` page plus adjacent days.
2. Update checklist/status content without erasing old logs.
3. Add Work Log rows for completed work.
4. Add Decision Log rows for decisions and scope changes.
5. Keep Related pages pointing to adjacent days and core docs.

### Audit Docs

Check for:

- missing Sources, Last updated, or Related pages
- stale checklist items
- broken wiki-style links
- orphan pages not listed in `docs/index.md`
- factual claims without source markers
- decisions hidden in prose instead of Decision Log
- old logs being rewritten instead of appended

Report findings first, then patch if the user asked you to fix.

## Project-Specific Guardrails

- Do not turn this project into general document RAG; keep docs centered on measurable security log triage, dataset, evaluation, fine-tuning, and demo workflow.
- Do not overclaim that the model proves a system was hacked. Use triage language: suspicious, likely pattern, evidence, recommended investigation.
- Do not commit real production logs, secrets, tokens, customer data, or unsanitized private telemetry.
- When docs mention external projects, prefer sources already collected in `References.md`.

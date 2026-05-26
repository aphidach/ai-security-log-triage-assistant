# AI Security Log Triage Assistant Frontend

Next.js demo UI for the security log triage POC.

## Run

```bash
npm install
cp .env.example .env.local
npm run dev -- --port 3000
```

Open `http://localhost:3000`.

The heuristic analyzer runs locally through the Next.js API route. Base-model
and fine-tuned analyzers use server-side OpenAI-compatible settings from
`.env.local`, so API keys are not exposed to the browser.

Required live endpoint variables:

- `OPENAI_COMPATIBLE_BASE_URL`, `OPENAI_COMPATIBLE_API_KEY`, `OPENAI_COMPATIBLE_MODEL`
- `OPENAI_FINETUNE_BASE_URL`, `OPENAI_FINETUNE_API_KEY`, `OPENAI_FINETUNE_MODEL`

## Checks

```bash
npx tsc --noEmit
npm run lint
npm run build
```

## Current Demo Surface

- paste or edit one log line
- choose one of five sample logs
- run the local heuristic analyzer through `/api/triage` without model keys
- call base-model and fine-tuned OpenAI-compatible endpoints when `.env.local` is configured
- view structured triage output and raw JSON
- highlight evidence substrings in the input log
- show unconfigured or endpoint-error state when live model settings are missing or unavailable
- show current comparison artifacts with Qwen3.5 v4.7 as the latest fine-tuned model
- show configured base and fine-tuned model names from `OPENAI_COMPATIBLE_MODEL` and `OPENAI_FINETUNE_MODEL` without exposing API keys or base URLs

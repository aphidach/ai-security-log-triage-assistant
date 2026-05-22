# AI Security Log Triage Assistant Frontend

Next.js demo UI for the security log triage POC.

## Run

```bash
npm install
npm run dev -- --port 3000
```

Open `http://localhost:3000`.

## Checks

```bash
npx tsc --noEmit
npm run lint
npm run build
```

## Current Demo Surface

- paste or edit one log line
- choose one of five sample logs
- run the local heuristic analyzer without model keys
- view structured triage output and raw JSON
- highlight evidence substrings in the input log
- show unconfigured state for base/fine-tuned analyzers until live endpoints are wired
- show current comparison artifacts without treating exploratory v3.5 probes as fixed-split results

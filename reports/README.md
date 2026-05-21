# Reports

This directory stores evaluation outputs for the AI Security Log Triage Assistant.

## Naming Convention

Use mode-specific report paths for output-contract experiments so repeated smoke runs do not overwrite each other.

Canonical smoke format:

```text
reports/{adapter}-{runtime}-{mode}-smoke.json
reports/{adapter}-{runtime}-{mode}-smoke.md
```

Canonical mini semantic eval format:

```text
reports/{adapter}-{runtime}-{mode}-mini-semantic-eval.json
reports/{adapter}-{runtime}-{mode}-mini-semantic-eval.md
```

Semantic error taxonomy infographic:

```text
reports/phase-{n}-semantic-error-taxonomy-infographic.html
```

Model-run mini semantic infographic:

```text
reports/phase-{n}-{model-version}-mini-semantic-eval-infographic.html
```

Canonical fixed split format:

```text
reports/finetuned-eval.json
reports/comparison.md
```

Phase 0 evidence files:

```text
reports/frozen-splits.sha256
reports/structured-output-run-artifacts.md
```

Runtime capability matrix:

```text
reports/structured-output-capability-matrix.md
```

## Tokens

| Token | Meaning | Examples |
| --- | --- | --- |
| `{adapter}` | Evaluator adapter name | `openai-compatible`, `openai-finetune`, `heuristic` |
| `{runtime}` | Serving backend or runtime profile | `current`, `vllm`, `sglang`, `lmstudio`, `ollama`, `tgi`, `unsloth-studio` |
| `{mode}` | Structured-output request mode | `responses-parse`, `json-schema`, `structured-outputs`, `guided-json`, `json-object`, `plain` |

Use lowercase kebab-case. Spell `output` correctly in notes and metadata, but omit it from the filename unless it is part of a model version label. Avoid names like `eval.json` for smoke experiments because they are easy to overwrite.

## Examples

```bash
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/openai-compatible-current-responses-parse-smoke.json \
  --comparison-out reports/openai-compatible-current-responses-parse-smoke.md
```

```bash
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/smoke-output-contract.jsonl \
  --out reports/openai-compatible-vllm-structured-outputs-smoke.json \
  --comparison-out reports/openai-compatible-vllm-structured-outputs-smoke.md
```

```bash
python3 scripts/evaluate.py \
  --adapter openai-compatible \
  --split data/splits/test.jsonl \
  --out reports/finetuned-eval.json \
  --comparison-out reports/comparison.md
```

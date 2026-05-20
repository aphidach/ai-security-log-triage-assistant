#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON_BIN_FALLBACK:-python3}"
fi

PHASE5_SPLIT="${PHASE5_SPLIT:-data/splits/mini-semantic-eval.jsonl}"
PHASE5_JSON_REPORT="${PHASE5_JSON_REPORT:-reports/openai-compatible-vllm-structured-outputs-mini-semantic-eval.json}"
PHASE5_MARKDOWN_REPORT="${PHASE5_MARKDOWN_REPORT:-reports/openai-compatible-vllm-structured-outputs-mini-semantic-eval.md}"

"$PYTHON_BIN" scripts/create_mini_semantic_eval_split.py \
  --source "${PHASE5_SOURCE_SPLIT:-data/splits/validation.jsonl}" \
  --out "$PHASE5_SPLIT" \
  --per-label "${PHASE5_PER_LABEL:-5}" \
  --exclude data/splits/test.jsonl \
  --exclude data/splits/smoke-output-contract.jsonl \
  --force

export OPENAI_COMPATIBLE_BASE_URL="${OPENAI_COMPATIBLE_BASE_URL:-http://192.168.8.141:8080/v1}"
export OPENAI_COMPATIBLE_API_KEY="${OPENAI_COMPATIBLE_API_KEY:-local}"
export OPENAI_COMPATIBLE_MODEL="${OPENAI_COMPATIBLE_MODEL:-lfm2-security-triage}"
export OPENAI_COMPATIBLE_RESPONSE_FORMAT="${OPENAI_COMPATIBLE_RESPONSE_FORMAT:-structured_outputs}"
export OPENAI_COMPATIBLE_SCHEMA_PATH="${OPENAI_COMPATIBLE_SCHEMA_PATH:-data/schemas/triage-output.schema.json}"

"$PYTHON_BIN" scripts/evaluate.py \
  --adapter openai-compatible \
  --split "$PHASE5_SPLIT" \
  --out "$PHASE5_JSON_REPORT" \
  --comparison-out "$PHASE5_MARKDOWN_REPORT"

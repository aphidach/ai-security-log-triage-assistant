#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

DEFAULT_MODEL_DIR="ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-7-auth-sqli-severity-calibration-merged-bf16-clean"
DEFAULT_OUT_DIR="ml/unsloth/outputs/qwen3-5-0-8b-security-triage-v4-7-gguf"

MODEL_DIR="${MODEL_DIR:-$DEFAULT_MODEL_DIR}"
LLAMA_CPP_DIR="${LLAMA_CPP_DIR:-$HOME/llama.cpp}"
GGUF_OUT_DIR="${GGUF_OUT_DIR:-$DEFAULT_OUT_DIR}"
GGUF_BASENAME="${GGUF_BASENAME:-qwen3-5-0-8b-security-triage-v4-7}"
GGUF_OUTTYPE="${GGUF_OUTTYPE:-f16}"
GGUF_QUANTIZATIONS="${GGUF_QUANTIZATIONS:-q4_k_m}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

LLAMA_CPP_DIR="${LLAMA_CPP_DIR/#\~/$HOME}"
CONVERT_SCRIPT="${CONVERT_SCRIPT:-$LLAMA_CPP_DIR/convert_hf_to_gguf.py}"
LLAMA_QUANTIZE_BIN="${LLAMA_QUANTIZE_BIN:-}"

usage() {
  cat <<'EOF'
Convert a clean Hugging Face/Transformers checkpoint to GGUF with llama.cpp.

Defaults are set for the current Qwen3.5 v4-7 clean BF16 merged checkpoint.

Environment variables:
  MODEL_DIR              Local clean HF checkpoint directory.
  LLAMA_CPP_DIR          llama.cpp checkout directory. Default: $HOME/llama.cpp
  CONVERT_SCRIPT         Override convert_hf_to_gguf.py path.
  LLAMA_QUANTIZE_BIN     Override llama-quantize binary path.
  GGUF_OUT_DIR           Output directory for GGUF files.
  GGUF_BASENAME          Output file basename.
  GGUF_OUTTYPE           Intermediate GGUF type: f16, bf16, f32, q8_0. Default: f16
  GGUF_QUANTIZATIONS     Comma-separated final quantizations. Default: q4_k_m
                          Use "none" to keep only the intermediate GGUF.
  PYTHON_BIN             Python executable. Default: python3

Example:
  LLAMA_CPP_DIR=$HOME/llama.cpp \
  GGUF_QUANTIZATIONS=q4_k_m,q8_0 \
  scripts/convert_hf_checkpoint_to_gguf.sh
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

absolute_path() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *) printf '%s/%s\n' "$ROOT" "$1" ;;
  esac
}

find_quantize_bin() {
  if [[ -n "$LLAMA_QUANTIZE_BIN" ]]; then
    printf '%s\n' "$LLAMA_QUANTIZE_BIN"
    return
  fi

  local candidate
  for candidate in \
    "$LLAMA_CPP_DIR/build/bin/llama-quantize" \
    "$LLAMA_CPP_DIR/llama-quantize" \
    "$LLAMA_CPP_DIR/build/bin/quantize" \
    "$LLAMA_CPP_DIR/quantize"; do
    if [[ -x "$candidate" ]]; then
      printf '%s\n' "$candidate"
      return
    fi
  done
}

MODEL_DIR="$(absolute_path "$MODEL_DIR")"
GGUF_OUT_DIR="$(absolute_path "$GGUF_OUT_DIR")"

if [[ ! -d "$MODEL_DIR" ]]; then
  cat >&2 <<EOF
Model directory not found: $MODEL_DIR

Set MODEL_DIR to a clean merged Hugging Face checkpoint directory.
EOF
  exit 1
fi

if [[ ! -f "$CONVERT_SCRIPT" ]]; then
  cat >&2 <<EOF
llama.cpp converter not found: $CONVERT_SCRIPT

Clone and build llama.cpp first, or set LLAMA_CPP_DIR/CONVERT_SCRIPT.
Example:
  git clone https://github.com/ggml-org/llama.cpp "$HOME/llama.cpp"
  cmake -S "$HOME/llama.cpp" -B "$HOME/llama.cpp/build" -DGGML_CUDA=ON
  cmake --build "$HOME/llama.cpp/build" --config Release -j
EOF
  exit 1
fi

mkdir -p "$GGUF_OUT_DIR"

BASE_GGUF="$GGUF_OUT_DIR/$GGUF_BASENAME-$GGUF_OUTTYPE.gguf"
RUN_GGUF="$BASE_GGUF"

echo "Converting HF checkpoint to GGUF"
echo "  model:     $MODEL_DIR"
echo "  converter: $CONVERT_SCRIPT"
echo "  outfile:   $BASE_GGUF"
echo "  outtype:   $GGUF_OUTTYPE"

"$PYTHON_BIN" "$CONVERT_SCRIPT" "$MODEL_DIR" \
  --outfile "$BASE_GGUF" \
  --outtype "$GGUF_OUTTYPE"

if [[ "$GGUF_QUANTIZATIONS" == "none" || -z "$GGUF_QUANTIZATIONS" ]]; then
  cat <<EOF
Done: $BASE_GGUF

Run with llama.cpp:
  llama-server -m "$RUN_GGUF" --port 8080 -c 2048 -ngl 99
EOF
  exit 0
fi

QUANTIZE_BIN="$(find_quantize_bin || true)"
if [[ -z "$QUANTIZE_BIN" ]]; then
  cat >&2 <<EOF
llama-quantize binary not found under: $LLAMA_CPP_DIR

Set LLAMA_QUANTIZE_BIN, or build llama.cpp first.
The intermediate GGUF was created:
  $BASE_GGUF
EOF
  exit 1
fi

IFS=',' read -r -a QUANTIZATION_LIST <<< "$GGUF_QUANTIZATIONS"
RUN_GGUF_SELECTED=0

for quantization in "${QUANTIZATION_LIST[@]}"; do
  quantization="${quantization//[[:space:]]/}"
  [[ -z "$quantization" ]] && continue

  quant_upper="$(printf '%s' "$quantization" | tr '[:lower:]' '[:upper:]')"
  quant_lower="$(printf '%s' "$quantization" | tr '[:upper:]' '[:lower:]')"

  case "$quant_upper" in
    NONE)
      continue
      ;;
    F16|BF16)
      echo "Skipping quantization $quant_upper; intermediate file is already $BASE_GGUF"
      continue
      ;;
  esac

  target="$GGUF_OUT_DIR/$GGUF_BASENAME-$quant_lower.gguf"
  echo "Quantizing GGUF"
  echo "  quantize: $QUANTIZE_BIN"
  echo "  method:   $quant_upper"
  echo "  target:   $target"
  "$QUANTIZE_BIN" "$BASE_GGUF" "$target" "$quant_upper"

  if [[ "$RUN_GGUF_SELECTED" -eq 0 ]]; then
    RUN_GGUF="$target"
    RUN_GGUF_SELECTED=1
  fi
done

cat <<EOF
Done.

Run with llama.cpp:
  llama-server -m "$RUN_GGUF" --port 8080 -c 2048 -ngl 99
EOF

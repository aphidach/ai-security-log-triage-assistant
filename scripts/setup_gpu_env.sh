#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
UV_BIN="${UV_BIN:-uv}"

cd "${ROOT_DIR}"

if ! command -v "${UV_BIN}" >/dev/null 2>&1; then
    echo "[setup-gpu] uv is required but was not found in PATH" >&2
    echo "[setup-gpu] install uv first, then create a GPU venv with: uv venv --seed .venv-gpu" >&2
    exit 1
fi

if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "[setup-gpu] python interpreter not found: ${PYTHON_BIN}" >&2
    exit 1
fi

echo "[setup-gpu] repo root: ${ROOT_DIR}"
echo "[setup-gpu] uv: $(command -v "${UV_BIN}")"
echo "[setup-gpu] python: $(${PYTHON_BIN} -c 'import sys; print(sys.executable)')"

readarray -t DETECTION_LINES < <("${PYTHON_BIN}" - <<'PY'
import importlib.util
import os
import sys

colab = int(any(key.startswith("COLAB_") for key in os.environ))
torch_missing = int(importlib.util.find_spec("torch") is None)
unsloth_missing = int(importlib.util.find_spec("unsloth") is None)
in_venv = int(sys.prefix != getattr(sys, "base_prefix", sys.prefix))

try:
    import numpy

    numpy_spec = f"numpy=={numpy.__version__}"
except Exception:
    numpy_spec = "numpy"

try:
    from PIL import Image

    pillow_module = __import__("PIL")
    pillow_spec = f"pillow=={pillow_module.__version__}"
except Exception:
    pillow_spec = "pillow"

print(f"COLAB_DETECTED={colab}")
print(f"TORCH_MISSING={torch_missing}")
print(f"UNSLOTH_MISSING={unsloth_missing}")
print(f"IN_VENV={in_venv}")
print(f"NUMPY_SPEC={numpy_spec}")
print(f"PILLOW_SPEC={pillow_spec}")
PY
)

for line in "${DETECTION_LINES[@]}"; do
    eval "${line}"
done

if [[ "${IN_VENV}" != "1" ]]; then
    echo "[setup-gpu] refusing to install into a non-virtualenv interpreter" >&2
    echo "[setup-gpu] create one first, for example:" >&2
    echo "[setup-gpu]   uv venv --seed .venv-gpu" >&2
    echo "[setup-gpu]   source .venv-gpu/bin/activate" >&2
    exit 1
fi

UV_PIP_INSTALL=("${UV_BIN}" "pip" "install" "--python" "${PYTHON_BIN}")

echo "[setup-gpu] colab=${COLAB_DETECTED} torch_missing=${TORCH_MISSING} unsloth_missing=${UNSLOTH_MISSING}"

if [[ "${TORCH_MISSING}" == "1" || "${COLAB_DETECTED}" == "1" ]]; then
    echo "[setup-gpu] installing core torch/unsloth stack"
    "${UV_PIP_INSTALL[@]}" \
        "torch==2.8.0" \
        "triton>=3.3.0" \
        "${NUMPY_SPEC}" \
        "${PILLOW_SPEC}" \
        torchvision \
        bitsandbytes \
        xformers==0.0.32.post2 \
        "unsloth_zoo[base] @ git+https://github.com/unslothai/unsloth-zoo" \
        "unsloth[base] @ git+https://github.com/unslothai/unsloth"
    "${UV_PIP_INSTALL[@]}" --no-deps "torchcodec==0.7.0"
elif [[ "${UNSLOTH_MISSING}" == "1" ]]; then
    echo "[setup-gpu] torch already present; installing unsloth"
    "${UV_PIP_INSTALL[@]}" unsloth
fi

echo "[setup-gpu] reconciling tokenizers/trl/transformers pins"
"${UV_PIP_INSTALL[@]}" --upgrade --no-deps \
    "tokenizers>=0.22.0,<=0.23.0" \
    trl==0.22.2 \
    unsloth \
    unsloth_zoo

"${UV_PIP_INSTALL[@]}" transformers==5.2.0

echo "[setup-gpu] installing flash attention helpers"
"${UV_PIP_INSTALL[@]}" --no-build-isolation flash-linear-attention causal_conv1d==1.6.0

echo "[setup-gpu] installing torchao"
"${UV_PIP_INSTALL[@]}" --no-deps --upgrade "torchao>=0.16.0"

echo "[setup-gpu] done"
echo "[setup-gpu] next steps:"
echo "  1. ${PYTHON_BIN} ml/unsloth/train_lora.py --preflight-only"
echo "  2. ${PYTHON_BIN} ml/unsloth/inference.py --preflight-only --log-line '2026-05-17T10:00:00+07:00 waf: GET /search?q=SLEEP(5) status=500'"

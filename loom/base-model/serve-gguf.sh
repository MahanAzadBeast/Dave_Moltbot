#!/usr/bin/env bash
# Serve any local GGUF base model to Loom on an OpenAI-compatible endpoint.
#
# Downloads a llama.cpp release build (no compiler needed) and starts
# llama-server, which exposes /v1/completions -- the plain completions API
# that base models want and that Loom's "openai" model type speaks.
#
# Usage:
#   ./loom/base-model/serve-gguf.sh /path/to/model.gguf [port]
#
# Getting a base-model GGUF (on a machine that can reach Hugging Face):
#   pip install -U "huggingface_hub[cli]"
#   hf download TheBloke/Mistral-7B-v0.1-GGUF mistral-7b-v0.1.Q4_K_M.gguf \
#       --local-dir ~/models
# Prefer genuinely BASE weights (no -Instruct / -Chat in the name):
#   Mistral-7B-v0.1, Llama-3.1-8B (base), Qwen2.5-7B (base).
#
# Then in Loom, Settings -> Model config -> Add Model:
#   Model id: local-gguf   type: openai   API base: http://127.0.0.1:8011/v1
# (Loom sends the *Model id* as the API model name; llama-server ignores it.)

set -euo pipefail

MODEL="${1:-}"
PORT="${2:-8011}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD="b6148"   # pinned release; verified to run in this repo's CI sandbox
ZIP="llama-${BUILD}-bin-ubuntu-x64.zip"
URL="https://github.com/ggml-org/llama.cpp/releases/download/${BUILD}/${ZIP}"

if [ -z "$MODEL" ] || [ ! -f "$MODEL" ]; then
    echo "Usage: $0 /path/to/model.gguf [port]" >&2
    exit 1
fi

BIN="$HERE/llamacpp/build/bin/llama-server"
if [ ! -x "$BIN" ]; then
    case "$(uname -s)" in
        Linux)
            echo "Fetching llama.cpp ${BUILD}..."
            curl -L --fail -o "$HERE/$ZIP" "$URL"
            unzip -oq "$HERE/$ZIP" -d "$HERE/llamacpp"
            chmod +x "$HERE"/llamacpp/build/bin/* || true
            ;;
        Darwin)
            echo "On macOS install llama.cpp with:  brew install llama.cpp" >&2
            echo "then run:  llama-server -m '$MODEL' --port $PORT" >&2
            exit 1
            ;;
        *)
            echo "Unsupported platform; install llama.cpp manually." >&2
            exit 1
            ;;
    esac
fi

echo "Serving $(basename "$MODEL") on http://127.0.0.1:${PORT}/v1"
LD_LIBRARY_PATH="$HERE/llamacpp/build/bin" exec "$BIN" \
    -m "$MODEL" --host 127.0.0.1 --port "$PORT" \
    -c 4096 -n 512 --threads "$(nproc 2>/dev/null || echo 4)"

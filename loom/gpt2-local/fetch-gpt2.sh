#!/usr/bin/env bash
# Download GPT-2 124M (ONNX, official onnx/models zoo) + its BPE tokenizer.
# Both come from GitHub-hosted sources, no Hugging Face account or API key
# needed. Verifies the model against the sha256 recorded in the LFS pointer.

set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

MODEL_URL="https://media.githubusercontent.com/media/onnx/models/main/validated/text/machine_comprehension/gpt-2/model/gpt2-lm-head-10.onnx"
MODEL_SHA256="12fbb1ec2d2d70c8ebd21a290a348a4109447b98582af64c6f93b6526d5c8f35"
TOKENIZER_URL="https://raw.githubusercontent.com/openai/whisper/main/whisper/assets/gpt2.tiktoken"

if [ ! -f "$HERE/gpt2-lm-head-10.onnx" ]; then
    echo "Downloading GPT-2 124M ONNX model (~665 MB)..."
    curl -L --fail -o "$HERE/gpt2-lm-head-10.onnx" "$MODEL_URL"
fi
echo "$MODEL_SHA256  $HERE/gpt2-lm-head-10.onnx" | sha256sum -c -

if [ ! -f "$HERE/gpt2.tiktoken" ]; then
    echo "Downloading GPT-2 BPE tokenizer..."
    curl -L --fail -o "$HERE/gpt2.tiktoken" "$TOKENIZER_URL"
fi

echo "Done. Start the server with:"
echo "  <loom venv>/bin/python $HERE/server.py \\"
echo "      --model $HERE/gpt2-lm-head-10.onnx --tokenizer $HERE/gpt2.tiktoken --port 8010"

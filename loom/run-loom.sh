#!/usr/bin/env bash
# Launch Loom. Run ./loom/install-loom.sh first.
#
# Reads API keys from the environment (or from loom/.env if present):
#   OPENAI_API_KEY      - OpenAI, or any OpenAI-compatible provider key
#                         (OpenRouter, Hyperbolic, ...) used with model
#                         type "openai" / "openai-custom"
#   TOGETHERAI_API_KEY  - Together AI (model type "together")

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLONE_DIR="$HERE/loom"
VENV_DIR="$HERE/.venv"

if [ ! -d "$CLONE_DIR" ] || [ ! -d "$VENV_DIR" ]; then
    echo "Loom is not installed yet. Run: ./loom/install-loom.sh" >&2
    exit 1
fi

# Optional local env file for keys (gitignored)
if [ -f "$HERE/.env" ]; then
    set -a
    # shellcheck disable=SC1091
    source "$HERE/.env"
    set +a
fi

cd "$CLONE_DIR"
exec "$VENV_DIR/bin/python" main.py "$@"

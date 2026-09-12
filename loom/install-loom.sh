#!/usr/bin/env bash
# Install socketteer/loom (tree-based writing interface for base models).
#
# Clones the upstream repo into loom/loom, creates a virtualenv with a
# Python that has tkinter, and installs modernized dependencies
# (upstream's pinned requirements no longer build on current Python).
#
# Usage:  ./loom/install-loom.sh
# Then:   ./loom/run-loom.sh

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLONE_DIR="$HERE/loom"
VENV_DIR="$HERE/.venv"

# --- Find a Python (3.10+) that has tkinter ---------------------------------
PYTHON=""
for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 \
       && "$candidate" -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null \
       && "$candidate" -c 'import tkinter' 2>/dev/null; then
        PYTHON="$candidate"
        break
    fi
done

if [ -z "$PYTHON" ]; then
    echo "ERROR: no Python 3.10+ with tkinter found." >&2
    echo "  Debian/Ubuntu:  sudo apt-get install python3-tk" >&2
    echo "  macOS (brew):   brew install python-tk" >&2
    echo "  Windows:        tkinter ships with the python.org installer" >&2
    exit 1
fi
echo "Using $PYTHON ($($PYTHON --version))"

# --- Clone loom --------------------------------------------------------------
if [ -d "$CLONE_DIR/.git" ]; then
    echo "Loom already cloned at $CLONE_DIR, pulling latest..."
    git -C "$CLONE_DIR" pull --ff-only || echo "  (pull failed, keeping existing checkout)"
else
    git clone https://github.com/socketteer/loom "$CLONE_DIR"
fi

# --- Virtualenv + dependencies ------------------------------------------------
if [ ! -d "$VENV_DIR" ]; then
    "$PYTHON" -m venv "$VENV_DIR"
fi
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$HERE/requirements-modern.txt"

# --- Smoke test ---------------------------------------------------------------
echo "Verifying Loom modules import..."
(cd "$CLONE_DIR" && "$VENV_DIR/bin/python" -c "import gpt, model, controller" >/dev/null)

echo
echo "Loom installed successfully."
echo
echo "To run:"
echo "  export OPENAI_API_KEY=sk-...   # or provider key, see loom/README.md"
echo "  ./loom/run-loom.sh"

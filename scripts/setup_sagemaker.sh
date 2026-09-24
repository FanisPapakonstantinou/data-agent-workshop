#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
VENV_DIR="$REPO_ROOT/.venv"
LOCK_FILE="$REPO_ROOT/requirements.lock.txt"
KERNEL_NAME="data-agent-workshop"
MARKER_FILE="$VENV_DIR/.requirements-lock.sha256"
PYTHON_BIN="${WORKSHOP_PYTHON:-python3}"

cd "$REPO_ROOT"

"$PYTHON_BIN" - <<'PY'
import sys

if sys.version_info < (3, 11) or sys.version_info >= (3, 13):
    raise SystemExit(
        f"Python 3.11 or 3.12 is required; found {sys.version.split()[0]}."
    )
PY

LOCK_HASH="$("$PYTHON_BIN" - "$LOCK_FILE" <<'PY'
import hashlib
import pathlib
import sys

print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"

if [[ ! -x "$VENV_DIR/bin/python" ]]; then
    echo "Creating workshop virtual environment..."
    "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

INSTALLED_HASH=""
if [[ -f "$MARKER_FILE" ]]; then
    INSTALLED_HASH="$(<"$MARKER_FILE")"
fi

if [[ "$INSTALLED_HASH" != "$LOCK_HASH" ]]; then
    echo "Installing pinned workshop dependencies..."
    "$VENV_DIR/bin/python" -m pip install --upgrade pip
    "$VENV_DIR/bin/python" -m pip install -r "$LOCK_FILE"
    printf '%s\n' "$LOCK_HASH" > "$MARKER_FILE"
else
    echo "Workshop dependencies are already up to date."
fi

echo "Registering the Jupyter kernel..."
"$VENV_DIR/bin/python" -m ipykernel install --user \
    --name "$KERNEL_NAME" \
    --display-name "Data Agent Workshop"

echo "Running the offline smoke test..."
"$VENV_DIR/bin/python" "$REPO_ROOT/scripts/smoke_test.py"

echo
echo "Setup complete. Select the 'Data Agent Workshop' kernel in JupyterLab."

#!/usr/bin/env bash
set -euo pipefail

# One-click helper to provision a local test environment for the GD FastAPI backend.
# - Creates/uses a virtual environment under .venv (override with VENV_DIR)
# - Installs Python dependencies
# - Exposes the FastAPI app on 0.0.0.0:$PORT (default 8000)
# - Wires up GD_EXCEL_PATH and GD_LOGO_PATH (if a logo file is present)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${VENV_DIR:-"$ROOT_DIR/.venv"}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
PORT="${PORT:-8000}"
APP_IMPORT_PATH="gd.api:app"

# Ensure Python is available
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[error] Python interpreter not found: $PYTHON_BIN" >&2
  exit 1
fi

# Create/activate the virtual environment
if [ ! -d "$VENV_DIR" ]; then
  echo "[info] Creating virtual environment at $VENV_DIR"
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# Install dependencies
python -m pip install --upgrade pip >/dev/null
python -m pip install -r "$ROOT_DIR/requirements.txt"

# Configure workbook/logo paths if not already set
export GD_EXCEL_PATH="${GD_EXCEL_PATH:-"$ROOT_DIR/GD_v1.xlsx"}"
if [ -z "${GD_LOGO_PATH:-}" ] && [ -f "$ROOT_DIR/Telefonica logo.png" ]; then
  export GD_LOGO_PATH="$ROOT_DIR/Telefonica logo.png"
fi

# Show active paths for confirmation
python - <<'PY'
from gd import config
print(config.describe_active_paths(), end="")
PY

# Launch the API server
echo "[info] Starting FastAPI app ($APP_IMPORT_PATH) on port $PORT"
exec python -m uvicorn "$APP_IMPORT_PATH" --host 0.0.0.0 --port "$PORT"

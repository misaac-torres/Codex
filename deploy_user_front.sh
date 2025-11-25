#!/usr/bin/env bash
set -euo pipefail

# One-click entrypoint to deploy the Telefónica-styled user front (Swagger UI)
# served by the GD FastAPI backend. This is a thin wrapper around the existing
# test environment helper to keep the command short and memorable.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "[info] Deploying the Telefónica user front (Swagger UI) in one step..."
exec "$SCRIPT_DIR/deploy_test_env.sh"

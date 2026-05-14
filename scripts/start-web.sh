#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD"
PYTHON_ENV_DIR="${PYTHON_ENV_DIR:-runtime}"
export PATH="$PWD/$PYTHON_ENV_DIR/bin:$PATH"
exec "$PYTHON_ENV_DIR/bin/uvicorn" app.main:app --host 127.0.0.1 --port "${PORT:-8000}"

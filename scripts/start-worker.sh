#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD"
PYTHON_ENV_DIR="${PYTHON_ENV_DIR:-runtime}"
exec "$PYTHON_ENV_DIR/bin/python" -m app.jobs.worker

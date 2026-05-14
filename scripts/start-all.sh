#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

./scripts/start-worker.sh &
worker_pid=$!
./scripts/start-web.sh &
web_pid=$!

stop_all() {
  kill "$web_pid" "$worker_pid" 2>/dev/null || true
  wait "$web_pid" "$worker_pid" 2>/dev/null || true
}

trap stop_all INT TERM EXIT

echo "Web running on http://127.0.0.1:${PORT:-8000}"
echo "Worker running in background pid=$worker_pid"
wait "$web_pid"

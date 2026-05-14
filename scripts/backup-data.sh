#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p backups
stamp="$(date +%Y%m%d-%H%M%S)"
tar -czf "backups/data-$stamp.tar.gz" data/app.db data/outputs 2>/dev/null || tar -czf "backups/data-$stamp.tar.gz" data
printf 'Backup created: backups/data-%s.tar.gz\n' "$stamp"

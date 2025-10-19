#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

echo "[start.sh] working dir: $(pwd)"
echo "[start.sh] listing contents:" && ls -a

exec gunicorn scripts.wsgi:app --config scripts/gunicorn.conf.py

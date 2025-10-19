#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

exec gunicorn scripts.wsgi:app --config scripts/gunicorn.conf.py

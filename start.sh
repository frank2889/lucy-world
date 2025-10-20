#!/usr/bin/env bash
set -euo pipefail

echo "========================================="
echo "Lucy World - DigitalOcean Startup Script"
echo "========================================="

# Move to repository root
cd "$(dirname "$0")"

echo "Working directory: $(pwd)"
echo "Python3 version: $(python3 --version 2>&1)"
echo "PORT: ${PORT:-not set}"
echo ""
echo "Directory contents:"
ls -la
echo ""
echo "Checking scripts directory:"
ls -la scripts/ | head -20
echo ""

# Verify Python can import the module
echo "Testing module import..."
python3 -c "import sys; sys.path.insert(0, '.'); from scripts.wsgi import app; print('✓ Module import successful')" || {
    echo "ERROR: Cannot import scripts.wsgi:app"
    echo "Python sys.path:"
    python3 -c "import sys; print('\n'.join(sys.path))"
    exit 1
}

echo ""
echo "Starting Gunicorn with scripts.wsgi:app..."
echo "========================================="

# Use python3 explicitly and add current dir to PYTHONPATH
export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}.":

exec python3 -m gunicorn scripts.wsgi:app \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers 2 \
    --worker-class sync \
    --timeout 30 \
    --log-level info \
    --access-logfile - \
    --error-logfile -

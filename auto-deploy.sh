#!/usr/bin/env bash

# Auto-deploy script for Lucy World Search
# Pulls the latest code, refreshes dependencies, and restarts services.

set -euo pipefail

echo "🚀 Lucy World Search – Auto Deploy"
echo "=================================="

# Configuration (override via environment variables when needed)
REPO_URL=${REPO_URL:-https://github.com/frank2889/lucy-world.git}
APP_DIR=${APP_DIR:-/var/www/lucy-world-search}
SERVICE_NAME=${SERVICE_NAME:-lucy-world-search}
NGINX_SERVICE=${NGINX_SERVICE:-nginx}
VENV_PATH=${VENV_PATH:-$APP_DIR/venv}
REQUIREMENTS_FILE=${REQUIREMENTS_FILE:-requirements.txt}
HEALTHCHECK_URL=${HEALTHCHECK_URL:-https://lucy.world/health}
OWNERSHIP_TARGET=${OWNERSHIP_TARGET:-www-data:www-data}

SYSTEMD_UNIT="/etc/systemd/system/${SERVICE_NAME}.service"

if [ ! -f "$SYSTEMD_UNIT" ]; then
    echo "❌ Systemd unit $SYSTEMD_UNIT not found. Run the initial provisioning first."
    exit 1
fi

if [ ! -d "$APP_DIR/.git" ]; then
    echo "❌ $APP_DIR does not contain a Git repository."
    exit 1
fi

echo "📥 Pulling latest code from $REPO_URL ..."

current_remote=$(git -C "$APP_DIR" remote get-url origin || true)
if [ "$current_remote" != "$REPO_URL" ]; then
    echo "🔁 Updating origin remote → $REPO_URL"
    git -C "$APP_DIR" remote set-url origin "$REPO_URL"
fi

git -C "$APP_DIR" fetch --prune origin
git -C "$APP_DIR" reset --hard origin/main

if command -v sudo >/dev/null 2>&1; then
    sudo chown -R "$OWNERSHIP_TARGET" "$APP_DIR" || true
else
    chown -R "$OWNERSHIP_TARGET" "$APP_DIR" 2>/dev/null || true
fi

PIP_BIN="$VENV_PATH/bin/pip"
PYTHON_BIN="$VENV_PATH/bin/python"

if [ ! -x "$PIP_BIN" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH (missing pip executable)."
    exit 1
fi

echo "📚 Updating Python dependencies from $REQUIREMENTS_FILE ..."
"$PIP_BIN" install --upgrade pip
"$PIP_BIN" install -r "$APP_DIR/$REQUIREMENTS_FILE"

# Optional: rebuild the frontend bundle if npm is available on the server.
if [ -f "$APP_DIR/frontend/package.json" ] && command -v npm >/dev/null 2>&1; then
    echo "🧱 Building frontend bundle..."
    (cd "$APP_DIR/frontend" && npm install && npm run build)
fi

echo "🔄 Restarting services..."
if command -v sudo >/dev/null 2>&1; then
    sudo systemctl restart "$SERVICE_NAME"
    sudo systemctl restart "$NGINX_SERVICE"
else
    systemctl restart "$SERVICE_NAME"
    systemctl restart "$NGINX_SERVICE"
fi

echo "📊 Verifying service state..."
sleep 3
if command -v sudo >/dev/null 2>&1; then
    sudo systemctl is-active --quiet "$SERVICE_NAME"
else
    systemctl is-active --quiet "$SERVICE_NAME"
fi
echo "✅ Gunicorn service is running"

if [ -n "$HEALTHCHECK_URL" ]; then
    echo "🌐 Health check → $HEALTHCHECK_URL"
    if curl -fsS "$HEALTHCHECK_URL" > /dev/null; then
        echo "✅ Health endpoint responded"
    else
        echo "❌ Health endpoint failed"
        exit 1
    fi
fi

echo ""
echo "🎉 Deployment complete"
echo "📍 App Directory: $APP_DIR"
echo "🔍 Health: $HEALTHCHECK_URL"
echo ""
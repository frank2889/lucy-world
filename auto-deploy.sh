#!/bin/bash

# Auto-deploy script for Lucy World Search
# This script pulls latest code from GitHub and deploys it

set -e

echo "🚀 Lucy World Search - Auto Deploy from GitHub"
echo "=============================================="

# Configuration
REPO_URL="https://github.com/YOUR_USERNAME/lucy-world-search.git"
APP_DIR="/var/www/lucy-world-search"
SERVICE_NAME="lucy-world-search"

# Check if we're on the server
if [ ! -f "/etc/systemd/system/$SERVICE_NAME.service" ]; then
    echo "❌ This appears to be the first deployment. Run initial deploy.sh first."
    exit 1
fi

echo "📥 Pulling latest code from GitHub..."

# Navigate to app directory
cd $APP_DIR

# Pull latest changes
git fetch origin
git reset --hard origin/main

# Update permissions
sudo chown -R www-data:www-data $APP_DIR

# Install/update dependencies
echo "📚 Updating dependencies..."
source venv/bin/activate
pip install -r requirements-prod.txt

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl restart nginx

# Check status
echo "📊 Checking service status..."
sleep 3
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service is running"
else
    echo "❌ Service failed to start"
    sudo journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi

# Test website
echo "🌐 Testing website..."
if curl -f -s https://lucy.world/health > /dev/null; then
    echo "✅ Website is responding"
else
    echo "❌ Website is not responding"
    exit 1
fi

echo ""
echo "🎉 Deployment successful!"
echo "📍 Website: https://lucy.world"
echo "🔍 Health: https://lucy.world/health"
echo ""
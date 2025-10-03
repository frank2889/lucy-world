#!/bin/bash

# Auto-deployment webhook for DigitalOcean
# This script runs on the server when GitHub pushes changes

echo "🔄 Auto-deployment triggered at $(date)"

# Navigate to the project directory
cd /var/www/lucy-world-search || {
    echo "❌ Project directory not found!"
    exit 1
}

# Pull latest changes from GitHub
echo "📦 Pulling latest changes from GitHub..."
git fetch origin
git reset --hard origin/main
git pull origin main

# Install any new dependencies
echo "📋 Checking dependencies..."
pip3 install -r requirements.txt --quiet

# Kill existing processes
echo "🛑 Stopping existing processes..."
pkill -f "python.*app.py" || true
pkill -f "gunicorn" || true
sleep 2

# Restart the application
echo "🚀 Starting Lucy World Search..."
export FLASK_ENV=production
export FLASK_APP=app.py

# Start with Gunicorn if available, otherwise use Flask directly
if command -v gunicorn &> /dev/null; then
    echo "🚀 Starting with Gunicorn..."
    nohup gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app > /var/log/lucy-world.log 2>&1 &
else
    echo "🚀 Starting with Flask..."
    nohup python3 app.py > /var/log/lucy-world.log 2>&1 &
fi

# Wait a moment for startup
sleep 3

# Check if it's running
if pgrep -f "python.*app|gunicorn" > /dev/null; then
    echo "✅ Lucy World Search is running!"
    echo "🌐 Available at: https://lucy.world"
else
    echo "❌ Failed to start Lucy World Search"
    echo "📋 Last 10 lines of log:"
    tail -10 /var/log/lucy-world.log
    exit 1
fi

echo "🎉 Auto-deployment completed successfully at $(date)"
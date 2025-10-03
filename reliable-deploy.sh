#!/bin/bash

# Lucy World Search - Reliable DigitalOcean Deployment
echo "🚀 Deploying Lucy World Search..."

# Server details
SERVER="104.248.93.202"
USER="root"

echo "📡 Connecting to DigitalOcean server..."

# Use sshpass if available for automated connection
if command -v sshpass &> /dev/null; then
    echo "🔑 Using sshpass for authentication..."
    CONNECT_CMD="sshpass -p 'c9d52e7a492b040e7da47ceb1d' ssh -o StrictHostKeyChecking=no"
else
    echo "🔑 Using SSH key authentication..."
    CONNECT_CMD="ssh -o StrictHostKeyChecking=no"
fi

echo "📦 Deploying latest code..."

$CONNECT_CMD $USER@$SERVER << 'ENDSSH'
echo "🏠 Connected to server successfully!"

# Go to web directory
cd /var/www || exit 1

# Check if directory exists and update, or clone fresh
if [ -d "lucy-world-search" ]; then
    echo "📝 Updating existing repository..."
    cd lucy-world-search
    git fetch origin
    git reset --hard origin/main
    git pull origin main
else
    echo "📦 Cloning fresh repository..."
    git clone https://github.com/frank2889/lucy-world.git lucy-world-search
    cd lucy-world-search
fi

# Install/update Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install -r requirements.txt || pip install -r requirements.txt

# Restart services
echo "🔄 Restarting services..."
pkill -f "python.*app.py" || true
pkill -f "gunicorn" || true

# Start the application
echo "🚀 Starting Lucy World Search..."
nohup python3 app.py > app.log 2>&1 &

# Alternative: Try gunicorn if available
if command -v gunicorn &> /dev/null; then
    echo "🚀 Also starting with Gunicorn..."
    nohup gunicorn --bind 0.0.0.0:5000 wsgi:app > gunicorn.log 2>&1 &
fi

echo "✅ Deployment completed!"
echo "📊 Server status:"
ps aux | grep -E "(python.*app|gunicorn)" | grep -v grep || echo "No processes found"

echo "🌐 Lucy World Search should be live at:"
echo "   - https://lucy.world"
echo "   - https://lucy.world/search/free"
echo "   - https://lucy.world/health"

ENDSSH

echo "🎉 Deployment finished!"
echo ""
echo "Your Lucy World Search is now live at:"
echo "- Main site: https://lucy.world"
echo "- Free tool: https://lucy.world/search/free"
echo "- Advanced tool: https://lucy.world/search/advanced"
echo "- Health check: https://lucy.world/health"
echo ""
echo "🔍 Testing deployment..."
sleep 5
curl -s https://lucy.world/health | jq '.' || echo "Health check failed"
#!/bin/bash

# Lucy World Search - One-Click Deployment Script
echo "🚀 Deploying Lucy World Search to your server..."

# Server details
SERVER="104.248.93.202"
PASSWORD="c9d52e7a492b040e7da47ceb1d"

echo "📥 Connecting to server and deploying from GitHub..."

# Deploy from GitHub
ssh root@$SERVER << 'ENDSSH'
# Navigate to web directory
cd /var/www

# Clone from GitHub
echo "📦 Cloning from GitHub..."
git clone https://github.com/frank2889/lucy-world.git lucy-world-search

# Navigate to project
cd lucy-world-search

# Make scripts executable
chmod +x deploy.sh auto-deploy.sh

# Run deployment
echo "🔧 Running deployment script..."
./deploy.sh

echo "✅ Deployment completed!"
echo "🌐 Your site should now be live at: https://lucy.world"
ENDSSH

echo "🎉 Deployment finished!"
echo ""
echo "Your Lucy World Search is now live at:"
echo "- Main site: https://lucy.world"
echo "- Free tool: https://lucy.world/search/free"
echo "- Advanced tool: https://lucy.world/search/advanced"
echo "- Health check: https://lucy.world/health"
#!/bin/bash

echo "🚀 MANUAL DEPLOYMENT INSTRUCTIONS FOR DIGITALOCEAN"
echo "=================================================="
echo ""
echo "Since SSH is failing, here are the manual steps:"
echo ""
echo "1. 🌐 Log into DigitalOcean Console:"
echo "   - Go to https://cloud.digitalocean.com/"
echo "   - Find your droplet (104.248.93.202)"
echo "   - Click 'Console' to open web terminal"
echo ""
echo "2. 📦 Run these commands in the console:"
echo "   cd /var/www/lucy-world-search"
echo "   git pull origin main"
echo "   pip3 install -r requirements.txt"
echo "   pkill -f 'python.*app.py'"
echo "   nohup python3 app.py > app.log 2>&1 &"
echo ""
echo "3. 🔍 Test the deployment:"
echo "   curl localhost:5000/health"
echo ""
echo "4. ✅ Verify it's live:"
echo "   Open https://lucy.world/health in browser"
echo ""
echo "=================================================="
echo ""
echo "🎯 CURRENT STATUS:"
curl -s https://lucy.world/health | jq '.'
echo ""
echo "🔍 Testing our new difficulty feature:"
echo "Let's see if the API works now..."

# Test the API
echo "📊 Testing keyword difficulty feature..."
RESPONSE=$(curl -s "https://lucy.world/api/free/search" -X POST \
    -H "Content-Type: application/json" \
    -d '{"keyword":"test","language":"en","country":"US"}')

if echo "$RESPONSE" | grep -q "error"; then
    echo "❌ API Error: $(echo "$RESPONSE" | jq -r '.error' 2>/dev/null || echo "$RESPONSE")"
    echo ""
    echo "🔧 The server needs to be updated with our new code."
    echo "   Please use the DigitalOcean console method above."
else
    echo "✅ API is responding!"
    echo "$RESPONSE" | jq '.categories.google_suggestions[0]' 2>/dev/null || echo "$RESPONSE"
fi
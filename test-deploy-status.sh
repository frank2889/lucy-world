#!/bin/bash

echo "🔄 FORCE REFRESH TEST - Triggering GitHub webhook"
echo "================================================"
echo ""
echo "✅ Our latest commits are pushed:"
git log --oneline -3
echo ""
echo "🎯 Key changes that should be live:"
echo "   - difficulty_score and difficulty_reasoning fields in KeywordData"
echo "   - KeywordDifficultyAnalyzer integration"
echo "   - Wikipedia removal"
echo "   - International country selector fixes"
echo ""
echo "🔍 Current server status:"
curl -s https://lucy.world/health | jq '.'
echo ""
echo "📊 Testing difficulty feature again..."

RESULT=$(curl -s "https://lucy.world/api/free/search" -X POST \
    -H "Content-Type: application/json" \
    -d '{"keyword":"test keyword","language":"en","country":"US"}')

echo "Response: $RESULT" | jq '.categories.google_suggestions[0] | {keyword, difficulty_score, difficulty_reasoning}' 2>/dev/null || echo "Raw: $RESULT"

echo ""
echo "🚀 If difficulty_score is still 0, the auto-deploy might:"
echo "   1. Have a delay (webhook processing time)"
echo "   2. Need manual trigger"
echo "   3. Require server restart"
echo ""
echo "💡 Since you have access and GitHub→DigitalOcean works,"
echo "   the update should happen automatically soon!"
#!/bin/bash

echo "🚀 PHIA - GitHub Upload Script"
echo "=============================="

cd /home/hrakashchauhan/personal-health-insights-agent

# Step 1: Authenticate with GitHub
echo "🔐 Step 1: GitHub Authentication"
echo "Please authenticate with your GitHub account..."
gh auth login

# Step 2: Create repository
echo ""
echo "📁 Step 2: Creating GitHub repository..."
gh repo create phia-health-insights \
  --public \
  --description "🏥 AI-Powered Personal Health Insights Agent - Analyze wearable data with Google Gemini AI" \
  --homepage "https://phia-health-insights.onrender.com"

# Step 3: Add remote and push
echo ""
echo "📤 Step 3: Uploading code to GitHub..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/hrakashchauhan/phia-health-insights.git
git branch -M main
git push -u origin main

echo ""
echo "✅ SUCCESS! PHIA uploaded to GitHub!"
echo ""
echo "🌐 Repository URL: https://github.com/hrakashchauhan/phia-health-insights"
echo ""
echo "🚀 Next: Deploy to Render for live hosting"
echo "   1. Go to: https://render.com"
echo "   2. Connect GitHub repository: phia-health-insights"
echo "   3. Add environment variables:"
echo "      - GOOGLE_API_KEY: <paste your own key — never commit it>"
echo "      - TAVILY_API_KEY: <paste your own key — never commit it>"
echo ""
echo "🎉 Your live URL will be: https://phia-health-insights.onrender.com"

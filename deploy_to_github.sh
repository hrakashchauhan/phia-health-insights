#!/bin/bash

echo "🚀 PHIA GitHub Deployment Guide"
echo "================================"
echo ""

# Check if git is configured
if ! git config user.name > /dev/null; then
    echo "⚠️  Git not configured. Please run:"
    echo "git config --global user.name 'Your Name'"
    echo "git config --global user.email 'your.email@example.com'"
    exit 1
fi

echo "📋 Step-by-step deployment instructions:"
echo ""

echo "1️⃣  CREATE GITHUB REPOSITORY"
echo "   • Go to: https://github.com/hrakashchauhan"
echo "   • Click 'New repository'"
echo "   • Repository name: phia-health-insights"
echo "   • Description: AI-Powered Personal Health Insights Agent"
echo "   • Make it Public"
echo "   • Don't initialize with README (we have one)"
echo "   • Click 'Create repository'"
echo ""

echo "2️⃣  UPLOAD TO GITHUB"
echo "   Run these commands:"
echo "   git remote add origin https://github.com/hrakashchauhan/phia-health-insights.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

echo "3️⃣  DEPLOY TO RENDER (FREE HOSTING)"
echo "   • Go to: https://render.com"
echo "   • Sign up/Login with GitHub"
echo "   • Click 'New' → 'Web Service'"
echo "   • Connect your GitHub repository: phia-health-insights"
echo "   • Settings:"
echo "     - Name: phia-health-insights"
echo "     - Environment: Python 3"
echo "     - Build Command: pip install -r requirements-web.txt"
echo "     - Start Command: gunicorn --bind 0.0.0.0:\$PORT app:app"
echo "   • Environment Variables:"
echo "     - GOOGLE_API_KEY: [Your Google API Key]"
echo "     - TAVILY_API_KEY: [Your Tavily API Key]"
echo "   • Click 'Create Web Service'"
echo ""

echo "4️⃣  YOUR LIVE URL WILL BE:"
echo "   https://phia-health-insights.onrender.com"
echo ""

echo "🔒 SECURITY NOTES:"
echo "   ✅ API keys are protected (not in repository)"
echo "   ✅ Environment variables used for sensitive data"
echo "   ✅ .gitignore prevents accidental key commits"
echo ""

echo "📱 FEATURES INCLUDED:"
echo "   ✅ AI-powered health insights"
echo "   ✅ Interactive web interface"
echo "   ✅ Real-time health data analysis"
echo "   ✅ Mobile-responsive design"
echo "   ✅ Production-ready deployment"
echo ""

echo "🎯 READY TO DEPLOY!"
echo "Follow the steps above to get your PHIA app live!"
echo ""

# Offer to run git commands
read -p "🤖 Would you like me to add the GitHub remote now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Adding GitHub remote..."
    git remote add origin https://github.com/hrakashchauhan/phia-health-insights.git 2>/dev/null || echo "Remote already exists"
    echo "✅ Remote added. Now run: git push -u origin main"
fi

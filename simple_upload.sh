#!/bin/bash

echo "🚀 Uploading PHIA to GitHub..."
echo "Repository: https://github.com/hrakashchauhan/phia-health-insights"
echo ""

cd /home/hrakashchauhan/personal-health-insights-agent

# Remove existing remote
git remote remove origin 2>/dev/null || true

# Add your repository
git remote add origin https://github.com/hrakashchauhan/phia-health-insights.git

# Set main branch
git branch -M main

echo "📤 Pushing files to GitHub..."
echo "You'll need to enter your GitHub username and personal access token"
echo ""

# Push to GitHub
git push -u origin main --force

echo ""
echo "✅ Upload complete!"
echo "🌐 View at: https://github.com/hrakashchauhan/phia-health-insights"

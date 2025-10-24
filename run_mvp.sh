#!/bin/bash

echo "🚀 Starting PHIA MVP - Full Working Prototype"
echo "============================================="

# Activate environment
source /home/hrakashchauhan/miniconda3/etc/profile.d/conda.sh
conda activate phia

# Change to project directory
cd /home/hrakashchauhan/personal-health-insights-agent

echo "✅ Environment activated"
echo "🏥 Starting PHIA MVP..."
echo ""
echo "Features included:"
echo "- User authentication & registration"
echo "- Personal health data logging"
echo "- AI-powered health insights"
echo "- Goal tracking (Premium feature)"
echo "- Advanced analytics (Premium feature)"
echo "- Subscription system (Free/Premium)"
echo ""
echo "🌐 Access at: http://localhost:8501"
echo "Press Ctrl+C to stop"
echo ""

# Run the MVP
streamlit run mvp_app.py --server.port 8501

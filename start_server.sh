#!/bin/bash

echo "🏥 PHIA - Personal Health Insights Agent"
echo "========================================"
echo "🚀 Starting Enhanced Web Server..."
echo ""

# Activate conda environment
source /home/hrakashchauhan/miniconda3/etc/profile.d/conda.sh
conda activate phia

# Change to project directory
cd /home/hrakashchauhan/personal-health-insights-agent

# Check if environment is activated
if [[ "$CONDA_DEFAULT_ENV" == "phia" ]]; then
    echo "✅ PHIA environment activated"
else
    echo "❌ Failed to activate PHIA environment"
    exit 1
fi

# Check if API keys exist
if [[ -f "api_keys.py" ]]; then
    echo "✅ API keys found"
else
    echo "❌ API keys not found. Please create api_keys.py with your keys."
    exit 1
fi

echo ""
echo "🌐 Starting web server..."
echo "📱 Access PHIA at: http://localhost:5000"
echo "🌍 Network access at: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"

# Start the Flask application
python app.py

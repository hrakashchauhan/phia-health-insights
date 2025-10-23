#!/bin/bash

# Script to start Jupyter notebook server for PHIA project

echo "Starting PHIA Jupyter Notebook Server..."
echo "========================================="

# Activate conda environment
source /home/hrakashchauhan/miniconda3/etc/profile.d/conda.sh
conda activate phia

# Change to project directory
cd /home/hrakashchauhan/personal-health-insights-agent

# Check if environment is activated
if [[ "$CONDA_DEFAULT_ENV" == "phia" ]]; then
    echo "✓ PHIA environment activated"
else
    echo "✗ Failed to activate PHIA environment"
    exit 1
fi

# Start Jupyter notebook
echo "Starting Jupyter notebook server..."
echo "The notebook will open in your default browser."
echo "If it doesn't open automatically, copy the URL from the output below."
echo ""
echo "To stop the server, press Ctrl+C in this terminal."
echo ""

jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root

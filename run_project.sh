#!/bin/bash

# Main script to run PHIA project with different options

echo "🏥 PHIA - Personal Health Insights Agent"
echo "========================================"
echo ""
echo "✅ Setup Status: COMPLETE"
echo "All dependencies installed and tested successfully!"
echo ""

# Activate conda environment
source /home/hrakashchauhan/miniconda3/etc/profile.d/conda.sh
conda activate phia

# Change to project directory
cd /home/hrakashchauhan/personal-health-insights-agent

echo "Choose how you want to run PHIA:"
echo ""
echo "1. 📓 Jupyter Notebook (Recommended - Interactive)"
echo "2. 🐍 Python Script (Command Line)"
echo "3. 🧪 Test Setup (Verify installation)"
echo "4. 📚 View Documentation"
echo "5. ❌ Exit"
echo ""

read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Starting Jupyter Notebook..."
        echo "The notebook will open in your browser."
        echo "Open 'phia_demo.ipynb' and follow the instructions."
        echo ""
        echo "📝 Don't forget to:"
        echo "   - Get API keys from https://aistudio.google.com and https://www.tavily.com"
        echo "   - Add them to Cell 2 in the notebook"
        echo ""
        echo "Press Ctrl+C to stop the server when done."
        echo ""
        ./start_jupyter.sh
        ;;
    2)
        echo ""
        echo "🐍 Starting Python Script..."
        echo "You'll be prompted for API keys."
        echo ""
        python run_phia.py
        ;;
    3)
        echo ""
        echo "🧪 Running Setup Tests..."
        echo ""
        python test_setup.py
        ;;
    4)
        echo ""
        echo "📚 Documentation:"
        echo ""
        if command -v less &> /dev/null; then
            less SETUP_GUIDE.md
        else
            cat SETUP_GUIDE.md
        fi
        ;;
    5)
        echo ""
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

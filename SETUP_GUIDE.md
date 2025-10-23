# PHIA (Personal Health Insights Agent) - Setup & Usage Guide

## ✅ Setup Status: COMPLETE

Your PHIA environment has been successfully set up and tested! All dependencies are installed and working correctly.

## 🚀 Quick Start

### Option 1: Using Jupyter Notebook (Recommended)

1. **Start Jupyter Server:**
   ```bash
   cd /home/hrakashchauhan/personal-health-insights-agent
   ./start_jupyter.sh
   ```

2. **Open the Demo Notebook:**
   - Open your browser and go to the URL shown in the terminal (usually `http://localhost:8888`)
   - Open `phia_demo.ipynb`

3. **Add API Keys:**
   - Get a Google/Gemini API key from: https://aistudio.google.com
   - Get a Tavily API key from: https://www.tavily.com/#pricing (free tier available)
   - Add your keys to Cell 2 in the notebook

4. **Run the Notebook:**
   - Run all cells in order
   - Modify the question in Cell 7 to ask your own health-related questions

### Option 2: Using Python Script

1. **Activate Environment:**
   ```bash
   source /home/hrakashchauhan/miniconda3/etc/profile.d/conda.sh
   conda activate phia
   cd /home/hrakashchauhan/personal-health-insights-agent
   ```

2. **Test Setup:**
   ```bash
   python test_setup.py
   ```

## 📊 Available Data

The project includes synthetic wearable user data:

- **Summary Data:** Daily health metrics (sleep, heart rate, activity, etc.)
- **Exercise Data:** Workout details and performance metrics
- **Profile Data:** User demographics and preferences

### Sample Users Available:
- User 502 (default in demo)
- User 465, 333, 171, 41 (used in evaluation)
- Many others in the `synthetic_wearable_users/` directory

To use a different user, change the file paths in Cell 4 of the notebook:
```python
summary_path = os.path.join("synthetic_wearable_users", "summary_df_XXX.csv")
activities_path = os.path.join("synthetic_wearable_users", "exercise_df_XXX.csv")
```

## 🤖 Example Questions You Can Ask

### Health Analysis:
- "How can I feel more awake and energetic during the day?"
- "What's affecting my sleep quality?"
- "How does my exercise routine impact my recovery?"

### Performance Optimization:
- "How can I improve my running performance?"
- "What's the best time for me to work out?"
- "How should I adjust my training for better results?"

### Data Insights:
- "What patterns do you see in my health data?"
- "How does my stress level correlate with my sleep?"
- "What was my best workout last month?"

## 🔧 Troubleshooting

### Common Issues:

1. **Import Errors:**
   - Make sure you're in the correct conda environment: `conda activate phia`
   - Verify you're in the project directory

2. **API Key Issues:**
   - Ensure your API keys are valid and have sufficient quota
   - Check that keys are properly set in the notebook

3. **Data Loading Issues:**
   - Verify the CSV files exist in `synthetic_wearable_users/`
   - Check file permissions

4. **Jupyter Issues:**
   - If notebook doesn't open, manually go to `http://localhost:8888`
   - Use the token shown in the terminal output

### Getting Help:

1. **Check the original README.md** for detailed project information
2. **Run the test script** to verify setup: `python test_setup.py`
3. **Check the logs** in the terminal for error messages

## 📁 Project Structure

```
personal-health-insights-agent/
├── phia_demo.ipynb          # Main demo notebook
├── test_setup.py            # Setup verification script
├── start_jupyter.sh         # Jupyter server launcher
├── data_utils.py            # Data loading utilities
├── phia_agent.py           # Core agent logic
├── prompt_templates.py     # Prompt templates
├── colab_utils.py          # Display utilities
├── few_shots/              # Example interactions (46 files)
├── synthetic_wearable_users/ # Sample user data
├── data/                   # Additional datasets
└── figs/                   # Figure generation code
```

## 🎯 Next Steps

1. **Explore the Demo:** Run through the notebook with the default question
2. **Try Different Users:** Load different synthetic users to see varied responses
3. **Ask Custom Questions:** Experiment with your own health-related queries
4. **Explore the Code:** Look at the agent logic in `phia_agent.py`
5. **Check the Paper:** Read the research paper for deeper understanding

## 📚 Additional Resources

- **Original Paper:** [Transforming Wearable Data into Personal Health Insights using Large Language Model Agents](https://arxiv.org/abs/2406.06464)
- **Google Blog Post:** [Advancing Personal Health and Wellness Insights with AI](https://research.google/blog/advancing-personal-health-and-wellness-insights-with-ai/)
- **Gemini API Docs:** https://ai.google.dev/docs
- **Tavily API Docs:** https://docs.tavily.com/

---

**Status:** ✅ Ready to use! All tests passed and environment is properly configured.

**Last Updated:** $(date)

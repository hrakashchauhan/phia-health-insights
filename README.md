# 🏥 PHIA - Personal Health Insights Agent

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Available-brightgreen)](https://your-app-url.onrender.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.1+-red)](https://flask.palletsprojects.com)
[![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)](https://ai.google.dev)

**PHIA** is an AI-powered Personal Health Insights Agent that analyzes wearable device data to provide personalized health recommendations and insights.

## 🌟 Features

- **AI-Powered Analysis**: Uses Google's Gemini AI for intelligent health insights
- **Comprehensive Health Metrics**: Sleep, activity, heart rate, and stress analysis
- **Interactive Web Interface**: Beautiful, responsive design for all devices
- **Real-time Chat**: Ask questions about your health data in natural language
- **Personalized Recommendations**: Evidence-based suggestions for health improvement
- **Data Visualization**: Clear charts and progress tracking

## 🚀 Live Demo

Try PHIA live: **[https://your-app-url.onrender.com](https://your-app-url.onrender.com)**

## 📊 What PHIA Analyzes

### Sleep Quality
- Sleep duration and consistency
- Deep sleep and REM percentages
- Sleep efficiency metrics
- Bedtime pattern analysis

### Physical Activity
- Daily step counts and trends
- Active zone minutes
- Workout frequency and intensity
- Activity pattern recognition

### Cardiovascular Health
- Resting heart rate trends
- Heart rate variability
- Recovery metrics
- Cardiovascular fitness indicators

### Stress & Recovery
- Stress management scores
- Recovery recommendations
- Lifestyle impact analysis
- Wellness optimization

## 🛠️ Installation

### Quick Start (Local Development)

1. **Clone the repository**
   ```bash
   git clone https://github.com/hrakashchauhan/phia-health-insights.git
   cd phia-health-insights
   ```

2. **Set up environment**
   ```bash
   conda create -n phia python=3.11 -y
   conda activate phia
   pip install -r requirements-web.txt
   ```

3. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

### API Keys Required

- **Google/Gemini API Key**: Get from [Google AI Studio](https://aistudio.google.com)
- **Tavily API Key** (optional): Get from [Tavily](https://www.tavily.com/#pricing)

## 🌐 Deployment

### Deploy to Render (Recommended)

1. Fork this repository
2. Connect to [Render](https://render.com)
3. Create a new Web Service
4. Set environment variables:
   - `GOOGLE_API_KEY`: Your Google/Gemini API key
   - `TAVILY_API_KEY`: Your Tavily API key (optional)
5. Deploy!

### Deploy to Heroku

```bash
heroku create your-app-name
heroku config:set GOOGLE_API_KEY=your_key_here
heroku config:set TAVILY_API_KEY=your_key_here
git push heroku main
```

## 💬 Example Questions

Ask PHIA anything about your health data:

- "How can I feel more awake and energetic during the day?"
- "What's affecting my sleep quality?"
- "How can I improve my running performance?"
- "What patterns do you see in my health data?"
- "How does my exercise routine impact my recovery?"
- "What's the best time for me to work out?"

## 🏗️ Architecture

```
PHIA/
├── app.py                 # Flask web application
├── config.py             # Configuration management
├── data_utils.py         # Data processing utilities
├── phia_agent.py         # AI agent core logic
├── prompt_templates.py   # AI prompt templates
├── templates/
│   └── index.html        # Web interface
├── synthetic_wearable_users/  # Sample health data
├── few_shots/            # AI training examples
└── requirements-web.txt  # Dependencies
```

## 🔒 Security

- API keys are never committed to the repository
- Environment variables used for sensitive data
- Secure configuration management
- Input validation and sanitization

## 📈 Health Data

PHIA works with synthetic wearable device data that includes:

- **29 days** of continuous health monitoring
- **Sleep metrics**: Duration, stages, efficiency
- **Activity data**: Steps, active minutes, workouts
- **Heart rate**: Resting HR, variability, zones
- **Stress indicators**: Management scores, recovery

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International License.

## 🙏 Acknowledgments

- Based on research: ["Transforming Wearable Data into Personal Health Insights using Large Language Model Agents"](https://arxiv.org/abs/2406.06464)
- Google Research for the foundational work
- Google AI for Gemini API
- Tavily for search capabilities

## 📞 Support

- 🐛 [Report Issues](https://github.com/hrakashchauhan/phia-health-insights/issues)
- 💬 [Discussions](https://github.com/hrakashchauhan/phia-health-insights/discussions)
- 📧 Contact: [your-email@example.com]

---

**⚠️ Disclaimer**: PHIA is for educational and research purposes. Always consult healthcare professionals for medical advice.

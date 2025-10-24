# 🏥 PHIA - Personal Health Insights Agent

**Advanced AI-Powered Health Analytics Platform**

PHIA is a comprehensive health platform that combines personal health tracking with advanced AI analytics to provide personalized insights and recommendations.

## 🚀 **Live Demo**

**Streamlit Cloud:** [https://phia-health-insights.streamlit.app](https://phia-health-insights.streamlit.app)

## ✨ **Key Features**

### 🤖 **AI Health Analyst**
- **Google Gemini Integration:** Advanced AI analysis of health patterns
- **Personalized Insights:** Data-driven recommendations based on your metrics
- **Pattern Recognition:** Identifies correlations between sleep, activity, stress, and mood
- **Professional Analysis:** Clinical-grade insights and preventive health strategies

### 📊 **Comprehensive Health Tracking**
- **Multi-Metric Monitoring:** Sleep, steps, heart rate, stress, weight, mood
- **Trend Analysis:** 7-day vs 30-day comparisons with directional insights
- **Interactive Dashboards:** Real-time visualization of health data
- **Goal Tracking:** Set and monitor health objectives

### 🔒 **Secure & Private**
- **Local Data Storage:** SQLite database for privacy
- **User Authentication:** Secure login system with password hashing
- **Personal Dashboards:** Individual user data isolation

## 🛠 **Technology Stack**

- **Frontend:** Streamlit with Plotly visualizations
- **Backend:** Python with SQLite database
- **AI Engine:** Google Gemini Pro for health analysis
- **Deployment:** Streamlit Cloud hosting

## 📱 **Quick Start**

### **Option 1: Use Live Demo**
Visit [https://phia-health-insights.streamlit.app](https://phia-health-insights.streamlit.app)

### **Option 2: Local Installation**

```bash
# Clone repository
git clone https://github.com/hrakashchauhan/phia-health-insights.git
cd phia-health-insights

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your Google API key to .env file

# Run application
streamlit run streamlit_app.py
```

## 🎯 **How to Use**

1. **Create Account:** Sign up with username, email, and password
2. **Log Health Data:** Enter daily metrics (sleep, steps, heart rate, etc.)
3. **View Dashboard:** Monitor trends and key health indicators
4. **Ask PHIA:** Get AI-powered insights about your health patterns

### **Sample Questions for AI:**
- "How is my sleep quality affecting my stress levels?"
- "What should I focus on to improve my energy?"
- "Analyze my cardiovascular fitness trends"
- "What correlations do you see in my health data?"

## 🏗 **Architecture**

```
PHIA Platform
├── User Interface (Streamlit)
├── Health Data Management (SQLite)
├── AI Analytics Engine (Gemini)
├── Visualization Layer (Plotly)
└── Authentication System
```

## 📈 **Health Metrics Tracked**

| Metric | Range | Purpose |
|--------|-------|---------|
| Sleep Hours | 0-12h | Sleep quality analysis |
| Daily Steps | 0-30k | Activity level monitoring |
| Heart Rate | 40-120 bpm | Cardiovascular fitness |
| Stress Score | 0-100 | Mental wellness tracking |
| Weight | 30-200 kg | Physical health monitoring |
| Mood | 1-10 | Mental health assessment |

## 🔬 **AI Analysis Features**

- **Pattern Recognition:** Identifies trends and correlations
- **Predictive Insights:** Early warning for health concerns
- **Personalized Recommendations:** Tailored advice based on data
- **Comparative Analysis:** Benchmarking against health standards
- **Risk Assessment:** Proactive health monitoring

## 🚀 **Deployment**

### **Streamlit Cloud**
- Automatic deployment from GitHub
- Environment variables configured in Streamlit settings
- SSL/HTTPS enabled by default

### **Local Development**
```bash
# Development server
streamlit run streamlit_app.py --server.port 8501

# Production server
streamlit run streamlit_app.py --server.port 80 --server.address 0.0.0.0
```

## 🔐 **Environment Variables**

```bash
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 📊 **Business Model**

PHIA operates on a freemium model with advanced AI features available to all users:

- **Core Features:** Health tracking, basic analytics, AI chat
- **Premium Features:** Advanced correlations, predictive insights, export capabilities
- **Enterprise:** HIPAA compliance, team dashboards, API access

## 🛣 **Roadmap**

### **Phase 1: MVP** ✅
- Basic health tracking
- AI chat integration
- User authentication
- Data visualization

### **Phase 2: Enhanced Analytics** 🚧
- Advanced pattern recognition
- Predictive health modeling
- Integration with wearables
- Mobile app development

### **Phase 3: Healthcare Integration** 📋
- HIPAA compliance
- Healthcare provider integration
- Clinical decision support
- Telemedicine features

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- Google Gemini AI for advanced health analytics
- Streamlit for rapid web app development
- Plotly for interactive visualizations
- Open source health data standards

## 📞 **Contact**

**Project Maintainer:** [Your Name]
**Email:** [your.email@example.com]
**GitHub:** [@hrakashchauhan](https://github.com/hrakashchauhan)

---

**Built with ❤️ for better health outcomes through AI-powered insights**

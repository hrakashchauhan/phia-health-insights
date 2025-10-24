import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import hashlib
import sqlite3
import os
import google.generativeai as genai
import json

# Page config
st.set_page_config(page_title="PHIA", page_icon="🏥", layout="wide")

# Configure Gemini AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', 'AIzaSyBbVQPjHOLxvtjjjjjjjjjjjjjjjjjjjjjjjjj')
genai.configure(api_key=GOOGLE_API_KEY)

def init_db():
    conn = sqlite3.connect('phia_mvp.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  email TEXT, created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS health_data
                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, 
                  sleep_hours REAL, steps INTEGER, heart_rate INTEGER, 
                  stress_score INTEGER, weight REAL, mood INTEGER,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, email):
    conn = sqlite3.connect('phia_mvp.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, email, created_at) VALUES (?, ?, ?, ?)",
                 (username, hash_password(password), email, datetime.now().isoformat()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect('phia_mvp.db')
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?",
             (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def get_user_data(user_id):
    conn = sqlite3.connect('phia_mvp.db')
    df = pd.read_sql_query("SELECT * FROM health_data WHERE user_id=? ORDER BY date DESC", 
                          conn, params=(user_id,))
    conn.close()
    return df

def save_health_data(user_id, date, sleep, steps, hr, stress, weight, mood):
    conn = sqlite3.connect('phia_mvp.db')
    c = conn.cursor()
    c.execute("""INSERT OR REPLACE INTO health_data 
                 (user_id, date, sleep_hours, steps, heart_rate, stress_score, weight, mood)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
             (user_id, date, sleep, steps, hr, stress, weight, mood))
    conn.commit()
    conn.close()

def analyze_health_patterns(user_data):
    """Comprehensive health data analysis for AI context"""
    if user_data.empty:
        return "No health data available for analysis."
    
    analysis = {}
    
    # Time-based analysis
    recent_7d = user_data.head(7)
    recent_30d = user_data.head(30)
    
    # Sleep analysis
    sleep_avg_7d = recent_7d['sleep_hours'].mean()
    sleep_avg_30d = recent_30d['sleep_hours'].mean()
    sleep_trend = "improving" if sleep_avg_7d > sleep_avg_30d else "declining" if sleep_avg_7d < sleep_avg_30d else "stable"
    sleep_consistency = recent_7d['sleep_hours'].std()
    
    analysis['sleep'] = {
        'avg_7d': sleep_avg_7d,
        'avg_30d': sleep_avg_30d,
        'trend': sleep_trend,
        'consistency': 'consistent' if sleep_consistency < 0.5 else 'inconsistent',
        'quality': 'excellent' if sleep_avg_7d >= 8 else 'good' if sleep_avg_7d >= 7 else 'poor'
    }
    
    # Activity analysis
    steps_avg_7d = recent_7d['steps'].mean()
    steps_avg_30d = recent_30d['steps'].mean()
    activity_trend = "increasing" if steps_avg_7d > steps_avg_30d else "decreasing" if steps_avg_7d < steps_avg_30d else "stable"
    
    analysis['activity'] = {
        'avg_7d': steps_avg_7d,
        'avg_30d': steps_avg_30d,
        'trend': activity_trend,
        'level': 'high' if steps_avg_7d >= 10000 else 'moderate' if steps_avg_7d >= 7000 else 'low'
    }
    
    # Cardiovascular analysis
    hr_avg = recent_7d['heart_rate'].mean()
    hr_variability = recent_7d['heart_rate'].std()
    
    analysis['cardiovascular'] = {
        'resting_hr': hr_avg,
        'variability': hr_variability,
        'fitness_level': 'excellent' if hr_avg < 60 else 'good' if hr_avg < 70 else 'average' if hr_avg < 80 else 'needs_improvement'
    }
    
    # Stress analysis
    stress_avg = recent_7d['stress_score'].mean()
    stress_trend_data = recent_7d['stress_score'].tolist()
    stress_trend = "improving" if len(stress_trend_data) > 1 and stress_trend_data[0] > stress_trend_data[-1] else "worsening" if len(stress_trend_data) > 1 and stress_trend_data[0] < stress_trend_data[-1] else "stable"
    
    analysis['stress'] = {
        'avg_level': stress_avg,
        'trend': stress_trend,
        'management': 'excellent' if stress_avg >= 80 else 'good' if stress_avg >= 65 else 'needs_attention'
    }
    
    # Weight analysis
    if len(recent_30d) > 1:
        weight_change = recent_7d['weight'].mean() - recent_30d['weight'].mean()
        analysis['weight'] = {
            'current': recent_7d['weight'].mean(),
            'change_30d': weight_change,
            'trend': 'increasing' if weight_change > 0.5 else 'decreasing' if weight_change < -0.5 else 'stable'
        }
    
    # Mood analysis
    mood_avg = recent_7d['mood'].mean()
    analysis['mood'] = {
        'avg_score': mood_avg,
        'status': 'excellent' if mood_avg >= 8 else 'good' if mood_avg >= 6 else 'concerning'
    }
    
    # Correlations and insights
    if len(user_data) >= 7:
        sleep_steps_corr = user_data['sleep_hours'].corr(user_data['steps'])
        sleep_mood_corr = user_data['sleep_hours'].corr(user_data['mood'])
        stress_sleep_corr = user_data['stress_score'].corr(user_data['sleep_hours'])
        
        analysis['correlations'] = {
            'sleep_activity': sleep_steps_corr,
            'sleep_mood': sleep_mood_corr,
            'stress_sleep': stress_sleep_corr
        }
    
    return analysis

def get_ai_response(question, user_data):
    """Advanced AI response using comprehensive health analysis"""
    if user_data.empty:
        return "Please log some health data first to receive personalized insights and recommendations."
    
    # Get comprehensive health analysis
    health_analysis = analyze_health_patterns(user_data)
    
    # Prepare detailed context for AI
    context = f"""
    COMPREHENSIVE HEALTH DATA ANALYSIS:
    
    SLEEP PATTERNS:
    - 7-day average: {health_analysis['sleep']['avg_7d']:.1f} hours
    - 30-day average: {health_analysis['sleep']['avg_30d']:.1f} hours
    - Trend: {health_analysis['sleep']['trend']}
    - Consistency: {health_analysis['sleep']['consistency']}
    - Quality assessment: {health_analysis['sleep']['quality']}
    
    PHYSICAL ACTIVITY:
    - 7-day average: {health_analysis['activity']['avg_7d']:.0f} steps
    - 30-day average: {health_analysis['activity']['avg_30d']:.0f} steps
    - Activity trend: {health_analysis['activity']['trend']}
    - Activity level: {health_analysis['activity']['level']}
    
    CARDIOVASCULAR HEALTH:
    - Resting heart rate: {health_analysis['cardiovascular']['resting_hr']:.0f} bpm
    - Heart rate variability: {health_analysis['cardiovascular']['variability']:.1f}
    - Fitness level: {health_analysis['cardiovascular']['fitness_level']}
    
    STRESS MANAGEMENT:
    - Average stress score: {health_analysis['stress']['avg_level']:.0f}/100
    - Stress trend: {health_analysis['stress']['trend']}
    - Management level: {health_analysis['stress']['management']}
    
    MENTAL WELLBEING:
    - Average mood: {health_analysis['mood']['avg_score']:.1f}/10
    - Mood status: {health_analysis['mood']['status']}
    
    WEIGHT MANAGEMENT:
    - Current weight: {health_analysis.get('weight', {}).get('current', 'N/A')} kg
    - 30-day change: {health_analysis.get('weight', {}).get('change_30d', 'N/A')} kg
    - Weight trend: {health_analysis.get('weight', {}).get('trend', 'N/A')}
    
    HEALTH CORRELATIONS:
    {f"- Sleep-Activity correlation: {health_analysis.get('correlations', {}).get('sleep_activity', 'N/A'):.2f}" if 'correlations' in health_analysis else ""}
    {f"- Sleep-Mood correlation: {health_analysis.get('correlations', {}).get('sleep_mood', 'N/A'):.2f}" if 'correlations' in health_analysis else ""}
    {f"- Stress-Sleep correlation: {health_analysis.get('correlations', {}).get('stress_sleep', 'N/A'):.2f}" if 'correlations' in health_analysis else ""}
    
    RECENT DATA POINTS: {len(user_data)} days of data available
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Enhanced prompt for professional medical insights
        prompt = f"""You are PHIA (Personal Health Insights Agent), an advanced AI health analyst with expertise in preventive medicine, wellness optimization, and data-driven health insights.

CONTEXT: {context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Analyze the comprehensive health data provided above
2. Identify patterns, trends, and correlations in the data
3. Provide evidence-based insights and recommendations
4. Consider interconnections between different health metrics
5. Offer actionable, specific advice based on the data patterns
6. Highlight any concerning trends that need attention
7. Suggest optimization strategies for overall wellness
8. Keep response professional yet accessible (150-200 words)

Focus on:
- Data-driven insights specific to this user's patterns
- Personalized recommendations based on trends
- Preventive health strategies
- Lifestyle optimization suggestions
- Risk factor identification and mitigation
- Holistic health approach considering all metrics

Provide a comprehensive, professional response that demonstrates deep analysis of the health data."""

        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        # Enhanced fallback with pattern analysis
        q = question.lower()
        
        if 'sleep' in q:
            sleep_info = health_analysis['sleep']
            return f"""**Sleep Analysis:** Your 7-day average is {sleep_info['avg_7d']:.1f}h ({sleep_info['quality']} quality, {sleep_info['consistency']} pattern). 
            
Trend: {sleep_info['trend']} compared to 30-day average ({health_analysis['sleep']['avg_30d']:.1f}h).

**Recommendations:** {'Maintain current habits' if sleep_info['quality'] == 'excellent' else 'Aim for 7-9 hours nightly with consistent bedtime routine'}."""

        elif 'activity' in q or 'steps' in q:
            activity_info = health_analysis['activity']
            return f"""**Activity Analysis:** {activity_info['level'].title()} activity level with {activity_info['avg_7d']:.0f} daily steps.
            
Trend: {activity_info['trend']} from 30-day average ({activity_info['avg_30d']:.0f} steps).

**Recommendations:** {'Excellent activity level!' if activity_info['level'] == 'high' else 'Increase to 8,000+ steps daily for optimal health'}."""

        elif 'heart' in q or 'cardiovascular' in q:
            cv_info = health_analysis['cardiovascular']
            return f"""**Cardiovascular Health:** Resting HR {cv_info['resting_hr']:.0f} bpm indicates {cv_info['fitness_level']} fitness level.
            
**Recommendations:** {'Maintain current fitness routine' if cv_info['fitness_level'] in ['excellent', 'good'] else 'Focus on cardio exercise to improve heart health'}."""

        elif 'stress' in q:
            stress_info = health_analysis['stress']
            return f"""**Stress Analysis:** Current level {stress_info['avg_level']:.0f}/100 ({stress_info['management']} management).
            
Trend: {stress_info['trend']} pattern observed.

**Recommendations:** {'Continue current stress management' if stress_info['management'] == 'excellent' else 'Implement meditation, exercise, and sleep optimization'}."""

        else:
            return f"""**Health Overview:** Sleep {health_analysis['sleep']['quality']} ({health_analysis['sleep']['avg_7d']:.1f}h), Activity {health_analysis['activity']['level']} ({health_analysis['activity']['avg_7d']:.0f} steps), Cardiovascular {health_analysis['cardiovascular']['fitness_level']}, Stress {health_analysis['stress']['management']}.

**Key Focus:** {health_analysis['sleep']['trend']} sleep, {health_analysis['activity']['trend']} activity. Ask specific questions for detailed insights."""

# Minimal CSS
st.markdown("""
<style>
    .main { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    .header { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; margin-bottom: 1.5rem; }
    .chat-message { background: #f1f3f4; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
    .ai-response { background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%); padding: 1.2rem; border-radius: 10px; margin: 1rem 0; border-left: 4px solid #2196f3; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize
init_db()

if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

def main():
    if st.session_state.user_id is None:
        st.markdown('<div class="header"><h2>🏥 PHIA Health Platform</h2><p>Advanced AI Health Analytics</p></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                user_id = authenticate_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.success("Welcome to PHIA!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        with tab2:
            new_username = st.text_input("Username", key="new_user")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password", key="new_pass")
            
            if st.button("Create Account"):
                if create_user(new_username, new_password, new_email):
                    st.success("Account created! Please login.")
                else:
                    st.error("Username exists")
        return
    
    # Main App
    st.markdown('<div class="header"><h3>🏥 PHIA Advanced Health Analytics</h3></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        page = st.selectbox("", ["📊 Overview", "📝 Log Data", "🤖 AI Health Analyst"])
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    if "Overview" in page:
        overview_page()
    elif "Log Data" in page:
        log_data_page()
    elif "AI Health" in page:
        chat_page()

def overview_page():
    user_data = get_user_data(st.session_state.user_id)
    
    if user_data.empty:
        st.info("Log your health data to unlock AI-powered insights.")
        return
    
    # Key metrics with analysis
    recent = user_data.iloc[0]
    analysis = analyze_health_patterns(user_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sleep Quality", f"{recent['sleep_hours']:.1f}h", 
                 f"{analysis['sleep']['quality'].title()}")
    with col2:
        st.metric("Activity Level", f"{recent['steps']:,}", 
                 f"{analysis['activity']['level'].title()}")
    with col3:
        st.metric("Heart Fitness", f"{recent['heart_rate']:.0f} bpm",
                 f"{analysis['cardiovascular']['fitness_level'].replace('_', ' ').title()}")
    with col4:
        st.metric("Stress Management", f"{recent['stress_score']:.0f}/100",
                 f"{analysis['stress']['management'].replace('_', ' ').title()}")
    
    # Trend analysis
    st.subheader("Health Trends & Patterns")
    metric = st.selectbox("Analyze Metric", ["sleep_hours", "steps", "heart_rate", "stress_score"])
    
    chart_data = user_data.head(30)
    fig = px.line(chart_data, x='date', y=metric, height=350,
                  title=f"{metric.replace('_', ' ').title()} - 30 Day Trend")
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)
    
    # Quick insights
    if len(user_data) >= 7:
        st.info(f"**AI Insight:** Sleep trend is {analysis['sleep']['trend']}, activity is {analysis['activity']['trend']}, and stress management is {analysis['stress']['management']}. Ask PHIA for detailed analysis!")

def log_data_page():
    st.subheader("Log Health Data")
    
    with st.form("health_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.now().date())
            sleep = st.number_input("Sleep Hours", 0.0, 12.0, 7.5, 0.5)
            steps = st.number_input("Steps", 0, 30000, 8000)
        
        with col2:
            heart_rate = st.number_input("Resting Heart Rate (bpm)", 40, 120, 65)
            stress = st.number_input("Stress Score (0=high stress, 100=no stress)", 0, 100, 75)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
            mood = st.number_input("Mood Score (1-10)", 1, 10, 7)
        
        if st.form_submit_button("💾 Save Health Data"):
            save_health_data(st.session_state.user_id, date.isoformat(), 
                           sleep, steps, heart_rate, stress, weight, mood)
            st.success("✅ Data saved! AI analysis updated.")
            st.rerun()

def chat_page():
    st.subheader("🤖 AI Health Analyst - Advanced Insights")
    
    user_data = get_user_data(st.session_state.user_id)
    
    if user_data.empty:
        st.warning("Please log health data first to enable AI analysis.")
        return
    
    # Professional health analysis buttons
    st.markdown("**Quick Professional Analysis:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🛌 Sleep Optimization"):
            st.session_state.messages.append({"role": "user", "content": "Analyze my sleep patterns and provide optimization strategies based on my data trends."})
    with col2:
        if st.button("🏃 Fitness Assessment"):
            st.session_state.messages.append({"role": "user", "content": "Evaluate my cardiovascular fitness and activity levels. What improvements should I focus on?"})
    with col3:
        if st.button("🧘 Stress Analysis"):
            st.session_state.messages.append({"role": "user", "content": "Analyze my stress patterns and their correlation with other health metrics. Provide management strategies."})
    with col4:
        if st.button("📊 Health Correlations"):
            st.session_state.messages.append({"role": "user", "content": "What correlations do you see between my different health metrics? What patterns should I be aware of?"})
    
    # Advanced chat input
    user_input = st.text_area("Ask PHIA for detailed health analysis:", 
                             placeholder="Example: How do my sleep patterns affect my stress levels and activity? What should I optimize first?",
                             height=80)
    
    if st.button("🔍 Get AI Analysis") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display conversation with enhanced formatting
    for i, msg in enumerate(st.session_state.messages[-8:]):
        if msg["role"] == "user":
            st.markdown(f"**🔍 Your Question:** {msg['content']}")
            
            # Generate AI response for the latest question
            if i == len(st.session_state.messages[-8:]) - 1:
                with st.spinner("🤖 PHIA is analyzing your health data patterns..."):
                    response = get_ai_response(msg["content"], user_data)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                st.markdown(f'''
                <div class="ai-response">
                    <strong>🤖 PHIA Professional Analysis:</strong><br><br>
                    {response}
                </div>
                ''', unsafe_allow_html=True)
                
        elif msg["role"] == "assistant":
            st.markdown(f'''
            <div class="ai-response">
                <strong>🤖 PHIA Professional Analysis:</strong><br><br>
                {msg["content"]}
            </div>
            ''', unsafe_allow_html=True)
    
    # Data summary for context
    if len(user_data) > 0:
        with st.expander("📋 Your Health Data Summary"):
            analysis = analyze_health_patterns(user_data)
            st.json({
                "Data Points": len(user_data),
                "Sleep Quality": analysis['sleep']['quality'],
                "Activity Level": analysis['activity']['level'],
                "Fitness Level": analysis['cardiovascular']['fitness_level'],
                "Stress Management": analysis['stress']['management'],
                "Recent Trends": {
                    "Sleep": analysis['sleep']['trend'],
                    "Activity": analysis['activity']['trend'],
                    "Stress": analysis['stress']['trend']
                }
            })

if __name__ == "__main__":
    main()

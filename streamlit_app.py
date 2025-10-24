import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
import hashlib
import sqlite3
import os
import google.generativeai as genai

# Page config
st.set_page_config(page_title="PHIA", page_icon="🏥", layout="wide")

# Configure Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY', 'AIzaSyBbVQPjHOLxvtjjjjjjjjjjjjjjjjjjjjjjjjj'))

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

def get_ai_response(question, user_data):
    if user_data.empty:
        return "Please log some health data first to get personalized insights."
    
    # Prepare data summary
    recent_data = user_data.head(7)
    data_summary = f"""
    Recent 7-day averages:
    - Sleep: {recent_data['sleep_hours'].mean():.1f} hours
    - Steps: {recent_data['steps'].mean():.0f} per day
    - Heart Rate: {recent_data['heart_rate'].mean():.0f} bpm
    - Stress Score: {recent_data['stress_score'].mean():.0f}/100
    - Weight: {recent_data['weight'].mean():.1f} kg
    - Mood: {recent_data['mood'].mean():.1f}/10
    
    Total data points: {len(user_data)} days
    """
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        prompt = f"""You are PHIA, a health insights AI. Answer this question based on the user's health data:

Question: {question}

User's Health Data:
{data_summary}

Provide a concise, helpful response with specific insights and actionable recommendations. Keep it under 150 words."""
        
        response = model.generate_content(prompt)
        return response.text
    except:
        # Fallback responses
        q = question.lower()
        if 'sleep' in q:
            avg_sleep = recent_data['sleep_hours'].mean()
            return f"Your average sleep is {avg_sleep:.1f}h. {'Good!' if avg_sleep >= 7 else 'Try for 7-8 hours nightly.'}"
        elif 'steps' in q or 'activity' in q:
            avg_steps = recent_data['steps'].mean()
            return f"Daily average: {avg_steps:.0f} steps. {'Great activity!' if avg_steps >= 8000 else 'Aim for 8,000+ steps daily.'}"
        elif 'heart' in q:
            avg_hr = recent_data['heart_rate'].mean()
            return f"Resting HR: {avg_hr:.0f} bpm. {'Excellent' if avg_hr < 60 else 'Good' if avg_hr < 70 else 'Fair'} fitness level."
        elif 'stress' in q:
            avg_stress = recent_data['stress_score'].mean()
            return f"Stress level: {avg_stress:.0f}/100. {'Low stress' if avg_stress > 80 else 'Consider stress management techniques.'}"
        else:
            return f"Recent averages: Sleep {recent_data['sleep_hours'].mean():.1f}h, Steps {recent_data['steps'].mean():.0f}, HR {recent_data['heart_rate'].mean():.0f}bpm"

# Minimal CSS
st.markdown("""
<style>
    .main { font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    .header { background: #f8f9fa; padding: 1.5rem; border-radius: 8px; text-align: center; margin-bottom: 1.5rem; }
    .chat-message { background: #f1f3f4; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; }
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
        st.markdown('<div class="header"><h2>🏥 PHIA Health Platform</h2></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            
            if st.button("Login"):
                user_id = authenticate_user(username, password)
                if user_id:
                    st.session_state.user_id = user_id
                    st.success("Welcome!")
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
    st.markdown('<div class="header"><h3>🏥 PHIA Dashboard</h3></div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        page = st.selectbox("", ["📊 Overview", "📝 Log Data", "💬 Ask PHIA"])
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    if "Overview" in page:
        overview_page()
    elif "Log Data" in page:
        log_data_page()
    elif "Ask PHIA" in page:
        chat_page()

def overview_page():
    user_data = get_user_data(st.session_state.user_id)
    
    if user_data.empty:
        st.info("Log your first health data to see insights.")
        return
    
    # Key metrics
    recent = user_data.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sleep", f"{recent['sleep_hours']:.1f}h")
    with col2:
        st.metric("Steps", f"{recent['steps']:,}")
    with col3:
        st.metric("Heart Rate", f"{recent['heart_rate']:.0f}")
    with col4:
        st.metric("Stress", f"{recent['stress_score']:.0f}/100")
    
    # Chart
    st.subheader("Trends")
    metric = st.selectbox("", ["sleep_hours", "steps", "heart_rate", "stress_score"])
    
    chart_data = user_data.head(14)
    fig = px.line(chart_data, x='date', y=metric, height=300)
    fig.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

def log_data_page():
    st.subheader("Log Health Data")
    
    with st.form("health_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.now().date())
            sleep = st.number_input("Sleep Hours", 0.0, 12.0, 7.5, 0.5)
            steps = st.number_input("Steps", 0, 30000, 8000)
        
        with col2:
            heart_rate = st.number_input("Heart Rate", 40, 120, 65)
            stress = st.number_input("Stress (0-100)", 0, 100, 75)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0)
            mood = st.number_input("Mood (1-10)", 1, 10, 7)
        
        if st.form_submit_button("Save"):
            save_health_data(st.session_state.user_id, date.isoformat(), 
                           sleep, steps, heart_rate, stress, weight, mood)
            st.success("Data saved!")
            st.rerun()

def chat_page():
    st.subheader("Ask PHIA About Your Health")
    
    user_data = get_user_data(st.session_state.user_id)
    
    # Quick questions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Sleep Quality"):
            st.session_state.messages.append({"role": "user", "content": "How is my sleep quality?"})
    with col2:
        if st.button("Activity Level"):
            st.session_state.messages.append({"role": "user", "content": "Am I active enough?"})
    with col3:
        if st.button("Health Summary"):
            st.session_state.messages.append({"role": "user", "content": "Give me a health summary"})
    
    # Chat input
    user_input = st.text_input("Ask about your health data:", placeholder="How can I improve my energy levels?")
    if st.button("Ask") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display conversation
    for i, msg in enumerate(st.session_state.messages[-6:]):
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
            if i == len(st.session_state.messages[-6:]) - 1:  # Only generate response for latest question
                with st.spinner("PHIA is analyzing..."):
                    response = get_ai_response(msg["content"], user_data)
                st.session_state.messages.append({"role": "assistant", "content": response})
                st.markdown(f'<div class="chat-message"><strong>🤖 PHIA:</strong><br>{response}</div>', unsafe_allow_html=True)
        elif msg["role"] == "assistant":
            st.markdown(f'<div class="chat-message"><strong>🤖 PHIA:</strong><br>{msg["content"]}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

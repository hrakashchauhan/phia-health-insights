import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import hashlib
import sqlite3
import os
import random

# Page config
st.set_page_config(page_title="PHIA MVP", page_icon="🏥", layout="wide")

# Initialize database
def init_db():
    conn = sqlite3.connect('phia_mvp.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, 
                  email TEXT, created_at TEXT, subscription TEXT DEFAULT 'free')''')
    
    # Health data table
    c.execute('''CREATE TABLE IF NOT EXISTS health_data
                 (id INTEGER PRIMARY KEY, user_id INTEGER, date TEXT, 
                  sleep_hours REAL, steps INTEGER, heart_rate INTEGER, 
                  stress_score INTEGER, weight REAL, mood INTEGER,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Goals table
    c.execute('''CREATE TABLE IF NOT EXISTS goals
                 (id INTEGER PRIMARY KEY, user_id INTEGER, goal_type TEXT,
                  target_value REAL, current_value REAL, deadline TEXT,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.commit()
    conn.close()
    
    # Seed demo data
    seed_demo_data()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def seed_demo_data():
    """Seed demo data for testing"""
    conn = sqlite3.connect('phia_mvp.db')
    c = conn.cursor()
    
    # Check if demo user exists
    c.execute("SELECT id FROM users WHERE username='demo_user'")
    if c.fetchone():
        conn.close()
        return
    
    try:
        # Create demo user
        c.execute("INSERT INTO users (username, password, email, created_at, subscription) VALUES (?, ?, ?, ?, ?)",
                 ('demo_user', hash_password('demo123'), 'demo@phia.com', datetime.now().isoformat(), 'premium'))
        user_id = c.lastrowid
        
        # Create sample health data for last 14 days
        for i in range(14):
            date = (datetime.now() - timedelta(days=i)).date().isoformat()
            sleep = round(random.uniform(6.5, 8.5), 1)
            steps = random.randint(6000, 12000)
            hr = random.randint(58, 75)
            stress = random.randint(65, 90)
            weight = round(random.uniform(68, 72), 1)
            mood = random.randint(6, 9)
            
            c.execute("""INSERT INTO health_data 
                         (user_id, date, sleep_hours, steps, heart_rate, stress_score, weight, mood)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (user_id, date, sleep, steps, hr, stress, weight, mood))
        
        # Create sample goals
        c.execute("INSERT INTO goals (user_id, goal_type, target_value, current_value, deadline) VALUES (?, ?, ?, ?, ?)",
                 (user_id, 'Daily Steps', 10000, 8500, (datetime.now() + timedelta(days=30)).date().isoformat()))
        c.execute("INSERT INTO goals (user_id, goal_type, target_value, current_value, deadline) VALUES (?, ?, ?, ?, ?)",
                 (user_id, 'Sleep Hours', 8.0, 7.2, (datetime.now() + timedelta(days=30)).date().isoformat()))
        
        conn.commit()
        
    except sqlite3.IntegrityError:
        pass  # Demo user already exists
    
    conn.close()

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
    c.execute("SELECT id, subscription FROM users WHERE username=? AND password=?",
             (username, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result

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

def get_user_goals(user_id):
    conn = sqlite3.connect('phia_mvp.db')
    df = pd.read_sql_query("SELECT * FROM goals WHERE user_id=?", conn, params=(user_id,))
    conn.close()
    return df

def save_goal(user_id, goal_type, target, deadline):
    conn = sqlite3.connect('phia_mvp.db')
    c = conn.cursor()
    c.execute("INSERT INTO goals (user_id, goal_type, target_value, current_value, deadline) VALUES (?, ?, ?, ?, ?)",
             (user_id, goal_type, target, 0, deadline))
    conn.commit()
    conn.close()

def get_ai_response(question, user_data, user_goals):
    if user_data.empty:
        return "Start logging your health data to get personalized insights!"
    
    recent_data = user_data.head(7)  # Last 7 days
    avg_sleep = recent_data['sleep_hours'].mean()
    avg_steps = recent_data['steps'].mean()
    avg_hr = recent_data['heart_rate'].mean()
    avg_stress = recent_data['stress_score'].mean()
    
    q = question.lower()
    
    if 'sleep' in q:
        trend = "improving" if recent_data['sleep_hours'].iloc[0] > avg_sleep else "stable"
        return f"""🛌 **Sleep Analysis:**
        
• Recent average: {avg_sleep:.1f} hours
• Trend: {trend}
• Recommendation: {'Great sleep habits!' if avg_sleep >= 7 else 'Aim for 7-8 hours nightly'}

💡 **Tips:**
- Consistent bedtime routine
- No screens 1 hour before bed
- Cool, dark room (65-68°F)"""

    elif 'steps' in q or 'activity' in q:
        goal_met = avg_steps >= 8000
        return f"""🚶 **Activity Analysis:**
        
• Daily average: {avg_steps:,.0f} steps
• Goal status: {'✅ Target met!' if goal_met else '📈 Keep pushing!'}
• Weekly trend: {'Strong' if avg_steps > 7000 else 'Needs boost'}

💡 **Boost Tips:**
- Take stairs instead of elevators
- Park farther away
- 10-minute walks after meals"""

    elif 'heart' in q:
        fitness_level = "Excellent" if avg_hr < 60 else "Good" if avg_hr < 70 else "Fair"
        return f"""❤️ **Heart Health:**
        
• Resting HR: {avg_hr:.0f} bpm
• Fitness level: {fitness_level}
• Recovery: {'Good' if avg_hr < 70 else 'Monitor closely'}

💡 **Heart Health Tips:**
- Regular cardio exercise
- Stress management
- Adequate sleep"""

    elif 'stress' in q:
        stress_level = "Low" if avg_stress > 75 else "Moderate" if avg_stress > 60 else "High"
        return f"""🧘 **Stress Management:**
        
• Stress level: {stress_level} ({avg_stress:.0f}/100)
• Recent pattern: {'Stable' if recent_data['stress_score'].std() < 10 else 'Variable'}

💡 **Stress Reduction:**
- Deep breathing exercises
- Regular physical activity
- Mindfulness meditation
- Adequate sleep"""

    else:
        return f"""📊 **Your Health Summary:**
        
• Sleep: {avg_sleep:.1f}h average
• Activity: {avg_steps:,.0f} steps/day
• Heart Rate: {avg_hr:.0f} bpm
• Stress: {avg_stress:.0f}/100

🎯 **I can help with:**
- Sleep optimization
- Activity planning
- Stress management
- Goal tracking

What would you like to explore?"""

# CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    .main { font-family: 'Inter', sans-serif; }
    
    .header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    
    .demo-info {
        background: #e8f5e8;
        border: 1px solid #4caf50;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    
    .goal-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #28a745;
        margin: 0.5rem 0;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 10px;
        border-left: 3px solid #667eea;
        background: #f8f9fa;
    }
    
    .subscription-badge {
        background: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .premium-feature {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'subscription' not in st.session_state:
    st.session_state.subscription = 'free'
if 'messages' not in st.session_state:
    st.session_state.messages = []

def main():
    # Authentication
    if st.session_state.user_id is None:
        st.markdown("""
        <div class="header">
            <h1>🏥 PHIA MVP</h1>
            <p>Personal Health Insights Agent</p>
            <p>Your AI-Powered Health Companion</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Demo info
        st.markdown("""
        <div class="demo-info">
            <h4>🎯 Try the Demo!</h4>
            <p><strong>Demo Account:</strong></p>
            <p>Username: <code>demo_user</code></p>
            <p>Password: <code>demo123</code></p>
            <p>This account has 14 days of sample health data and Premium features enabled!</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        
        with tab1:
            st.subheader("Welcome Back!")
            username = st.text_input("Username", key="login_user", value="demo_user")
            password = st.text_input("Password", type="password", key="login_pass", value="demo123")
            
            if st.button("Login"):
                result = authenticate_user(username, password)
                if result:
                    st.session_state.user_id = result[0]
                    st.session_state.username = username
                    st.session_state.subscription = result[1]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        
        with tab2:
            st.subheader("Join PHIA Today!")
            new_username = st.text_input("Choose Username", key="signup_user")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_pass")
            
            if st.button("Create Account"):
                if create_user(new_username, new_password, new_email):
                    st.success("Account created! Please login.")
                else:
                    st.error("Username already exists")
        
        return
    
    # Main App
    st.markdown(f"""
    <div class="header">
        <h1>🏥 Welcome back, {st.session_state.username}!</h1>
        <p>Your Personal Health Dashboard</p>
        <span class="subscription-badge">{st.session_state.subscription.upper()}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Navigation")
        page = st.selectbox("", ["Dashboard", "Log Health Data", "Goals", "AI Chat", "Analytics"])
        
        if st.button("Logout"):
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.subscription = 'free'
            st.rerun()
        
        if st.session_state.subscription == 'free':
            st.markdown("""
            ### 🚀 Upgrade to Premium
            - Unlimited data history
            - Advanced AI insights
            - Goal tracking
            - Priority support
            """)
            if st.button("Upgrade Now - $9.99/month"):
                st.info("Payment integration coming soon!")
    
    # Pages
    if page == "Dashboard":
        dashboard_page()
    elif page == "Log Health Data":
        log_data_page()
    elif page == "Goals":
        goals_page()
    elif page == "AI Chat":
        chat_page()
    elif page == "Analytics":
        analytics_page()

def dashboard_page():
    st.markdown("## 📊 Your Health Overview")
    
    user_data = get_user_data(st.session_state.user_id)
    
    if user_data.empty:
        st.info("👋 Welcome! Start by logging your health data to see insights.")
        if st.button("Log Your First Entry"):
            st.session_state.page = "Log Health Data"
            st.rerun()
        return
    
    # Recent metrics
    recent = user_data.iloc[0]
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("😴 Sleep", f"{recent['sleep_hours']:.1f}h", 
                 delta=f"{recent['sleep_hours'] - user_data['sleep_hours'].mean():.1f}h")
    with col2:
        st.metric("🚶 Steps", f"{recent['steps']:,}", 
                 delta=f"{recent['steps'] - user_data['steps'].mean():.0f}")
    with col3:
        st.metric("❤️ Heart Rate", f"{recent['heart_rate']:.0f} bpm",
                 delta=f"{recent['heart_rate'] - user_data['heart_rate'].mean():.0f}")
    with col4:
        st.metric("🧘 Stress", f"{recent['stress_score']:.0f}/100",
                 delta=f"{recent['stress_score'] - user_data['stress_score'].mean():.0f}")
    
    # Quick chart
    st.markdown("### 📈 7-Day Trends")
    chart_data = user_data.head(7)
    
    metric = st.selectbox("Select Metric", ["sleep_hours", "steps", "heart_rate", "stress_score"])
    
    fig = px.line(chart_data, x='date', y=metric, title=f"{metric.replace('_', ' ').title()} Trend")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
    
    # Quick insights
    st.markdown("### 💡 Quick Insights")
    avg_sleep = user_data['sleep_hours'].mean()
    avg_steps = user_data['steps'].mean()
    
    if avg_sleep < 7:
        st.warning("💤 Your sleep average is below 7 hours. Consider improving sleep hygiene.")
    if avg_steps < 8000:
        st.info("🚶 Try to increase daily steps to 8,000+ for better health.")
    if avg_sleep >= 7 and avg_steps >= 8000:
        st.success("🎉 Great job maintaining healthy habits!")

def log_data_page():
    st.markdown("## 📝 Log Your Health Data")
    
    with st.form("health_data_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Date", datetime.now().date())
            sleep = st.slider("Sleep Hours", 0.0, 12.0, 7.5, 0.5)
            steps = st.number_input("Steps", 0, 50000, 8000)
            heart_rate = st.slider("Resting Heart Rate", 40, 120, 65)
        
        with col2:
            stress = st.slider("Stress Level (0=high stress, 100=no stress)", 0, 100, 75)
            weight = st.number_input("Weight (kg)", 30.0, 200.0, 70.0, 0.1)
            mood = st.slider("Mood (1=poor, 10=excellent)", 1, 10, 7)
        
        if st.form_submit_button("Save Data"):
            save_health_data(st.session_state.user_id, date.isoformat(), 
                           sleep, steps, heart_rate, stress, weight, mood)
            st.success("✅ Health data saved!")
            st.rerun()

def goals_page():
    st.markdown("## 🎯 Your Health Goals")
    
    if st.session_state.subscription == 'free':
        st.markdown("""
        <div class="premium-feature">
            <h4>🔒 Premium Feature</h4>
            <p>Goal tracking is available for Premium subscribers. Upgrade to set and track your health goals!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Goal creation
    with st.expander("➕ Create New Goal"):
        goal_type = st.selectbox("Goal Type", ["Sleep Hours", "Daily Steps", "Weight Loss", "Stress Management"])
        target = st.number_input("Target Value", 0.0, 10000.0, 8000.0)
        deadline = st.date_input("Deadline", datetime.now().date() + timedelta(days=30))
        
        if st.button("Create Goal"):
            save_goal(st.session_state.user_id, goal_type, target, deadline.isoformat())
            st.success("Goal created!")
            st.rerun()
    
    # Display goals
    goals = get_user_goals(st.session_state.user_id)
    user_data = get_user_data(st.session_state.user_id)
    
    for _, goal in goals.iterrows():
        # Calculate progress
        if not user_data.empty:
            if goal['goal_type'] == 'Sleep Hours':
                current = user_data['sleep_hours'].mean()
            elif goal['goal_type'] == 'Daily Steps':
                current = user_data['steps'].mean()
            else:
                current = goal['current_value']
        else:
            current = 0
        
        progress = min(100, (current / goal['target_value']) * 100)
        
        st.markdown(f"""
        <div class="goal-card">
            <h4>{goal['goal_type']}</h4>
            <p>Target: {goal['target_value']} | Current: {current:.1f} | Progress: {progress:.0f}%</p>
            <div style="background: #e9ecef; border-radius: 10px; height: 10px;">
                <div style="background: #28a745; height: 10px; width: {progress}%; border-radius: 10px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def chat_page():
    st.markdown("## 💬 Chat with PHIA AI")
    
    user_data = get_user_data(st.session_state.user_id)
    user_goals = get_user_goals(st.session_state.user_id)
    
    # Quick questions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("How's my sleep?"):
            st.session_state.messages.append({"role": "user", "content": "How's my sleep?"})
    with col2:
        if st.button("Am I active enough?"):
            st.session_state.messages.append({"role": "user", "content": "Am I active enough?"})
    with col3:
        if st.button("Stress analysis"):
            st.session_state.messages.append({"role": "user", "content": "How are my stress levels?"})
    
    # Chat input
    user_input = st.text_input("Ask PHIA anything about your health:", key="chat_input")
    if st.button("Send") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display messages
    for msg in st.session_state.messages[-6:]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
            response = get_ai_response(msg["content"], user_data, user_goals)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(f"""
            <div class="chat-message">
                <strong>🤖 PHIA:</strong><br>{response}
            </div>
            """, unsafe_allow_html=True)

def analytics_page():
    st.markdown("## 📊 Advanced Analytics")
    
    if st.session_state.subscription == 'free':
        st.markdown("""
        <div class="premium-feature">
            <h4>🔒 Premium Feature</h4>
            <p>Advanced analytics available for Premium subscribers. Get detailed insights, correlations, and predictions!</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    user_data = get_user_data(st.session_state.user_id)
    
    if user_data.empty:
        st.info("No data available for analytics. Start logging your health data!")
        return
    
    # Correlation analysis
    st.markdown("### 🔗 Health Correlations")
    
    if len(user_data) >= 7:
        corr_data = user_data[['sleep_hours', 'steps', 'heart_rate', 'stress_score']].corr()
        fig = px.imshow(corr_data, text_auto=True, aspect="auto", title="Health Metrics Correlation")
        st.plotly_chart(fig, use_container_width=True)
    
    # Trends
    st.markdown("### 📈 Long-term Trends")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=user_data['date'], y=user_data['sleep_hours'], name='Sleep'))
    fig.add_trace(go.Scatter(x=user_data['date'], y=user_data['steps']/1000, name='Steps (k)'))
    fig.add_trace(go.Scatter(x=user_data['date'], y=user_data['stress_score'], name='Stress'))
    
    fig.update_layout(title="Multi-Metric Trends", height=400)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()

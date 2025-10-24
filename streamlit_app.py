import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="PHIA - Personal Health Insights Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main { font-family: 'Inter', sans-serif; }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .chat-message {
        padding: 1rem 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        animation: fadeIn 0.5s ease;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        margin-left: 20%;
        border-bottom-right-radius: 5px;
    }
    
    .ai-message {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        margin-right: 20%;
        border-bottom-left-radius: 5px;
        border-left: 4px solid #667eea;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'health_data' not in st.session_state:
    st.session_state.health_data = None

@st.cache_data
def load_health_data():
    """Generate comprehensive health data"""
    dates = pd.date_range(start='2024-09-24', periods=30, freq='D')
    np.random.seed(42)
    
    data = {
        'date': dates,
        'sleep_hours': np.random.normal(7.5, 0.8, 30).clip(5.5, 9.5),
        'deep_sleep_pct': np.random.normal(18, 3, 30).clip(10, 25),
        'rem_sleep_pct': np.random.normal(22, 4, 30).clip(15, 30),
        'steps': np.random.normal(9500, 1500, 30).clip(4000, 15000).astype(int),
        'active_minutes': np.random.normal(45, 15, 30).clip(15, 90).astype(int),
        'rhr': np.random.normal(65, 5, 30).clip(55, 80).astype(int),
        'hrv': np.random.normal(35, 8, 30).clip(20, 55),
        'stress_score': np.random.normal(78, 12, 30).clip(40, 100).astype(int),
        'calories_burned': np.random.normal(2200, 300, 30).clip(1800, 3000).astype(int),
    }
    
    return pd.DataFrame(data)

def get_health_status(value, metric_type):
    """Determine health status"""
    if metric_type == 'sleep':
        if value >= 7.5: return 'Excellent', '#10b981'
        elif value >= 6.5: return 'Good', '#3b82f6'
        elif value >= 5.5: return 'Fair', '#f59e0b'
        else: return 'Poor', '#ef4444'
    elif metric_type == 'steps':
        if value >= 10000: return 'Excellent', '#10b981'
        elif value >= 7500: return 'Good', '#3b82f6'
        elif value >= 5000: return 'Fair', '#f59e0b'
        else: return 'Poor', '#ef4444'
    elif metric_type == 'rhr':
        if value <= 60: return 'Excellent', '#10b981'
        elif value <= 70: return 'Good', '#3b82f6'
        elif value <= 80: return 'Fair', '#f59e0b'
        else: return 'Poor', '#ef4444'
    elif metric_type == 'stress':
        if value >= 80: return 'Excellent', '#10b981'
        elif value >= 70: return 'Good', '#3b82f6'
        elif value >= 60: return 'Fair', '#f59e0b'
        else: return 'Poor', '#ef4444'

def generate_response(question, health_data):
    """Generate contextual responses"""
    question_lower = question.lower()
    
    avg_sleep = health_data['sleep_hours'].mean()
    avg_steps = health_data['steps'].mean()
    avg_rhr = health_data['rhr'].mean()
    avg_stress = health_data['stress_score'].mean()
    
    if 'energy' in question_lower or 'tired' in question_lower:
        return f"""🌟 **Energy Optimization Plan:**

Based on your {avg_sleep:.1f}h average sleep and {avg_steps:,.0f} daily steps:

• **Sleep**: Aim for 7-8 hours consistently
• **Morning Light**: Get sunlight within 1 hour of waking
• **Hydration**: Start with 16-20oz water upon waking
• **Movement**: Your step count is great! Add energy breaks every 2 hours

💡 **Quick Boosters**: Power naps (10-20 min), protein snacks, deep breathing"""

    elif 'sleep' in question_lower:
        status, _ = get_health_status(avg_sleep, 'sleep')
        return f"""😴 **Sleep Analysis:**

Your sleep quality is **{status.lower()}** with {avg_sleep:.1f}h average.

🎯 **Optimization Tips:**
• Keep bedroom 65-68°F (18-20°C)
• No screens 1 hour before bed
• Consistent bedtime ±30 minutes
• Dark, quiet environment

Your {avg_rhr:.0f} bpm RHR shows good recovery!"""

    elif 'exercise' in question_lower or 'activity' in question_lower:
        status, _ = get_health_status(avg_steps, 'steps')
        return f"""🏃 **Activity Analysis:**

Your activity level is **{status.lower()}** with {avg_steps:,.0f} daily steps.

🎯 **Recommendations:**
• Strength training: 2-3x per week
• Zone 2 cardio: 150 min/week moderate intensity
• Recovery: 1-2 rest days weekly
• Variety: Mix walking, cycling, swimming

Your cardiovascular fitness looks solid!"""

    else:
        return f"""📊 **Your Health Snapshot:**

• Sleep: {avg_sleep:.1f}h average
• Activity: {avg_steps:,.0f} daily steps  
• Heart: {avg_rhr:.0f} bpm resting HR
• Stress: {avg_stress:.0f}/100 management score

🎯 **I can help with:**
• Energy and fatigue management
• Sleep optimization
• Exercise planning
• Stress reduction
• Recovery strategies

What would you like to explore?"""

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 PHIA</h1>
        <p>Personal Health Insights Agent</p>
        <p style="font-size: 1rem; margin-top: 1rem;">
            AI-Powered Health Analytics • Real-time Insights • Personalized Recommendations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    health_data = load_health_data()
    st.session_state.health_data = health_data
    
    # Key metrics
    avg_sleep = health_data['sleep_hours'].mean()
    avg_steps = health_data['steps'].mean()
    avg_rhr = health_data['rhr'].mean()
    avg_stress = health_data['stress_score'].mean()
    
    # Metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status, color = get_health_status(avg_sleep, 'sleep')
        st.metric("😴 Sleep", f"{avg_sleep:.1f}h", f"{status}")
    
    with col2:
        status, color = get_health_status(avg_steps, 'steps')
        st.metric("🚶 Steps", f"{avg_steps:,.0f}", f"{status}")
    
    with col3:
        status, color = get_health_status(avg_rhr, 'rhr')
        st.metric("❤️ RHR", f"{avg_rhr:.0f} bpm", f"{status}")
    
    with col4:
        status, color = get_health_status(avg_stress, 'stress')
        st.metric("🧘 Stress", f"{avg_stress:.0f}/100", f"{status}")
    
    # Charts
    st.markdown("## 📊 Health Trends")
    
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "💤 Sleep", "🏃 Activity"])
    
    with tab1:
        # Overview chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Sleep Duration', 'Daily Steps', 'Resting HR', 'Stress Score')
        )
        
        fig.add_trace(go.Scatter(x=health_data['date'], y=health_data['sleep_hours'],
                                mode='lines+markers', name='Sleep', line=dict(color='#667eea')), row=1, col=1)
        fig.add_trace(go.Scatter(x=health_data['date'], y=health_data['steps'],
                                mode='lines+markers', name='Steps', line=dict(color='#10b981')), row=1, col=2)
        fig.add_trace(go.Scatter(x=health_data['date'], y=health_data['rhr'],
                                mode='lines+markers', name='RHR', line=dict(color='#ef4444')), row=2, col=1)
        fig.add_trace(go.Scatter(x=health_data['date'], y=health_data['stress_score'],
                                mode='lines+markers', name='Stress', line=dict(color='#f59e0b')), row=2, col=2)
        
        fig.update_layout(height=600, showlegend=False, title_text="30-Day Health Overview")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_sleep = px.line(health_data, x='date', y='sleep_hours',
                               title='Sleep Duration Trend')
            fig_sleep.add_hline(y=7, line_dash="dash", annotation_text="Recommended (7h)")
            st.plotly_chart(fig_sleep, use_container_width=True)
        
        with col2:
            # Fixed pie chart
            avg_deep = health_data['deep_sleep_pct'].mean()
            avg_rem = health_data['rem_sleep_pct'].mean()
            avg_light = max(0, 100 - avg_deep - avg_rem)  # Ensure positive
            
            # Create pie chart with proper data
            labels = ['Deep Sleep', 'REM Sleep', 'Light Sleep']
            values = [avg_deep, avg_rem, avg_light]
            colors = ['#667eea', '#764ba2', '#e2e8f0']
            
            fig_pie = px.pie(values=values, names=labels, title='Sleep Composition',
                            color_discrete_sequence=colors)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_steps = px.bar(health_data, x='date', y='steps', title='Daily Steps')
            fig_steps.add_hline(y=8000, line_dash="dash", annotation_text="Target (8000)")
            st.plotly_chart(fig_steps, use_container_width=True)
        
        with col2:
            fig_hrv = px.line(health_data, x='date', y='hrv', title='Heart Rate Variability')
            st.plotly_chart(fig_hrv, use_container_width=True)
    
    # Chat Interface
    st.markdown("## 💬 Ask PHIA")
    
    # Quick buttons
    col1, col2, col3, col4 = st.columns(4)
    questions = [
        "How can I boost my energy?",
        "Analyze my sleep quality",
        "Am I active enough?",
        "How's my recovery?"
    ]
    
    for i, (col, question) in enumerate(zip([col1, col2, col3, col4], questions)):
        with col:
            if st.button(question, key=f"q_{i}"):
                st.session_state.messages.append({"role": "user", "content": question})
    
    # Chat input
    user_input = st.text_input("Ask about your health:", placeholder="e.g., How can I sleep better?")
    
    if st.button("Send") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display messages
    if st.session_state.messages:
        st.markdown("### Conversation")
        
        for message in st.session_state.messages[-4:]:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Generate response
                response = generate_response(message["content"], health_data)
                st.session_state.messages.append({"role": "assistant", "content": response})
                
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🤖 PHIA:</strong> {response}
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

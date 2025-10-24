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
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    .main {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styles */
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
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    /* Metric Cards */
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
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #666;
        font-weight: 500;
    }
    
    .metric-trend {
        font-size: 0.9rem;
        margin-top: 0.5rem;
    }
    
    .trend-up { color: #10b981; }
    .trend-down { color: #ef4444; }
    .trend-stable { color: #6b7280; }
    
    /* Chat Interface */
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-top: 2rem;
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
    
    /* Sidebar Styles */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Button Styles */
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
    
    /* Quick Action Buttons */
    .quick-action {
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.5rem;
    }
    
    .quick-action:hover {
        border-color: #667eea;
        background: #f8fafc;
        transform: translateY(-2px);
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-excellent { background: #10b981; }
    .status-good { background: #3b82f6; }
    .status-fair { background: #f59e0b; }
    .status-poor { background: #ef4444; }
    
    /* Hide Streamlit branding */
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
    np.random.seed(42)  # For consistent data
    
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
        'water_intake': np.random.normal(2.2, 0.5, 30).clip(1.0, 4.0),
    }
    
    return pd.DataFrame(data)

def get_health_status(value, metric_type):
    """Determine health status based on value and metric type"""
    if metric_type == 'sleep':
        if value >= 7.5: return 'excellent', '😴 Excellent'
        elif value >= 6.5: return 'good', '😊 Good'
        elif value >= 5.5: return 'fair', '😐 Fair'
        else: return 'poor', '😴 Poor'
    elif metric_type == 'steps':
        if value >= 10000: return 'excellent', '🚶 Excellent'
        elif value >= 7500: return 'good', '👍 Good'
        elif value >= 5000: return 'fair', '😐 Fair'
        else: return 'poor', '📉 Low'
    elif metric_type == 'rhr':
        if value <= 60: return 'excellent', '❤️ Excellent'
        elif value <= 70: return 'good', '💚 Good'
        elif value <= 80: return 'fair', '💛 Fair'
        else: return 'poor', '❤️ High'
    elif metric_type == 'stress':
        if value >= 80: return 'excellent', '🧘 Excellent'
        elif value >= 70: return 'good', '😌 Good'
        elif value >= 60: return 'fair', '😐 Fair'
        else: return 'poor', '😰 High Stress'

def create_metric_card(title, value, unit, trend, status_class, icon):
    """Create a metric card with modern styling"""
    return f"""
    <div class="metric-card">
        <div class="metric-value">{icon} {value}{unit}</div>
        <div class="metric-label">{title}</div>
        <div class="metric-trend trend-{trend.lower()}">{trend}</div>
        <span class="status-indicator status-{status_class}"></span>
    </div>
    """

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
    
    # Load health data
    health_data = load_health_data()
    st.session_state.health_data = health_data
    
    # Calculate key metrics
    recent_data = health_data.tail(7)
    avg_sleep = health_data['sleep_hours'].mean()
    avg_steps = health_data['steps'].mean()
    avg_rhr = health_data['rhr'].mean()
    avg_stress = health_data['stress_score'].mean()
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        sleep_status, sleep_label = get_health_status(avg_sleep, 'sleep')
        st.markdown(create_metric_card(
            "Average Sleep", f"{avg_sleep:.1f}", "h", 
            "Stable", sleep_status, "😴"
        ), unsafe_allow_html=True)
    
    with col2:
        steps_status, steps_label = get_health_status(avg_steps, 'steps')
        st.markdown(create_metric_card(
            "Daily Steps", f"{avg_steps:,.0f}", "", 
            "Up", steps_status, "🚶"
        ), unsafe_allow_html=True)
    
    with col3:
        rhr_status, rhr_label = get_health_status(avg_rhr, 'rhr')
        st.markdown(create_metric_card(
            "Resting HR", f"{avg_rhr:.0f}", " bpm", 
            "Stable", rhr_status, "❤️"
        ), unsafe_allow_html=True)
    
    with col4:
        stress_status, stress_label = get_health_status(avg_stress, 'stress')
        st.markdown(create_metric_card(
            "Stress Score", f"{avg_stress:.0f}", "/100", 
            "Good", stress_status, "🧘"
        ), unsafe_allow_html=True)
    
    # Charts section
    st.markdown("## 📊 Health Trends")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "💤 Sleep Analysis", "🏃 Activity & Recovery"])
    
    with tab1:
        # Multi-metric overview chart
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Sleep Duration', 'Daily Steps', 'Resting Heart Rate', 'Stress Management'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Sleep
        fig.add_trace(
            go.Scatter(x=health_data['date'], y=health_data['sleep_hours'],
                      mode='lines+markers', name='Sleep Hours',
                      line=dict(color='#667eea', width=3)),
            row=1, col=1
        )
        
        # Steps
        fig.add_trace(
            go.Scatter(x=health_data['date'], y=health_data['steps'],
                      mode='lines+markers', name='Steps',
                      line=dict(color='#10b981', width=3)),
            row=1, col=2
        )
        
        # Heart Rate
        fig.add_trace(
            go.Scatter(x=health_data['date'], y=health_data['rhr'],
                      mode='lines+markers', name='RHR',
                      line=dict(color='#ef4444', width=3)),
            row=2, col=1
        )
        
        # Stress
        fig.add_trace(
            go.Scatter(x=health_data['date'], y=health_data['stress_score'],
                      mode='lines+markers', name='Stress Score',
                      line=dict(color='#f59e0b', width=3)),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=False, 
                         title_text="30-Day Health Overview",
                         title_x=0.5, title_font_size=20)
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Sleep duration trend
            fig_sleep = px.line(health_data, x='date', y='sleep_hours',
                               title='Sleep Duration Trend',
                               color_discrete_sequence=['#667eea'])
            fig_sleep.add_hline(y=7, line_dash="dash", line_color="green",
                               annotation_text="Recommended minimum (7h)")
            fig_sleep.update_layout(height=400)
            st.plotly_chart(fig_sleep, use_container_width=True)
        
        with col2:
            # Sleep quality breakdown
            avg_deep = health_data['deep_sleep_pct'].mean()
            avg_rem = health_data['rem_sleep_pct'].mean()
            avg_light = 100 - avg_deep - avg_rem
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=['Deep Sleep', 'REM Sleep', 'Light Sleep'],
                values=[avg_deep, avg_rem, avg_light],
                hole=.3,
                colors=['#667eea', '#764ba2', '#e2e8f0']
            )])
            fig_pie.update_layout(title_text="Average Sleep Composition", height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Activity correlation
            fig_corr = px.scatter(health_data, x='steps', y='stress_score',
                                 size='active_minutes', color='sleep_hours',
                                 title='Activity vs Stress Correlation',
                                 color_continuous_scale='viridis')
            fig_corr.update_layout(height=400)
            st.plotly_chart(fig_corr, use_container_width=True)
        
        with col2:
            # HRV trend
            fig_hrv = px.line(health_data, x='date', y='hrv',
                             title='Heart Rate Variability Trend',
                             color_discrete_sequence=['#10b981'])
            fig_hrv.update_layout(height=400)
            st.plotly_chart(fig_hrv, use_container_width=True)
    
    # AI Chat Interface
    st.markdown("## 💬 Ask PHIA Anything")
    
    # Quick action buttons
    st.markdown("### Quick Insights")
    col1, col2, col3, col4 = st.columns(4)
    
    quick_questions = [
        "How can I improve my energy levels?",
        "What's my sleep quality like?",
        "Am I getting enough exercise?",
        "How's my recovery trending?"
    ]
    
    for i, (col, question) in enumerate(zip([col1, col2, col3, col4], quick_questions)):
        with col:
            if st.button(question, key=f"quick_{i}"):
                st.session_state.messages.append({"role": "user", "content": question})
    
    # Chat input
    user_input = st.text_input("💭 Ask me anything about your health:", 
                              placeholder="e.g., How can I optimize my sleep schedule?")
    
    if st.button("Send Message") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display chat messages
    if st.session_state.messages:
        st.markdown("### Conversation")
        
        for message in st.session_state.messages[-6:]:  # Show last 6 messages
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Generate AI response
                with st.spinner("🤖 PHIA is analyzing your health data..."):
                    time.sleep(1)  # Simulate processing
                    
                    # Simple response logic based on keywords
                    response = generate_response(message["content"], health_data)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                    st.markdown(f"""
                    <div class="chat-message ai-message">
                        <strong>🤖 PHIA:</strong> {response}
                    </div>
                    """, unsafe_allow_html=True)

def generate_response(question, health_data):
    """Generate contextual responses based on health data"""
    question_lower = question.lower()
    
    avg_sleep = health_data['sleep_hours'].mean()
    avg_steps = health_data['steps'].mean()
    avg_rhr = health_data['rhr'].mean()
    avg_stress = health_data['stress_score'].mean()
    
    if 'energy' in question_lower or 'tired' in question_lower:
        return f"""Based on your data, you're averaging {avg_sleep:.1f} hours of sleep. Here are personalized recommendations:

🌟 **Energy Optimization Plan:**
• **Sleep Consistency**: Aim for 7-8 hours nightly (you're at {avg_sleep:.1f}h)
• **Morning Sunlight**: Get 10-15 minutes of natural light within 1 hour of waking
• **Hydration**: Start your day with 16-20oz of water
• **Movement**: Your {avg_steps:,.0f} daily steps are great! Add 5-minute energy breaks every 2 hours

💡 **Quick Energy Boosters:**
• Power nap (10-20 minutes) if needed
• Protein-rich snacks instead of sugar
• Deep breathing exercises (4-7-8 technique)"""

    elif 'sleep' in question_lower:
        sleep_quality = "excellent" if avg_sleep >= 7.5 else "good" if avg_sleep >= 6.5 else "needs improvement"
        return f"""Your sleep analysis shows {sleep_quality} patterns:

😴 **Sleep Insights:**
• Average duration: {avg_sleep:.1f} hours
• Sleep efficiency appears stable
• RHR during sleep: {avg_rhr:.0f} bpm (good recovery indicator)

🎯 **Sleep Optimization Tips:**
• **Temperature**: Keep bedroom 65-68°F (18-20°C)
• **Blue Light**: Avoid screens 1 hour before bed
• **Routine**: Consistent bedtime ±30 minutes
• **Environment**: Dark, quiet, cool room

📊 **Your sleep correlates well with your {avg_stress:.0f}/100 stress management score!**"""

    elif 'exercise' in question_lower or 'activity' in question_lower:
        activity_level = "excellent" if avg_steps >= 10000 else "good" if avg_steps >= 7500 else "moderate"
        return f"""Your activity level is {activity_level}:

🏃 **Activity Analysis:**
• Daily steps: {avg_steps:,.0f} (Target: 8,000-10,000)
• Activity consistency looks strong
• Recovery metrics are healthy

🎯 **Activity Recommendations:**
• **Strength Training**: 2-3x per week for muscle health
• **Zone 2 Cardio**: 150 minutes moderate intensity weekly
• **Recovery**: 1-2 rest days per week
• **Variety**: Mix walking, cycling, swimming

💪 **Based on your {avg_rhr:.0f} bpm RHR, your cardiovascular fitness is solid!**"""

    elif 'recovery' in question_lower or 'stress' in question_lower:
        stress_level = "excellent" if avg_stress >= 80 else "good" if avg_stress >= 70 else "needs attention"
        return f"""Your recovery and stress management is {stress_level}:

🧘 **Recovery Insights:**
• Stress score: {avg_stress:.0f}/100
• HRV trends show good autonomic balance
• Sleep-recovery correlation is positive

🌿 **Recovery Enhancement:**
• **Meditation**: 10-15 minutes daily
• **Breathwork**: Box breathing (4-4-4-4 pattern)
• **Nature**: 20+ minutes outdoors daily
• **Social**: Quality time with loved ones

⚡ **Your {avg_steps:,.0f} daily steps support excellent stress management!**"""

    else:
        return f"""I can help you optimize your health! Here's your current snapshot:

📊 **Your Health Overview:**
• Sleep: {avg_sleep:.1f}h average (Target: 7-8h)
• Activity: {avg_steps:,.0f} daily steps
• Heart Health: {avg_rhr:.0f} bpm resting HR
• Stress Management: {avg_stress:.0f}/100

🎯 **I can provide insights on:**
• Energy and fatigue management
• Sleep optimization strategies
• Exercise and activity planning
• Stress reduction techniques
• Recovery and wellness tips

What specific area would you like to explore?"""

if __name__ == "__main__":
    main()

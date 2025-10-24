import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="PHIA", page_icon="🏥", layout="centered")

# Minimal CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');
    
    .main { 
        font-family: 'Inter', sans-serif; 
        max-width: 800px;
        margin: 0 auto;
    }
    
    .header {
        text-align: center;
        padding: 3rem 0 2rem 0;
        border-bottom: 1px solid #f0f0f0;
        margin-bottom: 2rem;
    }
    
    .header h1 {
        font-size: 2.5rem;
        font-weight: 300;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    
    .header p {
        color: #7f8c8d;
        font-size: 1rem;
        font-weight: 300;
    }
    
    .metric-row {
        display: flex;
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .metric {
        flex: 1;
        text-align: center;
        padding: 1.5rem;
        background: #fafafa;
        border-radius: 8px;
        border: 1px solid #f0f0f0;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 500;
        color: #2c3e50;
        margin-bottom: 0.3rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        font-weight: 400;
    }
    
    .chat-input {
        margin: 2rem 0;
        padding: 1rem;
        background: #fafafa;
        border-radius: 8px;
        border: 1px solid #f0f0f0;
    }
    
    .chat-message {
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 8px;
        border-left: 3px solid #3498db;
        background: #f8f9fa;
    }
    
    .stButton > button {
        background: #3498db;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1.5rem;
        font-weight: 400;
        font-size: 0.9rem;
    }
    
    .stButton > button:hover {
        background: #2980b9;
    }
    
    .chart-container {
        margin: 2rem 0;
        padding: 1rem;
        background: #fafafa;
        border-radius: 8px;
        border: 1px solid #f0f0f0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize
if 'messages' not in st.session_state:
    st.session_state.messages = []

@st.cache_data
def get_health_data():
    dates = pd.date_range('2024-10-01', periods=7, freq='D')
    np.random.seed(42)
    return pd.DataFrame({
        'date': dates,
        'sleep': np.random.normal(7.5, 0.5, 7).clip(6, 9),
        'steps': np.random.normal(9000, 1000, 7).clip(5000, 12000).astype(int),
        'heart_rate': np.random.normal(65, 5, 7).clip(55, 75).astype(int),
        'stress': np.random.normal(75, 10, 7).clip(50, 100).astype(int)
    })

def get_response(question, data):
    q = question.lower()
    if 'sleep' in q:
        avg = data['sleep'].mean()
        return f"Your average sleep is {avg:.1f} hours. {'Great!' if avg >= 7 else 'Try to get 7-8 hours nightly.'}"
    elif 'steps' in q or 'activity' in q:
        avg = data['steps'].mean()
        return f"You average {avg:,.0f} steps daily. {'Excellent!' if avg >= 8000 else 'Aim for 8,000+ steps.'}"
    elif 'heart' in q:
        avg = data['heart_rate'].mean()
        return f"Your resting heart rate averages {avg:.0f} bpm. This indicates good fitness."
    elif 'stress' in q:
        avg = data['stress'].mean()
        return f"Your stress management score is {avg:.0f}/100. {'Well managed!' if avg >= 70 else 'Consider relaxation techniques.'}"
    else:
        return "I can help with sleep, activity, heart rate, and stress insights. What interests you?"

def main():
    # Header
    st.markdown("""
    <div class="header">
        <h1>🏥 PHIA</h1>
        <p>Personal Health Insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get data
    data = get_health_data()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Sleep", f"{data['sleep'].mean():.1f}h")
    with col2:
        st.metric("Steps", f"{data['steps'].mean():,.0f}")
    with col3:
        st.metric("Heart Rate", f"{data['heart_rate'].mean():.0f} bpm")
    with col4:
        st.metric("Stress Score", f"{data['stress'].mean():.0f}/100")
    
    # Simple chart
    st.markdown("### Weekly Trends")
    
    chart_type = st.selectbox("", ["Sleep", "Steps", "Heart Rate", "Stress"], label_visibility="collapsed")
    
    if chart_type == "Sleep":
        fig = px.line(data, x='date', y='sleep', title="Sleep Hours")
    elif chart_type == "Steps":
        fig = px.bar(data, x='date', y='steps', title="Daily Steps")
    elif chart_type == "Heart Rate":
        fig = px.line(data, x='date', y='heart_rate', title="Resting Heart Rate")
    else:
        fig = px.line(data, x='date', y='stress', title="Stress Management Score")
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    fig.update_traces(line_color='#3498db')
    st.plotly_chart(fig, use_container_width=True)
    
    # Chat
    st.markdown("### Ask PHIA")
    
    # Quick buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("How's my sleep?"):
            st.session_state.messages.append({"role": "user", "content": "How's my sleep?"})
    with col2:
        if st.button("Am I active enough?"):
            st.session_state.messages.append({"role": "user", "content": "Am I active enough?"})
    
    # Input
    user_input = st.text_input("", placeholder="Ask about your health...", label_visibility="collapsed")
    if st.button("Send") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Messages
    for msg in st.session_state.messages[-4:]:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
            response = get_response(msg["content"], data)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.markdown(f"""
            <div class="chat-message">
                <strong>PHIA:</strong> {response}
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

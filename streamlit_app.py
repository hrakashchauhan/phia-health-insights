import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Page config
st.set_page_config(
    page_title="PHIA - Personal Health Insights Agent",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background: #e3f2fd;
        margin-left: 20%;
    }
    .ai-message {
        background: #f5f5f5;
        margin-right: 20%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'health_data' not in st.session_state:
    st.session_state.health_data = None

# Load sample health data
@st.cache_data
def load_health_data():
    dates = pd.date_range(start='2024-10-01', periods=30, freq='D')
    data = {
        'date': dates,
        'sleep_hours': [7.5, 8.0, 6.5, 7.8, 8.2, 7.0, 7.5, 6.8, 8.1, 7.3,
                       7.9, 6.9, 8.0, 7.4, 7.7, 8.3, 6.6, 7.8, 7.2, 8.0,
                       7.6, 7.1, 8.2, 7.5, 6.9, 7.8, 8.1, 7.3, 7.7, 8.0],
        'steps': [8500, 10200, 6800, 9500, 11000, 7200, 8800, 9200, 10500, 8900,
                 9800, 7500, 10200, 8700, 9300, 11200, 6900, 9600, 8400, 10100,
                 9000, 8200, 10800, 9400, 7800, 9700, 10300, 8600, 9100, 10000],
        'rhr': [65, 63, 68, 64, 62, 67, 65, 66, 61, 64,
               63, 68, 62, 65, 64, 60, 69, 63, 66, 62,
               64, 67, 61, 65, 68, 63, 62, 66, 64, 63],
        'stress_score': [75, 82, 68, 78, 85, 70, 76, 80, 88, 72,
                        79, 71, 84, 77, 81, 89, 69, 83, 74, 86,
                        78, 73, 87, 80, 72, 82, 85, 76, 79, 84]
    }
    return pd.DataFrame(data)

# Initialize AI
def initialize_ai():
    api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        return True
    return False

# AI Response function
def get_ai_response(question, health_data):
    try:
        if initialize_ai():
            model = genai.GenerativeModel('gemini-pro')
            
            # Create context from health data
            avg_sleep = health_data['sleep_hours'].mean()
            avg_steps = health_data['steps'].mean()
            avg_rhr = health_data['rhr'].mean()
            avg_stress = health_data['stress_score'].mean()
            
            context = f"""
            You are PHIA, a Personal Health Insights Agent. Based on this user's health data:
            - Average sleep: {avg_sleep:.1f} hours
            - Average steps: {avg_steps:.0f} per day
            - Average resting heart rate: {avg_rhr:.0f} bpm
            - Average stress score: {avg_stress:.0f}/100
            
            Answer their question with personalized insights and recommendations.
            """
            
            response = model.generate_content(context + "\n\nQuestion: " + question)
            return response.text
        else:
            # Fallback responses
            if 'sleep' in question.lower():
                return f"Based on your data, you're averaging {health_data['sleep_hours'].mean():.1f} hours of sleep. For better energy, try maintaining consistent bedtimes and limiting screen time before bed."
            elif 'energy' in question.lower() or 'awake' in question.lower():
                return "To feel more energetic: 1) Maintain 7-8 hours of sleep, 2) Stay hydrated, 3) Take short walks during the day, 4) Eat balanced meals."
            elif 'steps' in question.lower():
                return f"You're averaging {int(health_data['steps'].mean())} steps daily. Great job! Try to maintain 8,000+ steps for optimal health."
            elif 'heart' in question.lower():
                return f"Your average resting heart rate is {int(health_data['rhr'].mean())} bpm, which indicates good cardiovascular fitness."
            else:
                return "I can help you with questions about sleep, energy, activity, heart rate, and stress management. What would you like to know?"
    except Exception as e:
        return f"I'm having trouble accessing the AI right now, but I can still help with basic health insights. Error: {str(e)}"

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 PHIA</h1>
        <h3>Personal Health Insights Agent</h3>
        <p>AI-Powered Health Analytics & Personalized Recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    health_data = load_health_data()
    st.session_state.health_data = health_data
    
    # Sidebar
    st.sidebar.title("📊 Health Overview")
    
    # Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("💤 Avg Sleep", f"{health_data['sleep_hours'].mean():.1f}h")
        st.metric("❤️ Avg RHR", f"{health_data['rhr'].mean():.0f} bpm")
    
    with col2:
        st.metric("🚶 Avg Steps", f"{health_data['steps'].mean():.0f}")
        st.metric("🧘 Avg Stress", f"{health_data['stress_score'].mean():.0f}/100")
    
    # Charts
    st.subheader("📈 Health Trends")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Sleep", "Activity", "Heart Rate", "Stress"])
    
    with tab1:
        fig = px.line(health_data, x='date', y='sleep_hours', title='Sleep Duration Over Time')
        fig.add_hline(y=7, line_dash="dash", line_color="green", annotation_text="Recommended minimum")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.bar(health_data, x='date', y='steps', title='Daily Steps')
        fig.add_hline(y=8000, line_dash="dash", line_color="orange", annotation_text="Recommended minimum")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        fig = px.line(health_data, x='date', y='rhr', title='Resting Heart Rate')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        fig = px.line(health_data, x='date', y='stress_score', title='Stress Management Score')
        st.plotly_chart(fig, use_container_width=True)
    
    # Chat Interface
    st.subheader("💬 Ask PHIA")
    
    # Sample questions
    st.write("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("How can I feel more energetic?"):
            st.session_state.messages.append({"role": "user", "content": "How can I feel more energetic?"})
    
    with col2:
        if st.button("What's my sleep pattern?"):
            st.session_state.messages.append({"role": "user", "content": "What's my sleep pattern?"})
    
    with col3:
        if st.button("How active am I?"):
            st.session_state.messages.append({"role": "user", "content": "How active am I?"})
    
    # Chat input
    user_question = st.text_input("Ask me anything about your health:", placeholder="e.g., How can I improve my sleep quality?")
    
    if st.button("Ask PHIA") and user_question:
        st.session_state.messages.append({"role": "user", "content": user_question})
    
    # Process messages
    if st.session_state.messages:
        latest_message = st.session_state.messages[-1]
        if latest_message["role"] == "user":
            with st.spinner("🤖 PHIA is analyzing your health data..."):
                ai_response = get_ai_response(latest_message["content"], health_data)
                st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # Display chat history
    if st.session_state.messages:
        st.subheader("💭 Conversation")
        for message in st.session_state.messages[-6:]:  # Show last 6 messages
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message ai-message">
                    <strong>🤖 PHIA:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**🏥 PHIA** - Personal Health Insights Agent | Powered by AI")

if __name__ == "__main__":
    main()

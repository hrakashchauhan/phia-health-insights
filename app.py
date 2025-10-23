#!/usr/bin/env python3
"""
PHIA Web Frontend - Production-Ready Flask Application
"""

from flask import Flask, render_template, request, jsonify
import os
import sys
import glob
from datetime import datetime
import google.generativeai as genai
import traceback

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import configuration
from config import GOOGLE_API_KEY, TAVILY_API_KEY
from onetwo import ot
from onetwo.backends import gemini_api
from data_utils import load_persona
from phia_agent import get_react_agent, QUESTION_PREFIX

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'phia_health_insights_2024_production')

# Global variables
agent = None
summary_df = None
activities_df = None
profile_df = None
initialization_status = {"status": "initializing", "message": "Starting PHIA..."}

def initialize_phia():
    """Initialize PHIA agent"""
    global agent, summary_df, activities_df, profile_df, initialization_status
    
    try:
        initialization_status = {"status": "initializing", "message": "Configuring AI backend..."}
        
        # Configure API
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Setup LLM Backend
        models = list(genai.list_models())
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        if not available_models:
            raise Exception("No compatible AI models available")
            
        model_name = available_models[0]
        
        llm_engine = gemini_api.GeminiAPI(
            generate_model_name=model_name,
            api_key=GOOGLE_API_KEY,
            temperature=0.0,
        )
        llm_engine.register()
        
        initialization_status = {"status": "initializing", "message": "Loading health data..."}
        
        # Load Data
        summary_path = os.path.join("synthetic_wearable_users", "summary_df_502.csv")
        activities_path = os.path.join("synthetic_wearable_users", "exercise_df_502.csv")
        
        summary_df, activities_df, profile_df = load_persona(
            summary_path=summary_path,
            activities_path=activities_path,
            enforce_schema=True,
            temporally_localize="today"
        )
        
        initialization_status = {"status": "initializing", "message": "Loading AI knowledge base..."}
        
        # Load Exemplars
        exemplar_paths = glob.glob(os.path.join("few_shots", "*.ipynb"))
        
        initialization_status = {"status": "initializing", "message": "Creating AI health agent..."}
        
        # Create Agent
        agent = get_react_agent(
            summary_df=summary_df,
            activities_df=activities_df,
            profile_df=profile_df,
            example_files=exemplar_paths,
            tavily_api_key=TAVILY_API_KEY,
            use_mock_search=len(TAVILY_API_KEY) == 0
        )
        
        initialization_status = {"status": "ready", "message": "PHIA AI Agent Ready"}
        return True
        
    except Exception as e:
        error_msg = f"Failed to initialize PHIA: {str(e)}"
        initialization_status = {"status": "error", "message": error_msg}
        print(f"❌ {error_msg}")
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(initialization_status)

@app.route('/api/health-summary')
def health_summary():
    if summary_df is None:
        return jsonify({'error': 'PHIA not initialized'})
    
    try:
        recent_data = summary_df.tail(7)
        
        summary = {
            'sleep_avg': round(summary_df['sleep_minutes'].mean() / 60, 1),
            'sleep_recent': round(recent_data['sleep_minutes'].mean() / 60, 1),
            'steps_avg': int(summary_df['steps'].mean()),
            'steps_recent': int(recent_data['steps'].mean()),
            'rhr_avg': int(summary_df['resting_heart_rate'].mean()),
            'rhr_recent': int(recent_data['resting_heart_rate'].mean()),
            'stress_avg': int(summary_df['stress_management_score'].mean()),
            'stress_recent': int(recent_data['stress_management_score'].mean()),
            'deep_sleep': round(summary_df['deep_sleep_percent'].mean(), 1),
            'rem_sleep': round(summary_df['rem_sleep_percent'].mean(), 1),
            'total_days': len(summary_df),
            'total_workouts': len(activities_df)
        }
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/ask', methods=['POST'])
def ask_question():
    if agent is None:
        return jsonify({'error': 'PHIA not initialized'})
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'})
        
        full_question = QUESTION_PREFIX + question
        final_answer, final_state = ot.run(
            agent(inputs=full_question, return_final_state=True)
        )
        
        return jsonify({
            'answer': str(final_answer),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/sample-questions')
def sample_questions():
    questions = [
        "How can I feel more awake and energetic during the day?",
        "What's affecting my sleep quality?",
        "How can I improve my running performance?",
        "What are my recent sleep patterns?",
        "How has my activity level been?",
        "What's my average resting heart rate?",
        "How can I reduce stress?",
        "What's the best time for me to work out?",
        "How does my exercise routine impact my recovery?",
        "What patterns do you see in my health data?"
    ]
    return jsonify(questions)

if __name__ == '__main__':
    print("🏥 PHIA - Personal Health Insights Agent")
    print("🚀 Starting web server...")
    
    # Initialize PHIA
    import threading
    init_thread = threading.Thread(target=initialize_phia)
    init_thread.start()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

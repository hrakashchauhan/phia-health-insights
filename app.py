#!/usr/bin/env python3
"""
PHIA - Minimal Flask App for Render Deployment
"""

from flask import Flask, render_template, request, jsonify
import os
import pandas as pd
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)

# Configuration
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')

# Global variables
health_data = None
initialization_status = {"status": "initializing", "message": "Starting PHIA..."}

def load_sample_data():
    """Load sample health data"""
    global health_data
    try:
        # Create sample data if CSV doesn't exist
        data = {
            'sleep_hours': [7.5, 8.0, 6.5, 7.8, 8.2, 7.0, 7.5],
            'steps': [8500, 10200, 6800, 9500, 11000, 7200, 8800],
            'rhr': [65, 63, 68, 64, 62, 67, 65],
            'stress_score': [75, 82, 68, 78, 85, 70, 76]
        }
        health_data = pd.DataFrame(data)
        return True
    except Exception as e:
        print(f"Error loading data: {e}")
        return False

def initialize_ai():
    """Initialize AI if API key is available"""
    global initialization_status
    try:
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
            initialization_status = {"status": "ready", "message": "PHIA AI Ready"}
            return True
        else:
            initialization_status = {"status": "demo", "message": "Demo Mode - Add API keys for AI"}
            return False
    except Exception as e:
        initialization_status = {"status": "error", "message": f"AI Error: {str(e)}"}
        return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(initialization_status)

@app.route('/api/health-summary')
def health_summary():
    if health_data is None:
        return jsonify({'error': 'No health data available'})
    
    try:
        summary = {
            'sleep_avg': round(health_data['sleep_hours'].mean(), 1),
            'sleep_recent': round(health_data['sleep_hours'].tail(3).mean(), 1),
            'steps_avg': int(health_data['steps'].mean()),
            'steps_recent': int(health_data['steps'].tail(3).mean()),
            'rhr_avg': int(health_data['rhr'].mean()),
            'rhr_recent': int(health_data['rhr'].tail(3).mean()),
            'stress_avg': int(health_data['stress_score'].mean()),
            'stress_recent': int(health_data['stress_score'].tail(3).mean()),
            'deep_sleep': 15.2,
            'rem_sleep': 18.5,
            'total_days': len(health_data),
            'total_workouts': 4
        }
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'No question provided'})
        
        # Simple responses based on keywords
        if 'sleep' in question.lower():
            answer = "Based on your data, you're averaging 7.5 hours of sleep. For better energy, try maintaining consistent bedtimes and limiting screen time before bed."
        elif 'energy' in question.lower() or 'awake' in question.lower():
            answer = "To feel more energetic: 1) Maintain 7-8 hours of sleep, 2) Stay hydrated, 3) Take short walks during the day, 4) Eat balanced meals with protein and complex carbs."
        elif 'steps' in question.lower() or 'activity' in question.lower():
            answer = f"You're averaging {int(health_data['steps'].mean())} steps daily. Great job! Try to maintain 8,000+ steps for optimal health benefits."
        elif 'heart' in question.lower():
            answer = f"Your average resting heart rate is {int(health_data['rhr'].mean())} bpm, which indicates good cardiovascular fitness."
        elif 'stress' in question.lower():
            answer = f"Your stress management score averages {int(health_data['stress_score'].mean())}/100. Consider meditation, deep breathing, or regular exercise to improve."
        else:
            answer = "I can help you with questions about sleep, energy, activity, heart rate, and stress management. What specific aspect would you like to explore?"
        
        return jsonify({
            'answer': answer,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/sample-questions')
def sample_questions():
    questions = [
        "How can I feel more awake and energetic?",
        "What's my sleep pattern like?",
        "How active am I?",
        "What's my heart rate status?",
        "How can I manage stress better?",
        "What are my health trends?"
    ]
    return jsonify(questions)

if __name__ == '__main__':
    print("🏥 PHIA - Starting...")
    
    # Initialize
    load_sample_data()
    initialize_ai()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

#!/usr/bin/env python3
"""
Run PHIA with API keys for full AI capabilities
"""

import os
import sys
import glob
import google.generativeai as genai

current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

from api_keys import GOOGLE_API_KEY, TAVILY_API_KEY
from onetwo import ot
from onetwo.backends import gemini_api
from data_utils import load_persona
from phia_agent import get_react_agent, QUESTION_PREFIX

def main():
    print("🏥 PHIA - Personal Health Insights Agent")
    print("🔑 Running with FULL AI CAPABILITIES!")
    print("=" * 60)
    
    try:
        # Configure API
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Check available models
        print("🔍 Checking available models...")
        models = list(genai.list_models())
        available_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        print(f"Available models: {available_models[:3]}...")  # Show first 3
        
        # Use first available model
        model_name = available_models[0] if available_models else "gemini-pro"
        print(f"Using model: {model_name}")
        
        # Setup LLM Backend
        print("🤖 Setting up AI backend...")
        llm_engine = gemini_api.GeminiAPI(
            generate_model_name=model_name,
            api_key=GOOGLE_API_KEY,
            temperature=0.0,
        )
        llm_engine.register()
        print("✓ AI backend ready")
        
        # Load Data
        print("📊 Loading health data...")
        summary_path = os.path.join("synthetic_wearable_users", "summary_df_502.csv")
        activities_path = os.path.join("synthetic_wearable_users", "exercise_df_502.csv")
        
        summary_df, activities_df, profile_df = load_persona(
            summary_path=summary_path,
            activities_path=activities_path,
            enforce_schema=True,
            temporally_localize="today"
        )
        print("✓ Health data loaded")
        
        # Load Exemplars
        exemplar_paths = glob.glob(os.path.join("few_shots", "*.ipynb"))
        print(f"✓ Loaded {len(exemplar_paths)} AI examples")
        
        # Create Agent
        print("🧠 Creating AI health agent...")
        agent = get_react_agent(
            summary_df=summary_df,
            activities_df=activities_df,
            profile_df=profile_df,
            example_files=exemplar_paths,
            tavily_api_key=TAVILY_API_KEY,
            use_mock_search=False  # Use real search
        )
        print("✓ AI agent ready!")
        
        # Ask AI Question
        question = "How can I feel more awake and energetic during the day?"
        print(f"\n💬 Question: {question}")
        print("🤖 AI is analyzing your health data...")
        print("-" * 60)
        
        full_question = QUESTION_PREFIX + question
        final_answer, final_state = ot.run(
            agent(inputs=full_question, return_final_state=True)
        )
        
        print("\n💡 AI Health Insights:")
        print("=" * 60)
        print(final_answer)
        print("=" * 60)
        print("🎉 PHIA AI Analysis Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Simple script to run PHIA with API keys.
Usage: python run_phia.py
"""

import os
import sys
import glob
from IPython.display import HTML, display
import pandas as pd
import google.generativeai as genai

# Add current directory to path
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

from onetwo import ot
from onetwo.backends import gemini_api
from data_utils import load_persona
from colab_utils import format_react_state_html
from phia_agent import get_react_agent, QUESTION_PREFIX

def main():
    print("PHIA - Personal Health Insights Agent")
    print("=" * 50)
    
    # Get API keys from user
    print("\nAPI Key Setup:")
    print("You need two API keys to run PHIA:")
    print("1. Google/Gemini API key from: https://aistudio.google.com")
    print("2. Tavily API key from: https://www.tavily.com/#pricing")
    print()
    
    google_api_key = input("Enter your Google/Gemini API key: ").strip()
    if not google_api_key:
        print("❌ Google API key is required!")
        return
    
    tavily_api_key = input("Enter your Tavily API key (or press Enter to use mock search): ").strip()
    use_mock_search = not bool(tavily_api_key)
    
    if use_mock_search:
        print("⚠️  Using mock search (no real web search)")
    
    print("\n" + "=" * 50)
    
    try:
        # Configure Google API
        genai.configure(api_key=google_api_key)
        
        # Setup LLM Backend
        print("Setting up LLM backend...")
        llm_engine = gemini_api.GeminiAPI(
            generate_model_name="models/gemini-1.5-pro",
            api_key=google_api_key,
            temperature=0.0,
        )
        llm_engine.register()
        print("✓ LLM Backend registered")
        
        # Load Data
        print("Loading user data...")
        summary_path = os.path.join("synthetic_wearable_users", "summary_df_502.csv")
        activities_path = os.path.join("synthetic_wearable_users", "exercise_df_502.csv")
        
        summary_df, activities_df, profile_df = load_persona(
            summary_path=summary_path,
            activities_path=activities_path,
            enforce_schema=True,
            temporally_localize="today"
        )
        print(f"✓ Data loaded - Summary: {summary_df.shape}, Activities: {activities_df.shape}")
        
        # Load Exemplars
        print("Loading exemplars...")
        exemplar_paths = glob.glob(os.path.join("few_shots", "*.ipynb"))
        print(f"✓ Found {len(exemplar_paths)} exemplar notebooks")
        
        # Create Agent
        print("Creating agent...")
        agent = get_react_agent(
            summary_df=summary_df,
            activities_df=activities_df,
            profile_df=profile_df,
            example_files=exemplar_paths,
            tavily_api_key=tavily_api_key,
            use_mock_search=use_mock_search
        )
        print("✓ Agent created successfully!")
        
        print("\n" + "=" * 50)
        print("PHIA is ready! You can now ask health-related questions.")
        print("Type 'quit' to exit.")
        print("=" * 50)
        
        # Interactive loop
        while True:
            print("\nExample questions:")
            print("- How can I feel more awake and energetic during the day?")
            print("- What's affecting my sleep quality?")
            print("- How can I improve my running performance?")
            print()
            
            question = input("Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            if not question:
                continue
            
            print(f"\n🤖 Processing: {question}")
            print("-" * 50)
            
            try:
                full_question = QUESTION_PREFIX + question
                final_answer, final_state = ot.run(
                    agent(inputs=full_question, return_final_state=True)
                )
                
                print("\n📋 Agent Reasoning:")
                # Print a simplified version of the trace
                if hasattr(final_state, 'trace') and final_state.trace:
                    for i, step in enumerate(final_state.trace[-3:], 1):  # Show last 3 steps
                        if hasattr(step, 'content'):
                            content = str(step.content)[:200] + "..." if len(str(step.content)) > 200 else str(step.content)
                            print(f"  Step {i}: {content}")
                
                print(f"\n💡 Final Answer:")
                print("-" * 30)
                if final_answer:
                    print(final_answer)
                else:
                    print("No answer was returned by the agent.")
                
            except Exception as e:
                print(f"❌ Error processing question: {e}")
                print("Please try a different question or check your API keys.")
    
    except Exception as e:
        print(f"❌ Setup error: {e}")
        print("Please check your API keys and try again.")

if __name__ == "__main__":
    main()

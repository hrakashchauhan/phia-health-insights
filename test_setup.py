#!/usr/bin/env python3
"""
Test script to verify PHIA setup is working correctly.
This script tests the basic functionality without requiring API keys.
"""

import os
import sys
import pandas as pd
import importlib

def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    
    try:
        # Test standard library imports
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        print("✓ Standard libraries imported successfully")
        
        # Test Google Generative AI
        import google.generativeai as genai
        print("✓ Google Generative AI imported successfully")
        
        # Test OneTwo framework
        from onetwo import ot
        from onetwo.backends import gemini_api
        print("✓ OneTwo framework imported successfully")
        
        # Test local modules
        import data_utils
        import colab_utils
        import prompt_templates
        import phia_agent
        print("✓ Local modules imported successfully")
        
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_data_loading():
    """Test if sample data can be loaded."""
    print("\nTesting data loading...")
    
    try:
        from data_utils import load_persona
        
        # Test with sample user data
        summary_path = os.path.join("synthetic_wearable_users", "summary_df_502.csv")
        activities_path = os.path.join("synthetic_wearable_users", "exercise_df_502.csv")
        
        if not os.path.exists(summary_path):
            print(f"✗ Summary file not found: {summary_path}")
            return False
            
        if not os.path.exists(activities_path):
            print(f"✗ Activities file not found: {activities_path}")
            return False
        
        summary_df, activities_df, profile_df = load_persona(
            summary_path=summary_path,
            activities_path=activities_path,
            enforce_schema=True,
            temporally_localize="today"
        )
        
        print(f"✓ Data loaded successfully:")
        print(f"  - Summary DF shape: {summary_df.shape}")
        print(f"  - Activities DF shape: {activities_df.shape}")
        print(f"  - Profile DF shape: {profile_df.shape}")
        
        return True
    except Exception as e:
        print(f"✗ Data loading error: {e}")
        return False

def test_exemplars():
    """Test if exemplar notebooks are available."""
    print("\nTesting exemplars...")
    
    try:
        import glob
        exemplar_dir = "few_shots"
        exemplar_pattern = os.path.join(exemplar_dir, "*.ipynb")
        exemplar_paths = glob.glob(exemplar_pattern)
        
        if not exemplar_paths:
            print(f"✗ No exemplar notebooks found in {exemplar_dir}/")
            return False
        
        print(f"✓ Found {len(exemplar_paths)} exemplar notebooks")
        return True
    except Exception as e:
        print(f"✗ Exemplar loading error: {e}")
        return False

def test_agent_creation_without_api():
    """Test agent creation without API keys (will fail gracefully)."""
    print("\nTesting agent creation (without API keys)...")
    
    try:
        from phia_agent import get_react_agent
        from data_utils import load_persona
        import glob
        
        # Load data
        summary_path = os.path.join("synthetic_wearable_users", "summary_df_502.csv")
        activities_path = os.path.join("synthetic_wearable_users", "exercise_df_502.csv")
        
        summary_df, activities_df, profile_df = load_persona(
            summary_path=summary_path,
            activities_path=activities_path,
            enforce_schema=True,
            temporally_localize="today"
        )
        
        exemplar_paths = glob.glob(os.path.join("few_shots", "*.ipynb"))
        
        # Try to create agent (will fail without API keys, but should not crash)
        try:
            agent = get_react_agent(
                summary_df=summary_df,
                activities_df=activities_df,
                profile_df=profile_df,
                example_files=exemplar_paths,
                tavily_api_key="",  # Empty API key
                use_mock_search=True  # Use mock search to avoid API calls
            )
            print("✓ Agent creation structure is valid (API keys needed for actual use)")
        except Exception as api_error:
            if "api" in str(api_error).lower() or "key" in str(api_error).lower():
                print("✓ Agent creation structure is valid (API keys needed for actual use)")
                print(f"  Expected API error: {api_error}")
            else:
                raise api_error
        
        return True
    except Exception as e:
        print(f"✗ Agent creation test error: {e}")
        return False

def main():
    """Run all tests."""
    print("PHIA Setup Test")
    print("=" * 50)
    
    # Change to project directory
    project_dir = "/home/hrakashchauhan/personal-health-insights-agent"
    os.chdir(project_dir)
    
    # Add current directory to Python path
    if project_dir not in sys.path:
        sys.path.append(project_dir)
    
    tests = [
        test_imports,
        test_data_loading,
        test_exemplars,
        test_agent_creation_without_api
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Setup is working correctly!")
        print("\nNext steps:")
        print("1. Get a Google/Gemini API key from: https://aistudio.google.com")
        print("2. Get a Tavily API key from: https://www.tavily.com/#pricing")
        print("3. Run the Jupyter notebook: jupyter notebook phia_demo.ipynb")
        print("4. Add your API keys to the notebook and run the cells")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()

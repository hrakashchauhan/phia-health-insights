#!/usr/bin/env python3
"""
Configuration loader for PHIA - supports both .env and api_keys.py
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to get API keys from environment variables first, then fallback to api_keys.py
try:
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY', '')
    
    # If not found in environment, try importing from api_keys.py (for local development)
    if not GOOGLE_API_KEY:
        try:
            from api_keys import GOOGLE_API_KEY, TAVILY_API_KEY
        except ImportError:
            GOOGLE_API_KEY = None
            TAVILY_API_KEY = ''
            
except Exception as e:
    print(f"Warning: Could not load API keys: {e}")
    GOOGLE_API_KEY = None
    TAVILY_API_KEY = ''

# Validate required keys
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is required. Set it in .env file or api_keys.py")

print("✅ Configuration loaded successfully")

#!/bin/bash

# PHIA Health Platform Deployment Script

echo "🏥 PHIA Health Platform - Production Deployment"
echo "=============================================="

# Check if running in production environment
if [ "$NODE_ENV" = "production" ]; then
    echo "✅ Production environment detected"
else
    echo "⚠️  Warning: Not in production environment"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check for required environment variables
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ Error: GOOGLE_API_KEY environment variable not set"
    echo "Please set your Google Gemini API key in Streamlit Cloud secrets"
    exit 1
fi

echo "✅ Environment variables configured"

# Initialize database
echo "🗄️  Initializing database..."
python -c "
import sqlite3
import os

# Create database if it doesn't exist
if not os.path.exists('phia_mvp.db'):
    conn = sqlite3.connect('phia_mvp.db')
    conn.close()
    print('Database created successfully')
else:
    print('Database already exists')
"

# Health check
echo "🔍 Running health checks..."
python -c "
import streamlit as st
import pandas as pd
import plotly.express as px
import google.generativeai as genai
import os

try:
    # Test Gemini API
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY', 'test'))
    print('✅ Gemini AI configured')
    
    # Test database
    import sqlite3
    conn = sqlite3.connect('phia_mvp.db')
    conn.close()
    print('✅ Database connection successful')
    
    print('✅ All health checks passed')
except Exception as e:
    print(f'❌ Health check failed: {e}')
    exit(1)
"

echo "🚀 Starting PHIA Health Platform..."
echo "Access the application at: https://phia-health-insights.streamlit.app"

# Start the application
streamlit run streamlit_app.py --server.port=${PORT:-8501} --server.address=0.0.0.0

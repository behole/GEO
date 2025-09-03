#!/bin/bash
# Setup script for clean GEO system environment

echo "🧹 Setting up clean GEO system environment..."

# Create virtual environment
python3 -m venv geo_venv

# Activate virtual environment
source geo_venv/bin/activate

echo "✅ Virtual environment created and activated"

# Upgrade pip
pip install --upgrade pip

echo "📦 Installing GEO system dependencies..."

# Install core requirements
pip install -r requirements-minimal.txt

echo "🔍 Testing installation..."

# Test imports
python -c "
try:
    import openai
    import anthropic
    import google.generativeai as genai
    import aiohttp
    import pandas as pd
    import numpy as np
    print('✅ All core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

# Check for conflicts
pip check

echo "🎯 Environment setup complete!"
echo "To activate: source geo_venv/bin/activate"
echo "To test: python run_geo_system.py --help"

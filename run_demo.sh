#!/bin/bash
# SMP-7: Beautiful Hello World Demo Runner
# Usage: ./run_demo.sh

echo "🌟 Starting Beautiful Hello World Demo (SMP-7)"
echo "📍 Project: Golf Swing 3D Analyzer"
echo "⏰ $(date)"
echo ""

# Check if streamlit is available
if ! python3 -c "import streamlit" 2>/dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "🚀 Launching Streamlit demo..."
echo "🌐 Demo will be available at: http://localhost:8501"
echo ""

# Run the beautiful hello world demo
python3 -m streamlit run demo_hello_world.py --server.port 8501

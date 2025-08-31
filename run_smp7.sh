#!/bin/bash

echo "🚀 Starting SMP-7 Hello World Demo..."
echo "📍 Project: Golf Swing 3D Analyzer"
echo "🎯 Feature: Beautiful Streamlit Hello World"
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

echo "🌟 Launching SMP-7 Demo..."
streamlit run smp7_hello_world.py --server.port 8502

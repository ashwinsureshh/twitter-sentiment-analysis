#!/bin/bash

# Quick Start Script - Runs all components in the background
# Use this for quick testing

echo "🚀 Starting Twitter Sentiment Analysis System..."
echo ""

# Kill any existing processes
echo "Cleaning up existing processes..."
lsof -ti:9999 | xargs kill -9 2>/dev/null
pkill -f "streamlit run dashboard.py" 2>/dev/null
pkill -f "python_processor.py" 2>/dev/null
sleep 1

# Clean data directory to start fresh
echo "Resetting data (starting from 0 tweets)..."
rm -rf data
mkdir -p data
mkdir -p logs

# Activate virtual environment
source venv/bin/activate

# Start tweet producer in background
echo "✅ Starting Tweet Producer..."
python3 tweet_producer.py > logs/producer.log 2>&1 &
PRODUCER_PID=$!
sleep 2

# Set JAVA_HOME to Java 17 for Spark
export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"

# Start spark processor in background
echo "✅ Starting Spark Processor (with Java 17)..."
python3 spark_processor.py > logs/spark_processor.log 2>&1 &
PROCESSOR_PID=$!
sleep 5

# Start streamlit dashboard
echo "✅ Starting Streamlit Dashboard..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 System is running!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboard: http://localhost:8501"
echo "🔵 Tweet Producer PID: $PRODUCER_PID"
echo "🟢 Python Processor PID: $PROCESSOR_PID"
echo ""
echo "To stop all processes, press Ctrl+C or run:"
echo "  ./start.sh (choose option 4)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

streamlit run dashboard.py

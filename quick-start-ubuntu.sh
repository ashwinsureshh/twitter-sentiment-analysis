#!/bin/bash

# Quick Start Script for Ubuntu/Linux
# Runs all components in the background

echo "🚀 Starting Twitter Sentiment Analysis System (Ubuntu/Linux)..."
echo ""

# Kill any existing processes
echo "Cleaning up existing processes..."
lsof -ti:9999 | xargs kill -9 2>/dev/null
pkill -f "streamlit run dashboard.py" 2>/dev/null
pkill -f "spark_processor.py" 2>/dev/null
sleep 1

# Clean data directory to start fresh
echo "Resetting data (starting from 0 tweets)..."
rm -rf data
mkdir -p data
mkdir -p logs

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements-working.txt"
    exit 1
fi

# Start tweet producer in background
echo "✅ Starting Tweet Producer..."
python3 tweet_producer.py > logs/producer.log 2>&1 &
PRODUCER_PID=$!
sleep 2

# Set JAVA_HOME for Ubuntu (Standard Path)
# Try to detect Java 17
if [ -d "/usr/lib/jvm/java-17-openjdk-amd64" ]; then
    export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
elif [ -d "/usr/lib/jvm/java-17-openjdk-arm64" ]; then
    export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-arm64"
elif [ -d "/usr/lib/jvm/default-java" ]; then
    export JAVA_HOME="/usr/lib/jvm/default-java"
else
    echo "⚠️  Warning: Could not auto-detect Java 17 path. Using system default."
fi

echo "Using JAVA_HOME: $JAVA_HOME"

# Start spark processor in background
echo "✅ Starting Spark Processor..."
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
echo "🟢 Spark Processor PID: $PROCESSOR_PID"
echo ""
echo "To stop all processes, press Ctrl+C"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

streamlit run dashboard.py

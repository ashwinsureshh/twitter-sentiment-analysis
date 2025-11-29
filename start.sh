#!/bin/bash

# Twitter Sentiment Analysis - Startup Script
# This script helps you run the different components

echo "🐦 Twitter Sentiment Analysis"
echo "=============================="
echo ""
echo "Choose an option:"
echo "1. Start Tweet Producer (run this first)"
echo "2. Start Spark Processor (run this second)"
echo "3. Start Streamlit Dashboard (run this third)"
echo "4. Kill all processes"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
  1)
    echo "Starting Tweet Producer..."
    source venv/bin/activate
    python3 tweet_producer.py
    ;;
  2)
    echo "Starting Spark Processor (with Java 17)..."
    export JAVA_HOME="/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
    source venv/bin/activate
    python3 spark_processor.py
    ;;
  3)
    echo "Starting Streamlit Dashboard..."
    source venv/bin/activate
    streamlit run dashboard.py
    ;;
  4)
    echo "Killing all processes..."
    lsof -ti:9999 | xargs kill -9 2>/dev/null
    pkill -f "streamlit run dashboard.py" 2>/dev/null
    pkill -f "python_processor.py" 2>/dev/null
    echo "All processes killed."
    ;;
  *)
    echo "Invalid choice. Please run again and select 1-4."
    ;;
esac

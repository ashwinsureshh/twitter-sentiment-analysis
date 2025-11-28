import socket
import json
import pandas as pd
from textblob import TextBlob
from datetime import datetime
import os
import time

# Configuration
HOST = 'localhost'
PORT = 9999
DATA_FILE = "c:/Users/Gaming PC/BDA Project/data/tweets.csv"

def get_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def process_stream():
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    
    # Initialize CSV if it doesn't exist
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=["text", "timestamp", "topic", "sentiment"]).to_csv(DATA_FILE, index=False)

    print(f"Connecting to {HOST}:{PORT}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, PORT))
        print("Connected! Listening for tweets...")
        
        buffer = ""
        while True:
            data = s.recv(1024).decode('utf-8')
            if not data:
                break
            
            buffer += data
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                if not line.strip():
                    continue
                
                try:
                    tweet = json.loads(line)
                    sentiment = get_sentiment(tweet['text'])
                    
                    # Create record
                    record = {
                        "text": tweet['text'],
                        "timestamp": tweet['timestamp'],
                        "topic": tweet['topic'],
                        "sentiment": sentiment
                    }
                    
                    # Append to CSV
                    df = pd.DataFrame([record])
                    df.to_csv(DATA_FILE, mode='a', header=False, index=False)
                    
                    print(f"Processed: {tweet['topic']} -> {sentiment}")
                    
                except json.JSONDecodeError:
                    continue
                    
    except ConnectionRefusedError:
        print("Connection refused. Make sure tweet_producer.py is running!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        s.close()

if __name__ == "__main__":
    process_stream()

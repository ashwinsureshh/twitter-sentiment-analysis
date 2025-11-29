import socket
import time
import json
import pandas as pd
import os
import random
from datetime import datetime

HOST = 'localhost'
PORT = 9999
DATA_FILE = "dataset/source_tweets.csv"
SPEED_FACTOR = 0.5

def load_dataset():
    if not os.path.exists(DATA_FILE):
        print(f"❌ Error: {DATA_FILE} not found!")
        return None
    
    print(f"Loading dataset from {DATA_FILE}...")
    try:
        df = pd.read_csv(DATA_FILE, encoding='latin-1', header=None)
        if isinstance(df.iloc[0,0], str) and "target" in str(df.iloc[0,0]):
             df = pd.read_csv(DATA_FILE)
        else:
             df.columns = ["target", "ids", "date", "flag", "user", "text"]
             
        return df
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return None

def start_server():
    df = load_dataset()
    if df is None:
        return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((HOST, PORT))
    except OSError:
        print(f"❌ Port {PORT} is already in use. Killing old process...")
        os.system(f"lsof -ti:{PORT} | xargs kill -9")
        time.sleep(5)
        s.bind((HOST, PORT))
        
    s.listen(1)
    print(f"Listening on {HOST}:{PORT}...")
    print(f"Streaming {len(df)} tweets from file...")
    
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    
    try:
        while True:
            for index, row in df.iterrows():
                text = str(row['text'])
                
                if 'topic' in row:
                    topic = row['topic']
                else:
                    words = text.split()
                    topic = next((w for w in words if w[0].isupper() and len(w) > 3), "General")

                tweet = {
                    "text": text,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "topic": topic
                }
                
                message = json.dumps(tweet) + "\n"
                try:
                    conn.sendall(message.encode('utf-8'))
                    print(f"Sent: {text[:50]}...")
                    time.sleep(SPEED_FACTOR)
                except (BrokenPipeError, ConnectionResetError):
                    print("Client disconnected. Waiting for new connection...")
                    conn.close()
                    conn, addr = s.accept()
                    print(f"Reconnected by {addr}")
                    
            print("Reached end of dataset. Restarting loop...")
            
    except KeyboardInterrupt:
        print("\nStopping server...")
    finally:
        conn.close()
        s.close()

if __name__ == "__main__":
    start_server()

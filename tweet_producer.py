import socket
import time
import json
import random
from datetime import datetime

# Mock data for simulation
TOPICS = ["Apple", "Google", "Microsoft", "Amazon", "Tesla", "Bitcoin", "AI", "Python"]
POSITIVE_WORDS = ["great", "awesome", "good", "amazing", "love", "fantastic", "happy", "excellent"]
NEGATIVE_WORDS = ["bad", "terrible", "hate", "awful", "worst", "poor", "sad", "disappointing"]
NEUTRAL_WORDS = ["is", "the", "are", "was", "has", "will", "today", "yesterday"]

def generate_tweet():
    topic = random.choice(TOPICS)
    sentiment = random.choice(["positive", "negative", "neutral"])
    
    if sentiment == "positive":
        text = f"{topic} is {random.choice(POSITIVE_WORDS)} and {random.choice(POSITIVE_WORDS)}!"
    elif sentiment == "negative":
        text = f"{topic} is {random.choice(NEGATIVE_WORDS)} and {random.choice(NEGATIVE_WORDS)}."
    else:
        text = f"{topic} {random.choice(NEUTRAL_WORDS)} released a new update."
        
    return {
        "text": text,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "topic": topic
    }

def start_server(host='localhost', port=9999):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    print(f"Listening on {host}:{port}...")
    
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    
    try:
        while True:
            tweet = generate_tweet()
            message = json.dumps(tweet) + "\n"  # Newline delimiter for Spark
            conn.sendall(message.encode('utf-8'))
            print(f"Sent: {message.strip()}")
            time.sleep(1) # Send one tweet every second
    except (BrokenPipeError, ConnectionResetError):
        print("Client disconnected.")
    finally:
        conn.close()
        s.close()

if __name__ == "__main__":
    start_server()

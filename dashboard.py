import streamlit as st
import pandas as pd
import time
import os
import glob

st.set_page_config(page_title="Real-Time Twitter Sentiment", layout="wide")

st.title("🐦 Real-Time Twitter Sentiment Analysis")

DATA_DIR = "data"

def load_data():
    csv_path = os.path.join(DATA_DIR, "tweets.csv")
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=["text", "timestamp", "topic", "sentiment"])
    
    try:
        df = pd.read_csv(csv_path)
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["text", "timestamp", "topic", "sentiment"])

placeholder = st.empty()

while True:
    df = load_data()
    
    with placeholder.container():
        total_tweets = len(df)
        positive_count = len(df[df['sentiment'] == 'Positive'])
        negative_count = len(df[df['sentiment'] == 'Negative'])
        neutral_count = len(df[df['sentiment'] == 'Neutral'])
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric(label="Total Tweets", value=total_tweets)
        kpi2.metric(label="Positive", value=positive_count)
        kpi3.metric(label="Negative", value=negative_count)
        kpi4.metric(label="Neutral", value=neutral_count)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Sentiment Distribution")
            if not df.empty:
                sentiment_counts = df['sentiment'].value_counts()
                st.bar_chart(sentiment_counts)
            else:
                st.write("Waiting for data...")

        with col2:
            st.subheader("Recent Tweets")
            if not df.empty:
                st.dataframe(df.tail(10)[['topic', 'sentiment', 'text']])
            else:
                st.write("Waiting for data...")

    time.sleep(2)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import time
import os
from io import BytesIO

st.set_page_config(
    page_title="Twitter Sentiment Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    h1 {
        color: #ffffff;
        font-weight: 700;
        padding-bottom: 20px;
        border-bottom: 3px solid #4CAF50;
    }
    h3 {
        color: #ffffff;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Real-Time Twitter Sentiment Analysis")
st.markdown("### Live streaming sentiment analysis powered by Apache Spark")

DATA_DIR = "data"

def load_data():
    csv_path = os.path.join(DATA_DIR, "tweets.csv")
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=["text", "timestamp", "topic", "sentiment"])
    
    try:
        df = pd.read_csv(csv_path)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=["text", "timestamp", "topic", "sentiment"])

with st.sidebar:
    st.header("⚙️ Controls")
    
    sentiment_filter = st.multiselect(
        "Filter by Sentiment",
        options=["Positive", "Negative", "Neutral"],
        default=["Positive", "Negative", "Neutral"]
    )
    
    st.markdown("---")
    
    auto_refresh = st.checkbox("Auto Refresh", value=True)
    refresh_interval = st.slider("Refresh Interval (seconds)", 1, 10, 2)
    
    st.markdown("---")
    
    if st.button("🔄 Refresh Now"):
        st.rerun()

placeholder = st.empty()

while True:
    df = load_data()
    
    if not df.empty and sentiment_filter:
        df_filtered = df[df['sentiment'].isin(sentiment_filter)]
    else:
        df_filtered = df
    
    with placeholder.container():
        total_tweets = len(df_filtered)
        positive_count = len(df_filtered[df_filtered['sentiment'] == 'Positive'])
        negative_count = len(df_filtered[df_filtered['sentiment'] == 'Negative'])
        neutral_count = len(df_filtered[df_filtered['sentiment'] == 'Neutral'])
        
        positive_pct = (positive_count / total_tweets * 100) if total_tweets > 0 else 0
        negative_pct = (negative_count / total_tweets * 100) if total_tweets > 0 else 0
        neutral_pct = (neutral_count / total_tweets * 100) if total_tweets > 0 else 0
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric(
            label="📈 Total Tweets",
            value=f"{total_tweets:,}"
        )
        col2.metric(
            label="😊 Positive",
            value=f"{positive_count:,}",
            delta=f"{positive_pct:.1f}%"
        )
        col3.metric(
            label="😞 Negative",
            value=f"{negative_count:,}",
            delta=f"{negative_pct:.1f}%",
            delta_color="inverse"
        )
        col4.metric(
            label="😐 Neutral",
            value=f"{neutral_count:,}",
            delta=f"{neutral_pct:.1f}%"
        )
        
        if not df_filtered.empty:
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            col5.download_button(
                label="📥 Export CSV",
                data=csv,
                file_name=f"sentiment_data_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "☁️ Word Clouds", "📈 Trends", "🔥 Topics"])
        
        with tab1:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📊 Sentiment Distribution")
                if not df_filtered.empty:
                    sentiment_counts = df_filtered['sentiment'].value_counts()
                    
                    colors = {
                        'Positive': '#4CAF50',
                        'Negative': '#f44336',
                        'Neutral': '#FFC107'
                    }
                    
                    fig = go.Figure(data=[go.Pie(
                        labels=sentiment_counts.index,
                        values=sentiment_counts.values,
                        hole=0.4,
                        marker=dict(colors=[colors.get(x, '#888888') for x in sentiment_counts.index]),
                        textinfo='label+percent',
                        textfont_size=14
                    )])
                    
                    fig.update_layout(
                        showlegend=True,
                        height=400,
                        margin=dict(t=0, b=0, l=0, r=0),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("⏳ Waiting for data stream...")

            with col2:
                st.subheader("💬 Recent Tweets")
                if not df_filtered.empty:
                    recent_df = df_filtered.tail(10)[['sentiment', 'topic', 'text']].copy()
                    
                    def color_sentiment(val):
                        if val == 'Positive':
                            return 'background-color: #1b5e20; color: white'
                        elif val == 'Negative':
                            return 'background-color: #b71c1c; color: white'
                        else:
                            return 'background-color: #f57f17; color: white'
                    
                    styled_df = recent_df.style.applymap(color_sentiment, subset=['sentiment'])
                    st.dataframe(styled_df, use_container_width=True, height=400)
                else:
                    st.info("⏳ Waiting for tweets...")
        
        with tab2:
            st.subheader("☁️ Word Clouds by Sentiment")
            
            if not df_filtered.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 😊 Positive Words")
                    positive_text = ' '.join(df_filtered[df_filtered['sentiment'] == 'Positive']['text'].astype(str))
                    if positive_text.strip():
                        wordcloud = WordCloud(width=400, height=300, background_color='#1e2130', 
                                            colormap='Greens').generate(positive_text)
                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        fig.patch.set_facecolor('#0e1117')
                        st.pyplot(fig)
                        plt.close()
                    else:
                        st.info("No positive tweets yet")
                
                with col2:
                    st.markdown("### 😞 Negative Words")
                    negative_text = ' '.join(df_filtered[df_filtered['sentiment'] == 'Negative']['text'].astype(str))
                    if negative_text.strip():
                        wordcloud = WordCloud(width=400, height=300, background_color='#1e2130',
                                            colormap='Reds').generate(negative_text)
                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.imshow(wordcloud, interpolation='bilinear')
                        ax.axis('off')
                        fig.patch.set_facecolor('#0e1117')
                        st.pyplot(fig)
                        plt.close()
                    else:
                        st.info("No negative tweets yet")
            else:
                st.info("⏳ Waiting for data to generate word clouds...")
        
        with tab3:
            st.subheader("📈 Sentiment Over Time")
            
            if not df_filtered.empty and 'timestamp' in df_filtered.columns:
                df_time = df_filtered.copy()
                df_time['minute'] = df_time['timestamp'].dt.floor('T')
                time_sentiment = df_time.groupby(['minute', 'sentiment']).size().reset_index(name='count')
                
                fig = px.line(
                    time_sentiment,
                    x='minute',
                    y='count',
                    color='sentiment',
                    color_discrete_map={
                        'Positive': '#4CAF50',
                        'Negative': '#f44336',
                        'Neutral': '#FFC107'
                    },
                    labels={'minute': 'Time', 'count': 'Tweet Count'}
                )
                
                fig.update_layout(
                    height=400,
                    margin=dict(t=0, b=0, l=0, r=0),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white'),
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#333333')
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⏳ Waiting for time-series data...")
        
        with tab4:
            st.subheader("🔥 Top Topics")
            
            if not df_filtered.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    topic_counts = df_filtered['topic'].value_counts().head(10)
                    
                    fig = go.Figure(data=[go.Bar(
                        x=topic_counts.values,
                        y=topic_counts.index,
                        orientation='h',
                        marker=dict(color='#4CAF50')
                    )])
                    
                    fig.update_layout(
                        title="Most Discussed Topics",
                        height=400,
                        margin=dict(t=40, b=0, l=0, r=0),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(showgrid=True, gridcolor='#333333'),
                        yaxis=dict(showgrid=False)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("### Topic Sentiment Breakdown")
                    topic_sentiment = df_filtered.groupby(['topic', 'sentiment']).size().reset_index(name='count')
                    top_topics = df_filtered['topic'].value_counts().head(5).index
                    topic_sentiment_filtered = topic_sentiment[topic_sentiment['topic'].isin(top_topics)]
                    
                    fig = px.bar(
                        topic_sentiment_filtered,
                        x='topic',
                        y='count',
                        color='sentiment',
                        color_discrete_map={
                            'Positive': '#4CAF50',
                            'Negative': '#f44336',
                            'Neutral': '#FFC107'
                        },
                        barmode='stack'
                    )
                    
                    fig.update_layout(
                        height=400,
                        margin=dict(t=0, b=0, l=0, r=0),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='white'),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='#333333')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("⏳ Waiting for topic data...")

    if not auto_refresh:
        break
    
    time.sleep(refresh_interval)

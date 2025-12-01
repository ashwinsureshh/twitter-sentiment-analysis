import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
import os

st.set_page_config(
    page_title="Twitter Sentiment Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        
        positive_pct = (positive_count / total_tweets * 100) if total_tweets > 0 else 0
        negative_pct = (negative_count / total_tweets * 100) if total_tweets > 0 else 0
        neutral_pct = (neutral_count / total_tweets * 100) if total_tweets > 0 else 0
        
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        kpi1.metric(
            label="📈 Total Tweets Analyzed",
            value=f"{total_tweets:,}",
            delta=f"{total_tweets} processed"
        )
        kpi2.metric(
            label="😊 Positive",
            value=f"{positive_count:,}",
            delta=f"{positive_pct:.1f}%"
        )
        kpi3.metric(
            label="😞 Negative",
            value=f"{negative_count:,}",
            delta=f"{negative_pct:.1f}%",
            delta_color="inverse"
        )
        kpi4.metric(
            label="😐 Neutral",
            value=f"{neutral_count:,}",
            delta=f"{neutral_pct:.1f}%"
        )
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📊 Sentiment Distribution")
            if not df.empty:
                sentiment_counts = df['sentiment'].value_counts()
                
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
            st.subheader("🔥 Sentiment Trend")
            if not df.empty and len(df) > 1:
                df_trend = df.copy()
                df_trend['batch'] = range(len(df_trend))
                df_trend = df_trend.groupby(['batch', 'sentiment']).size().reset_index(name='count')
                
                fig = px.line(
                    df_trend,
                    x='batch',
                    y='count',
                    color='sentiment',
                    color_discrete_map={
                        'Positive': '#4CAF50',
                        'Negative': '#f44336',
                        'Neutral': '#FFC107'
                    }
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
                st.info("⏳ Waiting for trend data...")
        
        st.markdown("---")
        st.subheader("💬 Recent Tweets")
        
        if not df.empty:
            recent_df = df.tail(10)[['sentiment', 'topic', 'text']].copy()
            
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

    time.sleep(2)

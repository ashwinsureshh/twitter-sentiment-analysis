# Twitter Sentiment Analysis

Real-time Twitter sentiment analysis using Python and Streamlit.

## Setup

1. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

2. **Install dependencies (if not already installed):**
   ```bash
   pip install pandas textblob streamlit
   ```

## Running the Application

### Option 1: Quick Start (Recommended)
Run everything with a single command:

```bash
./quick-start.sh
```

This will automatically start all three components and open the dashboard in your browser.

### Option 2: Manual (3 Separate Terminals)


You need to run **two separate terminals** in the correct order:

### Terminal 1: Start the Tweet Producer
This simulates a stream of tweets on port 9999.

```bash
source venv/bin/activate
python3 tweet_producer.py
```

You should see: `Server listening on localhost:9999`

### Terminal 2: Start the Python Processor
This connects to the tweet stream and performs sentiment analysis.

```bash
source venv/bin/activate
python3 python_processor.py
```

You should see: `Connected! Listening for tweets...` and sentiment analysis results.

### Terminal 3: Start the Dashboard
This displays the real-time sentiment analysis dashboard.

```bash
source venv/bin/activate
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

## Project Structure

- `tweet_producer.py` - Simulates a Twitter stream by sending mock tweets via socket
- `python_processor.py` - Processes tweets and performs sentiment analysis using TextBlob
- `dashboard.py` - Streamlit dashboard for visualizing sentiment analysis results
- `data/tweets.csv` - Stores processed tweets with sentiment scores
- `spark_processor.py` - Alternative Spark-based processor (requires PySpark setup)

## Notes

- Make sure to start the tweet producer **first** before starting the processor
- The dashboard updates every 2 seconds automatically
- All data is stored in the `data/` directory

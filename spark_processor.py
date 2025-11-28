from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from textblob import TextBlob
import os
import shutil

# Define schema for incoming data
schema = StructType([
    StructField("text", StringType(), True),
    StructField("timestamp", StringType(), True),
    StructField("topic", StringType(), True)
])

def get_sentiment(text):
    analysis = TextBlob(text)
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"

# Register UDF
sentiment_udf = udf(get_sentiment, StringType())

def process_stream():
    spark = SparkSession.builder \
        .appName("TwitterSentimentAnalysis") \
        .getOrCreate()

    # Explicitly set hadoop.home.dir to help winutils find the binaries
    spark.sparkContext._jsc.hadoopConfiguration().set("hadoop.home.dir", "c:/Users/Gaming PC/BDA Project/hadoop")

    spark.sparkContext.setLogLevel("ERROR")

    # Read from socket
    lines = spark.readStream \
        .format("socket") \
        .option("host", "localhost") \
        .option("port", 9999) \
        .load()

    # Parse JSON
    tweets = lines.select(from_json(col("value"), schema).alias("data")).select("data.*")

    # Apply sentiment analysis
    tweets_with_sentiment = tweets.withColumn("sentiment", sentiment_udf(col("text")))

    # Define a function to write each batch to CSV using Pandas
    # This bypasses Hadoop's NativeIO issues on Windows
    def write_to_csv(batch_df, batch_id):
        pdf = batch_df.toPandas()
        if not pdf.empty:
            # Append to a single CSV file
            mode = 'a' if os.path.exists("c:/Users/Gaming PC/BDA Project/data/tweets.csv") else 'w'
            header = False if mode == 'a' else True
            pdf.to_csv("c:/Users/Gaming PC/BDA Project/data/tweets.csv", mode=mode, header=header, index=False)

    # Ensure data directory exists
    if not os.path.exists("c:/Users/Gaming PC/BDA Project/data"):
        os.makedirs("c:/Users/Gaming PC/BDA Project/data")

    # Write stream using foreachBatch
    # Note: We removed checkpointLocation to avoid HDFS metadata operations that fail on Windows
    query = tweets_with_sentiment.writeStream \
        .outputMode("append") \
        .foreachBatch(write_to_csv) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    # Clean up previous run data
    if os.path.exists("c:/Users/Gaming PC/BDA Project/data"):
        shutil.rmtree("c:/Users/Gaming PC/BDA Project/data")
    if os.path.exists("c:/Users/Gaming PC/BDA Project/checkpoint"):
        shutil.rmtree("c:/Users/Gaming PC/BDA Project/checkpoint")
        
    process_stream()

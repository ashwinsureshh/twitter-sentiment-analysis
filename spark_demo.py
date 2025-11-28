"""
PySpark Demonstration Script
This demonstrates PySpark concepts for the sentiment analysis project.
Note: This is a simplified demo that processes a static dataset rather than streaming,
to avoid Windows-specific Hadoop compatibility issues.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col
from pyspark.sql.types import StringType, StructType, StructField
from textblob import TextBlob

def analyze_sentiment(text):
    """Analyze sentiment using TextBlob"""
    analysis = TextBlob(str(text))
    if analysis.sentiment.polarity > 0:
        return "Positive"
    elif analysis.sentiment.polarity < 0:
        return "Negative"
    else:
        return "Neutral"

def demo_batch_processing():
    """Demonstrate PySpark batch processing for sentiment analysis"""
    
    # Create Spark session
    spark = SparkSession.builder \
        .appName("SentimentAnalysisDemo") \
        .master("local[*]") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")
    
    # Create sample data
    sample_data = [
        ("I love this product! It's amazing!", "Product Review"),
        ("This is terrible, worst experience ever", "Product Review"),
        ("It's okay, nothing special", "Product Review"),
        ("Absolutely fantastic! Highly recommend", "Product Review"),
        ("Not good at all, very disappointed", "Product Review")
    ]
    
    # Define schema
    schema = StructType([
        StructField("text", StringType(), True),
        StructField("category", StringType(), True)
    ])
    
    # Create DataFrame
    df = spark.createDataFrame(sample_data, schema)
    
    print("\n=== Original Data ===")
    df.show(truncate=False)
    
    # Register UDF for sentiment analysis
    sentiment_udf = udf(analyze_sentiment, StringType())
    
    # Apply sentiment analysis
    df_with_sentiment = df.withColumn("sentiment", sentiment_udf(col("text")))
    
    print("\n=== Data with Sentiment Analysis ===")
    df_with_sentiment.show(truncate=False)
    
    # Aggregate results
    print("\n=== Sentiment Distribution ===")
    df_with_sentiment.groupBy("sentiment").count().show()
    
    spark.stop()
    print("\nDemo completed successfully!")

if __name__ == "__main__":
    print("PySpark Sentiment Analysis Demonstration")
    print("=" * 50)
    demo_batch_processing()

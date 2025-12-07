from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, udf, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from textblob import TextBlob
import os
import shutil

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

sentiment_udf = udf(get_sentiment, StringType())

def process_stream():
    os.environ["HADOOP_USER_NAME"] = "unknown"

    spark = SparkSession.builder \
        .appName("TwitterSentimentAnalysis") \
        .master("local[*]") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")
    
    sc = spark.sparkContext

    lines = spark.readStream \
        .format("socket") \
        .option("host", "localhost") \
        .option("port", 9999) \
        .load()

    tweets = lines.select(from_json(col("value"), schema).alias("data")).select("data.*")

    tweets_with_sentiment = tweets.withColumn("sentiment", sentiment_udf(col("text")))

    def write_to_csv(batch_df, batch_id):
        if not batch_df.isEmpty():
            rdd = batch_df.rdd
            
            processed_rdd = rdd.map(lambda row: (
                row['text'],
                row['timestamp'],
                row['topic'],
                row['sentiment']
            ))
            
            header_rdd = sc.parallelize([("text", "timestamp", "topic", "sentiment")])
            
            if not os.path.exists("data/tweets.csv"):
                combined_rdd = header_rdd.union(processed_rdd)
                combined_rdd.coalesce(1).saveAsTextFile("data/temp_output")
                
                temp_file = None
                for file in os.listdir("data/temp_output"):
                    if file.startswith("part-"):
                        temp_file = os.path.join("data/temp_output", file)
                        break
                
                if temp_file:
                    with open(temp_file, 'r') as f:
                        content = f.read()
                    
                    formatted_content = content.replace("('", "").replace("')", "").replace("', '", ",")
                    
                    with open("data/tweets.csv", 'w') as f:
                        f.write(formatted_content)
                    
                    shutil.rmtree("data/temp_output")
            else:
                pdf = batch_df.toPandas()
                pdf.to_csv("data/tweets.csv", mode='a', header=False, index=False)

    if not os.path.exists("data"):
        os.makedirs("data")

    query = tweets_with_sentiment.writeStream \
        .outputMode("append") \
        .foreachBatch(write_to_csv) \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    if os.path.exists("data"):
        shutil.rmtree("data")
    if os.path.exists("checkpoint"):
        shutil.rmtree("checkpoint")
        
    process_stream()

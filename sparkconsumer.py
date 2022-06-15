
from operator import contains
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StringType, StructType, DateType, StructField, IntegerType, FloatType
from pyspark.sql.types import *
from pyspark.sql.functions import col, split
from pyspark.sql import functions as F
from scorer import Scorer, getscore
from pymongo import MongoClient
import argparse
import json

mongoclient = MongoClient(port=27017)
db = mongoclient.twitto



# Argument parsing
# Argument parsing
parser = argparse.ArgumentParser(description='Fetch some tweets from kafka')
parser.add_argument('--kafkaport', type=int, default=9092, help="Kafka port")
parser.add_argument('--kafkahost', type=str, default="localhost", help="Kafka hostname")
parser.add_argument('--mongohost', type=str, default="localhost", help="Mongo hostname")
parser.add_argument('--mongoport', type=int, default=27017, help="Mongo port")
parser.add_argument('-t', '--topic', type=str, default="twitto", help="The name of the topic. Carefull, this should be the same in producer.py")
args = parser.parse_args()

def process(batch_df,batch_id):
    
    for col in batch_df.collect():
        
        
        result = db.test.insert_one({'text':col['text'],'score':col['score']})
        print(f'Inserted {result.inserted_id} with score {result}')
    pass


# mise en place de la session en chargeant les drivers 
spark = SparkSession \
    .builder \
    .appName("TwitterSentimentAnalysis") \
    .config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector:10.0.0') \
    .config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0') \
    .getOrCreate()


# nous modifions le niveau de log a error
spark.sparkContext.setLogLevel("ERROR")

# ouverture dun flux vers kafka server 
# en entrée nous indiquons host port et topic

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers",f"{args.kafkahost}:{args.kafkaport}") \
    .option("subscribe", f"{args.topic}") \
    .load()

 
#sc = Scorer()
#Instanciation de la methode getscore et on le parse en float
score = F.udf(getscore, FloatType())

#Recuppération de des valeurs en string  
tweet_df_string = df.selectExpr("CAST(value AS STRING)")

# dans notre 
twt = StructType() \
    .add("text",StringType()) \
    .add("created_at",DateType()) \


values = df.select(from_json(df.value.cast("string"), twt).alias("tweet"))


df1 = values.select("tweet.*")

order3 = df1 \
    .withColumn("score",score(col("text")))



#dsw = (order3.writeStream.format("mongodb").queryName("ToMDB").option('spark.mongodb.connection.uri', 'mongodb+srv://moons:mongomoons@cluster0.eky2uou.mongodb.net/?retryWrites=true&w=majority').option('spark.mongodb.database', 'twitto').option('spark.mongodb.collection', 'test').trigger(continuous="10 seconds").outputMode("append").start().awaitTermination());

query = order3.writeStream.queryName("test_tweets") \
        .foreachBatch(process).start()
query.awaitTermination()


print("----- streaming is running -------")


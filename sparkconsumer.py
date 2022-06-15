import argparse
import json

from const import TWEET_FIELDS
from scorer import Scorer

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StringType, StructType, FloatType, DateType, IntegerType
from pyspark.sql.types import *
from pyspark.sql.functions import col, split
from pyspark.sql import functions as F
from pymongo import MongoClient
from time import sleep


# Argument parsing
# Argument parsing
parser = argparse.ArgumentParser(description='Fetch some tweets from kafka')
parser.add_argument('--kafkaport', type=int, default=9092, help="Kafka port")
parser.add_argument('--kafkahost', type=str, default="localhost", help="Kafka hostname")
parser.add_argument('--mongohost', type=str, default="localhost", help="Mongo hostname")
parser.add_argument('--mongoport', type=int, default=27017, help="Mongo port")
parser.add_argument('-t', '--topic', type=str, default="twitto", help="The name of the topic. Carefull, this should be the same in producer.py")
args = parser.parse_args()


# Connect to MongoDB
mongoclient = MongoClient(host=[f'{args.mongohost}:{args.mongoport}'])
db = mongoclient.twitto

# TODO: find a better solution
SLEEP_TIME = 5
print(f"Waiting {SLEEP_TIME}s for services to start...")
sleep(SLEEP_TIME)
print("Starting ...")

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

 
sc = Scorer()
#Instanciation de la methode getscore et on le parse en float
score = F.udf(sc.score, FloatType())

# Recuperation des fields depuis la constante tweet_fields
linker = {"str":StringType()}
twt = StructType()
for k, v in TWEET_FIELDS.items():
    twt.add(k, linker[v])

def db_insert(batch_df, batch_id):
    """
    insere les colones de batch_df dans la db mongo
    """
    for col in batch_df.collect():
        print(col.asDict())
        result = db.test.insert_one(col.asDict())
        print(f'Inserted {result.inserted_id} with score {result}')

values = df.select(from_json(df.value.cast("string"), twt).alias("tweet"))

df1 = values.select("tweet.*")

order = df1.withColumn("score", score(col("text")))

query = order.writeStream.queryName("test_tweets") \
        .foreachBatch(db_insert).start()
query.awaitTermination()


print("----- streaming is running -------")
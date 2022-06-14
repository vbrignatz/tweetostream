from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StringType, StructType, DateType
from pyspark.sql.types import *
from pyspark.sql.functions import col, split
from pyspark.sql import functions as F
from scorer import Scorer, getscore
from pymongo import MongoClient
import argparse
from time import sleep

# Argument parsing
parser = argparse.ArgumentParser(description='Fetch some tweets from kafka')
parser.add_argument('--kafkaport', type=int, default=9092, help="Kafka port")
parser.add_argument('--kafkahost', type=str, default="localhost", help="Kafka hostname")
parser.add_argument('--mongohost', type=str, default="localhost", help="Mongo hostname")
parser.add_argument('--mongoport', type=int, default=27017, help="Mongo port")
parser.add_argument('-t', '--topic', type=str, default="twitto", help="The name of the topic. Carefull, this should be the same in producer.py")
args = parser.parse_args()

mongoclient = MongoClient(host=[f'{args.mongohost}:{args.mongoport}'])
db = mongoclient.twitto

def process(batch_df, batch_id):
    for col in batch_df.collect():
        #print(col)
        result = db.test.insert_one({'text':col['text'],'score':col['score']})
        print(f'Inserted {result.inserted_id} with score {result}')
    pass


# TODO: find a better solution
SLEEP_TIME = 10
print(f"Waiting {SLEEP_TIME}s for services to start...")
sleep(SLEEP_TIME)
print("Starting ...")

spark = SparkSession.\
        builder.\
        appName("Sparktostream").\
        config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector_2.11:2.4.4'). \
        config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0'). \
        getOrCreate()



spark.sparkContext.setLogLevel("ERROR")

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers",f"{args.kafkahost}:{args.kafkaport}") \
    .option("subscribe", f"{args.topic}") \
    .load()

sc = Scorer()
score = F.udf(getscore, FloatType())

tweet_df_string = df.selectExpr("CAST(value AS STRING)")

twt = StructType() \
    .add("text",StringType()) \
    .add("created_at",DateType()) \
    .add("entities",StringType())


values = df.select(from_json(df.value.cast("string"), twt).alias("tweet"))


df1 = values.select("tweet.*")


order3 = df1 \
    .withColumn("score",score(col("text"))
  
    )
#selectionner uniquement les tweets qui contiennene le mot marvel
order3 = order3.filter(col("entities").contains("dccomic"))


#obtenir une sortie d'ecran des stream
twt1 = order3\
    .writeStream \
    .outputMode("update") \
    .option("truncate","false") \
    .format("console") \
    .start()

twt1.awaitTermination()



#query = order3.writeStream.queryName("test_tweets").foreachBatch(process).start()
#query.awaitTermination()

print("----- streaming is running -------")

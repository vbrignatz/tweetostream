from ast import Starred
from doctest import master
from lib2to3.pgen2.pgen import DFAState
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StringType, StructType, StructField
from pyspark.sql.types import *
from pyspark.sql.functions import col, split
from pyspark.sql import functions as F
from scorer import Scorer, getscore
from pymongo import MongoClient




spark = SparkSession.\
        builder.\
        appName("streamingExampleWrite").\
        config('spark.jars.packages', 'org.mongodb.spark:mongo-spark-connector:10.0.0').\
        config('spark.jars.packages', 'org.apache.spark:spark-sql-kafka-0-10_2.12:3.0.0').\
        getOrCreate()



        


spark.sparkContext.setLogLevel("ERROR")

df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "twitto") \
    .load()

sc = Scorer()
score = F.udf(getscore, FloatType())

tweet_df_string = df.selectExpr("CAST(value AS STRING)")

twt = StructType() \
    .add("text",StringType()) \
    .add("created_at",DateType())


values = df.select(from_json(df.value.cast("string"), twt).alias("tweet"))


df1 = values.select("tweet.*")

order3 = df1 \
    .withColumn("score",score(col("text")))
#obtenir une sortie d'ecran des stream
twt1 = order3\
    .writeStream \
    .outputMode("update") \
    .option("truncate","false") \
    .format("console") \
    .start()

twt1.awaitTermination()



print("----- streaming is running -------")

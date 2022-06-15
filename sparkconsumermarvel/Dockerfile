FROM datamechanics/spark:3.2.1-latest
ENV PYSPARK_MAJOR_PYTHON_VERSION=3.7
WORKDIR /code
COPY sparkconsumermarvel/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY consumerSparkMarvel.py .
COPY scorer.py .
#CMD ["python3", "-u", "consumerSparkMarvel.py", "--kafkahost", "kafka_server", "--kafkaport", "9092", "--mongohost", "mongo_server", "--mongoport", "27017", "--topic", "covid"]
CMD ["spark-submit", "--master", "local[2]","-u","consumerSparkMarvel.py", "--kafkahost", "kafka_server", "--kafkaport", "9092", "--mongohost", "mongo_server", "--mongoport", "27017", "--topic", "covid"]



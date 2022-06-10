FROM gcr.io/datamechanics/spark:platform-3.1-dm14
ENV PYSPARK_MAJOR_PYTHON_VERSION=3
WORKDIR /code
COPY sparkconsumer/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY sparkconsumer.py .
COPY scorer.py .
CMD ["python3", "-u", "sparkconsumer.py", "--kafkahost", "kafka_server", "--kafkaport", "9092", "--mongohost", "mongo_server", "--mongoport", "27017", "--topic", "covid"]



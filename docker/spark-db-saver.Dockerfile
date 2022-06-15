FROM datamechanics/spark:3.2.1-latest
ENV PYSPARK_MAJOR_PYTHON_VERSION=3.7
WORKDIR /code
COPY requirements/spark-db-saver.requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY src/spark-db-saver.py .
COPY src/scorer.py .
COPY src/const.py .
CMD ["python3", "-u", "spark-db-saver.py", "--kafkahost", "kafka_server", "--kafkaport", "9092", "--mongohost", "mongo_server", "--mongoport", "27017", "--topic", "covid"]



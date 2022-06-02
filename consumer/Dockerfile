FROM python:3.9
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY consumer.py .
COPY scorer.py .
CMD ["python3", "-u", "consumer.py", "--kafkahost", "kafka_server", "--kafkaport", "9092", "--mongohost", "mongo_server", "--mongoport", "27017", "--topic", "covid"]
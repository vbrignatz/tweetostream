FROM python:3.9
WORKDIR /code
COPY requirements/requirements-consumer.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY src/consumer.py .
COPY src/scorer.py .
CMD ["python3", "-u", "consumer.py", "--kafkahost", "kafka-cp-kafka-headless", "--kafkaport", "9092", "--mongohost", "mongodb.default.svc.cluster.local", "--mongoport", "27017", "--topic", "covid"]
FROM python:3.9
WORKDIR /code
COPY requirements/requirements-producer.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY src/producer.py .
COPY secret.json .
CMD ["python3", "-u", "producer.py", "covid", "lang:en", "--host", "kafka-cp-kafka-headless", "--port", "9092", "--topic", "covid"]
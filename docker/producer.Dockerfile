FROM python:3.9
WORKDIR /code
COPY requirements/producer.requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY src/producer.py .
COPY src/const.py .
COPY secret.json .
CMD ["python3", "-u", "producer.py", "covid", "lang:en", "--host", "kafka_server", "--port", "9092", "--topic", "covid"]
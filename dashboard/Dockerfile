# FROM python:3.9
FROM tiangolo/uwsgi-nginx-flask:python3.10
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY dashboard.py .
COPY scorer.py .
CMD ["python3", "-u", "dashboard.py", "100", "--kafkahost", "kafka_server", "--kafkaport", "9092", "--mongohost", "mongo_server", "--mongoport", "27017", "--topic", "covid", "--port", "8085", "--log", "erros.log"]
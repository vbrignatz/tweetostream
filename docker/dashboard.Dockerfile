# FROM python:3.9
FROM tiangolo/uwsgi-nginx-flask:python3.10
WORKDIR /code
COPY requirements/requirements-dashboard.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY src/dashboard.py .
COPY src/scorer.py .
CMD ["python3", "-u", "dashboard.py", "60", "--kafkahost", "kafka-cp-kafka-headless", "--kafkaport", "9092", "--mongohost", "mongodb.default.svc.cluster.local", "--mongoport", "27017", "--topic", "covid", "--port", "8085", "--log", "erros.log"]
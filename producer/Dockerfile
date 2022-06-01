FROM python:3.9
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY producer.py .
COPY secret.json .
CMD ["python3", "-u", "producer.py"]
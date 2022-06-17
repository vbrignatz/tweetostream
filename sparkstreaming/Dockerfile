FROM python:3.9
WORKDIR /code
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY streamingspark.py .
COPY scorer.py .
CMD ["python3", "-u", "streamingspark.py", "--sparkhost", "localhost", "--sparkport", "9092", "--topic", "covid"]




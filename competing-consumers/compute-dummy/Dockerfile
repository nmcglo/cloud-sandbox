FROM registry.access.redhat.com/ubi8/python-39

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY dummy_server.py .
COPY dummy_consumer.py .

EXPOSE 8000

CMD ["uvicorn", "dummy_consumer:app", "--host", "0.0.0.0", "--port", "8000"]

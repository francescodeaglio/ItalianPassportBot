FROM passportcommon:latest

WORKDIR /app
COPY dispatcher/requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

COPY dispatcher/ /app

CMD ["python3", "consumer.py"]
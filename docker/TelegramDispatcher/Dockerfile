FROM passportcommon:latest

WORKDIR /app
COPY telegram_dispatcher/requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

COPY telegram_dispatcher/ /app

CMD ["python3", "consumer.py"]
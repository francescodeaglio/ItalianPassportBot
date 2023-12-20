FROM passportcommon:latest

WORKDIR /app
COPY bot/requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

COPY bot/ /app

CMD ["python3", "bot.py"]
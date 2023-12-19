FROM passportcommon:latest

WORKDIR /app
COPY poller/requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

COPY poller/ /app

CMD ["python3", "poller.py"]
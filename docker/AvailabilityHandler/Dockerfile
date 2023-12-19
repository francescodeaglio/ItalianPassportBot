FROM passportcommon:latest

WORKDIR /app
COPY availability_handler/requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

COPY availability_handler/ /app

CMD ["python3", "avail_runner.py"]
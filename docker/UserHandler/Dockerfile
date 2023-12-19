FROM passportcommon:latest

WORKDIR /app
COPY user_handler/requirements.txt /app
RUN pip install --no-cache-dir --requirement /app/requirements.txt

COPY user_handler/ /app

CMD ["python3", "user_runner.py"]
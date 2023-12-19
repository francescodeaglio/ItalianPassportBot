FROM python:3.10-slim-bullseye

RUN apt-get update \
  && apt-get install -y --no-install-recommends --no-install-suggests \
  build-essential default-libmysqlclient-dev \
  && pip install --no-cache-dir --upgrade pip


WORKDIR /app/common
COPY common/requirements.txt /app/common
RUN pip install --no-cache-dir --requirement /app/common/requirements.txt

COPY common /app/common

ENV MYSQL_PORT="3306"
ENV MYSQL_HOST="database"
ENV MYSQL_USER="mysql_user"
ENV MYSQL_DB="passport"
ENV MYSQL_PASSWORD="Pass123"
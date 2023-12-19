#!/bin/bash

# Wait for RabbitMQ to start
sleep 10

# RabbitMQ connection parameters
RABBITMQ_HOST=${RABBITMQ_HOST:-"localhost"}
RABBITMQ_PORT=${RABBITMQ_PORT:-5672}
RABBITMQ_USER=${RABBITMQ_USER:-"guest"}
RABBITMQ_PASSWORD=${RABBITMQ_PASSWORD:-"guest"}

# Create queues
rabbitmqadmin declare queue name=new_availability durable=true
rabbitmqadmin declare queue name=new_user durable=true
rabbitmqadmin declare queue name=message durable=true
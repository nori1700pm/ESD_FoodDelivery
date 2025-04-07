#!/usr/bin/env python3

"""
A standalone script to create exchanges and queues on RabbitMQ.
"""

import pika
import os
import time
import sys

amqp_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
amqp_port = int(os.environ.get('RABBITMQ_PORT', 5672))
exchange_name = "order_topic"
exchange_type = "topic"


def create_exchange(hostname, port, exchange_name, exchange_type):
    print(f"Connecting to AMQP broker {hostname}:{port}...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname,
            port=port,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    print("Connected")

    print("Opening channel...")
    channel = connection.channel()

    print(f"Declaring exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name,
        exchange_type=exchange_type,
        durable=True
    )

    return channel


def create_queue(channel, exchange_name, queue_name, binding_keys):
    print(f"Declaring queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)

    for binding_key in binding_keys:
        print(f"Binding '{queue_name}' to '{exchange_name}' with key '{binding_key}'")
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=binding_key
        )


# --- Retry Logic ---
MAX_RETRIES = 5
for attempt in range(1, MAX_RETRIES + 1):
    try:
        print(f"[Attempt {attempt}] Connecting to RabbitMQ...")
        channel = create_exchange(
            hostname=amqp_host,
            port=amqp_port,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
        )
        break  # If successful, exit the loop
    except pika.exceptions.AMQPConnectionError as e:
        print(f"❌ Connection failed: {e}")
        if attempt == MAX_RETRIES:
            print("🚨 All connection attempts failed.")
            sys.exit(1)
        time.sleep(5)

# Declare queues after successful connection
create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="error_queue",
    binding_keys=[
        "order.*.error",
        "payment.*.error",
        "wallet.*.error",
    ],
)

create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="notification_queue",
    binding_keys=[
        "wallet.payment.error",
        "order.cancel.notification",
        "driver.assigned.notification"
    ],
)

print("RabbitMQ setup complete.")

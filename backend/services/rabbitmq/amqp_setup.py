#!/usr/bin/env python3

"""
A standalone script to create exchanges and queues on RabbitMQ.
"""

import pika
import os

amqp_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
amqp_port = int(os.environ.get('RABBITMQ_PORT', 5672))
exchange_name = "order_topic"
exchange_type = "topic"


def create_exchange(hostname, port, exchange_name, exchange_type):
    print(f"Connecting to AMQP broker {hostname}:{port}...")
    # connect to the broker
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=hostname,
            port=port,
            heartbeat=300,
            blocked_connection_timeout=300,
        )
    )
    print("Connected")

    print("Open channel")
    channel = connection.channel()

    # Set up the exchange if the exchange doesn't exist
    print(f"Declare exchange: {exchange_name}")
    channel.exchange_declare(
        exchange=exchange_name, 
        exchange_type=exchange_type, 
        durable=True
    )
    # 'durable' makes the exchange survive broker restarts

    return channel


def create_queue(channel, exchange_name, queue_name, binding_keys):
    print(f"Bind to queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    # 'durable' makes the queue survive broker restarts

    # bind the queue to the exchange via the routing_key
    for binding_key in binding_keys:
        print(f"Binding queue to exchange with key: {binding_key}")
        channel.queue_bind(
            exchange=exchange_name,
            queue=queue_name,
            routing_key=binding_key
        )


channel = create_exchange(
    hostname=amqp_host,
    port=amqp_port,
    exchange_name=exchange_name,
    exchange_type=exchange_type,
)

# queues are created and declared here
create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="error_queue",
    binding_keys=[
                "order.*.error",    # All order errors
                "payment.*.error",   # All payment errors
                "wallet.*.error"     # All wallet errors
                ],
)

create_queue(
    channel=channel,
    exchange_name=exchange_name,
    queue_name="Activity_Log",
    binding_keys=["#"],
)

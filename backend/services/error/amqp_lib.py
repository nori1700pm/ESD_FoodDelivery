"""
Reusable AMQP-related functions

References:
https://pika.readthedocs.io/en/stable/_modules/pika/exceptions.html#ConnectionClosed
"""

import time
import pika


def connect(hostname, port, exchange_name, exchange_type, max_retries=12, retry_interval=5,):
     retries = 0

     # loop to retry connection up to 12 times
     # with a retry interval of 5 seconds
     while retries < max_retries:
          retries += 1
          try:
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

                # Declare the exchange (create if doesn't exist)
                print(f"Declaring exchange: {exchange_name}")
                channel.exchange_declare(
                     exchange=exchange_name,
                     exchange_type=exchange_type,
                     durable=True  # Survive broker restart
                )

                # Declare the queue
                print(f"Declaring queue: error_queue")
                channel.queue_declare(
                    queue='error_queue',
                    durable=True  # Survive broker restart
                )

                # Bind the queue to the exchange
                binding_keys = [
                    "order.*.error",    # All order errors
                    "payment.*.error",   # All payment errors
                    "wallet.*.error"     # All wallet errors
                ]
                
                for binding_key in binding_keys:
                    print(f"Binding queue to exchange with key: {binding_key}")
                    channel.queue_bind(
                        exchange=exchange_name,
                        queue='error_queue',
                        routing_key=binding_key
                    )

                print("Setup complete")
                return connection, channel

          except pika.exceptions.AMQPConnectionError as exception:
                print(f"Failed to connect: {exception=}")
                print(f"Retrying in {retry_interval} seconds...")
                time.sleep(retry_interval)

     raise Exception(f"Max {max_retries} retries exceeded...")


def close(connection, channel):
     channel.close()
     connection.close()

def is_connection_open(connection):
    try:
        connection.process_data_events()
        return True     
    except pika.exceptions.AMQPError as e:
        print("AMQP Error:", e)
        return False


def start_consuming(
     hostname, port, exchange_name, exchange_type, queue_name, callback
):
     while True:
          try:
                connection, channel = connect(
                     hostname=hostname,
                     port=port,
                     exchange_name=exchange_name,
                     exchange_type=exchange_type,
                )

                print(f"Consuming from queue: {queue_name}")
                channel.basic_consume(
                     queue=queue_name, on_message_callback=callback, auto_ack=True
                )
                channel.start_consuming()

          except pika.exceptions.ConnectionClosedByBroker:
                print("Connection closed. Try to reconnect...")
                continue

          except KeyboardInterrupt:
                close(connection, channel)
                break

          except Exception as e:
                print(f"Error: {e}")
                print("Retrying in 5 seconds...")
                time.sleep(5)
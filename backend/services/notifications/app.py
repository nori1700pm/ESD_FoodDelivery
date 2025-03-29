import os
import json
import rabbitmq.amqp_lib as amqp_lib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

rabbit_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
rabbit_port = int(os.environ.get('RABBITMQ_PORT', 5672))
exchange_name = "order_topic"
exchange_type = "topic"
queue_name = "error_queue" 

def callback(channel, method, properties, body):
    # required signature for the callback; no return
    try:
        error = json.loads(body)
        print(f"JSON: {error}")

        message = Mail(
        from_email='nomnomgodelivery@gmail.com',
        to_emails='chaizheqing2004@gmail.com',
        subject=error['message'],
        html_content='There is insufficient balance in your wallet, please top up!')
        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(str(e))

    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"Message: {body}")
    print()


if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        amqp_lib.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )
    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")


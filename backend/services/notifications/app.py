import os
import json
import rabbitmq.amqp_lib as amqp_lib
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Personalization
import time

rabbit_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
rabbit_port = int(os.environ.get('RABBITMQ_PORT', 5672))
exchange_name = "order_topic"
exchange_type = "topic"
queue_name = "notification_queue" #### take note ive changed the queue name!  

def callback(channel, method, properties, body):
    try:
        message_data = json.loads(body)
        print(f"Received message: {message_data}")
        print(f"Routing key: {method.routing_key}")  # Add this for debugging

        # Initialize Mail with personalization
        message = Mail(from_email=Email('nomnomgodelivery@gmail.com'))
        personalization = Personalization()
        personalization.add_to(To('tabithasim223@gmail.com')) # recipient

        # Check message type based on routing key
        if method.routing_key == "order.cancel.notification":
            print("Processing cancellation notification")
            # Use the same template ID as other notifications for now
            personalization.dynamic_template_data = {
                "payment_message": message_data.get('message', 'No message provided'),
                "timestamp": "2025-03-30 06:59:12"  # Current timestamp
            }
            message.template_id = 'd-2a1e47b9a8b944c5a79fc1883a089cbf'  # Use the working template ID
        else:
            print("Processing other notification")
            personalization.dynamic_template_data = {
                "payment_message": message_data.get('message', 'No message provided'),
                "timestamp": "2025-03-30 06:59:12"  # Current timestamp
            }
            message.template_id = 'd-2a1e47b9a8b944c5a79fc1883a089cbf'

        message.add_personalization(personalization)
        
        print("Preparing to send email with data:", personalization.dynamic_template_data)

        try:
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            if not os.environ.get('SENDGRID_API_KEY'):
                print("WARNING: SENDGRID_API_KEY environment variable is not set")
            response = sg.send(message)
            print(f"Email sent! Status code: {response.status_code}")
            print(f"Response headers: {response.headers}")
        except Exception as e:
            print(f"ERROR sending email: {str(e)}")

    except Exception as e:
        print(f"Unable to process message: {e}")
        print(f"Message body: {body}")
    print()

if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        print("[DEBUG] Notification service is starting...")
        amqp_lib.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )

        # If we get here, start_consuming() returned instead of blocking
        print("[WARNING] Consumer stopped unexpectedly. Restarting in 5 seconds...")
        time.sleep(5)

    except Exception as exception:
        print(f"  Unable to connect to RabbitMQ.\n     {exception=}\n")


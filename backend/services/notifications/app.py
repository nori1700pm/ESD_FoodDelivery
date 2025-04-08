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
queue_name = "notification_queue"

def callback(channel, method, properties, body):
    try:
        message_data = json.loads(body)
        print(f"JSON: {message_data}")

        recipient_email = message_data.get('recipient')
        
        # Initialize Mail correctly with personalization
        message = Mail(from_email=Email('nomnomgodelivery@gmail.com'))
        personalization = Personalization()
        personalization.add_to(To(recipient_email)) 

        base_data = {
            "subject": message_data.get("subject"),
            "subtotal": round(float(message_data.get('subtotal', 0)), 2),
            "delivery_fee": round(float(message_data.get('delivery_fee', 0)), 2),
            "total": round(float(message_data.get('total', 0)), 2),
        }


        # Check message type based on routing key and payment status (filter here)

        # Cancellation of Order - Refund
        if method.routing_key == "order.cancel.notification":
            print("Processing cancellation notification")
            base_data.update({
                "payment_status": message_data.get('payment_status'),
                "payment_message": message_data.get('message', 'No message provided'),
            })
            message.template_id = 'd-2a1e47b9a8b944c5a79fc1883a089cbf'

        # Notifications for insufficient balance (payment error)
        elif method.routing_key == "wallet.payment.error":
            base_data.update({
                "payment_status": message_data.get('payment_status'),
                "payment_message": message_data.get('message', 'No message provided')
            })

            message.template_id = 'd-2a1e47b9a8b944c5a79fc1883a089cbf'

        # Successful driver assigned
        elif method.routing_key == "driver.assigned.notification":
            base_data.update({
                "items": message_data.get('items', []),
                "order_ID": message_data.get("order_id"),
                "driver_ID": message_data.get("driver_id")
            })

            message.template_id = 'd-5aea4bf87a9f4737a69f8c42851049c2'

        personalization.dynamic_template_data = base_data
        message.add_personalization(personalization)   

        # Code block will send the email here
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
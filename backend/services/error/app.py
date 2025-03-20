#!/usr/bin/env python3
import os
import amqp_lib
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import datetime

# Initialize Firebase from environment variable
firebase_config = os.environ.get('FIREBASE_CONFIG')
if firebase_config:
    cred = credentials.Certificate(json.loads(firebase_config))
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    print("Warning: FIREBASE_CONFIG environment variable not set")

# Get RabbitMQ configuration from environment
rabbit_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
rabbit_port = int(os.environ.get('RABBITMQ_PORT', 5672))
exchange_name = "order_topic"
exchange_type = "topic"
queue_name = "error_queue"  # Changed from "Error" to be consistent

def callback(channel, method, properties, body):
    try:
        error = json.loads(body)
        print(f"Error message (JSON): {error}")
        
        # Store error in Firebase if initialized
        if 'db' in globals():
            error_ref = db.collection('errors').document()
            error_data = {
                'timestamp': datetime.datetime.now(),
                'error_details': error,
                'routing_key': method.routing_key
            }
            error_ref.set(error_data)
            print(f"Error stored in Firebase with ID: {error_ref.id}")
        else:
            print("Warning: Firebase not initialized, error not stored")
        
    except Exception as e:
        print(f"Unable to parse JSON: {e=}")
        print(f"Error message: {body}")
    print()

if __name__ == "__main__":
    print(f"This is {os.path.basename(__file__)} - amqp consumer...")
    try:
        amqp_lib.start_consuming(
            rabbit_host, rabbit_port, exchange_name, exchange_type, queue_name, callback
        )
    except Exception as exception:
        print(f"Unable to connect to RabbitMQ.\n     {exception=}\n")
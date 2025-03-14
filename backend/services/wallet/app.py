from flask import Flask, request, jsonify
import json
import os
from firebase_admin import credentials, firestore, initialize_app
import pika
import uuid
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
# Initialize Firebase
firebase_config = os.environ.get('FIREBASE_CONFIG')
firebase_config_dict = json.loads(firebase_config)
cred = credentials.Certificate(firebase_config_dict)
initialize_app(cred)
db = firestore.client()

RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')

# RabbitMQ setup
def send_error_to_queue(error_details):
    try:
        # RabbitMQ connection parameters
        credentials = pika.PlainCredentials('guest', 'guest')  # Update with your credentials
        parameters = pika.ConnectionParameters('rabbitmq', 5672, '/', credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Declare the error queue
        channel.queue_declare(queue='error_queue', durable=True)

        # Send error message
        channel.basic_publish(
            exchange='',
            routing_key='error_queue',
            body=json.dumps(error_details),
            properties=pika.BasicProperties(
                delivery_mode=2  # Make message persistent
            )
        )

        connection.close()
        return True
    except Exception as e:
        print(f"Error sending to queue: {str(e)}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/wallet/<customer_id>', methods=['GET'])
def get_wallet(customer_id):
    try:
        wallet_ref = db.collection('wallets').document(customer_id)
        wallet = wallet_ref.get()
        
        if not wallet.exists:
            # Create wallet if it doesn't exist
            wallet_ref.set({
                'balance': 0.0,
                'customerId': customer_id
            })
            return jsonify({'balance': 0.0}), 200
            
        return jsonify({'balance': wallet.to_dict().get('balance', 0.0)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/wallet/<customer_id>/process-payment', methods=['POST'])
def process_payment(customer_id):
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        order_id = data.get('orderId')

        if not amount or not order_id:
            return jsonify({'error': 'Missing amount or orderId'}), 400

        wallet_ref = db.collection('wallets').document(customer_id)
        wallet = wallet_ref.get()

        if not wallet.exists:
            error_details = {
                'errorId': str(uuid.uuid4()),
                'custId': customer_id,
                'orderId': order_id,
                'message': 'Wallet not found'
            }
            send_error_to_queue(error_details)
            return jsonify({'error': 'Wallet not found'}), 404

        current_balance = wallet.to_dict().get('balance', 0.0)

        if current_balance < amount:
            error_details = {
                'errorId': str(uuid.uuid4()),
                'custId': customer_id,
                'orderId': order_id,
                'message': 'Insufficient balance'
            }
            send_error_to_queue(error_details)
            return jsonify({
                'error': 'Insufficient balance',
                'currentBalance': current_balance,
                'required': amount
            }), 400

        # Process payment
        new_balance = current_balance - amount
        wallet_ref.update({
            'balance': new_balance,
            'updatedAt': firestore.SERVER_TIMESTAMP
        })

        return jsonify({
            'message': 'Payment processed successfully',
            'newBalance': new_balance,
            'transactionAmount': amount
        }), 200

    except Exception as e:
        error_details = {
            'errorId': str(uuid.uuid4()),
            'custId': customer_id,
            'orderId': order_id if 'order_id' in locals() else None,
            'message': f'Payment processing error: {str(e)}'
        }
        send_error_to_queue(error_details)
        return jsonify({'error': str(e)}), 500
    
@app.route('/wallet/<customer_id>', methods=['PUT'])
def update_wallet(customer_id):
    try:
        data = request.get_json()
        new_balance = float(data.get('balance', 0))

        if new_balance < 0:
            return jsonify({'error': 'Balance cannot be negative'}), 400

        wallet_ref = db.collection('wallets').document(customer_id)
        wallet = wallet_ref.get()
        
        if not wallet.exists:
            wallet_ref.set({
                'balance': new_balance,
                'customerId': customer_id,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
        else:
            wallet_ref.update({
                'balance': new_balance,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            
        return jsonify({
            'message': 'Wallet updated successfully',
            'balance': new_balance
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
from flask import Flask, request, jsonify
import json
import os
from firebase_admin import credentials, firestore, initialize_app
import pika
import uuid
from flask_cors import CORS
import traceback  
import rabbitmq.amqp_lib as amqp_lib
import rabbitmq.amqp_setup 


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Firebase
firebase_config = os.environ.get('FIREBASE_CONFIG')
firebase_config_dict = json.loads(firebase_config)
cred = credentials.Certificate(firebase_config_dict)
initialize_app(cred)
db = firestore.client()
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
PORT = int(os.environ.get('PORT', 5002)) 

exchange_name = "order_topic"
exchange_type = "topic"
queue_name = "error_queue"  # Changed from "Error" to be consistent

# RabbitMQ setup
def send_error_to_queue(error_details):
    try:
        print("  Connecting to AMQP broker...")
        connection, channel = amqp_lib.connect(
            hostname=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            exchange_name='order_topic',
            exchange_type='topic',
        )

        print("  Publishing error message to queue...")
        channel.basic_publish(
            exchange='order_topic',
            routing_key='wallet.payment.error',
            body=json.dumps(error_details),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()
        print("  Error message sent successfully ✅")
        return True

    except Exception as e:
        print(f"  ❌ Failed to send error to queue: {str(e)}")
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
            wallet_ref.set({
                'balance': 0.0,
                'customerId': customer_id,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            current_balance = 0.0
        else:
            current_balance = wallet.to_dict().get('balance', 0.0)

        if current_balance < amount:
            error_details = {
                'errorId': str(uuid.uuid4()),
                'custId': customer_id,
                'orderId': order_id,
                'message': 'Insufficient balance'
            }
            print("Attempting sending error to queue")
            send_error_to_queue(error_details)
            return jsonify({
                'error': 'Insufficient balance',
                'currentBalance': current_balance,
                'required': amount
            }), 400

        # Process payment
        new_balance = current_balance - amount
        
        # Use a transaction to ensure atomic update
        transaction = db.transaction()
        @firestore.transactional
        def update_in_transaction(transaction, wallet_ref):
            wallet = wallet_ref.get(transaction=transaction)
            if not wallet.exists:
                raise ValueError("Wallet no longer exists")
            
            current_balance = wallet.to_dict().get('balance', 0.0)
            if current_balance < amount:
                raise ValueError("Insufficient balance")
                
            transaction.update(wallet_ref, {
                'balance': firestore.Increment(-amount),
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            
            return current_balance - amount

        try:
            new_balance = update_in_transaction(transaction, wallet_ref)
        except Exception as e:
            error_details = {
                'errorId': str(uuid.uuid4()),
                'custId': customer_id,
                'orderId': order_id,
                'message': f'Transaction failed: {str(e)}'
            }
            send_error_to_queue(error_details)
            return jsonify({'error': str(e)}), 400

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
    
# @app.route('/users/<user_id>', methods=['GET'])
# def get_user_profile(user_id):
#     try:
#         print(f"Fetching profile for user ID: {user_id}")
        
#         # Get user document from Firestore
#         user_ref = db.collection('users').document(user_id)
#         user = user_ref.get()
        
#         print(f"Firebase response - Document exists: {user.exists}")
        
#         if not user.exists:
#             error_response = {
#                 'error': 'User not found',
#                 'user_id': user_id
#             }
#             print(f"User not found response: {error_response}")
#             return jsonify(error_response), 404
            
#         user_data = user.to_dict()
#         print(f"Raw user data from Firebase:", user_data)
        
#         # Make sure we're returning ALL fields from Firestore
#         response_data = {
#             'uid': user_id,
#             'address': user_data.get('address', ''),
#             'name': user_data.get('name', ''),
#             'email': user_data.get('email', ''),
#             'phone': user_data.get('phone', '')  # Also include phone
#         }
        
#         print(f"Sending response from wallet service:", response_data)
#         return jsonify(response_data), 200
        
#     except Exception as e:
#         error_msg = f"Error fetching user profile: {str(e)}"
#         print(error_msg)
#         print(f"Stack trace: {traceback.format_exc()}")
#         return jsonify({'error': error_msg}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
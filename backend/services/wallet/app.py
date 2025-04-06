from flask import Flask, request, jsonify, redirect
import json
import os
from firebase_admin import credentials, firestore, initialize_app
import uuid
from flask_cors import CORS
import traceback  
import pika
import stripe


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize Firebase
firebase_config = os.environ.get('FIREBASE_CONFIG')
firebase_config_dict = json.loads(firebase_config)
cred = credentials.Certificate(firebase_config_dict)
initialize_app(cred)
db = firestore.client()
PORT = int(os.environ.get('PORT', 5002))

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')

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
                'orderId': order_id,
                'recipient': "chaizheqing2004@gmail.com", #data.get('custEmail'),
                'subject': 'Insufficient Wallet Balance',
                'subtotal': data.get('subtotal'),
                'payment_status': 'UNPAID',
                'delivery_fee':data.get('delivery_fee'),
                'total':amount,
                "message": f"""
                    Due to insufficient balance, the order #{order_id} is unprocessed. 
                    Please top up your wallet balance before proceeding.
                    """
            }
            return jsonify({
                'error': error_details,
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
        return jsonify({'error': str(e)}), 500

@app.route('/wallet/<customer_id>', methods=['PUT'])
def update_wallet(customer_id):
    try:
        data = request.get_json()
        print("Received data:", data)
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

# Create a Stripe checkout session for wallet top-up
@app.route('/wallet/<customer_id>/create-stripe-checkout', methods=['POST'])
def create_stripe_checkout(customer_id):
    try:
        data = request.get_json()
        amount = float(data.get('amount', 0))
        
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than 0'}), 400
            
        # Convert to cents for Stripe
        amount_cents = int(amount * 100)
        
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'sgd',
                    'product_data': {
                        'name': 'Wallet Top-up',
                        'description': f'Add ${amount:.2f} to your NomNomGo wallet'
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f'{frontend_url}/wallet-success?session_id={{CHECKOUT_SESSION_ID}}&customer_id={customer_id}&amount={amount}',
            cancel_url=f'{frontend_url}/wallet?canceled=true',
            metadata={
                'customer_id': customer_id,
                'amount': str(amount),
                'type': 'wallet_topup'
            }
        )
        
        return jsonify({
            'id': checkout_session.id,
            'url': checkout_session.url
        }), 200
        
    except Exception as e:
        print(f"Error creating checkout session: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# Process successful Stripe payments
@app.route('/wallet/process-stripe-success', methods=['POST'])
def process_stripe_success():
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        customer_id = data.get('customer_id')
        amount = float(data.get('amount', 0))
        
        if not session_id or not customer_id or amount <= 0:
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Verify the session with Stripe
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Verify session belongs to this customer and is paid
            if session.metadata.get('customer_id') != customer_id or session.payment_status != 'paid':
                return jsonify({'error': 'Invalid session or payment not completed'}), 400
                
        except stripe.error.StripeError as e:
            return jsonify({'error': f'Stripe error: {str(e)}'}), 400
            
        # Add the amount to user's wallet
        wallet_ref = db.collection('wallets').document(customer_id)
        wallet = wallet_ref.get()
        
        if not wallet.exists:
            wallet_ref.set({
                'balance': amount,
                'customerId': customer_id,
                'createdAt': firestore.SERVER_TIMESTAMP,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            current_balance = amount
        else:
            current_balance = wallet.to_dict().get('balance', 0)
            new_balance = current_balance + amount
            wallet_ref.update({
                'balance': new_balance,
                'updatedAt': firestore.SERVER_TIMESTAMP
            })
            current_balance = new_balance
            
        # Record the transaction
        db.collection('wallet_transactions').add({
            'customerId': customer_id,
            'amount': amount,
            'type': 'credit',
            'method': 'stripe',
            'stripeSessionId': session_id,
            'status': 'completed',
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({
            'success': True,
            'balance': current_balance,
            'amount': amount
        }), 200
        
    except Exception as e:
        print(f"Error processing Stripe success: {str(e)}")
        print(f"Stack trace: {traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
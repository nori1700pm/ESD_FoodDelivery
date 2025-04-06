from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from invokes import invoke_http
from firebase_admin import credentials, firestore, initialize_app
import pika
from datetime import datetime
import pytz
import rabbitmq.amqp_lib as amqp_lib

app = Flask(__name__)
CORS(app)

# Initialize Firebase
firebase_config = os.environ.get('FIREBASE_CONFIG')
firebase_config_dict = json.loads(firebase_config)
cred = credentials.Certificate(firebase_config_dict)
initialize_app(cred)
db = firestore.client()

# Add RabbitMQ configuration
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
EXCHANGE_NAME = "order_topic"

# URLs for other services
ORDER_URL = os.environ.get('orderURL') or "http://order-service:5001"
WALLET_URL = os.environ.get('walletURL') or "http://wallet-service:5002"
CUSTOMER_URL = os.environ.get('customerURL') or "http://customer-service:4000"

def publish_message(routing_key, message):
    try:
        print("  Connecting to AMQP broker...")
        connection, channel = amqp_lib.connect(
            hostname=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            exchange_name='order_topic',
            exchange_type='topic',
        )
        
        # Publish the message
        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        connection.close()
        print(f"Published message to {routing_key}: {message}")
        
    except Exception as e:
        print(f"Error publishing message: {str(e)}")

@app.route("/health")
def health_check():
    return jsonify({"message": "Service is healthy"}), 200

@app.route("/deliver-food/cancel/<order_id>", methods=['POST'])
def cancel_order(order_id):
    """
    Cancel an order and process refund
    """
    try:
        print(f"\n=== Starting order cancellation for order {order_id} ===")
        
        # Step 1: Get the order details 
        print(f"Fetching order details from {ORDER_URL}/orders/{order_id}")
        order_result = invoke_http(
            f"{ORDER_URL}/orders/{order_id}",
            method="GET"
        )
        print("Order result:", order_result)
        
        if not order_result or 'error' in order_result:
            print(f"Order not found or error: {order_result}")
            return jsonify({
                "code": 404,
                "message": f"Order {order_id} not found or error occurred."
            }), 404

        # Step 2: Process refund to customer's wallet
        customer_id = order_result.get('customerId')
        order_amount = float(order_result.get('price', 0))
        
        print(f"\nProcessing refund for customer {customer_id}, amount: {order_amount}")
        
        # Get current wallet balance
        print(f"Fetching wallet balance from {WALLET_URL}/wallet/{customer_id}")
        wallet_result = invoke_http(
            f"{WALLET_URL}/wallet/{customer_id}",
            method="GET"
        )
        print("Wallet result:", wallet_result)
        
        if not wallet_result or 'error' in wallet_result:
            print(f"Wallet error: {wallet_result}")
            return jsonify({
                "code": 500,
                "message": f"Failed to get wallet information: {wallet_result.get('error', 'Unknown error')}"
            }), 500

        current_balance = float(wallet_result.get('balance', 0))
        new_balance = current_balance + order_amount

        # Update wallet with refund
        print(f"Updating wallet balance to {new_balance}")
        refund_result = invoke_http(
            f"{WALLET_URL}/wallet/{customer_id}",
            method="PUT",
            json={"balance": new_balance}
        )
        print("Refund result:", refund_result)
        
        if not refund_result or 'error' in refund_result:
            print(f"Refund error: {refund_result}")
            return jsonify({
                "code": 500,
                "message": f"Failed to process refund: {refund_result.get('error', 'Unknown error')}"
            }), 500

        # Step 3: Update order status
        sg_timezone = pytz.timezone('Asia/Singapore') # Define the Singapore timezone
        current_sg_time = datetime.now(sg_timezone).strftime('%Y-%m-%d %H:%M:%S')
        update_data = {
            "status": "CANCELLED",
            "paymentStatus": "REFUNDED",
            "driverStatus": 'CANCELLED',  
            "updatedAt": current_sg_time
        }
        
        print(f"\nUpdating order status: {update_data}")
        final_update = invoke_http(
            f"{ORDER_URL}/orders/{order_id}/status",  
            method="PUT",
            json=update_data
        )
        print("Order update result:", final_update)

        if not final_update or 'error' in final_update:
            print(f"Order update error: {final_update}")
            return jsonify({
                "code": 500,
                "message": f"Failed to update order status: {final_update.get('error', 'Unknown error')}"
            }), 500

        # Step 4: Send notification
        try:
            # Get customer details
            print(f"\nFetching customer details from {CUSTOMER_URL}/customers/{customer_id}")
            customer_result = invoke_http(
                f"{CUSTOMER_URL}/customers/{customer_id}",
                method="GET"
            )
            print("Customer result:", customer_result)

            if customer_result and 'error' not in customer_result:
                delivery_fee = float(order_result.get('deliveryFee', 0))
                subtotal = order_amount - delivery_fee
                payment_status = "REFUNDED"
                # Prepare notification data
                notification_data = {
                    #"recipient": customer_result.get('email'),
                    "recipient": "chaizheqing2004@gmail.com",  # Hard-code test email
                    "subject": "Order Cancelled and Refund Processed",
                    "subtotal": f"{subtotal:.2f}",  
                    "payment_status": payment_status,
                    "delivery_fee": f"{delivery_fee:.2f}",  
                    "total": f"{order_amount:.2f}",            
                    "message": f"""
                    Your order #{order_id} has been cancelled.
                    A refund of ${order_amount:.2f} has been processed to your wallet.
                    Your new wallet balance is ${new_balance:.2f}.
                    """,
                }

                # Publish notification
                publish_message(
                    routing_key="order.cancel.notification",
                    message=notification_data
                )
                print("Notification queued successfully")

        except Exception as notification_error:
            print(f"Notification error (non-critical): {notification_error}")
            

        # Return success response
        return jsonify({
            "code": 200,
            "data": {
                "order_status": final_update,
                "refund_status": refund_result,
                "message": "Order cancelled successfully and refund processed"
            }
        })

    except Exception as e:
        print(f"Error in cancel_order: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred while cancelling the order: {str(e)}"
        }), 500
    
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for Food Delivery Cancellation")
    app.run(host="0.0.0.0", port=5005, debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from invokes import invoke_http
from firebase_admin import credentials, firestore, initialize_app
import pika

app = Flask(__name__)
CORS(app)

# Initialize Firebase
firebase_config = os.environ.get('FIREBASE_CONFIG')
firebase_config_dict = json.loads(firebase_config)
cred = credentials.Certificate(firebase_config_dict)
initialize_app(cred)
db = firestore.client()

# URLs for other services
ORDER_URL = os.environ.get('orderURL') or "http://order-service:5001"
WALLET_URL = os.environ.get('walletURL') or "http://wallet-service:5002"
CUSTOMER_URL = os.environ.get('customerURL') or "http://customer-service:4000"

@app.route("/health")
def health_check():
    return jsonify({"message": "Service is healthy"}), 200

@app.route("/deliver-food/cancel/<order_id>", methods=['POST'])
def cancel_order(order_id):
    """
    Cancel an order and process refund
    """
    try:
        # Step 1: Get the order details first
        order_result = invoke_http(
            f"{ORDER_URL}/orders/{order_id}",
            method="GET"
        )
        
        if 'error' in order_result:
            return jsonify({
                "code": 404,
                "message": f"Order {order_id} not found."
            }), 404

        # Step 2: Update order status to Failed
        update_result = invoke_http(
            f"{ORDER_URL}/orders/{order_id}/status",
            method="PATCH",
            json={
                "status": "Failed",
                "deliveryStatus": "Failed"
            }
        )
        
        if 'error' in update_result:
            return jsonify({
                "code": 500,
                "message": f"Failed to update order status: {update_result['error']}"
            }), 500

        # Step 3: Process refund to customer's wallet
        customer_id = order_result.get('customerId')
        order_amount = float(order_result.get('price', 0))
        
        # Get current wallet balance
        wallet_result = invoke_http(
            f"{WALLET_URL}/wallet/{customer_id}",
            method="GET"
        )
        
        if 'error' in wallet_result:
            return jsonify({
                "code": 500,
                "message": f"Failed to get wallet: {wallet_result['error']}"
            }), 500

        current_balance = float(wallet_result.get('balance', 0))
        new_balance = current_balance + order_amount

        # Update wallet with refund
        refund_result = invoke_http(
            f"{WALLET_URL}/wallet/{customer_id}",
            method="PUT",
            json={"balance": new_balance}
        )
        
        if 'error' in refund_result:
            return jsonify({
                "code": 500,
                "message": f"Failed to process refund: {refund_result['error']}"
            }), 500

        # Step 4: Final update of order status to Cancelled
        final_update = invoke_http(
            f"{ORDER_URL}/orders/{order_id}/status",
            method="PATCH",
            json={"status": "Cancelled"}
        )

        return jsonify({
            "code": 200,
            "data": {
                "order_status": final_update,
                "refund_status": refund_result
            }
        })

    except Exception as e:
        return jsonify({
            "code": 500,
            "message": f"An error occurred while cancelling the order: {str(e)}"
        }), 500

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for Food Delivery Cancellation")
    app.run(host="0.0.0.0", port=5005, debug=True)
from flask import Flask, request, jsonify
from flask_cors import CORS
from invokes import invoke_http
import os
from os import environ
import uuid
import datetime  # Add this import

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:5173"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": True
     }})

order_URL = environ.get('orderURL') or 'http://localhost:5001/orders'
wallet_URL = environ.get('walletURL') or 'http://localhost:3000'
error_URL = environ.get('errorURL') or 'http://localhost:5002'

@app.route("/create-order", methods=['POST', 'OPTIONS'])
def create_order():
    # Handle preflight request
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    if not request.is_json:
        return jsonify({
            "code": 400,
            "message": "Invalid JSON input: " + str(request.get_data())
        }), 400

    try:
        print('\n=== Creating New Order ===')
        data = request.get_json()
        print('Received order data:', data)

        # Validate required fields
        required_fields = ['custId', 'orderId', 'items', 'address', 'amount']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "code": 400,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Prepare order data
        order_data = {
            'customerId': data['custId'],
            'items': data['items'],
            'deliveryAddress': data['address'],
            'price': data['amount'],
            'status': 'PENDING',
            'paymentStatus': 'PENDING',
            'restaurantId': data.get('restaurantId', 'unknown'),
            'restaurantName': data.get('restaurantName', 'Unknown Restaurant'),
            'orderId': data['orderId'],
            'createdAt': datetime.datetime.utcnow().isoformat(),
            'updatedAt': datetime.datetime.utcnow().isoformat()
        }

        # Create order in order service
        print('\n-----Invoking order microservice-----')
        order_result = invoke_http(
            f"{order_URL}",
            method='POST',
            json=order_data
        )
        print('order_result:', order_result)

        return jsonify({
            "code": 200,
            "data": order_result,
            "message": "Order created successfully"
        }), 200

    except Exception as e:
        print(f"Error in create_order: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred while creating the order: {str(e)}"
        }), 500
     
@app.route("/pay-delivery", methods=['POST'])
def pay_delivery():
    if not request.is_json:
        return jsonify({
            "code": 400,
            "message": "Invalid JSON input: " + str(request.get_data())
        }), 400

    try:
        print('\n=== Processing Payment Request ===')
        data = request.get_json()
        print('Received data:', data)
        
        cust_id = data.get('custId')
        order_id = data.get('orderId')

        if not all([cust_id, order_id]):
            return jsonify({
                "code": 400,
                "message": "Missing customer ID or order ID."
            }), 400
        
        # Get order details from order microservice
        print('\n-----Invoking order microservice-----')
        order_result = invoke_http(
            f"{order_URL}/{order_id}",
            method='GET'
        )
        print('order_result:', order_result)
        
        if order_result.get('code', 200) not in range(200, 300):
            raise ValueError("Order not found")

        # Check if driver is assigned
        if not order_result.get('data', {}).get('driverId'):
            return jsonify({
                "code": 400,
                "message": "Cannot process payment: Driver not yet assigned"
            }), 400

        price = order_result.get('data', {}).get('price')
        if not price:
            raise ValueError("Invalid order: price not found")

        # Process payment through wallet microservice
        print('\n-----Invoking wallet microservice-----')
        wallet_result = invoke_http(
            f"{wallet_URL}/wallet/{cust_id}/process-payment",
            method='POST',
            json={
                "amount": price,
                "orderId": order_id
            }
        )
        print('wallet_result:', wallet_result)

        if wallet_result.get('error'):
            # Update order status to payment failed
            invoke_http(
                f"{order_URL}/{order_id}/status",
                method='PATCH',
                json={"status": "PAYMENT_FAILED"}
            )
            raise ValueError(wallet_result.get('error'))

        # Update order status to paid
        invoke_http(
            f"{order_URL}/{order_id}/status",
            method='PATCH',
            json={"status": "PAID"}
        )

        return jsonify({
            "code": 200,
            "data": {
                "order_result": order_result,
                "wallet_result": wallet_result
            },
            "message": "Payment processed successfully"
        }), 200

    except Exception as e:
        print(f"Error in pay_delivery: {str(e)}")
        error_id = str(uuid.uuid4())
        error_details = {
            "errorId": error_id,
            "custId": cust_id if 'cust_id' in locals() else None,
            "orderId": order_id if 'order_id' in locals() else None,
            "message": str(e)
        }

        print('\n-----Publishing error to error service-----')
        error_result = invoke_http(
            error_URL,
            method="POST",
            json=error_details
        )
        print('error_result:', error_result)

        return jsonify({
            "code": 500,
            "message": f"An error occurred while processing the payment: {str(e)}"
        }), 500

@app.route("/user-profile/<user_id>", methods=['GET'])
def get_user_profile(user_id):
    try:
        print(f'\n-----Fetching profile for user: {user_id}-----')
        
        # Get user profile from wallet service
        wallet_response = invoke_http(
            f"{wallet_URL}/users/{user_id}",
            method='GET'
        )
        
        # Get wallet balance
        balance_response = invoke_http(
            f"{wallet_URL}/wallet/{user_id}",
            method='GET'
        )
        
        print('Wallet service responses:', wallet_response, balance_response)
        
        if isinstance(wallet_response, dict):
            if wallet_response.get('error'):
                return jsonify({
                    "code": 404,
                    "message": wallet_response['error']
                }), 404
            
            # Combine profile and balance data
            response_data = {
                "uid": user_id,
                "address": wallet_response.get('address', ''),
                "name": wallet_response.get('name', ''),
                "email": wallet_response.get('email', ''),
                "balance": balance_response.get('balance', 0.0)
            }
            
            return jsonify({
                "code": 200,
                "data": response_data
            }), 200
                
        return jsonify({
            "code": 500,
            "message": f"Unexpected response format from wallet service"
        }), 500

    except Exception as e:
        print(f"Error in get_user_profile: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"Service error: {str(e)}"
        }), 500
    
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for handling payment")
    app.run(host="0.0.0.0", port=5003, debug=True)
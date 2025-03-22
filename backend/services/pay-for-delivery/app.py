from flask import Flask, request, jsonify
from flask_cors import CORS
from invokes import invoke_http
import os
from os import environ
import uuid
from datetime import datetime, timezone, timedelta
import json 

app = Flask(__name__)
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:5173"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": True
     }})

PORT = int(os.environ.get('PORT', 5004))
order_URL = environ.get('orderURL') or 'http://localhost:5001'
wallet_URL = environ.get('walletURL') or 'http://localhost:5002'
error_URL = environ.get('errorURL') or 'http://localhost:5003'

@app.route("/create-order", methods=['POST', 'OPTIONS'])
def create_order():
    # Handle preflight request
    sg_timezone = timezone(timedelta(hours=8))
    current_sg_time = datetime.now(sg_timezone)
    timestamp = current_sg_time.isoformat()
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

        # Get restaurant info from first item only
        first_item = data['items'][0]
        restaurant_info = {
            'restaurantId': first_item.get('restaurant', {}).get('id', 'unknown'),
            'restaurantName': first_item.get('restaurant', {}).get('name', 'Unknown Restaurant')
        }

        # Clean up items to remove redundant restaurant info
        cleaned_items = []
        for item in data['items']:
            cleaned_item = {
                'id': item['id'],
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity']
            }
            cleaned_items.append(cleaned_item)

        # Prepare order data with cleaned structure
        order_data = {
            'customerId': data['custId'],
            'orderId': data['orderId'],
            'items': cleaned_items,
            'deliveryAddress': data['address'],
            'price': data['amount'],
            'driverId': None,
            'driverStatus': 'PENDING',
            'paymentStatus': 'PENDING',
            'status': 'PENDING', 
            'restaurantId': restaurant_info['restaurantId'],
            'restaurantName': restaurant_info['restaurantName'],
            'createdAt': timestamp,
            'updatedAt': timestamp
        }

        print('\n-----Invoking order microservice-----')
        order_result = invoke_http(
            f"{order_URL}/orders",
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
            f"{order_URL}/orders/{order_id}",
            method='GET'
        )
        print('order_result:', order_result)
        
        if 'error' in order_result:
            raise ValueError(order_result['error'])

        # Check if driver is assigned
        if not order_result.get('driverId'):  # Changed this line
            return jsonify({
                "code": 400,
                "message": "Cannot process payment: Driver not yet assigned"
            }), 400

        price = order_result.get('price')  # Changed this line
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
            # Update payment status to failed
            invoke_http(
                f"{order_URL}/orders/{order_id}/status",
                method='PATCH',
                json={
                    "paymentStatus": "PAYMENT_FAILED",
                    "status": "PAYMENT_FAILED"
                }
            )
            raise ValueError(wallet_result.get('error'))

        # Update payment status to paid
        invoke_http(
            f"{order_URL}/orders/{order_id}/status",
            method='PATCH',
            json={
                "paymentStatus": "PAID",
                "status": "PAID"
            }
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
            
            # Pass through ALL fields from wallet service
            response_data = {
                "uid": user_id,
                "address": wallet_response.get('address', ''),
                "name": wallet_response.get('name', ''),
                "email": wallet_response.get('email', ''),
                "phone": wallet_response.get('phone', ''),
                "balance": balance_response.get('balance', 0.0)
            }
            
            print('Processed response data:', response_data)
            
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
    app.run(host="0.0.0.0", port=PORT, debug=True)
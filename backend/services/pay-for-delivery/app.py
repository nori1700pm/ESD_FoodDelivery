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
customer_URL = environ.get('customerURL') or 'http://localhost:4000'

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
            'restaurantId': (
                first_item.get('restaurantId') or 
                first_item.get('restaurant', {}).get('id') or 
                'unknown'
            ),
            'restaurantName': (
                first_item.get('restaurantName') or 
                first_item.get('restaurant', {}).get('name') or 
                'Unknown Restaurant'
            )
        }
        print("Extracted restaurant info:", json.dumps(restaurant_info, indent=2))  # Debug log
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
        
        # Validate required fields
        required_fields = ['custId', 'orderId', 'amount', 'items', 'address', 'restaurantId', 'restaurantName']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "code": 400,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Process payment through wallet microservice first
        print('\n-----Invoking wallet microservice-----')
        wallet_result = invoke_http(
            f"{wallet_URL}/wallet/{data['custId']}/process-payment",
            method='POST',
            json={
                "amount": data['amount'],
                "orderId": data['orderId']
            }
        )
        print('wallet_result:', wallet_result)

        if wallet_result.get('error'):
            # Payment failed - return error message
            return jsonify({
                "code": 400,
                "message": "Insufficient balance",
                "data": wallet_result
            }), 400

        # Payment successful - create order
        print('\n-----Creating order-----')
        sg_timezone = timezone(timedelta(hours=8))
        current_sg_time = datetime.now(sg_timezone)
        timestamp = current_sg_time.isoformat()

        # Clean up items
        cleaned_items = []
        for item in data['items']:
            cleaned_item = {
                'id': item['id'],
                'name': item['name'],
                'price': item['price'],
                'quantity': item['quantity']
            }
            cleaned_items.append(cleaned_item)

        # Prepare order data
        order_data = {
            'customerId': data['custId'],
            'orderId': data['orderId'],
            'items': cleaned_items,
            'deliveryAddress': data['address'],
            'price': data['amount'],
            'driverId': None,
            'driverStatus': 'PENDING',
            'paymentStatus': 'PAID',  # Set as PAID since payment successful
            'status': 'PAID',  # Set as PAID since payment successful
            'restaurantId': data['restaurantId'],
            'restaurantName': data['restaurantName'],
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

        if isinstance(order_result, dict) and order_result.get('error'):
            # Order creation failed
            return jsonify({
                "code": 500,
                "message": f"Payment successful but order creation failed: {order_result.get('error')}",
                "data": {
                    "wallet_result": wallet_result,
                    "order_error": order_result
                }
            }), 500

        return jsonify({
            "code": 200,
            "data": {
                "wallet_result": wallet_result,
                "order_result": order_result
            },
            "message": "Payment processed and order created successfully"
        }), 200

    except Exception as e:
        print(f"Error in pay_delivery: {str(e)}")
        error_id = str(uuid.uuid4())
        error_details = {
            "errorId": error_id,
            "custId": data['custId'] if 'data' in locals() else None,
            "orderId": data['orderId'] if 'data' in locals() else None,
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
        customer_response = invoke_http(
            f"{customer_URL}/customers/{user_id}",
            method='GET'
        )
        
        # Get wallet balance
        balance_response = invoke_http(
            f"{wallet_URL}/wallet/{user_id}",
            method='GET'
        )
        
        print('Wallet service responses:', customer_response, balance_response)
        
        if isinstance(customer_response, dict):
            if customer_response.get('error'):
                return jsonify({
                    "code": 404,
                    "message": customer_response['error']
                }), 404
            
            # Pass through ALL fields from wallet service
            response_data = {
                "uid": user_id,
                "address": customer_response.get('address', ''),
                "name": customer_response.get('name', ''),
                "email": customer_response.get('email', ''),
                "phone": customer_response.get('phone', ''),
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
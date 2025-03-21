# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from invokes import invoke_http
# import os  # Change this line
# from os import environ  # Keep this line if you want both
# import uuid


# app = Flask(__name__)
# CORS(app)

# # URLs for the microservices
# order_URL = environ.get('orderURL') or 'http://localhost:5001/order'
# wallet_URL = environ.get('walletURL') or 'http://localhost:3000/wallet'
# error_URL = environ.get('errorURL') or 'http://localhost:5002/error'

# @app.route("/pay-delivery", methods=['POST'])
# def pay_delivery():
#     if not request.is_json:
#         return jsonify({
#             "code": 400,
#             "message": "Invalid JSON input: " + str(request.get_data())
#         }), 400

#     try:
#         data = request.get_json()
#         cust_id = data.get('custId')
#         order_id = data.get('orderId')

#         if not all([cust_id, order_id]):
#             return jsonify({
#                 "code": 400,
#                 "message": "Missing customer ID or order ID."
#             }), 400

#         # 2. Get order details from order microservice
#         print('\n-----Invoking order microservice-----')
#         order_result = invoke_http(
#             f"{order_URL}/{order_id}",
#             method='GET'
#         )
#         print('order_result:', order_result)

#         # Check the order service invoke result
#         code = order_result.get('code', 200)
#         if code not in range(200, 300):
#             return jsonify({
#                 "code": 400,
#                 "message": "Order not found."
#             }), 400

#         # Extract price from order details
#         price = order_result.get('data', {}).get('price')
#         if not price:
#             return jsonify({
#                 "code": 400,
#                 "message": "Invalid order: price not found"
#             }), 400

#         # 4. Process payment through wallet microservice
#         print('\n-----Invoking wallet microservice-----')
#         wallet_result = invoke_http(
#             f"{wallet_URL}/{cust_id}/process-payment",
#             method='POST',
#             json={
#                 "amount": price,
#                 "orderId": order_id
#             }
#         )
#         print('wallet_result:', wallet_result)

#         # Check if payment was successful
#         if wallet_result.get('error'):
#             # 6. Send payment error to error microservice
#             error_id = str(uuid.uuid4())
#             error_details = {
#                 "errorId": error_id,
#                 "custId": cust_id,
#                 "orderId": order_id,
#                 "message": wallet_result.get('error')
#             }
            
#             print('\n-----Publishing the error message with routing key-----')
#             error_result = invoke_http(
#                 error_URL,
#                 method="POST",
#                 json=error_details
#             )
#             print('error_result:', error_result)

#             return jsonify({
#                 "code": 400,
#                 "data": {
#                     "order_result": order_result,
#                     "wallet_result": wallet_result,
#                     "error_result": error_result
#                 },
#                 "message": "Payment failed due to insufficient balance."
#             }), 400

#         # Return success response
#         return jsonify({
#             "code": 200,
#             "data": {
#                 "order_result": order_result,
#                 "wallet_result": wallet_result
#             },
#             "message": "Payment processed successfully."
#         }), 200

#     except Exception as e:
#         # Unexpected error
#         error_id = str(uuid.uuid4())
#         error_details = {
#             "errorId": error_id,
#             "custId": cust_id if 'cust_id' in locals() else None,
#             "orderId": order_id if 'order_id' in locals() else None,
#             "message": str(e)
#         }

#         print('\n-----Publishing the error message-----')
#         error_result = invoke_http(
#             error_URL,
#             method="POST",
#             json=error_details
#         )
#         print('error_result:', error_result)

#         return jsonify({
#             "code": 500,
#             "message": f"An error occurred while processing the payment: {str(e)}"
#         }), 500

# if __name__ == "__main__":
#     print("This is flask " + os.path.basename(__file__) + " for handling payment")
#     app.run(host="0.0.0.0", port=5003, debug=True)

from flask import Flask, request, jsonify
from flask_cors import CORS
from invokes import invoke_http
import os
from os import environ
import uuid

app = Flask(__name__)
CORS(app)

# URLs for the microservices
wallet_URL = environ.get('walletURL') or 'http://localhost:3000'
error_URL = environ.get('errorURL') or 'http://localhost:5002'
#order_URL = environ.get('orderURL')

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
        
        # Extract required fields
        cust_id = data.get('custId')
        order_id = data.get('orderId')
        amount = float(data.get('amount', 0))

        if not all([cust_id, order_id, amount]):
            missing_fields = []
            if not cust_id: missing_fields.append('custId')
            if not order_id: missing_fields.append('orderId')
            if not amount: missing_fields.append('amount')
            
            return jsonify({
                "code": 400,
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Process payment through wallet microservice
        print('\n-----Invoking wallet microservice-----')
        wallet_result = invoke_http(
            f"{wallet_URL}/wallet/{cust_id}/process-payment",
            method='POST',
            json={
                "amount": amount,
                "orderId": order_id
            }
        )
        print('wallet_result:', wallet_result)

        # Check if payment was successful
        if wallet_result.get('error'):
            error_id = str(uuid.uuid4())
            error_details = {
                "errorId": error_id,
                "custId": cust_id,
                "orderId": order_id,
                "message": wallet_result.get('error')
            }
            
            print('\n-----Publishing error to error service-----')
            error_result = invoke_http(
                error_URL,
                method="POST",
                json=error_details
            )
            print('error_result:', error_result)

            return jsonify({
                "code": 400,
                "data": {
                    "wallet_result": wallet_result,
                    "error_result": error_result
                },
                "message": wallet_result.get('error')
            }), 400

        # Return success response
        return jsonify({
            "code": 200,
            "data": {
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
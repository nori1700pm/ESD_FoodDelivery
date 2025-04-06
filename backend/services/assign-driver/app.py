from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from invokes import invoke_http  
import rabbitmq.amqp_lib as amqp_lib
import pika 
import threading  
import time  
from datetime import datetime, timezone, timedelta  

app = Flask(__name__)
CORS(app)

# Service URLs
ORDER_URL = os.environ.get('orderURL', "http://order-service:5001")
DRIVER_URL = os.environ.get('driverURL', "https://personal-shkrtsry.outsystemscloud.com/DriverServiceModule/rest/NomNomGo")
WALLET_URL = os.environ.get('walletURL', "http://wallet-service:5002")
CUSTOMER_URL = os.environ.get('customerURL', "http://customer-service:4000")

# Rabbit MQ variable
RABBITMQ_PORT = int(os.environ.get('RABBITMQ_PORT', 5672))
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
PORT = int(os.environ.get('PORT', 5002)) 

exchange_name = "order_topic"
exchange_type = "topic"
queue_name = "notification_queue"  


def fetch_and_update_driver(restaurant_id):
    # Update the driver availability check
    try:
        # Get available drivers for the restaurant using new endpoint
        available_drivers = invoke_http(f"{DRIVER_URL}/status/{restaurant_id}", method="GET")
        if not available_drivers or not available_drivers.get('FullResult'):
            return None, {"message": "No available drivers"}, 404
            
        sorted_drivers = sorted(available_drivers['FullResult'], key=lambda x: float(x.get('Distance', float('inf'))))
        
        available_driver = None
        for driver in sorted_drivers:
            if driver.get('DriverStatus', '').upper() == 'AVAILABLE':
                available_driver = driver
                break
                
        if not available_driver:
            return None, {"message": "No available drivers found"}, 404
            
        driver_id = available_driver['DriverId']
        
        # Update driver status to busy
        driver_update = invoke_http(
            f"{DRIVER_URL}/drivers",
            method="PUT",
            json={
                "DriverId": driver_id,
                "DriverStatus": "Busy",
                "DriverName": available_driver.get("DriverName", ""),
                "DriverNumber": available_driver.get("DriverNumber", 0),
                "DriverLocation": available_driver.get("DriverLocation", ""),
                "DriverEmail": available_driver.get("DriverEmail", "")
            }
        )

        if not driver_update or not driver_update.get('Success', False):
            return None, {
                "message": f"Failed to update driver status: {driver_update.get('ErrorMessage', 'Unknown error')}"
            }, 500
            
        return driver_id, None, None

    except Exception as e:
        return None, {"message": f"Error assigning driver: {str(e)}"}, 500
    
def schedule_order_cancellation(order_id):
    """Schedule order cancellation after 15 minutes if still pending"""
    def cancel_after_delay():
        time.sleep(900)  #15 minutes
        # time.sleep(120) # 2 mins for testing
        # Check current order status
        try:
            order_result = invoke_http(
                f"{ORDER_URL}/orders/{order_id}",
                method="GET"
            )
            
            if order_result.get('status') == 'PREPARING':
                # Cancel the order
                cancel_order(order_id)
        except Exception as e:
            print(f"Error in scheduled cancellation for order {order_id}: {str(e)}")
    
    # Start cancellation thread
    thread = threading.Thread(target=cancel_after_delay, daemon=True)
    thread.start()

def update_order(order_id, driver_id):
    # Extract OrderID from the request payload
    try:
        # request_data = request.get_json()
        # order_id = request_data.get("OrderID")  # Ensure OrderID is included in the request payload

        # if not order_id:
        #     return {"message": "OrderID is missing in the request payload"}, 400

        # Update the specific order with driver info and status
        order_update = invoke_http(
            f"{ORDER_URL}/orders/{order_id}/status",  
            method="PUT",
            json={
                "status": "PREPARING",
                "driverId": driver_id,
                "driverStatus": "PENDING" if driver_id is None else "ASSIGNED"
            }
        )

        if 'error' in order_update:
            return {"message": f"Failed to update order: {order_update['error']}"}, 500
            
        return order_update, None
        
    except Exception as e:
        print(f"Error in update_order: {str(e)}")  
        return {"message": f"Error updating order: {str(e)}"}, 500


# RabbitMQ  - for successful driver assignment
def send_notification(driver_id, order_id, customer_id): 
    try:
        print(f"\n=== Retrieving order {order_id} ===")
        order_result = invoke_http(
            f"{ORDER_URL}/orders/{order_id}",
            method="GET"
        )
        print("Order result:", order_result)

        # Get customer details
        print(f"\nFetching customer details from {CUSTOMER_URL}/customers/{customer_id}")
        customer_result = invoke_http(
            f"{CUSTOMER_URL}/customers/{customer_id}",
            method="GET"
        )
        print("Customer result:", customer_result)
        
        if not order_result or 'error' in order_result:
            print(f"Order not found or error: {order_result}")
            return jsonify({
                "code": 404,
                "message": f"Order {order_id} not found or error occurred."
            }), 404
        
        order_amount = float(order_result.get('price', 0))
        delivery_fee = float(order_result.get('deliveryFee', 0))
        subtotal = order_amount - delivery_fee
        payment_status = "PAID"

        order_info = {
            "recipient": customer_result.get('email'),
            # "recipient": "chaizheqing2004@gmail.com",  
            "order_id": order_id,
            "driver_id": driver_id,
            "subject": "Thanks for your order",
            "subtotal": f"{subtotal:.2f}",  
            "payment_status": payment_status,
            "delivery_fee": f"{delivery_fee:.2f}",  
            "total": f"{order_amount:.2f}",            
            "items": [
                {
                    "item_name": item.get("name"),
                    "item_qty": item.get("quantity"),
                    "item_price": f"{item.get('price', 0):.2f}",
                    "img_src": item.get('image')
                }
                for item in order_result.get("items", [])
            ]
        }

        print("  Connecting to AMQP broker...")
        connection, channel = amqp_lib.connect(
            hostname=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            exchange_name='order_topic',
            exchange_type='topic',
        )

        print("Publishing driver assignment message to notification queue")
        channel.basic_publish(
            exchange='order_topic',
            routing_key='driver.assigned.notification',
            body=json.dumps(order_info),
            properties=pika.BasicProperties(delivery_mode=2)
        )

        connection.close()

        print("Message sent successfully")
        return True
    except Exception as e:
        print(f"Error sending notification: {str(e)}")  
        return None

# Main endpoint
@app.route("/assign/<order_id>", methods=['POST'])
def assign_driver(order_id):
    """
    Main endpoint to assign a driver to an order
    """
    try:
        # First get the order details to get restaurant_id
        order_details = invoke_http(
            f"{ORDER_URL}/orders/{order_id}",
            method="GET"
        )
        
        if 'error' in order_details:
            return jsonify({
                "code": 404,
                "message": f"Order not found: {order_details['error']}"
            }), 404
            
        restaurant_id = order_details.get('restaurantId')
        if not restaurant_id:
            return jsonify({
                "code": 400,
                "message": "Order does not have a restaurant ID"
            }), 400
            
        # Step 1: Fetch and update driver status
        driver_id, error_response, error_code = fetch_and_update_driver(restaurant_id)
        if error_response and error_code == 404:

            # No available drivers - set order to pending and schedule auto-cancellation
            update_order(order_id, None)
            schedule_order_cancellation(order_id)
            check_and_assign_driver(order_id, restaurant_id)
            return jsonify({
                "code": 202,
                "message": "No drivers currently available. Will assign when one becomes available."
            }), 202
        elif error_response:
            return jsonify({
                "code": error_code,
                "message": error_response['message']
            }), error_code
        
        # Step 2: Update order with driver information
        order_update, error = update_order(order_id, driver_id)
        if error:
            return jsonify({
                "code": 500,
                "message": error['message']
            }), 500
        
        # Step 3: Send notification 
        send_notification(driver_id, order_id, order_details.get('customerId'))
        
        return jsonify({
            "code": 200,
            "data": {
                "order_update": order_update,
                "driver_id": driver_id
            },
            "message": "Driver assigned successfully" if driver_id else "Order set to pending"
        }), 200


    except Exception as e:
        print(f"Error in assign_driver: {str(e)}") 
        return jsonify({
            "code": 500,
            "message": f"An error occurred while assigning driver: {str(e)}"
        }), 500

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
        sg_timezone = timezone(timedelta(hours=8)) # Define the Singapore timezone
        current_sg_time = datetime.now(sg_timezone)
        timestamp = current_sg_time.strftime('%Y-%m-%d %H:%M:%S')
        update_data = {
            "status": "CANCELLED",
            "paymentStatus": "REFUNDED",
            "driverStatus": 'CANCELLED',  
            "updatedAt": timestamp
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
                # Prepare notification data
                notification_data = {
                    "recipient": customer_result.get('email'),  
                    "subject": "Order Cancelled and Refund Processed",
                    "subtotal": f"{subtotal:.2f}",  
                    "payment_status": "REFUNDED",
                    "delivery_fee": f"{delivery_fee:.2f}",  
                    "total": f"{order_amount:.2f}",            
                    "message": f"""
                    Your order #{order_id} has been cancelled.
                    A refund of ${order_amount:.2f} has been processed to your wallet.
                    Your new wallet balance is ${new_balance:.2f}.
                    """
                }

                # Publish notification
                print("  Connecting to AMQP broker...")
                connection, channel = amqp_lib.connect(
                    hostname=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    exchange_name='order_topic',
                    exchange_type='topic',
                )

                # Publish to RabbitMQ
                channel.basic_publish(
                    exchange='order_topic',
                    routing_key='order.cancel.notification',
                    body=json.dumps(notification_data),
                    properties=pika.BasicProperties(delivery_mode=2)
                )

                connection.close()
                print("Notification queued successfully")

        except Exception as notification_error:
            print(f"Notification error (non-critical): {notification_error}")

        # Return success response
        return jsonify({
            "code": 200,
            "data": {
                "order_status": final_update,
                "refund_status": refund_result,
                "message": "Order cancelled and refund processed"
            }
        })

    except Exception as e:
        print(f"Error in cancel_order: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred while cancelling the order: {str(e)}"
        }), 500

def check_and_assign_driver(order_id, restaurant_id):
    """Continuously check for available drivers and assign when found"""
    def check_driver_loop():
        while True:
            try:
                # Get current order status
                order_result = invoke_http(
                    f"{ORDER_URL}/orders/{order_id}",
                    method="GET"
                )
                
                # If order is cancelled or already has a driver, stop checking
                if (order_result.get('status') in ['CANCELLED', 'DELIVERED', 'COMPLETED'] or 
                    order_result.get('driverStatus') != 'PENDING'):
                    break
                
                # Try to get an available driver
                driver_id, error_response, error_code = fetch_and_update_driver(restaurant_id)
                
                if driver_id:  # If we found an available driver
                    # Update order with the new driver
                    update_order(order_id, driver_id)
                    print(f"Successfully assigned driver {driver_id} to order {order_id}")
                    send_notification(driver_id, order_id, order_result.get('customerId'))

                    break
                    
                # Wait before checking again
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in check_driver_loop for order {order_id}: {str(e)}")
                time.sleep(30)  # Wait before retrying after error
    
    # Start the checking thread
    thread = threading.Thread(target=check_driver_loop, daemon=True)
    thread.start()

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for assigning drivers")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5006)), debug=True)

    
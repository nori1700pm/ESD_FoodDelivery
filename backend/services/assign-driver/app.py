from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from invokes import invoke_http  

app = Flask(__name__)
CORS(app)

# Service URLs
ORDER_URL = os.environ.get('orderURL', "http://order-service:5001")
NOTIFICATION_URL = os.environ.get('notificationURL', "http://notification-service:6000")
DRIVER_URL = os.environ.get('driverURL', "https://personal-shkrtsry.outsystemscloud.com/DriverServiceModule/rest/NomNomGo")

def fetch_and_update_driver(restaurant_id):
    # get available drivers
    try:
        available_drivers = invoke_http(f"{DRIVER_URL}/nearestDriver/{restaurant_id}", method="GET")
        if not available_drivers:  # Check for empty response
            return None, {"message": "No available drivers"}, 404
            
        # get driver ID from  response
        driver_id = available_drivers['Location']['driverId']

        # Select first available driver
        # selected_driver = available_drivers[0]
        # driver_id = selected_driver.get("DriverID")
        
        driver_details = invoke_http(
            f"{DRIVER_URL}/getDriversById?Id={driver_id}",
            method="GET"
        )
        
        if not driver_details or not driver_details.get('Driver'):
            return None, {"message": "Failed to get driver details"}, 500

        driver_info = driver_details['Driver']

        # Check if driver is actually available
        if driver_info.get('DriverStatus', '').upper() != 'AVAILABLE':
            
            # Get all drivers for this restaurant
            all_drivers = invoke_http(
                f"{DRIVER_URL}/nearestDrivers/{restaurant_id}",
                method="GET"
            )
            
            if not all_drivers or 'Locations' not in all_drivers:
                return None, {"message": "No other available drivers found"}, 404
                
            # Find the first available driver
            available_driver = None
            for driver_location in all_drivers['Locations']:
                temp_driver_id = driver_location['driverId']
                temp_driver_details = invoke_http(
                    f"{DRIVER_URL}/getDriversById?Id={temp_driver_id}",
                    method="GET"
                )
                
                if (temp_driver_details and 
                    temp_driver_details.get('Driver') and 
                    temp_driver_details['Driver'].get('DriverStatus', '').upper() == 'AVAILABLE'):
                    available_driver = temp_driver_details['Driver']
                    driver_id = temp_driver_id
                    driver_info = available_driver
                    break
            
            if not available_driver:
                return None, {"message": "No available drivers found"}, 404
            
        # update driver status to 'busy'
        driver_update = invoke_http(
            f"{DRIVER_URL}/drivers",
            method="PUT",
            json={
                "DriverId": driver_id,
                "DriverStatus": "Busy",
                "DriverName": driver_info.get("DriverName", ""),
                "DriverNumber": driver_info.get("DriverNumber", 0),
                "DriverLocation": driver_info.get("DriverLocation", ""),
                "DriverEmail": driver_info.get("DriverEmail", "")
            }
        )

        if not driver_update or not driver_update.get('Success', False):
                return None, {
                    "message": f"Failed to update driver status: {driver_update.get('ErrorMessage', 'Unknown error')}"
                }, 500
            
        return driver_id, None, None

    except Exception as e:
        return None, {"message": f"Error assigning driver: {str(e)}"}, 500

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
                "driverStatus": "ASSIGNED"
            }
        )

        if 'error' in order_update:
            return {"message": f"Failed to update order: {order_update['error']}"}, 500
            
        return order_update, None
        
    except Exception as e:
        print(f"Error in update_order: {str(e)}")  
        return {"message": f"Error updating order: {str(e)}"}, 500

def send_notification(driver_id, order_id): #not done yet
    try:
        notification_response = invoke_http(
            f"{NOTIFICATION_URL}/notify",
            method="POST",
            json={"DriverID": driver_id, "OrderID": order_id}
        )
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
        if error_response:
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
        send_notification(driver_id, order_id)
        
        return jsonify({
            "code": 200,
            "data": {
                "order_update": order_update,
                "driver_id": driver_id
            },
            "message": "Driver assigned successfully"
        }), 200

    except Exception as e:
        print(f"Error in assign_driver: {str(e)}") 
        return jsonify({
            "code": 500,
            "message": f"An error occurred while assigning driver: {str(e)}"
        }), 500

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for assigning drivers")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5006)), debug=True)

    
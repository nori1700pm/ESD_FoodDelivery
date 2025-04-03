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

def fetch_and_update_driver():
    # Fetch available drivers
    available_drivers = invoke_http(f"{DRIVER_URL}/drivers/available", method="GET")
    if not available_drivers:  # Check for empty response
        return None, {"message": "No available drivers"}, 404
    
    # Select first available driver
    selected_driver = available_drivers[0]
    driver_id = selected_driver.get("DriverID")
    
    # Update driver status to 'out for delivery'
    driver_update = invoke_http(
        f"{DRIVER_URL}/drivers/{driver_id}/status",
        method="PUT",
        json={"status": "BUSY"}
    )
    if driver_update.get("status") != "success":
        return None, {"message": "Failed to update driver status"}, 500
    
    return driver_id, None, None  # Return driver ID on success

def update_order(driver_id):
    # Extract OrderID from the request payload
    request_data = request.get_json()
    order_id = request_data.get("OrderID")  # Ensure OrderID is included in the request payload

    if not order_id:
        return {"message": "OrderID is missing in the request payload"}, 400

    # Update the specific order with driver info and status
    order_update = invoke_http(
        f"{ORDER_URL}/orders/{order_id}/update",  # Target the correct OrderID
        method="PUT",
        json={"DriverID": driver_id, "Status": "OUT FOR DELIVERY"}
    )

    if not order_update or order_update.get("status") != "success":
        return {"message": "Failed to update order"}, 500

    return order_update  # Return the updated order info

def send_notification(driver_id, order_id):
    # Notify relevant parties
    invoke_http(
        f"{NOTIFICATION_URL}/notify",
        method="POST",
        json={"DriverID": driver_id, "OrderID": order_id}
    )

# Main endpoint
@app.route("/assign-driver", methods=['POST'])
def assign_driver():
    # Step 1: Fetch and update driver status
    driver_id, error_response, error_code = fetch_and_update_driver()
    if error_response:
        return jsonify(error_response), error_code
    
    # Step 2: Update order with driver information
    order_update = update_order(driver_id)
    
    # Step 3: Send notification
    # send_notification(driver_id, order_update.get("OrderID"))
    
    return jsonify({
        "message": "Driver assigned successfully",
        "DriverID": driver_id
    }), 200

if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for assigning drivers")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5006)), debug=True)

    
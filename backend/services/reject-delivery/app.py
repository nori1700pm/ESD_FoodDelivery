from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from invokes import invoke_http
from firebase_admin import credentials, firestore, initialize_app
import time
from datetime import datetime, timedelta
import threading

app = Flask(__name__)
CORS(app)

# Initialize Firebase
firebase_config = os.environ.get('FIREBASE_CONFIG')
firebase_config_dict = json.loads(firebase_config)
cred = credentials.Certificate(firebase_config_dict)
initialize_app(cred)
db = firestore.client()

# Service URLs - get from environment variables or use defaults
ORDER_URL = os.environ.get('orderURL') or "http://order-service:5001"
DRIVERS_URL = os.environ.get('driversURL') or "https://personal-shkrtsry.outsystemscloud.com/DriverServiceModule/rest/NomNomGo"
ASSIGN_DRIVER_URL = os.environ.get('assignDriverURL') or "http://assign-driver:5006"

def update_driver_status(driver_id, status, driver_info=None):
    try:
        # Construct the request body with consistent status casing
        request_body = {
            "DriverId": int(driver_id),
            "DriverStatus": status.upper(),  # Ensure consistent uppercase status
            "DriverName": driver_info.get("DriverName", ""),
            "DriverNumber": driver_info.get("DriverNumber", 0),
            "DriverLocation": driver_info.get("DriverLocation", ""),
            "DriverEmail": driver_info.get("DriverEmail", "")  
        }
        
        # Use consistent endpoint
        return invoke_http(
            f"{DRIVERS_URL}/drivers",
            method="PUT",
            json=request_body
        )
    except Exception as e:
        print(f"Error updating driver status: {str(e)}")
        return {"error": str(e)}

def set_driver_available_after_delay(driver_id, driver_info):
    """Background task to update driver status after delay"""
    try:
        print(f"Starting 5-minute timer for driver {driver_id}")
        time.sleep(300)  # 5 minutes
        print(f"Timer finished - Setting driver {driver_id} back to AVAILABLE")
        
        # Use the same endpoint and format as the main update
        response = invoke_http(
            f"{DRIVERS_URL}/drivers",
            method="PUT",
            json={
                "DriverId": int(driver_id),
                "DriverStatus": "Available",
                "DriverName": driver_info.get("DriverName", ""),
                "DriverNumber": driver_info.get("DriverNumber", 0),
                "DriverLocation": driver_info.get("DriverLocation", ""),
                "DriverEmail": driver_info.get("DriverEmail", "")
            }
        )
        print(f"Update driver status response: {response}")
        
    except Exception as e:
        print(f"Error in set_driver_available_after_delay: {str(e)}")

@app.route("/reject-delivery/<order_id>/<driver_id>", methods=['POST'])
def reject_delivery(order_id, driver_id):
    try:
        # Step 1: Get current order details (unchanged)
        order_result = invoke_http(
            f"{ORDER_URL}/orders/{order_id}",
            method="GET"
        )
        
        if 'error' in order_result:
            return jsonify({
                "code": 404,
                "message": f"Order {order_id} not found."
            }), 404

        # Step 2: Get current driver details using getDriversById
        driver_result = invoke_http(
            f"{DRIVERS_URL}/getDriversById?Id={driver_id}",
            method="GET"
        )

        print(f"Current driver status: {driver_result}")  # Debug log

        if not driver_result or not driver_result.get('Driver'):
            return jsonify({
                "code": 404,
                "message": f"Driver information not found."
            }), 404

        # Step 3: Update order status 
        order_update = invoke_http(
            f"{ORDER_URL}/orders/{order_id}/status",
            method="PUT",
            json={
                "status": "PREPARING",
                "driverId": None,
                "driverStatus": "PENDING"
            }
        )
                
        if 'error' in order_update:
            return jsonify({
                "code": 500,
                "message": f"Failed to update order: {order_update['error']}"
            }), 500

        # Step 4: Set driver status to BUSY with consistent casing
        print(f"Setting driver {driver_id} to BUSY")  
        driver_update = invoke_http(
            f"{DRIVERS_URL}/drivers",
            method="PUT",
            json={
                "DriverId": int(driver_id),
                "DriverStatus": "Busy",  
                "DriverName": driver_result.get('Driver', {}).get('DriverName', ''),
                "DriverNumber": driver_result.get('Driver', {}).get('DriverNumber', 0),
                "DriverLocation": driver_result.get('Driver', {}).get('DriverLocation', ''),
                "DriverEmail": driver_result.get('Driver', {}).get('DriverEmail', '') 
            }
        )
        print(f"Driver update response: {driver_update}")  

        if 'error' in driver_update:
            return jsonify({
                "code": 500,
                "message": f"Failed to update driver status"
            }), 500

        # Pass driver info to the background thread
        thread = threading.Thread(
            target=set_driver_available_after_delay,
            args=(driver_id, driver_result.get('Driver', {})),
            daemon=True
        )
        thread.start()
        print(f"Started background thread for driver {driver_id}") 

        # Step 5: Trigger reassignment of driver
        assign_result = invoke_http(
            f"{ASSIGN_DRIVER_URL}/assign/{order_id}",
            method="POST"
        )

        return jsonify({
            "code": 200,
            "data": {
                "order_status": order_update,
                "driver_status": driver_update,
                "assign_result": assign_result
            },
            "message": "Delivery rejected successfully. Finding new driver."
        })

    except Exception as e:
        print(f"Error in reject_delivery: {str(e)}")
        return jsonify({
            "code": 500,
            "message": f"An error occurred while processing the rejection: {str(e)}"
        }), 500
             
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for handling delivery rejections")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5008)), debug=True)
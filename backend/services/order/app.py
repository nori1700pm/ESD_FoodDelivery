from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime, timezone, timedelta


app = Flask(__name__)
CORS(app, 
     resources={r"/*": {
         "origins": ["http://localhost:5173"],
         "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
         "allow_headers": ["Content-Type", "Authorization"],
         "expose_headers": ["Content-Type"],
         "supports_credentials": True
     }})

# Initialize Firebase
firebase_config = os.environ.get('FIREBASE_CONFIG')
print(f"FIREBASE_CONFIG: {firebase_config}")
firebase_config_dict = json.loads(firebase_config)
cred = credentials.Certificate(firebase_config_dict)
initialize_app(cred)
db = firestore.client()

PORT = int(os.environ.get('PORT', 5001))


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'order-service'})
  
@app.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders or filter by customerId"""
    try:
        print("="*50)
        print("GET /orders hit")
        customer_id = request.args.get('customerId')
        print(f"Requesting orders for customer ID: {customer_id}")
        
        def convert_timestamps(order_dict):
            for key, value in order_dict.items():
                if isinstance(value, datetime):
                    order_dict[key] = value.isoformat()
            return order_dict
        
        if customer_id:
            orders_ref = db.collection('orders')
            query = orders_ref.where('customerId', '==', customer_id)
            orders = [convert_timestamps(doc.to_dict()) | {'id': doc.id} for doc in query.stream()]
            print(f"Found {len(orders)} orders for customer")
            print("Orders:", json.dumps(orders, indent=2))
        else:
            orders_ref = db.collection('orders')
            print("No customer ID provided, fetching all orders")
            orders = [convert_timestamps(doc.to_dict()) | {'id': doc.id} for doc in orders_ref.stream()]
            print(f"Found {len(orders)} total orders")
        
        return jsonify(orders)
    except Exception as e:
        print(f"Error in get_orders: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        print(f"Getting order with ID: {order_id}")  # Debug log
        order_ref = db.collection('orders').document(order_id)
        order = order_ref.get()
        
        if not order.exists:
            print(f"Order not found: {order_id}")  # Debug log
            return jsonify({'error': 'Order not found'}), 404
        
        order_data = order.to_dict()
        order_data['orderId'] = order.id  # Make sure orderId is included
        
        # Convert Firestore timestamps to ISO format strings
        for key, value in order_data.items():
            if isinstance(value, datetime):
                order_data[key] = value.isoformat()
                
        print(f"Found order: {json.dumps(order_data, indent=2)}")  # Debug log
        return jsonify(order_data)
    except Exception as e:
        print(f"Error getting order: {str(e)}")  # Debug log
        return jsonify({'error': str(e)}), 500
    
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data = request.json
        print("Received order data:", order_data)
        
        # Validate required fields
        required_fields = ['customerId', 'items', 'price', 'status', 'deliveryAddress']
        missing_fields = [field for field in required_fields if field not in order_data]
        if missing_fields:
            return jsonify({'error': f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Ensure timestamps are in SGT
        sg_timezone = timezone(timedelta(hours=8))
        current_sg_time = datetime.now(sg_timezone)
        
        # If timestamps aren't provided, use current SGT
        if 'createdAt' not in order_data:
            order_data['createdAt'] = current_sg_time.isoformat()
        if 'updatedAt' not in order_data:
            order_data['updatedAt'] = current_sg_time.isoformat()
            
        print("Final order data being saved:", order_data)
        
        # Save to Firestore
        order_ref = db.collection('orders').document(order_data.get('orderId'))
        order_ref.set(order_data)
        
        return jsonify(order_data), 201
        
    except Exception as e:
        print(f"Error creating order: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an existing order"""
    try:
        order_data = request.json
        
        # Update timestamp
        order_data['updatedAt'] = firestore.SERVER_TIMESTAMP
        
        # Update in Firestore
        order_ref = db.collection('orders').document(order_id)
        order = order_ref.get()
        
        if not order.exists:
            return jsonify({'error': 'Order not found'}), 404
        
        order_ref.update(order_data)
        
        return jsonify({'id': order_id, **order_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<order_id>/status', methods=['PATCH'])
def update_order_status(order_id):
    """Update order status fields"""
    try:
        status_data = request.json
        valid_status_fields = ['status', 'driverStatus', 'paymentStatus', 'driverId']
        
        # Check if at least one valid status field is present
        if not any(field in status_data for field in valid_status_fields):
            return jsonify({
                'error': 'At least one status field (status, driverStatus, paymentStatus) is required'
            }), 400
        
        # Update in Firestore
        order_ref = db.collection('orders').document(order_id)
        order = order_ref.get()
        
        if not order.exists:
            return jsonify({'error': 'Order not found'}), 404
        
        # Create update data without SERVER_TIMESTAMP
        update_data = {}
        
        # Include any provided status fields
        for field in valid_status_fields:
            if field in status_data:
                update_data[field] = status_data[field]
        
        # Add timestamp separately
        sg_timezone = timezone(timedelta(hours=8))
        current_sg_time = datetime.now(sg_timezone)
        update_data['updatedAt'] = current_sg_time.isoformat()
        
        # Perform the update
        order_ref.update(update_data)
        
        # Return the updated data
        response_data = {
            'id': order_id,
            **update_data
        }
        
        return jsonify(response_data)
    except Exception as e:
        print(f"Error updating order status: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    print("This is flask " + os.path.basename(__file__) + " for Order microservice")
    app.run(host='0.0.0.0', port=PORT, debug=True)
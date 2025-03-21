import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize Firebase
firebase_config = os.environ.get('FIREBASE_CONFIG')
print(f"FIREBASE_CONFIG: {firebase_config}")
firebase_config_dict = json.loads(firebase_config)
cred = credentials.Certificate(firebase_config_dict)
initialize_app(cred)
db = firestore.client()


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'service': 'order-service'})
  
# Get orders by customer ID
@app.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders or filter by customerId"""
    try:
        print("GET /orders hit")
        customer_id = request.args.get('customerId')
        
        if customer_id:
            orders_ref = db.collection('orders')
            query = orders_ref.where('customerId', '==', customer_id)
            orders = [doc.to_dict() | {'id': doc.id} for doc in query.stream()]
        else:
            orders_ref = db.collection('orders')
            print(orders_ref)
            orders = [doc.to_dict() | {'id': doc.id} for doc in orders_ref.stream()]
        
        return jsonify(orders)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        order_ref = db.collection('orders').document(order_id)
        order = order_ref.get()
        
        if not order.exists:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify(order.to_dict() | {'id': order.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        order_data = request.json
        
        # Validate required fields
        required_fields = ['customerId', 'restaurantId', 'items', 'price', 'status']
        for field in required_fields:
            if field not in order_data:
                return jsonify({'error': f"Missing required field: {field}"}), 400
        
        # Add timestamps
        order_data['createdAt'] = firestore.SERVER_TIMESTAMP
        order_data['updatedAt'] = firestore.SERVER_TIMESTAMP
        
        # Save to Firestore
        order_ref = db.collection('orders').document()
        order_ref.set(order_data)
        
        # Return the created order with ID
        return jsonify({'id': order_ref.id, **order_data}), 201
    except Exception as e:
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
    """Update just the status of an order"""
    try:
        status_data = request.json
        
        if 'status' not in status_data:
            return jsonify({'error': 'Status field is required'}), 400
        
        # Update in Firestore
        order_ref = db.collection('orders').document(order_id)
        order = order_ref.get()
        
        if not order.exists:
            return jsonify({'error': 'Order not found'}), 404
        
        order_ref.update({
            'status': status_data['status'],
            'updatedAt': firestore.SERVER_TIMESTAMP
        })
        
        return jsonify({'id': order_id, 'status': status_data['status']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=True)

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 3000))
#     app.run(host='0.0.0.0', port=port, debug=os.environ.get('DEBUG', 'false').lower() == 'true')

import os
import json
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, auth
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

# Create a new customer
@app.route('/customers', methods=['POST'])
def create_customer():
    try:
        data = request.json
        print(f"Received data: {data}")
        if not data:
            return jsonify({"error": "Request body is required"}), 400
        
        # Validate required fields
        required_fields = ['address', 'name', 'email', 'password', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f"Missing required field: {field}"}), 400

        # Check if a customer with the same email already exists in Firebase Authentication
        email = data.get('email')
        try:
            auth.get_user_by_email(email)
            return jsonify({"error": "Customer with this email already exists"}), 400
        except auth.UserNotFoundError:
            pass  # Email does not exist, proceed to create the user

        # Create a new user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=data.get('password')
        )
        uid = user.uid  # Use the Firebase Authentication UID

        # Remove password from the data before storing in Firestore
        del data['password']
        data['uid'] = uid  # Assign the Firebase UID to the customer data

        # Store customer data in Firestore
        customer_ref = db.collection('users').document(uid)
        customer_ref.set(data)
        return jsonify({"message": "Customer created", "customer": data}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to create customer: {e}"}), 500

# Read customer details
@app.route('/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        print(f"Fetching customer with ID: {customer_id}")
        customer_ref = db.collection('users').document(customer_id)
        customer = customer_ref.get()
        print(f"Customer exists: {customer.exists}")
        if not customer.exists:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(customer.to_dict()), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch customer: {e}"}), 500

# Get all customers
@app.route('/customers', methods=['GET'])
def get_all_customers():
    try:
        print("Fetching all customers")
        customers = db.collection('users').stream()
        customer_list = [customer.to_dict() for customer in customers]
        return jsonify(customer_list), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch customers: {e}"}), 500

# Update customer information
@app.route('/customers/<customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer_ref = db.collection('users').document(customer_id)  
        if not customer_ref.get().exists:
            return jsonify({"error": "Customer not found"}), 404
        data = request.json
        customer_ref.update(data)
        return jsonify({"message": "Customer updated", "customer": data}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update customer: {e}"}), 500

# Delete a customer
@app.route('/customers/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer_ref = db.collection('users').document(customer_id)  
        if not customer_ref.get().exists:
            return jsonify({"error": "Customer not found"}), 404
        customer_ref.delete()
        return jsonify({"message": "Customer deleted"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete customer: {e}"}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"error": f"Health check failed: {e}"}), 500

# Run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000, debug=True)


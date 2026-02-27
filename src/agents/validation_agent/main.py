
import os
import requests
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

# CONFIGURATION
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:5000")
PLANNER_URL = os.getenv("PLANNER_URL", "http://localhost:5001")
SHARED_SECRET_KEY = "dev-secret-key-change-in-prod" 

def verify_token(token):
    # In production, verify against Auth Service or use public key
    try:
        # Mock verification for now using shared secret
        payload = jwt.decode(token, SHARED_SECRET_KEY, algorithms=["HS256"])
        return payload
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

@app.route('/validate', methods=['POST'])
def validate_request():
    # 1. Check Auth
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
         return jsonify({"error": "Unauthorized"}), 401
    token = auth_header.split(" ")[1]
    user = verify_token(token)
    if not user:
        return jsonify({"error": "Invalid Token"}), 401

    # 2. Validate Payload (Schema Check)
    data = request.json
    if not data:
        return jsonify({"error": "Empty payload"}), 400
    
    required_fields = ["patient_id", "procedure_code", "diagnosis_code", "payer_id"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {missing}"}), 400


    # 3. Forward to Planner
    # Ensure no PHI leaks in logs
    print(f"Valid request from {user.get('sub')}, forwarding to Planner.")

    # Client Certs
    CERT_DIR = os.path.join(os.getcwd(), "src", "config", "security")
    CLIENT_CERT = (os.path.join(CERT_DIR, "client.crt"), os.path.join(CERT_DIR, "client.key"))
    CA_CERT = os.path.join(CERT_DIR, "ca.crt")
    
    try:
        resp = requests.post(f"{PLANNER_URL}/plan", json=data, headers={"Authorization": auth_header}, cert=CLIENT_CERT, verify=False)
        
        # Debugging ID issue
        planner_data = resp.json()
        print(f"Planner Response: {planner_data}")
        
        return jsonify(planner_data), resp.status_code
    except Exception as e:
        print(f"Planner Call Failed: {e}")
        return jsonify({"error": f"Failed to contact Planner: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5002))
    # Enable mTLS
    cert_dir = os.path.join(os.getcwd(), "src", "config", "security")
    cert_file = os.path.join(cert_dir, "server.crt")
    key_file = os.path.join(cert_dir, "server.key")
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Starting with TLS using {cert_file}")
        app.run(host='0.0.0.0', port=port, ssl_context=(cert_file, key_file))
    else:
        print("Certificates not found, starting HTTP only")
        app.run(host='0.0.0.0', port=port)

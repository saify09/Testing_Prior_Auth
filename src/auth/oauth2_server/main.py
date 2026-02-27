
import datetime
import uuid
from flask import Flask, request, jsonify
import jwt

app = Flask(__name__)

# CONFIGURATION
SECRET_KEY = "dev-secret-key-change-in-prod"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MOCK DATABASE of CLIENTS
CLIENTS = {
    "client_id_validation": "client_secret_validation",
    "client_id_planner": "client_secret_planner",
    "client_id_external": "client_secret_external"
}

@app.route('/token', methods=['POST'])
def issue_token():
    # OAuth2 Client Credentials Flow
    client_id = request.form.get('client_id')
    client_secret = request.form.get('client_secret')
    grant_type = request.form.get('grant_type')

    if grant_type != 'client_credentials':
        return jsonify({"error": "unsupported_grant_type"}), 400

    if not client_id or not client_secret:
        return jsonify({"error": "invalid_client"}), 401

    if client_id not in CLIENTS or CLIENTS[client_id] != client_secret:
        return jsonify({"error": "invalid_client"}), 401

    # Generate Token
    expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = {
        "sub": client_id,
        "exp": expiration,
        "iat": datetime.datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "scope": "read write" # Mock scopes
    }

    token = jwt.encode(token_payload, SECRET_KEY, algorithm=ALGORITHM)

    return jsonify({
        "access_token": token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    })

@app.route('/verify', methods=['POST'])
def verify_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"valid": False, "error": "Missing or invalid Authorization header"}), 401
    
    token = auth_header.split(" ")[1]
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return jsonify({"valid": True, "payload": payload})
    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "Invalid token"}), 401

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # Enable mTLS
    import os
    port = 5000
    cert_dir = os.path.join(os.getcwd(), "src", "config", "security")
    cert_file = os.path.join(cert_dir, "server.crt")
    key_file = os.path.join(cert_dir, "server.key")
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Starting with TLS using {cert_file}")
        app.run(host='0.0.0.0', port=5000, ssl_context=(cert_file, key_file))
    else:
        app.run(host='0.0.0.0', port=5000)

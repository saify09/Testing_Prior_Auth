
import os
import requests
from flask import Flask, request, jsonify
from src.infrastructure.database import Repository

app = Flask(__name__)
repo = Repository()

# CONFIGURATION
DENIAL_URL = os.getenv("DENIAL_URL", "http://localhost:5003")
FHIR_AGENT_URL = os.getenv("FHIR_AGENT_URL", "http://localhost:5004")
EDI_AGENT_URL = os.getenv("EDI_AGENT_URL", "http://localhost:5005")

# Client Certs
CERT_DIR = os.path.join(os.getcwd(), "src", "config", "security")
CLIENT_CERT = (os.path.join(CERT_DIR, "client.crt"), os.path.join(CERT_DIR, "client.key"))
VERIFY_SSL = False # CA_CERT if os.path.exists(CA_CERT) else False

@app.route('/plan', methods=['POST'])
def plan_workflow():
    data = request.json
    auth_header = request.headers.get('Authorization')
    
    # 1. Persist Request
    try:
        req_id = repo.add_request(data)
        print(f"Planner stored request {req_id} for patient {data.get('patient_id')}")
    except Exception as e:
        print(f"DB Error: {e}")
        return jsonify({"error": "Database error"}), 500

    # 2. Prediction (Denial Risk)
    risk_score = 0.0
    try:
        resp = requests.post(f"{DENIAL_URL}/predict", json=data, headers={"Authorization": auth_header}, cert=CLIENT_CERT, verify=VERIFY_SSL)
        if resp.status_code == 200:
            risk_score = resp.json().get("risk_score", 0.0)
            repo.update_status(req_id, "PROCESSING", risk_score=risk_score)
    except Exception as e:
        print(f"Warning: Could not get denial prediction: {e}")

    # 3. Decision Logic
    payer_id = data.get("payer_id")
    
    if risk_score > 0.8:
        repo.update_status(req_id, "PENDING_REVIEW", reason="High denial risk")
        return jsonify({"status": "PENDING_REVIEW", "reason": "High denial risk", "risk_score": risk_score, "id": req_id}), 200

    if payer_id == "UHC":
        # Route to FHIR
        try:
            resp = requests.post(f"{FHIR_AGENT_URL}/submit_fhir", json=data, headers={"Authorization": auth_header}, cert=CLIENT_CERT, verify=VERIFY_SSL)
            repo.update_status(req_id, "SUBMITTED_FHIR", agent_response=resp.json())
            
            # Merge ID into response for frontend
            response_data = resp.json()
            response_data['id'] = req_id
            print(f"Planner returning: {response_data}") # DEBUG
            return jsonify(response_data), resp.status_code
        except Exception as e:
            repo.update_status(req_id, "ERROR_FHIR")
            return jsonify({"error": f"FHIR Agent failed: {e}"}), 500
    else:
        # Route to EDI
        try:
            resp = requests.post(f"{EDI_AGENT_URL}/submit_edi", json=data, headers={"Authorization": auth_header}, cert=CLIENT_CERT, verify=VERIFY_SSL)
            repo.update_status(req_id, "SUBMITTED_EDI", agent_response=resp.json())
            
            # Merge ID into response for frontend
            response_data = resp.json()
            response_data['id'] = req_id
            return jsonify(response_data), resp.status_code
        except Exception as e:
            repo.update_status(req_id, "ERROR_EDI")
            return jsonify({"error": f"EDI Agent failed: {e}"}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5001))
    # Enable mTLS
    cert_dir = os.path.join(os.getcwd(), "src", "config", "security")
    cert_file = os.path.join(cert_dir, "server.crt")
    key_file = os.path.join(cert_dir, "server.key")
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Starting with TLS using {cert_file}")
        app.run(host='0.0.0.0', port=port, ssl_context=(cert_file, key_file))
    else:
        app.run(host='0.0.0.0', port=port)

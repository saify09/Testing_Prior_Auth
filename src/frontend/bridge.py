
from flask import Flask, request, jsonify, send_from_directory
import requests
import time
import os
import logging

app = Flask(__name__, static_folder='../../static')

# Configuration from environment or defaults for local-within-container communication
AUTH_URL = os.getenv("AUTH_URL", "http://localhost:5000")
VALIDATION_URL = os.getenv("VALIDATION_URL", "http://localhost:5002")
MONITORING_URL = os.getenv("MONITORING_URL", "http://localhost:5006")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

@app.route('/agent/run', methods=['POST'])
def run_agent():
    try:
        data = request.json
        logger.info(f"Received request for original frontend: {data}")

        # 1. Get Auth Token
        auth_payload = {
            "client_id": "client_id_external",
            "client_secret": "client_secret_external",
            "grant_type": "client_credentials"
        }
        token_resp = requests.post(f"{AUTH_URL}/token", data=auth_payload)
        token_resp.raise_for_status()
        token = token_resp.json().get("access_token")

        # 2. Submit to Validation Agent
        headers = {"Authorization": f"Bearer {token}"}
        # Original UI fields: patientId, payer, procedureCode, diagnosisCode, clinicalNotes
        # New API fields: patient_id, payer_id, procedure_code, diagnosis_code, provider_id? 
        # Let's map them.
        api_payload = {
            "patient_id": data.get("patientId"),
            "payer_id": data.get("payer"),
            "procedure_code": data.get("procedureCode"),
            "diagnosis_code": data.get("diagnosisCode"),
            "notes": data.get("clinicalNotes"), # Changed from provider_id to notes if supported, or just pass notes
            "provider_id": "DEFAULT_DOC"
        }
        
        submit_resp = requests.post(f"{VALIDATION_URL}/validate", json=api_payload, headers=headers)
        submit_resp.raise_for_status()
        submit_data = submit_resp.json()
        req_id = submit_data.get("id")

        # 3. Poll Monitoring Agent for result
        final_result = None
        for _ in range(30): # Poll for up to 30 seconds
            time.sleep(1)
            status_resp = requests.get(f"{MONITORING_URL}/status/{req_id}")
            if status_resp.status_code == 200:
                status_data = status_resp.json()
                if status_data.get("status") in ["COMPLETED", "DENIED", "APPROVED", "PENDING_REVIEW"]:
                    # Original frontend expects 'final_explanation'
                    explanation = status_data.get("agent_response", {}).get("final_explanation")
                    if not explanation:
                        explanation = status_data.get("reason", "No detailed explanation yet.")
                    
                    final_result = {
                        "id": req_id,
                        "status": status_data.get("status"),
                        "final_explanation": explanation
                    }
                    break
        
        if not final_result:
            return jsonify({"error": "Processing timed out"}), 504

        return jsonify(final_result)

    except Exception as e:
        logger.error(f"Bridge error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # HF Spaces uses port 7860
    app.run(host='0.0.0.0', port=7860)

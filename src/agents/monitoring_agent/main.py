
import os
from flask import Flask, jsonify
from src.infrastructure.database import Repository

app = Flask(__name__)
repo = Repository()

@app.route('/status/<ref_id>', methods=['GET'])
def check_status(ref_id):
    # Now querying the database instead of in-memory dict
    # Note: ref_id in our simplified DB is the UUID, but FHIR/EDI agents return 
    # mock external IDs (FHIR-123). In a real system, we'd map these.
    # For this phase, we assume the user queries by the internal UUID returned by Planner.
    details = repo.get_status_details(ref_id)
    if details:
        return jsonify(details)
    return jsonify({"status": "UNKNOWN"})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5006))
    cert_dir = os.path.join(os.getcwd(), "src", "config", "security")
    cert_file = os.path.join(cert_dir, "server.crt")
    key_file = os.path.join(cert_dir, "server.key")
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Starting with TLS using {cert_file}")
        app.run(host='0.0.0.0', port=port, ssl_context=(cert_file, key_file))
    else:
        app.run(host='0.0.0.0', port=port)

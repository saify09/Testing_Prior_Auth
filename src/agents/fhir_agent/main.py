
import os
from flask import Flask, request, jsonify

from fhir.resources.claim import Claim
from fhir.resources.patient import Patient
from fhir.resources.practitioner import Practitioner
from fhir.resources.coding import Coding
from fhir.resources.codeableconcept import CodeableConcept
import uuid
from datetime import datetime

app = Flask(__name__)

@app.route('/submit_fhir', methods=['POST'])
def submit_fhir():
    data = request.json
    try:
        # 1. Validate / Construct Patient
        patient = Patient(id=data.get("patient_id", "unknown"))
        
        # 2. Construct Claim
        claim = Claim(
            id=str(uuid.uuid4()),
            status="active",
            use="preauthorization",
            patient={"reference": f"Patient/{patient.id}"},
            created=datetime.now().isoformat(),
            provider={"reference": f"Practitioner/{data.get('provider_id', 'DOC-555')}"},
            priority={"coding": [{"code": "normal"}]},
            insurance=[{
                "sequence": 1,
                "focal": True,
                "coverage": {"reference": "Coverage/1"}
            }],
            item=[{
                "sequence": 1,
                "productOrService": {
                    "coding": [{
                        "system": "http://www.ama-assn.org/go/cpt",
                        "code": data.get("procedure_code")
                    }]
                }
            }],
            diagnosis=[{
                "sequence": 1,
                "diagnosisCodeableConcept": {
                    "coding": [{
                        "system": "http://hl7.org/fhir/sid/icd-10",
                        "code": data.get("diagnosis_code")
                    }]
                }
            }]
        )
        
        # Validate (this will raise Pydantic ValidationError if invalid)
        claim_json = claim.json()
        print(f"Validated FHIR Claim: {claim.id}")
        
        # Simulate Payer Response
        return jsonify({
            "status": "APPROVED",
            "payer_ref": f"FHIR-{claim.id[:8]}",
            "fhir_resource": claim.dict()
        }), 200
        
    except Exception as e:
        print(f"FHIR Validation Error: {e}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5004))
    cert_dir = os.path.join(os.getcwd(), "src", "config", "security")
    cert_file = os.path.join(cert_dir, "server.crt")
    key_file = os.path.join(cert_dir, "server.key")
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Starting with TLS using {cert_file}")
        app.run(host='0.0.0.0', port=port, ssl_context=(cert_file, key_file))
    else:
        app.run(host='0.0.0.0', port=port)


import time
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

VALIDATION_URL = "https://localhost:5002/validate"
MONITORING_URL = "https://localhost:5006/status"

def get_auth_token():
    import jwt
    import datetime
    payload = {
        "sub": "test_client",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }
    return jwt.encode(payload, "dev-secret-key-change-in-prod", algorithm="HS256")

def test_advanced_logic():
    print("Starting Advanced Logic Test...")
    token = get_auth_token()
    
    # Payload for EDI (Payer != UHC)
    payload_edi = {
        "patient_id": "P-EDI-1",
        "procedure_code": "71045",
        "diagnosis_code": "J18.9",
        "payer_id": "Cigna",
        "provider_id": "DOC-1"
    }
    
    print(f"Sending EDI Request...")
    try:
        # verify=False for local self-signed
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.post(VALIDATION_URL, json=payload_edi, headers=headers, verify=False)
        print(f"Response Status: {resp.status_code}")
        data = resp.json()
        print(f"Response Body: {data}")
        
        req_id = data.get("id")
        if not req_id:
            print("FAILURE: No ID returned")
            return

        # Poll for status details
        print(f"Polling status for {req_id}...")
        for _ in range(5):
            time.sleep(2)
            status_resp = requests.get(f"{MONITORING_URL}/{req_id}", verify=False)
            status_data = status_resp.json()
            print(f"Status: {status_data.get('status')}")
            
            if status_data.get('agent_response'):
                print("SUCCESS: Found Agent Response in DB!")
                print(json.dumps(status_data.get('agent_response'), indent=2))
                break
        else:
            print("FAILURE: Agent response not found after polling")

    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_advanced_logic()

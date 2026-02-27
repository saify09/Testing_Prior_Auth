
import time
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

VALIDATION_URL = "https://localhost:5002/validate"
planner_url = "https://localhost:5001/plan"

def get_auth_token():
    # Mock token generation (in reality, call Auth Service)
    # Using the shared secret to sign a token for testing
    import jwt
    import datetime
    
    payload = {
        "sub": "test_client",
        "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
    }
    return jwt.encode(payload, "dev-secret-key-change-in-prod", algorithm="HS256")

def test_flow():
    print("Starting E2E Test...")
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "patient_id": "P12345",
        "procedure_code": "71045",
        "diagnosis_code": "J18.9",
        "payer_id": "UHC"
    }
    
    print(f"Sending request to Validation Agent: {VALIDATION_URL}")
    try:
        # verify=False because we are using self-signed certs and this is a quick test
        resp = requests.post(VALIDATION_URL, json=payload, headers=headers, verify=False)
        print(f"Response Status: {resp.status_code}")
        print(f"Response Body: {resp.json()}")
        
        if resp.status_code == 200:
            print("SUCCESS: Flow completed.")
        else:
            print("FAILURE: Flow failed.")
            
    except Exception as e:
        print(f"ERROR: Could not connect to services. Are they running? {e}")

if __name__ == "__main__":
    test_flow()


import os
import pickle
import numpy as np
from flask import Flask, request, jsonify

app = Flask(__name__)

# Load Model
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
model = None
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    print(f"Loaded model from {MODEL_PATH}")
except Exception as e:
    print(f"Failed to load model: {e}")

@app.route('/predict', methods=['POST'])
def predict_denial():
    data = request.json
    
    # Preprocess Data to match training features
    # Features: [payer_id, procedure_risk, diagnosis_match, doc_score]
    # Simple mapping for demo
    payer_map = {"UHC": 0, "Cigna": 1, "Aetna": 2}
    payer = payer_map.get(data.get("payer_id"), 0)
    
    # Mock feature extraction from codes
    proc_risk = 0 # Low
    if data.get("procedure_code") == "71045": proc_risk = 1 # Med
    
    diag_match = 1 # Yes
    if data.get("diagnosis_code") == "Z00.00": diag_match = 0 # No match logic mock
    
    doc_score = 85 # Good documentation default
    
    features = np.array([[payer, proc_risk, diag_match, doc_score]])
    
    risk_score = 0.5 # Default
    if model:
        try:
            # Predict class (0=Approved, 1=Denied)
            prediction = model.predict(features)[0]
            # Get probability of denial (class 1)
            probs = model.predict_proba(features)
            risk_score = probs[0][1] 
        except Exception as e:
            print(f"Prediction Error: {e}")
    
    return jsonify({"risk_score": float(risk_score)})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5003))
    cert_dir = os.path.join(os.getcwd(), "src", "config", "security")
    cert_file = os.path.join(cert_dir, "server.crt")
    key_file = os.path.join(cert_dir, "server.key")
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Starting with TLS using {cert_file}")
        app.run(host='0.0.0.0', port=port, ssl_context=(cert_file, key_file))
    else:
        app.run(host='0.0.0.0', port=port)

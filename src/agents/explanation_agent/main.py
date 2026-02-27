
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/explain', methods=['POST'])
def explain_decision():
    data = request.json
    risk_score = data.get("risk_score", 0.0)
    decision = data.get("decision", "UNKNOWN")
    
    explanation = "Standard approval based on medical necessity."
    
    if decision == "DENIED" or risk_score > 0.5:
        explanation = "High risk of denial due to missing clinical documentation for diagnosis code."
    
    if data.get("missing_fields"):
        explanation = f"Missing required fields: {data.get('missing_fields')}"

    return jsonify({"explanation": explanation})

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5007))
    cert_dir = os.path.join(os.getcwd(), "src", "config", "security")
    cert_file = os.path.join(cert_dir, "server.crt")
    key_file = os.path.join(cert_dir, "server.key")
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Starting with TLS using {cert_file}")
        app.run(host='0.0.0.0', port=port, ssl_context=(cert_file, key_file))
    else:
        app.run(host='0.0.0.0', port=port)

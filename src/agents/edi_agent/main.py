
import os
from flask import Flask, request, jsonify

import datetime

def generate_x12_278(data):
    # Simplified X12 278 Generation
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    current_time = datetime.datetime.now().strftime("%H%M")
    
    # 1. ISA - Interchange Control Header
    isa = f"ISA*00*          *00*          *ZZ*SENDERID       *ZZ*PAYERID        *{current_date}*{current_time}*^*00501*000000001*0*T*:~"
    
    # 2. GS - Functional Group Header
    gs = f"GS*HI*SENDERID*PAYERID*{current_date}*{current_time}*1*X*005010X217~"
    
    # 3. ST - Transaction Set Header
    st = "ST*278*0001*005010X217~"
    
    # 4. BHT - Beginning of Hierarchical Transaction
    bht = f"BHT*0007*13*REQUEST123*{current_date}*{current_time}*RU~"
    
    # 5. NM1 - Source Name (Provider)
    nm1_pr = "NM1*1P*2*PROVIDER NAME*****XX*1234567890~"
    
    # 6. NM1 - Receiver Name (Payer)
    nm1_py = "NM1*X3*2*PAYER NAME*****PI*PAYER123~"
    
    # 7. NM1 - Subscriber Name (Patient)
    nm1_il = f"NM1*IL*1*PATIENT*****MI*{data.get('patient_id')}~"
    
    # 8. HI - Health Care Diagnosis
    hi = f"HI*BK:{data.get('diagnosis_code')}~"
    
    # 9. SV1 - Professional Service
    sv = f"SV1*HC:{data.get('procedure_code')}*150.00*UN*1***1~"
    
    # 10. Trailers
    se = "SE*10*0001~"
    ge = "GE*1*1~"
    iea = "IEA*1*000000001~"
    
    return f"{isa}{gs}{st}{bht}{nm1_pr}{nm1_py}{nm1_il}{hi}{sv}{se}{ge}{iea}"

app = Flask(__name__)

@app.route('/submit_edi', methods=['POST'])
def submit_edi():
    data = request.json
    try:
        x12_payload = generate_x12_278(data)
        print(f"Generated X12: {x12_payload}")
        
        return jsonify({
            "status": "APPROVED", 
            "payer_ref": "EDI-987654",
            "x12_request": x12_payload
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5005))
    cert_dir = os.path.join(os.getcwd(), "src", "config", "security")
    cert_file = os.path.join(cert_dir, "server.crt")
    key_file = os.path.join(cert_dir, "server.key")
    if os.path.exists(cert_file) and os.path.exists(key_file):
        print(f"Starting with TLS using {cert_file}")
        app.run(host='0.0.0.0', port=port, ssl_context=(cert_file, key_file))
    else:
        app.run(host='0.0.0.0', port=port)

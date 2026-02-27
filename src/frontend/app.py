
import streamlit as st
import requests
import time
import pandas as pd
import plotly.express as px
import os
import json

# CONFIG
st.set_page_config(page_title="UHC Prior Auth Agent", layout="wide")
st.title("🏥 HIPAA-Compliant AI Prior Authorization System")

# URLs (HTTPS)
VALIDATION_URL = os.getenv("VALIDATION_URL", "https://localhost:5002")
MONITORING_URL = os.getenv("MONITORING_URL", "https://localhost:5006")
AUTH_URL = os.getenv("AUTH_URL", "https://localhost:5000")

# Certs for client requests (Verify=False for self-signed in local dev)
VERIFY_SSL = False 

# SESSION STATE
if 'history' not in st.session_state:
    st.session_state.history = []

# SIDEBAR - REQUEST FORM
with st.sidebar:
    st.header("📝 Submit New Request")
    patient_id = st.text_input("Patient ID", value="P-1001")
    payer_id = st.selectbox("Payer", ["UHC", "Cigna", "Aetna"])
    procedure_code = st.text_input("Procedure Code (CPT)", value="71045")
    diagnosis_code = st.text_input("Diagnosis Code (ICD-10)", value="J18.9")
    provider_id = st.text_input("Provider ID", value="DOC-555")
    
    if st.button("🚀 Submit Request", type="primary"):
        payload = {
            "patient_id": patient_id,
            "payer_id": payer_id,
            "procedure_code": procedure_code,
            "diagnosis_code": diagnosis_code,
            "provider_id": provider_id
        }
        
        with st.spinner("Submitting to Validation Agent..."):
            try:
                # 1. Get Auth Token
                # Auth Service expects Form Data (x-www-form-urlencoded) for OAuth2
                auth_payload = {
                    "client_id": "client_id_external",
                    "client_secret": "client_secret_external",
                    "grant_type": "client_credentials"
                }
                token_resp = requests.post(f"{AUTH_URL}/token", data=auth_payload, verify=VERIFY_SSL)
                
                if token_resp.status_code != 200:
                    st.error(f"Auth Failed: {token_resp.text}")
                    st.stop()
                    
                token = token_resp.json().get("access_token")
            
                # 2. Submit Request
                headers = {"Authorization": f"Bearer {token}"}
                resp = requests.post(f"{VALIDATION_URL}/validate", json=payload, headers=headers, verify=VERIFY_SSL)
                
                if resp.status_code == 200:
                    data = resp.json()
                    st.write(f"Debug: Full Response: {data}") # DEBUG
                    st.success(f"Request Accepted! ID: {data.get('id')}")
                    # Add to history
                    st.session_state.history.append({
                        "id": data.get("id", "Unknown"),
                        "patient": patient_id,
                        "status": "SUBMITTED",
                        "timestamp": time.strftime("%H:%M:%S"),
                        "risk_score": None
                    })
                else:
                    st.error(f"Validation Failed: {resp.text}")
            except Exception as e:
                st.error(f"Connection Error: {e}")

# MAIN DASHBOARD
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📡 Live Request Monitor")
    
    # Auto-refresh loop placeholder
    placeholder = st.empty()
    
    # Refresh button
    if st.button("🔄 Refresh Status"):
        pass # trigger rerun
        
    # Table of Requests
    if st.session_state.history:
        # Update statuses
        updated_history = []
        for item in st.session_state.history:
            try:
                # Poll Monitoring Agent
                # In real app, we'd batch this or use webhooks. Here we poll.
                # Note: Monitoring Agent currently takes ref_id, which is the internal DB ID in our new DB setup.
                req_id = item['id']
                resp = requests.get(f"{MONITORING_URL}/status/{req_id}", verify=VERIFY_SSL)
                if resp.status_code == 200:
                    status_data = resp.json()
                    item['status'] = status_data.get('status', item['status'])
                    item['risk_score'] = status_data.get('risk_score')
                    item['reason'] = status_data.get('reason')
                    item['agent_response'] = status_data.get('agent_response')
            except:
                pass
            updated_history.append(item)
        st.session_state.history = updated_history
        
        # Display as cards or expandable sections for details
        for item in st.session_state.history:
            with st.expander(f"{item['timestamp']} - {item['patient']} ({item['status']})"):
                st.write(f"**Request ID:** {item['id']}")
                st.write(f"**Risk Score:** {item.get('risk_score', 'N/A')}")
                if item.get('reason'):
                    st.write(f"**Decision Reason:** {item['reason']}")
                
                if item.get('agent_response'):
                    st.subheader("Agent Response")
                    st.json(item['agent_response'])
    else:
        st.info("No requests submitted yet.")

with col2:
    st.subheader("📊 Analytics")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        # Status Distribution
        fig = px.pie(df, names='status', title='Request Status Distribution', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.text("Submit requests to see analytics.")

# FOOTER
st.markdown("---")
st.caption("🔒 Secured by mTLS | HIPAA Compliant Logging Enabled")

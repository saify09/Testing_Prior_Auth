from .base_agent import BaseAgent
from models import AgentState
import httpx

class UHCAPIAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="UHC API Agent",
            role="Manages secure communication, token refresh, and submission to PAS"
        )
        self.base_url = "http://localhost:8001"

    async def process(self, state: AgentState) -> AgentState:
        # Check if we need to submit
        if not state.auth_required:
            self.log("No auth required. Skipping submission.")
            return state
            
        if state.validation_status != "valid":
             self.log("Validation not passed. Cannot submit.")
             return state

        self.log("Initiating Submission Process...")

        try:
            async with httpx.AsyncClient() as client:
                 # 1. Auth
                self.log("Authenticating...")
                auth_payload = {"grant_type": "client_credentials", "client_id": "valid_client", "client_secret": "valid_secret"}
                
                token_res = await client.post(f"{self.base_url}/oauth/token", json=auth_payload)
                
                if token_res.status_code != 200:
                    self.log("Authentication Failed.")
                    state.submission_outcome = "error"
                    return state
                    
                token = token_res.json()["access_token"]
                state.access_token = token
                self.log_secure("Authenticated secure session.", [token])

                # 2. Submit PAS
                self.log("Submitting Prior Authorization Request...")
                headers = {"Authorization": f"Bearer {token}"}
                payload = {
                    "cptCode": state.cpt_code,
                    "diagnosisCode": state.diagnosis_code,
                    "clinicalNotes": state.clinical_notes,
                    "memberId": state.member_id,
                    "providerId": state.provider_id
                }
                
                pas_res = await client.post(f"{self.base_url}/pas/submit", json=payload, headers=headers)
                
                if pas_res.status_code == 200:
                    data = pas_res.json()
                    state.submission_id = data["id"]
                    state.submission_outcome = data["outcome"]
                    self.log(f"Submission Complete. Outcome: {data['outcome']}")
                else:
                    self.log(f"Submission Error: {pas_res.status_code} - {pas_res.text}")
                    state.submission_outcome = "error"

        except Exception as e:
            self.log(f"API Error: {e}")
            state.submission_outcome = "error"

        return state

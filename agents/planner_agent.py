from .base_agent import BaseAgent
from models import AgentState
import httpx

class PlannerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Planner Agent",
            role="Strategist deciding the workflow based on Coverage Requirements Discovery (CRD)"
        )
        self.base_url = "http://localhost:8001" # Mock API URL

    async def process(self, state: AgentState) -> AgentState:
        self.log("Determining workflow strategy (CRD)...")
        
        # If Validation passed, we check if PA is required.
        if state.validation_status != "valid":
            self.log("Skipping CRD Check due to invalid validation status.")
            return state
            
        try:
            self.log("Executing CRD Check...")
            
            async with httpx.AsyncClient() as client:
                # Auth
                auth_payload = {"grant_type": "client_credentials", "client_id": "valid_client", "client_secret": "valid_secret"}
                token_res = await client.post(f"{self.base_url}/oauth/token", json=auth_payload)
                token = token_res.json().get("access_token")
                
                # CRD Check
                crd_payload = {"cptCode": state.cpt_code, "context": "planning"}
                headers = {"Authorization": f"Bearer {token}"}
                
                crd_res = await client.post(f"{self.base_url}/crd/coverage-requirement", json=crd_payload, headers=headers)
                
                if crd_res.status_code == 200:
                    crd_data = crd_res.json()
                    if "Prior Authorization is required" in crd_data.get("detail", ""):
                        state.auth_required = True
                        self.log("CRD Result: Prior Auth IS required.")
                    else:
                        state.auth_required = False
                        self.log("CRD Result: Prior Auth NOT required.")
                else:
                     self.log(f"CRD Check Failed: {crd_res.status_code}")
                     state.auth_required = True # Default to safe
                 
        except Exception as e:
            self.log(f"Error during CRD: {e}")
            state.auth_required = True # Fallback

        return state

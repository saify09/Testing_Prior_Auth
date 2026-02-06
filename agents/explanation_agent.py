from .base_agent import BaseAgent
from models import AgentState

class ExplanationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Explanation Agent",
            role="Clinical Liaison who translates complex UHC status codes into clear instructions for healthcare providers"
        )

    async def process(self, state: AgentState) -> AgentState:
        self.log("Generating Explanation...")
        
        # Scenario 1: Validation Failed
        if state.validation_status == "invalid":
            state.final_explanation = (
                f"Prepare for Denial Avoidance.\n"
                f"ACTION REQUIRED: The system detected missing information: {state.gap_analysis}\n"
                f"Please update the clinical records and re-run the agent."
            )
            return state

        # Scenario 2: Auth Not Required
        if state.auth_required is False:
             state.final_explanation = (
                "Good news. No Prior Authorization is required for this procedure (CPT "
                f"{state.cpt_code}). You may proceed with scheduling."
            )
             return state

        # Scenario 3: Submission Results
        elif state.submission_outcome == "approved":
            state.final_explanation = (
                f"SUCCESS: Authorization Approved.\n"
                f"Auth ID: {state.submission_id}\n"
                f"REASON: Clinical documentation successfully demonstrated medical necessity for CPT {state.cpt_code}.\n"
                f"NEXT STEPS: Procedure is authorized. Please retain Auth ID for billing."
            )
        elif state.submission_outcome == "pended":
            state.final_explanation = (
                f"STATUS: Pending Review.\n"
                f"Ref ID: {state.submission_id}\n"
                f"The request has been received but requires manual clinical review. "
                "Monitor the dashboard for updates within 24-48 hours."
            )
        elif state.submission_outcome == "denied":
             state.final_explanation = (
                f"ALERT: Authorization Denied.\n"
                f"Ref ID: {state.submission_id}\n"
                "Review the clinical criteria for verifying medical necessity."
            )
        else:
             state.final_explanation = "System Error: Unable to complete the request. Please contact support."

        self.log(f"Explanation Generated: {state.final_explanation[:50]}...")
        return state

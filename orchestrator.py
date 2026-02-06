import asyncio
import argparse
from models import AgentState, ServiceRequest
from agents.validation_agent import ValidationAgent
from agents.planner_agent import PlannerAgent
from agents.uhc_api_agent import UHCAPIAgent
from agents.explanation_agent import ExplanationAgent

async def run_orchestrator(request: ServiceRequest):
    print(">>> Agentic AI Connector for UHC Prior Authorization API <<<")
    print("------------------------------------------------------------")
    
    # 1. Initialize State
    state = AgentState(
        cpt_code=request.cpt_code,
        diagnosis_code=request.diagnosis_code,
        clinical_notes=request.clinical_notes,
        member_id=request.member_id,
        provider_id=request.provider_id
    )
    
    # 2. Initialize Agents
    compliance_officer = ValidationAgent()
    strategist = PlannerAgent()
    connector = UHCAPIAgent()
    liaison = ExplanationAgent()
    
    # 3. Execution Loop
    
    # Step 1: Validation
    print("\n[Orchestrator]: Activating Validation Agent...")
    state = await compliance_officer.process(state)
    
    if state.validation_status == "invalid":
        print("[Orchestrator]: Validation Failed. Skipping to Explanation.")
        state = await liaison.process(state)
        print("\nFINAL OUTPUT:\n" + state.final_explanation)
        return state

    # Step 2: Planning / Discovery
    print("\n[Orchestrator]: Activating Planner Agent...")
    state = await strategist.process(state)
    
    # Step 3: API Execution
    print("\n[Orchestrator]: Activating UHC API Agent...")
    state = await connector.process(state)
    
    # Step 4: Explanation
    print("\n[Orchestrator]: Activating Explanation Agent...")
    state = await liaison.process(state)
    
    print("\n------------------------------------------------------------")
    print("FINAL OUTPUT:")
    print(state.final_explanation)
    print("------------------------------------------------------------")
    return state

if __name__ == "__main__":
    # Sample Test Cases can be toggled via CLI or defaulted
    parser = argparse.ArgumentParser()
    parser.add_argument("--cpt", default="70450", help="CPT Code")
    parser.add_argument("--notes", default="Short note", help="Clinical Notes")
    args = parser.parse_args()
    
    req = ServiceRequest(
        member_id="123456789",
        cpt_code=args.cpt, # 70450 requires PA
        diagnosis_code="R51",
        clinical_notes=args.notes,
        provider_id="PROV001"
    )
    
    asyncio.run(run_orchestrator(req))

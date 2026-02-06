from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import datetime

app = FastAPI(title="Mock UHC API", description="Simulates UHC Eligibility & PAS Endpoints")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---

class TokenRequest(BaseModel):
    grant_type: str
    client_id: str
    client_secret: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class CoverageRequest(BaseModel):
    memberId: str
    providerId: str
    serviceType: Optional[str] = None

class CoverageResponse(BaseModel):
    status: str
    coverageId: str
    planName: str
    effectiveDate: str

class SubmitRequest(BaseModel):
    cptCode: str
    diagnosisCode: str
    clinicalNotes: str
    priorAuthorizationId: Optional[str] = None

class SubmitResponse(BaseModel):
    id: str
    status: str
    outcome: str # "approved", "denied", "pended"
    text: Optional[str] = None

# --- In-Memory Store ---
# Simulating a valid member database
VALID_MEMBERS = {"123456789": "John Doe", "987654321": "Jane Smith"}
VALID_CPT_CODES = ["99213", "70450", "93000"] # Example valid codes
PRIOR_AUTH_REQUIRED = ["70450"] # CT Head requires PA

# --- Endpoints ---

@app.post("/oauth/token", response_model=TokenResponse)
async def get_token(request: TokenRequest):
    """Simulates OAuth2 token generation."""
    if request.client_id == "valid_client" and request.client_secret == "valid_secret":
        return TokenResponse(
            access_token=f"mock_token_{uuid.uuid4()}",
            token_type="Bearer",
            expires_in=3600
        )
    raise HTTPException(status_code=401, detail="Invalid client credentials")

def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer mock_token_"):
        raise HTTPException(status_code=401, detail="Invalid mock token")
    return authorization

@app.post("/crd/coverage-requirement", tags=["CRD"])
async def check_coverage_requirement(request: Dict[str, Any], token: str = Depends(verify_token)):
    """
    Simulates Coverage Requirements Discovery (CRD).
    Determines if Prior Auth is needed based on CPT code in the FHIR-like request.
    This is a simplified mock.
    """
    # Simply looking for a code in the raw dict for this prototype
    # In real FHIR, we'd parse the Bundle/ServiceRequest
    cpt = request.get("cptCode", "")
    
    if cpt in PRIOR_AUTH_REQUIRED:
        return {
            "resourceType": "CoverageRequirement",
            "status": "active",
            "appliesTo": ["prior-auth"],
            "detail": "Prior Authorization is required for this procedure."
        }
    
    return {
        "resourceType": "CoverageRequirement",
        "status": "active",
        "appliesTo": [],
        "detail": "No Prior Authorization required."
    }

@app.get("/eligibility/coverage", response_model=CoverageResponse)
async def check_coverage(memberId: str, providerId: str, token: str = Depends(verify_token)):
    """Simulates checking member eligibility."""
    if memberId in VALID_MEMBERS:
        return CoverageResponse(
            status="active",
            coverageId=f"cov_{uuid.uuid4()}",
            planName="UHC Mock Plan Gold",
            effectiveDate="2025-01-01"
        )
    raise HTTPException(status_code=404, detail="Member not found")

@app.post("/pas/submit", response_model=SubmitResponse)
async def submit_pas(request: SubmitRequest, token: str = Depends(verify_token)):
    """
    Simulates the Prior Authorization Submission (PAS).
    Simple logic: 
    - If notes validation fails (handled by caller usually, but we check length here for 'mock' backend logic) -> Denied
    - If CPT is in 'requires auth' list -> Approved (simulating good clinical data)
    """
    
    # Mock logic: If CPT requires auth, we check notes complexity
    if request.cptCode in PRIOR_AUTH_REQUIRED:
        # Simulate 'medical necessity' check
        # We assume the agent already validated, but the payer API also has its own checks.
        # We'll rely on length and keyword heuristic here too for consistency in the prototype.
        
        notes = request.clinicalNotes.lower()
        
        # Stricter Check: Must have specific "medical necessity" keywords (Severity/History)
        necessity_markers = ["chronic", "severe", "acute", "worsening", "persistent", "history", "failed", "unresponsive"]
        has_necessity = any(w in notes for w in necessity_markers)
        
        if len(notes) > 20 and has_necessity: 
             return SubmitResponse(
                id=f"pas_{uuid.uuid4()}",
                status="complete",
                outcome="approved",
                text="Authorization granted based on clinical evidence."
            )
        else:
             return SubmitResponse(
                id=f"pas_{uuid.uuid4()}",
                status="complete",
                outcome="pended",
                text="Insufficient clinical information provided. Please submit detailed history."
            )
            
    # If it was sent here but didn't even require auth?
    return SubmitResponse(
        id=f"pas_{uuid.uuid4()}",
        status="complete",
        outcome="approved", # Auto-approve
        text="No prior authorization required for this code, effectively approved."
    )

from orchestrator import run_orchestrator
from models import ServiceRequest
from fastapi.staticfiles import StaticFiles

@app.post("/agent/run")
async def run_agent(request: ServiceRequest):
    """Executes the agentic loop via the Orchestrator."""
    state = await run_orchestrator(request)
    return state

@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

app.mount("/", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

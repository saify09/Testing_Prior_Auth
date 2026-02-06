from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class AgentState(BaseModel):
    """Shared state passed between agents."""
    cpt_code: Optional[str] = None
    diagnosis_code: Optional[str] = None
    clinical_notes: Optional[str] = None
    member_id: Optional[str] = None
    provider_id: Optional[str] = None
    
    # Internal flags
    auth_required: Optional[bool] = None
    validation_status: str = "pending" # pending, valid, invalid
    gap_analysis: Optional[str] = None # Details if invalid
    
    # API Results
    access_token: Optional[str] = None
    coverage_status: Optional[str] = None
    submission_id: Optional[str] = None
    submission_outcome: Optional[str] = None # approved, denied, pended
    final_explanation: Optional[str] = None
    
class ServiceRequest(BaseModel):
    """Input payload for the orchestration."""
    member_id: str
    cpt_code: str
    diagnosis_code: str
    clinical_notes: str
    provider_id: str

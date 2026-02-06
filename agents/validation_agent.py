from .base_agent import BaseAgent
from models import AgentState

class ValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Validation Agent",
            role="Compliance Officer ensuring all CPT codes and clinical notes meet UHC's DTR standards"
        )

    async def process(self, state: AgentState) -> AgentState:
        # HIPAA Compliance: Redact Member ID and Notes from logs
        self.log_secure("Starting validation of clinical data...", [state.member_id, state.clinical_notes])
        
        # 1. Validate Codes
        if not state.cpt_code or not state.diagnosis_code:
            state.validation_status = "invalid"
            state.gap_analysis = "Missing CPT or Diagnosis Code."
            self.log("Failed: Missing codes.")
            return state

        # 2. Validate Clinical Notes (Mock DTR check)
        # Enhanced to detect gibberish or non-medical content
        notes = state.clinical_notes.lower().strip()
        
        # Heuristic 1: Minimum Length (must be substantial)
        if not notes or len(notes) < 15:
            state.validation_status = "invalid"
            state.gap_analysis = "Clinical notes are too brief. Please provide detailed medical history."
            self.log("Failed: Notes too short.")
            return state

        # Heuristic 2: Specificity Check (Severity/Duration + Anatomy/Symptom)
        # To prevent "patient has abdomen pain" (too generic) from passing.
        
        # Category A: Anatomy & Symptoms (What/Where)
        anatomy_symptoms = [
            "pain", "symptoms", "diagnosis", "abdomen", "chest", "head", "back", "leg", "arm", 
            "mass", "bleeding", "swelling", "fracture", "infection", "headache", "migraine", 
            "anaemia", "tumor", "lesion", "cyst", "fatigue", "nausea", "vomiting"
        ]
        
        # Category B: Severity, Duration, & Action (Why now?)
        context_severity = [
            "severe", "chronic", "acute", "worsening", "persistent", "unresponsive", "failed", 
            "indicated", "necessary", "emergency", "critical", "recurring", "recurrent", 
            "history", "failed medication", "treatment", "therapy", "biopsy", "scan", "xray", 
            "ct", "mr", "ultrasound", "antibiotic"
        ]
        
        has_anatomy = any(w in notes for w in anatomy_symptoms)
        has_context = any(w in notes for w in context_severity)
        
        if not (has_anatomy and has_context):
            state.validation_status = "invalid"
            state.gap_analysis = (
                "Clinical notes are too generic. Please specify Severity (e.g., 'severe', 'chronic'), "
                "Duration (e.g., 'persistent'), or Prior Treatments."
            )
            self.log("Failed: Missing severity/context qualifiers.")
            return state

        # Heuristic 3: Vowel Ratio (Gibberish Detector)
        # Gibberish like "sjbchhgsgh" usually has very few vowels.
        vowels = "aeiou"
        vowel_count = sum(1 for char in notes if char in vowels)
        total_chars = len([c for c in notes if c.isalpha()])
        
        if total_chars > 0 and (vowel_count / total_chars) < 0.2:
             state.validation_status = "invalid"
             state.gap_analysis = "Clinical notes appear unrecognizable. Please write in clear, complete sentences."
             self.log("Failed: Gibbberish detected (low vowel ratio).")
             return state


            
        state.validation_status = "valid"
        state.gap_analysis = None
        self.log("Validation Successful. Data appears complete.")
        return state

from typing import Any, Dict
from models import AgentState

class BaseAgent:
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
    
    async def process(self, state: AgentState) -> AgentState:
        """
        Main method to be implemented by child agents.
        Receives current state, performs logic, updates and returns state.
        """
        raise NotImplementedError("Subclasses must implement process()")
    
    def log(self, message: str):
        print(f"[{self.name}]: {message}")

    def log_secure(self, message: str, phi_data: list):
        """Logs a message with PHI redacted for HIPAA compliance."""
        safe_msg = message
        for item in phi_data:
            if item:
                safe_msg = safe_msg.replace(item, "[REDACTED-PHI]")
        print(f"[{self.name}]: {safe_msg}")

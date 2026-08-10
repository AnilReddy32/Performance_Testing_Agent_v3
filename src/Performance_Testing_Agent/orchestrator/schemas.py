from pydantic import BaseModel
from typing import List, Optional, Dict
 
 
# ==========================================
# Request received from FastAPI
# ==========================================
 
class UserRequest(BaseModel):
    query: str
 
 
# ==========================================
# Router Response
# ==========================================
 
class RouterResponse(BaseModel):
    selected_agents: List[str]
 
 
# ==========================================
# Final API Response
# ==========================================
 
class OrchestratorResponse(BaseModel):
    success: bool
    message: str
    selected_agents: List[str]
    data: Optional[Dict] = None
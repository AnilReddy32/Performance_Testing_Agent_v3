from typing import TypedDict, Optional
 
 
class AgentState(TypedDict):
    """ Shared state used by all agents.
    Every agent reads from this state, update only its own section, and 
    returns the updated state"""
 
    user_query: str
 
    selected_agents: list[str]
 
    test_execution: Optional[dict]
 
    monitoring: Optional[dict]
 
    security: Optional[dict]
 
    analysis: Optional[dict]
 
    report: Optional[dict]
 
    final_response: Optional[dict]
from .base_agent import BaseAgent
 
 
class ReportAgent(BaseAgent):
 
    async def execute(self, state):
 
        print("===== Report Agent =====")
 
        state["report"] = {
 
            "status": "Generated",
 
            "summary": {
 
                "test_execution": state.get("test_execution"),
 
                "monitoring": state.get("monitoring"),
 
                "security": state.get("security"),
 
                "analysis": state.get("analysis")
 
            }
 
        }
 
        state["final_response"] = state["report"]
 
        return state
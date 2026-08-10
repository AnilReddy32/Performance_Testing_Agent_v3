from .state import AgentState
from .router import Router
from .registry import AGENT_REGISTRY
from .logger import logger
 
 
class Orchestrator:
    """
    Main Orchestrator
    
    Responsibilities:
    1. Receive user query
    2. Ask router which agent to execute
    3. Execute selected agents
    4. Return final response
    """
 
    def __init__(self):
        self.router = Router()
 
    async def execute(self, user_query: str):
 
        # ---------------------------------------
        # Step 1 : Initialize Agent State
        # ---------------------------------------
 
        state: AgentState = {
            "user_query": user_query,
            "selected_agents": [],
 
            "test_execution": None,
            "monitoring": None,
            "security": None,
            "analysis": None,
            "report": None,
 
            "final_response": None
        }
 
        # ---------------------------------------
        # Step 2 : Route Query
        # ---------------------------------------
        logger.info("Selecting Agents....")
 
        selected_agents = await self.router.route(user_query)

        print("Selected Agents:", selected_agents)
 
        state["selected_agents"] = selected_agents
 
        logger.info(f"Selected Agents : {selected_agents}")
 
        # ---------------------------------------
        # Step 3 : Execute Agents
        # ---------------------------------------
 
        for agent_name in selected_agents:

            print("Executing:", agent_name)

            agent = AGENT_REGISTRY.get(agent_name)

            print("Agent:", agent)
 
            if agent is None:
                raise Exception(f"{agent_name} not found.")
 
            state = await agent.execute(state)

            print("State after execution:", state)

        logger.info("All Agents completed")
 
        # ---------------------------------------
        # Step 4 : Return Final Response
        # ---------------------------------------
        if state["report"]:
            return state["report"]

        return{
            "message": "Execution completed",
            "state": state

        }
        
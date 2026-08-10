from .base_agent import BaseAgent
 
 
class MonitoringAgent(BaseAgent):
 
    async def execute(self, state):
 
        print("===== Monitoring Agent =====")
 
        state["monitoring"] = {
 
            "cpu_usage": 72.8,
            "memory_usage": 65.1,
            "db_connections": 145,
            "api_latency": 1.8,
            "tps": 1200
 
        }
 
        return state
from .base_agent import BaseAgent
 
 
class AnalysisAgent(BaseAgent):
 
    async def execute(self, state):
 
        print("===== Analysis Agent =====")
 
        monitoring = state.get("monitoring")
 
        test = state.get("test_execution")
 
        recommendation = []
 
        if monitoring:
 
            if monitoring["cpu_usage"] > 80:
                recommendation.append(
                    "Increase CPU Allocation"
                )
 
            if monitoring["memory_usage"] > 80:
                recommendation.append(
                    "Increase Memory"
                )
 
        if test:
 
            if test["error_rate"] > 1:
                recommendation.append(
                    "Investigate API Errors"
                )
 
            if test["avg_response_time"] > 2:
                recommendation.append(
                    "Optimize Database Queries"
                )
 
        if not recommendation:
            recommendation.append(
                "System Performance is Good"
            )
 
        state["analysis"] = {
 
            "status": "Completed",
 
            "recommendations": recommendation
 
        }
 
        return state
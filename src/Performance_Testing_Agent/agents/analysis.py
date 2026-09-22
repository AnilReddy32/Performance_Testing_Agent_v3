from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext

from ..config import LITELLM_MODEL_NAME, TEMPERATURE


def run_analysis(tool_context: ToolContext) -> dict:
    """Performs root-cause / bottleneck analysis and produces
    recommendations.

    Takes no arguments - it reads whatever test-execution and monitoring
    results were already collected earlier in this conversation directly
    from shared session state ("test_execution_result", "monitoring_result"),
    so it should only be called after that data has actually been collected.
    Stores its own result under "analysis_result".
    """

    print("===== Analysis Agent: run_analysis =====")

    test_execution = tool_context.state.get("test_execution_result")
    monitoring = tool_context.state.get("monitoring_result")

    recommendation = []

    if monitoring:
        if monitoring.get("cpu_usage", 0) > 80:
            recommendation.append("Increase CPU Allocation")

        if monitoring.get("memory_usage", 0) > 80:
            recommendation.append("Increase Memory")

    if test_execution:
        if test_execution.get("error_rate", 0) > 1:
            recommendation.append("Investigate API Errors")

        if test_execution.get("avg_response_time", 0) > 2:
            recommendation.append("Optimize Database Queries")

    if not recommendation:
        recommendation.append("System Performance is Good")

    result = {
        "status": "Completed",
        "recommendations": recommendation,
    }

    tool_context.state["analysis_result"] = result

    return result


analysis_agent = LlmAgent(
    name="analysis_agent",
    model=LiteLlm(
        model=LITELLM_MODEL_NAME,
        temperature=TEMPERATURE,
    ),
    mode="single_turn",  # call-and-return, like an ADK workflow node, not a sticky chat transfer
    instruction=(
        "You are the Analysis Agent for a Banking AI Performance Testing "
        "System. Whenever you are asked for root cause analysis, "
        "bottleneck detection, performance recommendations, SLA validation, "
        "historical comparison, or fixes to recommend, call run_analysis "
        "(it takes no arguments - it reads prior results itself) and "
        "report back its exact results."
    ),
    description=(
        "Analyzes previously collected test-execution and monitoring "
        "results to detect bottlenecks and recommend fixes."
    ),
    tools=[run_analysis],
)

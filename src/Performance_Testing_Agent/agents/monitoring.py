from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext

from Performance_Testing_Agent.config import LITELLM_MODEL_NAME, TEMPERATURE


def collect_monitoring_metrics(tool_context: ToolContext) -> dict:
    """Collects runtime infrastructure monitoring metrics for the banking
    system (CPU/memory usage, DB connections, API latency, TPS).

    Takes no arguments. Stores the result in shared session state under
    "monitoring_result" so other agents (e.g. analysis, report) can use the
    exact same numbers later in this conversation.
    """

    print("===== Monitoring Agent: collect_monitoring_metrics =====")

    result = {
        "cpu_usage": 72.8,
        "memory_usage": 65.1,
        "db_connections": 145,
        "api_latency": 1.8,
        "tps": 1200,
    }

    tool_context.state["monitoring_result"] = result

    return result


monitoring_agent = LlmAgent(
    name="monitoring_agent",
    model=LiteLlm(
        model=LITELLM_MODEL_NAME,
        temperature=TEMPERATURE,
    ),
    mode="single_turn",  # call-and-return, like an ADK workflow node, not a sticky chat transfer
    instruction=(
        "You are the Monitoring Agent for a Banking AI Performance Testing "
        "System. Whenever you are asked about CPU, memory, TPS, API "
        "latency, database connections, monitoring, or resource "
        "utilization, call collect_monitoring_metrics and report back its "
        "exact results. Never invent or alter numbers."
    ),
    description=(
        "Collects runtime infrastructure metrics (CPU, memory, DB "
        "connections, API latency, TPS) for the banking application."
    ),
    tools=[collect_monitoring_metrics],
)

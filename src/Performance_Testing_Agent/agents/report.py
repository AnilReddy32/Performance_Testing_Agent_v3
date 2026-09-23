from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext

from ..config import LITELLM_MODEL_NAME, TEMPERATURE


def generate_report(tool_context: ToolContext) -> dict:
    """Generates the final consolidated performance testing report.

    Takes no arguments - it reads whatever test_execution, monitoring,
    security, and analysis results were already collected earlier in this
    conversation directly from shared session state, so it should only be
    called LAST, after everything else the user asked for has already run.
    Stores its own result under "report_result".
    """

    print("===== Report Agent: generate_report =====")

    result = {
        "status": "Generated",
        "summary": {
            "test_execution": tool_context.state.get("test_execution_result"),
            "monitoring": tool_context.state.get("monitoring_result"),
            "security": tool_context.state.get("security_result"),
            "analysis": tool_context.state.get("analysis_result"),
        },
    }

    tool_context.state["report_result"] = result

    return result


report_agent = LlmAgent(
    name="report_agent",
    model=LiteLlm(
        model=LITELLM_MODEL_NAME,
        temperature=TEMPERATURE,
    ),
    mode="single_turn",  # call-and-return, like an ADK workflow node, not a sticky chat transfer
    instruction=(
        "You are the Report Agent for a Banking AI Performance Testing "
        "System. Whenever a PDF, HTML, JSON report, summary, dashboard, "
        "executive report, or final report is requested, call "
        "generate_report (it takes no arguments - it reads prior results "
        "itself) and report back its exact results."
    ),
    description=(
        "Generates the final consolidated report from whatever "
        "test-execution, monitoring, security, and analysis results were "
        "collected earlier in the conversation."
    ),
    tools=[generate_report],
)

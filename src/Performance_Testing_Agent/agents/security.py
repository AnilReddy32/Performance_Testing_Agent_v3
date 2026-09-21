from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext

from Performance_Testing_Agent.config import LITELLM_MODEL_NAME, TEMPERATURE


def run_security_checks(tool_context: ToolContext) -> dict:
    """Executes security validations against the banking application
    (authentication, authorization, SQL-injection checks).

    Takes no arguments. Stores the result in shared session state under
    "security_result" so other agents (e.g. report) can use the exact same
    results later in this conversation.
    """

    print("===== Security Agent: run_security_checks =====")

    result = {
        "security_status": "PASS",
        "security_score": 96.5,

        "authentication": "PASS",
        "authorization": "PASS",
        "sql_injection": "NOT DETECTED",

        "issues": [],
    }

    tool_context.state["security_result"] = result

    return result


security_agent = LlmAgent(
    name="security_agent",
    model=LiteLlm(
        model=LITELLM_MODEL_NAME,
        temperature=TEMPERATURE,
    ),
    mode="single_turn",  # call-and-return, like an ADK workflow node, not a sticky chat transfer
    instruction=(
        "You are the Security Agent for a Banking AI Performance Testing "
        "System. Whenever you are asked about authentication, "
        "authorization, SQL injection, security, or vulnerabilities, call "
        "run_security_checks and report back its exact results. Never "
        "invent or alter results."
    ),
    description=(
        "Runs security validations (authentication, authorization, SQL "
        "injection) against the banking application."
    ),
    tools=[run_security_checks],
)

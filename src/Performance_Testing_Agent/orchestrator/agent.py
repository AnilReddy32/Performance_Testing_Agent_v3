from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from Performance_Testing_Agent.config import LITELLM_MODEL_NAME, TEMPERATURE
from Performance_Testing_Agent.agents.test_execution import test_execution_agent
from Performance_Testing_Agent.agents.monitoring import monitoring_agent
from Performance_Testing_Agent.agents.security import security_agent
from Performance_Testing_Agent.agents.analysis import analysis_agent
from Performance_Testing_Agent.agents.report import report_agent

from .prompts import ORCHESTRATOR_SYSTEM_PROMPT


def build_orchestrator_agent() -> LlmAgent:
    """
    Builds the top-level ADK agent.

    Each domain capability (test execution, monitoring, security, analysis,
    report) is its own real LlmAgent, defined in agents/*.py, wired in here
    as a genuine ADK sub_agent - not a plain function tool. Each teammate
    can own one of those files and swap the mock function for a real
    integration (real k6/JMeter run, real Prometheus query, real Jira/
    Confluence call, etc.) without touching this orchestrator.

    Every sub-agent sets mode="single_turn" (see agents/*.py). That makes
    ADK wrap it as a call-and-return node rather than a full chat "transfer"
    - i.e. the orchestrator calls it, gets a result back, and stays in
    control, which is what lets it run several sub-agents in sequence and
    then produce one final report. Without mode="single_turn", an ADK
    sub-agent would be a one-way handoff target the LLM can "transfer_to",
    permanently giving up control of the conversation - not what we want
    for a sequencing orchestrator.

    Results are shared between sub-agents via session state (see
    tool_context.state inside each agent's tool function in agents/*.py)
    rather than by the orchestrator re-typing numbers into follow-up
    requests, so exact values never get corrupted by an LLM paraphrasing
    them along the way.
    """

    return LlmAgent(
        name="performance_testing_orchestrator",
        model=LiteLlm(
            model=LITELLM_MODEL_NAME,
            temperature=TEMPERATURE,
        ),
        instruction=ORCHESTRATOR_SYSTEM_PROMPT,
        description=(
            "Orchestrates the test-execution, monitoring, security, "
            "analysis and reporting sub-agents for a banking application."
        ),
        sub_agents=[
            test_execution_agent,
            monitoring_agent,
            security_agent,
            analysis_agent,
            report_agent,
        ],
    )


# ADK CLI / dev tooling (e.g. `adk web`, `adk run`) looks for a module-level
# `root_agent` variable, so it is exposed here as well.
root_agent = build_orchestrator_agent()

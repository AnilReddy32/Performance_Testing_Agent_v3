import sys
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import AgentTool

from ..config import LITELLM_MODEL_NAME, TEMPERATURE

# test_execution_agent_adk uses absolute `app.*` imports internally (it's
# built to run standalone via `adk web`/`adk run` from inside its own
# folder, which puts that folder on sys.path). Add it here so those
# internal imports resolve when this package imports it too.
_ADK_APP_ROOT = Path(__file__).resolve().parents[1] / "agents" / "test_execution_agent_adk"
if str(_ADK_APP_ROOT) not in sys.path:
    sys.path.insert(0, str(_ADK_APP_ROOT))



_SECURITY_ADK_ROOT = Path(__file__).resolve().parents[1] / "agents" / "security_agent_adk"
if str(_SECURITY_ADK_ROOT) not in sys.path:
    sys.path.insert(0, str(_SECURITY_ADK_ROOT))

from app.agent import root_agent as test_execution_agent

from security_agent.config import settings

from ..agents.security_agent_adk.security_agent.agent import root_agent as security_agent

from ..agents.monitoring_agent_adk.app.agent import monitoring_agent
# from ..agents.security import security_agent
from ..agents.Analysis_Report_agent_adk.app.agents.analysis.agent import analysis_agent
from ..agents.Analysis_Report_agent_adk.app.agents.report.agent import report_agent

from .prompts import ORCHESTRATOR_SYSTEM_PROMPT
from .tools import (
    bind_explicit_catalog_case,
    load_catalog_test_case,
    record_test_case_prompt,
)



def build_orchestrator_agent() -> LlmAgent:
    """
    Builds the top-level ADK agent.

    Each specialist is wrapped as an AgentTool, allowing the orchestrator
    to call specialists in sequence and retain control. AgentTool forwards
    shared-state updates between its nested runner and this session.

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
        before_agent_callback=bind_explicit_catalog_case,
        description=(
            "Orchestrates the test-execution, monitoring, security, "
            "analysis and reporting sub-agents for a banking application."
        ),
        tools=[
            record_test_case_prompt,
            load_catalog_test_case,
            AgentTool(agent=test_execution_agent, skip_summarization=True),
            AgentTool(agent=monitoring_agent, skip_summarization=True),
            AgentTool(agent=security_agent, skip_summarization=True),
            AgentTool(agent=analysis_agent, skip_summarization=True),
            AgentTool(agent=report_agent, skip_summarization=True),
        ],
    )


# ADK CLI / dev tooling (e.g. `adk web`, `adk run`) looks for a module-level
# `root_agent` variable, so it is exposed here as well.
# root_agent = build_orchestrator_agent()

root_agent = build_orchestrator_agent()




# import sys
# from pathlib import Path

# from google.adk.agents import LlmAgent
# from google.adk.models.lite_llm import LiteLlm

# from ..config import LITELLM_MODEL_NAME, TEMPERATURE

# # test_execution_agent_adk uses absolute `app.*` imports internally (it's
# # built to run standalone via `adk web`/`adk run` from inside its own
# # folder, which puts that folder on sys.path). Add it here so those
# # internal imports resolve when this package imports it too.
# _ADK_APP_ROOT = Path(__file__).resolve().parents[1] / "agents" / "test_execution_agent_adk"
# if str(_ADK_APP_ROOT) not in sys.path:
#     sys.path.insert(0, str(_ADK_APP_ROOT))



# _SECURITY_ADK_ROOT = Path(__file__).resolve().parents[1] / "agents" / "security_agent_adk"
# if str(_SECURITY_ADK_ROOT) not in sys.path:
#     sys.path.insert(0, str(_SECURITY_ADK_ROOT))

# from app.agent import root_agent as test_execution_agent

# from security_agent.config import settings

# from ..agents.security_agent_adk.security_agent.agent import root_agent as security_agent

# from ..agents.monitoring_agent_adk.app.agent import monitoring_agent
# # from ..agents.security import security_agent
# from ..agents.Analysis_Report_agent_adk.app.agents.analysis.agent import analysis_agent
# from ..agents.Analysis_Report_agent_adk.app.agents.report.agent import report_agent

# from .prompts import ORCHESTRATOR_SYSTEM_PROMPT



# def build_orchestrator_agent() -> LlmAgent:
#     """
#     Builds the top-level ADK agent.

#     Each domain capability (test execution, monitoring, security, analysis,
#     report) is its own real LlmAgent, defined in agents/*.py, wired in here
#     as a genuine ADK sub_agent - not a plain function tool. Each teammate
#     can own one of those files and swap the mock function for a real
#     integration (real k6/JMeter run, real Prometheus query, real Jira/
#     Confluence call, etc.) without touching this orchestrator.

#     Every sub-agent sets mode="single_turn" (see agents/*.py). That makes
#     ADK wrap it as a call-and-return node rather than a full chat "transfer"
#     - i.e. the orchestrator calls it, gets a result back, and stays in
#     control, which is what lets it run several sub-agents in sequence and
#     then produce one final report. Without mode="single_turn", an ADK
#     sub-agent would be a one-way handoff target the LLM can "transfer_to",
#     permanently giving up control of the conversation - not what we want
#     for a sequencing orchestrator.

#     Results are shared between sub-agents via session state (see
#     tool_context.state inside each agent's tool function in agents/*.py)
#     rather than by the orchestrator re-typing numbers into follow-up
#     requests, so exact values never get corrupted by an LLM paraphrasing
#     them along the way.
#     """

#     return LlmAgent(
#         name="performance_testing_orchestrator",
#         model=LiteLlm(
#             model=LITELLM_MODEL_NAME,
#             temperature=TEMPERATURE,
#         ),
#         instruction=ORCHESTRATOR_SYSTEM_PROMPT,
#         description=(
#             "Orchestrates the test-execution, monitoring, security, "
#             "analysis and reporting sub-agents for a banking application."
#         ),
#         sub_agents=[
#             test_execution_agent,
#             monitoring_agent,
#             security_agent,
#             analysis_agent,
#             report_agent,
#         ],
#     )


# # ADK CLI / dev tooling (e.g. `adk web`, `adk run`) looks for a module-level
# # `root_agent` variable, so it is exposed here as well.
# # root_agent = build_orchestrator_agent()

# root_agent = build_orchestrator_agent()
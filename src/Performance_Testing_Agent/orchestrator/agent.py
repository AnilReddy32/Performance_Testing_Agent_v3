import sys
import re
from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.agents.context import Context
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import AgentTool
from google.genai import types as genai_types

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
from .pipeline import complete_real_k6_pipeline, json_object
from .tools import (
    bind_explicit_catalog_case,
    load_catalog_test_case,
    record_test_case_prompt,
)


_PIPELINE_REQUEST = re.compile(
    r"\b(?:run|execute|monitor|analy[sz]e?|report|pdf|test case)\b|"
    r"\b(?:PTC|WTC)-\d{3}\b",
    re.IGNORECASE,
)


async def _complete_real_k6_pipeline_for_adk_web(
    callback_context: Context,
) -> genai_types.Content | None:
    """Complete missing REAL k6/JMeter stages when ADK Web runs root_agent directly.

    FastAPI uses the same completion function from Orchestrator.execute. This
    callback covers ADK Web's direct root_agent entry point and skips
    current-job results already produced by the LLM delegation path.
    """
    user_content = callback_context.user_content
    user_query = "\n".join(
        part.text for part in user_content.parts if part.text
    ) if user_content and user_content.parts else ""
    if not user_query or not _PIPELINE_REQUEST.search(user_query):
        return None

    async def invoke_agent(agent, message: str) -> None:
        # ADK's workflow wrapper mutates an LlmAgent with mode=None to
        # single_turn. Use a shallow model copy so AgentTool's shared agent
        # instance keeps its existing configuration for future turns.
        agent_node = agent.model_copy(update={"mode": "single_turn"})
        await callback_context.run_node(agent_node, node_input=message)

    pipeline = await complete_real_k6_pipeline(
        state=callback_context.state,
        user_query=user_query,
        invoke_agent=invoke_agent,
        monitoring_agent=monitoring_agent,
        security_agent=security_agent,
        analysis_agent=analysis_agent,
        report_agent=report_agent,
    )
    if pipeline is None:
        return None

    # If the LLM already completed every stage, preserve its natural-language
    # answer. When this callback had to fill a stage, make that completion
    # visible in ADK Web's final response.
    if all(
        status == "already_available" or status.startswith("skipped:")
        for status in pipeline.values()
    ):
        return None

    report_result = json_object(callback_context.state.get("report_result"))
    report_path = report_result.get("file_path") if report_result else None
    profile = callback_context.state.get("workload_profile")
    tool = profile.get("tool") if isinstance(profile, dict) else "k6"
    pipeline_label = "REAL JMeter pipeline" if tool == "jmeter" else "REAL k6 pipeline"
    if isinstance(report_path, str) and report_path:
        message = f"{pipeline_label} completed. Final report: {report_path}"
    else:
        stage_summary = ", ".join(
            f"{stage}={status}" for stage, status in pipeline.items()
        )
        message = (
            f"{pipeline_label} finished with an incomplete report stage. "
            f"Stage status: {stage_summary}"
        )
    return genai_types.Content(
        role="model",
        parts=[genai_types.Part(text=message)],
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
        after_agent_callback=_complete_real_k6_pipeline_for_adk_web,
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

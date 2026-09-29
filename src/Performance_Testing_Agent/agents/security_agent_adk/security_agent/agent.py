from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import AgentTool

from security_agent.config import settings
from security_agent.tools.api_tool import get_api_information
from security_agent.tools.profile_tool import get_application_profile
from security_agent.tools.security_tool import assess_authentication, assess_jwt, assess_rbac, assess_oauth, assess_mfa, assess_api_security, assess_rate_limiting,     assess_sql_injection, assess_xss, assess_csrf

from security_agent.tools.assessment_tool import (create_assessment_state, record_evidence, record_assessment, record_missing_evidence, finalize_assessment)


BASE_DIR = Path(__file__).resolve().parent
SKILL_PATH = BASE_DIR / "prompts" / "security_agent_skill.md"


def load_security_skill() -> str:
    """Load the Security Agent behavioral specification."""
    return SKILL_PATH.read_text(encoding="utf-8")


if not settings.OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY is not configured."
    )

if not settings.OPENAI_MODEL:
    raise RuntimeError(
        "OPENAI_MODEL is not configured."
    )


# All 16 security tools live on this sub-agent instead of on root_agent
# directly. It is wrapped with AgentTool below (not registered via
# sub_agents=[...]), so it shows up in the adk web agent graph as a single
# node instead of expanding into all 16 underlying tools. AgentTool runs it
# through its own nested Runner/session, but forwards every state delta
# from the nested run back onto the caller's real session (see
# AgentTool.run_async's "Forward state delta to parent session" step), so
# tool_context.state writes such as finalize_assessment's security_result
# still land on the real session exactly as before.
#
# mode='chat' is required here (not 'single_turn'): AgentTool runs this
# agent as the root of its own nested Runner, and Runner.run_async only
# accepts a directly-run LlmAgent whose mode is 'chat' or 'task'.
security_operations_agent = LlmAgent(
    name="security_operations_agent",
    model=LiteLlm(
        model=settings.OPENAI_MODEL,
    ),
    mode="chat",
    description=(
        "Runs the full application and API security assessment workflow "
        "(evidence retrieval, deterministic validators, and assessment "
        "state finalization) for the given security objective and returns "
        "the structured SecurityResponse."
    ),
    instruction=load_security_skill(),
    tools=[
        get_application_profile,
        get_api_information,

        assess_authentication,
        assess_jwt,
        assess_rbac,
        assess_oauth,
        assess_mfa,
        assess_api_security,
        assess_rate_limiting,
        assess_sql_injection,
        assess_xss,
        assess_csrf,

        create_assessment_state,
        record_evidence,
        record_assessment,
        record_missing_evidence,
        finalize_assessment,
    ],
)


root_agent = LlmAgent(
    name="security_agent",
    model=LiteLlm(
        model=settings.OPENAI_MODEL,
    ),
    mode = "single_turn",
    description=(
        "Production-grade Security Agent responsible for "
        "application and API security assessment."
    ),
    instruction=(
        "Forward the incoming security objective verbatim to the "
        "`security_operations_agent` tool and return its result exactly "
        "as received, with no modification, reformatting, summarization, "
        "or added commentary. Do not call any other tool."
    ),
    tools=[AgentTool(agent=security_operations_agent)],
)


app = App(
    name="security_agent",
    root_agent=root_agent,
)


__all__ = ["root_agent", "app"]
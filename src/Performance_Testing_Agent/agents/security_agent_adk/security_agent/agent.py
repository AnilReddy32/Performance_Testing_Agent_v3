from pathlib import Path

from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.models.lite_llm import LiteLlm

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


root_agent = LlmAgent(
    name="security_agent",
    model=LiteLlm(
        model=settings.OPENAI_MODEL,
    ),
    description=(
        "Production-grade Security Agent responsible for "
        "application and API security assessment."
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


app = App(
    name="security_agent",
    root_agent=root_agent,
)


__all__ = ["root_agent", "app"]
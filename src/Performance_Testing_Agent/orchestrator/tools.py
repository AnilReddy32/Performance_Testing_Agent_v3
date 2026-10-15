"""
Orchestrator-level tools.

record_test_case_prompt is the one new piece needed so the final report
can include the user's original request verbatim: it's an ordinary tool
call (same pattern every other agent in this codebase already uses to
write results into shared session state via tool_context.state), not a
framework-level callback.
"""

from typing import Any

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import ToolContext

from Performance_Testing_Agent.execution_context import (
    create_context_for_test_case,
    extract_catalog_test_case_id,
)
from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case


def record_test_case_prompt(prompt: str, tool_context: ToolContext) -> dict:
    """
    Records the user's exact original request text into shared session
    state under "test_case_prompt". Must be called ONCE, at the very start
    of handling any new user request, BEFORE any other agent runs.

    prompt: the user's message, copied verbatim - never paraphrased.
    """
    tool_context.state["test_case_prompt"] = prompt
    return {"recorded": True}


def bind_explicit_catalog_case(
    callback_context: CallbackContext,
) -> None:
    """Bind an explicit PTC/WTC ID before the orchestrator plans its turn."""
    content = callback_context.user_content
    if content is None:
        return
    request_text = "\n".join(
        part.text for part in content.parts if part.text
    )
    test_case_id = extract_catalog_test_case_id(request_text)
    if test_case_id is None:
        return
    state = callback_context.state
    if state.get("test_case_id") == test_case_id:
        return
    _bind_catalog_test_case(test_case_id, state, "ADK_WEB")


def load_catalog_test_case(
    test_case_id: str,
    tool_context: ToolContext,
) -> dict:
    """Bind an explicitly selected trusted catalog case to this ADK session."""
    normalized_id = test_case_id.strip().upper()
    if not normalized_id:
        raise ValueError("A catalog test_case_id is required.")

    return _bind_catalog_test_case(
        normalized_id,
        tool_context.state,
        "ADK_WEB",
    )


def _bind_catalog_test_case(
    normalized_id: str,
    state: Any,
    source_id: str,
) -> dict:
    case = get_test_case(normalized_id)
    existing_id = state.get("test_case_id")
    execution_status = state.get("execution_status")
    if existing_id == normalized_id:
        return {
            "status": "already_loaded",
            "test_case_id": normalized_id,
            "name": case["name"],
            "execution_mode": state.get("execution_mode"),
            "job_id": state.get("job_id"),
        }

    can_replace_job = execution_status in {
        "not_started",
        "needs_input",
        "blocked",
        "prepared",
        "completed",
        "failed",
    }
    if existing_id is not None and not can_replace_job:
        raise ValueError(
            "This session already has a different trusted test case "
            f"({existing_id}) and an active or unrecognized job."
        )
    if state.get("job_id") is not None and execution_status not in {
        "not_started",
        "needs_input",
        "blocked",
        "prepared",
        "completed",
        "failed",
    }:
        raise ValueError(
            "This session has an active or unrecognized execution job; "
            "start a new session before selecting another catalog case."
        )

    context = create_context_for_test_case(case, source_id=source_id)
    state.update(context)
    state.update(
        {
            state_key: None
            for state_key in (
                "test_execution_result",
                "execution_stage_result",
                "monitoring_result",
                "security_result",
                "analysis_result",
                "report_result",
            )
        }
    )
    return {
        "status": "loaded",
        "test_case_id": normalized_id,
        "name": case["name"],
        "execution_mode": context["execution_mode"],
        "preflight": context["execution_preflight"],
        "job_id": context["job_id"],
    }
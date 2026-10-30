from typing import Any
from google.adk.tools import ToolContext
from security_agent.models.assessment import AssessmentState
from security_agent.models.request import (
    SecurityAssessmentRequest,
    build_security_assessment_request,
)
from security_agent.security.assessment import (
    add_assessment,
    add_evidence,
    add_missing_evidence,
    build_security_response,
    update_conflicts,
)
from security_agent.passive.service import run_passive_checks
from security_agent.security.evaluation import evaluate_configured_controls
from security_agent.security.profiles import select_profile
from security_agent.tools.state_utils import snapshot_session_state
from security_agent.tools.live_test_tool import execute_authorized_live_test


def get_security_assessment_context(
    objective: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Return the request contract and matched profile identity from trusted job state."""

    request = build_security_assessment_request(
        objective=objective,
        session_state=snapshot_session_state(tool_context.state),
    )
    # Security assessments can be repeated for the same performance job.
    # Clear any previous observation so finalization cannot reuse stale data.
    tool_context.state["security_live_test_result"] = None
    tool_context.state["security_passive_result"] = None
    tool_context.state["security_result_fresh"] = False
    return request.model_dump(mode="json")


def evaluate_configured_security_controls(
    objective: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Run requested deterministic validators on the trusted matched profile."""
    session_state = snapshot_session_state(tool_context.state)
    request = build_security_assessment_request(objective, session_state)
    try:
        selection = select_profile(session_state)
    except (OSError, ValueError) as exc:
        selection = {
            "status": "no_match",
            "reason": f"The versioned application profile registry could not be used: {exc}",
        }
    return evaluate_configured_controls(request, selection)


def create_assessment_state(
    objective: str,
    request_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Create a new security assessment state.

    Args:
        objective: Original security assessment objective.

    Returns:
        Serialized assessment state.
    """

    context = (
        SecurityAssessmentRequest.model_validate(request_context)
        if request_context is not None
        else None
    )
    state = AssessmentState(objective=objective, request_context=context)

    return state.model_dump()


def record_evidence(
    state_data: dict[str, Any],
    source: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """
    Record retrieved security evidence in the assessment state.
    """

    state = AssessmentState.model_validate(state_data)

    state = add_evidence(
        state=state,
        source=source,
        data=data,
    )

    return state.model_dump()


def record_assessment(
    state_data: dict[str, Any],
    control: str,
    result: dict[str, Any],
    evidence_sources: list[str] | None = None,
) -> dict[str, Any]:
    """
    Record a deterministic security assessment result.
    """

    state = AssessmentState.model_validate(state_data)

    state = add_assessment(
        state=state,
        control=control,
        result=result,
        evidence_sources=evidence_sources,
    )

    state = update_conflicts(state)

    return state.model_dump()


def record_missing_evidence(
    state_data: dict[str, Any],
    requirement: str,
) -> dict[str, Any]:
    """
    Record evidence required but unavailable.
    """

    state = AssessmentState.model_validate(state_data)

    state = add_missing_evidence(
        state=state,
        requirement=requirement,
    )

    return state.model_dump()


def finalize_assessment(
    state_data: dict[str, Any],
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Convert the accumulated assessment state into the
    standard SecurityResponse contract.
    """

    state = AssessmentState.model_validate(state_data)
    # Always bind the finalized result to the current trusted session context.
    # The incoming request_context is useful to the agent while it works, but
    # it is not authoritative for job, target, or live-test authorization.
    state.request_context = build_security_assessment_request(
        objective=state.objective,
        session_state=snapshot_session_state(tool_context.state),
    )
    session_state = snapshot_session_state(tool_context.state)
    try:
        selection = select_profile(session_state)
    except (OSError, ValueError) as exc:
        selection = {
            "status": "no_match",
            "reason": f"The versioned application profile registry could not be used: {exc}",
        }
    evaluation = evaluate_configured_controls(state.request_context, selection)
    live_result = session_state.get("security_live_test_result")
    if not state.request_context.live_testing_requested or not isinstance(live_result, dict):
        live_result = None
    elif live_result.get("job_id") != state.request_context.job_id:
        live_result = None
    elif live_result.get("status") in {"completed", "failed"} and (
        live_result.get("target_origin") != state.request_context.target_origin
        or live_result.get("endpoint") != state.request_context.endpoint
        or live_result.get("method") != "HEAD"
    ):
        live_result = None
    passive_result = session_state.get("security_passive_result")
    result = build_security_response(
        state,
        evaluation=evaluation,
        live_result=live_result,
        passive_result=passive_result if isinstance(passive_result, dict) else None,
    ).model_dump(mode="json")

    tool_context.state["security_result"] = result
    # Marks this run's result as the one the agent must answer with verbatim.
    tool_context.state["security_result_fresh"] = True

    return result


async def finalize_assessment_with_live_observation(
    state_data: dict[str, Any],
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Ensure requested bounded live observation runs before finalization.

    The model may call the observation tool explicitly during its workflow. If
    it skips that tool, this deterministic finalization step performs the same
    guarded operation so a requested check cannot silently become ``not_run``.
    """
    assessment = AssessmentState.model_validate(state_data)
    session_state = snapshot_session_state(tool_context.state)
    request = build_security_assessment_request(
        objective=assessment.objective,
        session_state=session_state,
    )
    if request.passive_assessment_requested:
        # The passive assessment is deterministic and replaces the single HEAD
        # observation; run it here so it cannot be skipped by the model.
        existing = session_state.get("security_passive_result")
        if not (isinstance(existing, dict) and existing.get("job_id") == request.job_id):
            tool_context.state["security_passive_result"] = await run_passive_checks(
                session_state
            )
    else:
        live_result = session_state.get("security_live_test_result")
        if request.live_testing_requested and not isinstance(live_result, dict):
            await execute_authorized_live_test(assessment.objective, tool_context)
    return finalize_assessment(state_data, tool_context)

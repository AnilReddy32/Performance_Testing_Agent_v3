from typing import Any

from security_agent.models.assessment import AssessmentState
from security_agent.security.assessment import (
    add_assessment,
    add_evidence,
    add_missing_evidence,
    build_security_response,
    update_conflicts,
)


def create_assessment_state(
    objective: str,
) -> dict[str, Any]:
    """
    Create a new security assessment state.

    Args:
        objective: Original security assessment objective.

    Returns:
        Serialized assessment state.
    """

    state = AssessmentState(
        objective=objective,
    )

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
) -> dict[str, Any]:
    """
    Convert the accumulated assessment state into the
    standard SecurityResponse contract.
    """

    state = AssessmentState.model_validate(state_data)

    return build_security_response(state).model_dump()
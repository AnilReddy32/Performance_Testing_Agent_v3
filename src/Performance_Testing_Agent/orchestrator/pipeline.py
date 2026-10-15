"""Deterministic completion for terminal REAL k6 orchestration runs."""

import json
import re
from collections.abc import Awaitable, Callable, MutableMapping
from typing import Any

from Performance_Testing_Agent.orchestrator.logger import logger

_SECURITY_REQUEST = re.compile(
    r"\b(?:security|vulnerabilit\w*|penetration|sql injection|"
    r"authentication|authorization|oauth|owasp)\b",
    re.IGNORECASE,
)
_SECURITY_NEGATION = re.compile(
    r"\b(?:do not|don't|without|skip)\s+(?:run\s+)?security\b",
    re.IGNORECASE,
)


def json_object(value: object) -> dict | None:
    """Normalize structured agent state, whose output_key may be JSON text."""
    if isinstance(value, dict):
        return value
    if not isinstance(value, str):
        return None
    candidate = value.strip()
    if candidate.startswith("```") and candidate.endswith("```"):
        candidate = candidate.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
    try:
        parsed = json.loads(candidate)
    except (TypeError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


async def complete_real_k6_pipeline(
    *,
    state: MutableMapping[str, Any],
    user_query: str,
    invoke_agent: Callable[[Any, str], Awaitable[None]],
    monitoring_agent: Any,
    security_agent: Any,
    analysis_agent: Any,
    report_agent: Any,
    agents_called: list[str] | None = None,
) -> dict[str, str] | None:
    """Fill missing downstream stages for terminal REAL k6 jobs only.

    The supplied invoker determines the ADK entry point, while this function
    owns common gating, job checks, and idempotent stage sequencing. It never
    starts or repeats k6 execution.
    """
    profile = state.get("workload_profile")
    execution_status = state.get("execution_status")
    if (
        state.get("execution_mode") != "REAL"
        or not isinstance(profile, dict)
        or profile.get("tool") != "k6"
        or execution_status not in {"completed", "failed", "blocked", "needs_input"}
    ):
        return None

    job_id = state.get("job_id")
    if not isinstance(job_id, str) or not job_id:
        return None

    pipeline: dict[str, str] = {}

    async def invoke_if_missing(
        stage: str,
        agent: Any,
        message: str,
        result_key: str,
        *,
        current_job_required: bool = True,
    ) -> None:
        existing = json_object(state.get(result_key))
        if existing is not None and (
            not current_job_required or existing.get("job_id") == job_id
        ):
            state[result_key] = existing
            pipeline[stage] = "already_available"
            return

        try:
            await invoke_agent(agent, message)
            if agents_called is not None and agent.name not in agents_called:
                agents_called.append(agent.name)
            result = json_object(state.get(result_key))
            if result is not None and (
                not current_job_required or result.get("job_id") == job_id
            ):
                state[result_key] = result
                pipeline[stage] = "completed"
            else:
                pipeline[stage] = "missing_result"
        except Exception as exc:  # keep later independent stages available
            logger.exception("REAL k6 pipeline stage %s failed", stage)
            pipeline[stage] = f"failed: {type(exc).__name__}: {exc}"

    if execution_status == "completed":
        await invoke_if_missing(
            "monitoring",
            monitoring_agent,
            "Monitor the completed REAL k6 execution for this job. "
            "Use only its current job-scoped REAL monitoring samples; "
            "do not substitute simulated values.",
            "monitoring_result",
        )
    else:
        pipeline["monitoring"] = "skipped: execution was not completed"

    security_requested = bool(_SECURITY_REQUEST.search(user_query)) and not bool(
        _SECURITY_NEGATION.search(user_query)
    )
    if security_requested:
        await invoke_if_missing(
            "security",
            security_agent,
            "Perform the security assessment explicitly requested in this "
            "user request for the current API/test context. Do not claim "
            "checks that were not performed. User request: " + user_query,
            "security_result",
            current_job_required=False,
        )
    else:
        pipeline["security"] = "skipped: not requested"

    await invoke_if_missing(
        "analysis",
        analysis_agent,
        "Analyze the current job using its current test_execution_result, "
        "monitoring_result, and any explicitly requested security_result. "
        "Do not use results from another job. Follow your required tool "
        "sequence and return the structured analysis.",
        "analysis_result",
    )

    analysis = json_object(state.get("analysis_result"))
    if analysis is None or analysis.get("job_id") != job_id:
        pipeline["report"] = "skipped: current-job analysis is unavailable"
        state["real_k6_pipeline"] = pipeline
        return pipeline

    await invoke_if_missing(
        "report",
        report_agent,
        "Generate the final PDF report for the current job from its "
        "analysis_result. Include only current-job evidence, run the "
        "report tool sequence, and return the structured report result.",
        "report_result",
    )

    state["real_k6_pipeline"] = pipeline
    return pipeline

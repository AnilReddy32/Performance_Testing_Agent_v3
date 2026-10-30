"""Deterministic completion for terminal REAL performance-test runs."""

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
# The automatic passive assessment is on by default; the text can opt out. The
# wording rules mirror jira_agent_integration.stage_plan so both entry points
# read a refusal the same way.
_SECURITY_WORD = re.compile(
    r"\b(?:security|vulnerabilit\w*|penetration|pen[- ]?test\w*|owasp|sql injection)\b",
    re.IGNORECASE,
)
_NEGATION_WORDS = {
    "not", "don't", "dont", "never", "skip", "skipping", "without",
    "exclude", "excluding", "avoid", "no", "omit", "omitting",
    "ignore", "ignoring", "disable", "disabling",
}
# "don't forget security", "do not miss the security checks": a negation that
# asks for the opposite of a refusal.
_REVERSING_WORDS = {
    "forget", "forgetting", "miss", "overlook", "neglect",
    "problem", "problems", "issue", "issues", "doubt", "worries",
}
_LEAVE_OUT = re.compile(r"\bleave\s+out\b", re.IGNORECASE)
_NOT_NEEDED_AFTER = re.compile(
    r"\b(?:is\s+not|isn't|not)\s+(?:required|needed|necessary|wanted)\b|\bunnecessary\b"
    r"|\b(?:out\s+of\s+scope|disabled|skipped|excluded|off)\b"
    r"|\bnot\s+this\s+time\b|[:\-]\s*(?:skip|off|no|none)\b",
    re.IGNORECASE,
)
_CLAUSE_SPLIT = re.compile(r"[.!?;\n,]+")
# Result keys the Analysis step may drop when it re-types the security result.
_SECURITY_CHECK_KEYS = ("check_results", "check_summary", "assessment_outcome")

# Takes the pipeline state and returns a complete security result for the
# current job, or None when an automatic assessment does not apply to it.
PassiveSecurity = Callable[[MutableMapping[str, Any]], Awaitable["dict[str, Any] | None"]]


def _refused_mentions(user_query: str) -> list[bool]:
    """One flag per security keyword in the text: is that mention a refusal?"""
    flags: list[bool] = []
    for clause in _CLAUSE_SPLIT.split(user_query or ""):
        for match in _SECURITY_WORD.finditer(clause):
            before = clause[: match.start()]
            nearby = re.findall(r"[\w']+", before.lower())[-6:]
            negations = sum(word in _NEGATION_WORDS for word in nearby) + bool(
                _LEAVE_OUT.search(before[-24:])
            )
            refused_before = negations == 1 and not set(nearby) & _REVERSING_WORDS
            refused_after = bool(_NOT_NEEDED_AFTER.search(clause[match.end():]))
            flags.append(refused_before or refused_after)
    return flags


def security_opted_out(user_query: str) -> bool:
    """True when the request text asks for security to be skipped.

    The explicit forms ("do not run security", "skip security", "without
    security") always opt out. Other wordings ("no penetration testing",
    "security: skip", "omit security") opt out only when every security mention
    in the text is a refusal, so "assess the security surface but skip the
    vulnerability scan" still asks for security.
    """
    if _SECURITY_NEGATION.search(user_query or ""):
        return True
    flags = _refused_mentions(user_query)
    return bool(flags) and all(flags)


def _security_ran_too_early(result: dict | None) -> bool:
    """True for a security result blocked because the performance run had not ended."""
    if not isinstance(result, dict):
        return False
    live = result.get("live_test_result")
    live = live if isinstance(live, dict) else {}
    return live.get("reason_code") == "run_not_finished" or (
        "only after the performance execution has ended" in str(live.get("reason", ""))
    )


def _security_for_prompt(security_result: object) -> object:
    """The model needs the verdict, not every check's raw evidence to re-type."""
    if isinstance(security_result, dict) and "check_results" in security_result:
        return {k: v for k, v in security_result.items() if k != "check_results"}
    return security_result


def _restore_security_checks(
    analysis: dict[str, Any], state: MutableMapping[str, Any], job_id: str
) -> None:
    """Carry the per-check verdicts into the analysis exactly as the agent produced them.

    The Analysis agent re-types the security result, so the pipeline puts the
    authoritative check fields back rather than trusting the copy. Results
    without per-check verdicts are left exactly as they were.
    """
    current = json_object(state.get("security_result"))
    if (
        current is None
        or current.get("job_id") != job_id
        or not isinstance(current.get("check_results"), list)
    ):
        return
    summary = analysis.get("security_summary")
    if not isinstance(summary, dict):
        try:
            from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.agents.analysis.tools import (
                summarize_security,
            )

            rebuilt = summarize_security(current, job_id)
        except Exception:
            logger.exception("Could not rebuild the security summary for the analysis")
            return
        if rebuilt:
            analysis["security_summary"] = rebuilt
            if (
                str(rebuilt.get("status", "")).upper() == "FAIL"
                and analysis.get("overall_status") != "fail"
            ):
                analysis["overall_status"] = "fail"
        return
    if summary.get("job_id") != job_id:
        return
    for key in _SECURITY_CHECK_KEYS:
        if key in current:
            summary[key] = current[key]


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


async def _run_automatic_security(
    *,
    state: MutableMapping[str, Any],
    user_query: str,
    job_id: str,
    execution_status: object,
    passive_security: PassiveSecurity | None,
    persist_state: Callable[[dict[str, Any]], Awaitable[None]] | None,
    analysis_ready: bool = False,
) -> str:
    """Run the model-free passive assessment for a run that did not ask for security.

    Returns the pipeline stage status. Nothing is sent unless every condition
    holds: an assessor was supplied, the run ended, the text does not opt out,
    and the assessor itself finds an external HTTPS API target.
    """
    skipped = "skipped: not requested"
    if (
        passive_security is None
        or execution_status not in {"completed", "failed"}
        or security_opted_out(user_query)
    ):
        return skipped
    if analysis_ready:
        # Analysis (and so the report) already exist without security; a late scan
        # could not reach them, so nothing is sent.
        return "skipped: analysis was already produced for this job"
    existing = json_object(state.get("security_result"))
    if existing is not None and existing.get("job_id") == job_id:
        state["security_result"] = existing
        return "already_available"
    try:
        result = await passive_security(state)
    except Exception as exc:  # security must never stop analysis or the report
        logger.exception("Automatic passive security assessment failed")
        return f"failed: {type(exc).__name__}: {exc}"
    if result is None:
        return skipped
    if not isinstance(result, dict) or result.get("job_id") != job_id:
        return "missing_result"
    state["security_result"] = result
    if persist_state is not None:
        try:
            await persist_state({"security_result": result})
        except Exception:
            logger.exception("Could not persist the automatic security result")
    return "completed (automatic passive assessment)"


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
    persist_state: Callable[[dict[str, Any]], Awaitable[None]] | None = None,
    monitoring_requested: bool | None = None,
    security_requested: bool | None = None,
    passive_security: PassiveSecurity | None = None,
) -> dict[str, str] | None:
    """Fill missing downstream stages for terminal REAL k6 and JMeter jobs.

    The supplied invoker determines the ADK entry point, while this function
    owns common gating, job checks, and idempotent stage sequencing. It never
    starts or repeats the load test.

    monitoring_requested / security_requested let a caller that has already
    planned its stages decide them explicitly. None keeps the default: monitor
    every completed run, and run the full security agent when the query asks
    for it. A run that did not ask for security still gets the automatic
    passive assessment when ``passive_security`` is supplied, the target is an
    external API, and the text does not opt out.
    """
    profile = state.get("workload_profile")
    tool = profile.get("tool") if isinstance(profile, dict) else None
    execution_status = state.get("execution_status")
    if (
        state.get("execution_mode") != "REAL"
        or not isinstance(profile, dict)
        or tool not in {"k6", "jmeter"}
        or execution_status not in {"completed", "failed", "blocked", "needs_input"}
    ):
        return None

    pipeline_state_key = (
        "real_jmeter_pipeline" if tool == "jmeter" else "real_k6_pipeline"
    )

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
        existing_is_current = existing is not None and (
            not current_job_required or existing.get("job_id") == job_id
        )
        if result_key == "report_result":
            existing_is_current = bool(
                existing_is_current and isinstance(existing.get("file_path"), str)
                and existing["file_path"].strip()
                and existing.get("report_format") in {"pdf", "both"}
                and existing.get("rejected") is False
            )
        if existing_is_current:
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
            logger.exception("REAL performance pipeline stage %s failed", stage)
            pipeline[stage] = f"failed: {type(exc).__name__}: {exc}"

    if monitoring_requested is False:
        pipeline["monitoring"] = "skipped: not requested"
    elif execution_status == "completed":
        await invoke_if_missing(
            "monitoring",
            monitoring_agent,
            f"Monitor the completed REAL {tool} execution for this job. "
            "Use only its current job-scoped REAL monitoring samples; "
            "do not substitute simulated values.",
            "monitoring_result",
        )
    else:
        pipeline["monitoring"] = "skipped: execution was not completed"

    if _security_ran_too_early(json_object(state.get("security_result"))):
        # It was blocked only because it started while the test was still running.
        # The run has ended now, so that result is not the answer: assess again.
        logger.info("Discarding a security result produced before the run ended.")
        state["security_result"] = None
    if security_requested is None:
        security_requested = bool(
            _SECURITY_REQUEST.search(user_query)
        ) and not security_opted_out(user_query)
    if security_requested:
        await invoke_if_missing(
            "security",
            security_agent,
            "Perform the security assessment explicitly requested in this "
            "user request for the current API/test context. Do not claim "
            "checks that were not performed. User request: " + user_query,
            "security_result",
            current_job_required=True,
        )
    else:
        pipeline["security"] = await _run_automatic_security(
            state=state,
            user_query=user_query,
            job_id=job_id,
            execution_status=execution_status,
            passive_security=passive_security,
            persist_state=persist_state,
            analysis_ready=(
                (json_object(state.get("analysis_result")) or {}).get("job_id") == job_id
            ),
        )

    execution_stage = json_object(state.get("execution_stage_result")) or {}
    execution_artifacts = state.get("execution_artifacts")
    artifact_values = (
        execution_artifacts.get("artifacts", {})
        if isinstance(execution_artifacts, dict)
        and execution_artifacts.get("job_id") == job_id
        else {}
    )
    analysis_inputs = {
        "job_id": job_id,
        "execution_mode": "REAL",
        "execution_status": execution_status,
        "execution_stage_result": execution_stage,
        "test_execution_result": (
            state.get("test_execution_result")
            if isinstance(state.get("test_execution_result"), dict)
            and state["test_execution_result"].get("job_id") == job_id
            else None
        ),
        "monitoring_result": (
            state.get("monitoring_result")
            if isinstance(state.get("monitoring_result"), dict)
            and state["monitoring_result"].get("job_id") == job_id
            else None
        ),
        "security_result": (
            state.get("security_result")
            if isinstance(state.get("security_result"), dict)
            and state["security_result"].get("job_id") == job_id
            else None
        ),
        "execution_artifacts": artifact_values,
    }
    # An automatic scan that could assess nothing (target blocked, DNS failure, every
    # check inconclusive) must not make an otherwise clean run look worse: Analysis
    # is not shown it. The result is still attached for the report to display.
    automatic_but_unassessed = (
        pipeline.get("security", "").startswith("completed (automatic")
        and isinstance(analysis_inputs["security_result"], dict)
        and analysis_inputs["security_result"].get("assessment_outcome") == "not_assessed"
    )
    await invoke_if_missing(
        "analysis",
        analysis_agent,
        "Analyze the current job using its current test_execution_result, "
        "monitoring_result, execution_stage_result, and any security_result "
        "shown below. Use only evidence for this "
        "job. If execution failed or metrics are absent, preserve the failure "
        "as unavailable/invalid data and do not invent measurements. Follow "
        "your tool sequence and return structured analysis. Current-job "
        "inputs: " + json.dumps(
            {
                **analysis_inputs,
                "security_result": (
                    None
                    if automatic_but_unassessed
                    else _security_for_prompt(analysis_inputs["security_result"])
                ),
            },
            separators=(",", ":"),
            default=str,
        ),
        "analysis_result",
    )

    analysis = json_object(state.get("analysis_result"))
    analysis_is_current = analysis is not None and analysis.get("job_id") == job_id
    if not analysis_is_current:
        pipeline["analysis"] = pipeline.get(
            "analysis", "missing_result: current-job analysis is unavailable"
        )
        analysis = None
    elif isinstance(analysis.get("security_summary"), dict):
        if analysis["security_summary"].get("job_id") != job_id:
            logger.warning("Ignoring Analysis security_summary with a mismatched job_id")
            analysis["security_summary"] = None
    if analysis is not None:
        _restore_security_checks(analysis, state, job_id)

    terminal_analysis_unusable = (
        analysis is None
        or analysis.get("ready_for_report") is False
        or analysis.get("data_quality_status") == "invalid"
    )
    stage_status = str(execution_stage.get("status") or execution_status)
    execution_message = execution_stage.get("message")
    if not isinstance(execution_message, str) or not execution_message.strip():
        execution_message = (
            "The REAL execution failed before usable metrics were available."
            if execution_status == "failed"
            else "The REAL execution completed."
        )
    outcome: dict[str, Any] = {
        "job_id": job_id,
        "execution_mode": "REAL",
        "execution_status": execution_status,
        "security_requested": security_requested,
        "runner_status": stage_status,
        "message": execution_message,
    }
    for field in ("exit_code", "thresholds_passed", "threshold_failures", "blocked_reasons"):
        if field in execution_stage:
            outcome[field] = execution_stage[field]
    for key in ("monitoring_result", "security_result"):
        current_result = json_object(analysis_inputs.get(key))
        if current_result is not None:
            outcome[key] = current_result

    workload_profile = state.get("workload_profile")
    safe_profile_fields = (
        "tool", "target_url", "endpoint", "method", "users", "max_rps",
        "duration_seconds", "ramp_up_seconds", "expected_status_code",
        "p95_threshold_ms",
    )
    safe_profile = (
        {
            key: workload_profile[key]
            for key in safe_profile_fields
            if workload_profile.get(key) is not None
        }
        if isinstance(workload_profile, dict)
        else {}
    )

    if terminal_analysis_unusable or execution_status == "failed":
        failure_message = execution_message
        if execution_status != "failed" and terminal_analysis_unusable:
            failure_message = (
                analysis.get("unusable_reason")
                if isinstance(analysis, dict)
                else "Analysis did not return a current-job result."
            )
            outcome["message"] = failure_message

        app_name = (
            str((state.get("workload_profile") or {}).get("application") or "Unknown")
            if isinstance(state.get("workload_profile"), dict)
            else "Unknown"
        )
        scenario = str(
            state.get("test_case_name")
            or (state.get("workload_profile") or {}).get("scenario")
            or "Performance Test"
        )
        report_context = (
            analysis.get("time_series_analysis")
            if isinstance(analysis, dict)
            and isinstance(analysis.get("time_series_analysis"), dict)
            else {}
        )
        artifacts = (
            artifact_values
            if isinstance(artifact_values, dict)
            else {}
        )
        if isinstance(report_context, dict):
            report_context.setdefault("execution_artifacts", artifacts)
        summary = (
            f"REAL {tool} execution status: {execution_status}. {failure_message} "
            "No performance conclusion is drawn from metrics that were unavailable."
        )
        if execution_status == "completed" and terminal_analysis_unusable:
            summary = (
                f"REAL {tool} execution completed, but the available results could "
                f"not be validated for analysis: {failure_message}"
            )
        security_for_status = (analysis or {}).get("security_summary")
        if not isinstance(security_for_status, dict):
            security_for_status = outcome.get("security_result")
        security_failed = (
            isinstance(security_for_status, dict)
            and str(security_for_status.get("status", "")).upper() == "FAIL"
            and security_for_status.get("job_id") == job_id
        )
        analysis = {
            **(analysis or {}),
            "job_id": job_id,
            "application": str((analysis or {}).get("application") or app_name),
            "scenario": str((analysis or {}).get("scenario") or scenario),
            "test_case_prompt": (analysis or {}).get("test_case_prompt") or user_query,
            "data_quality_status": (analysis or {}).get("data_quality_status") or "invalid",
            "unusable_reason": (analysis or {}).get("unusable_reason") or failure_message,
            "overall_status": (
                "fail" if execution_status == "failed" or security_failed else "warning"
            ),
            "api_findings": (analysis or {}).get("api_findings") or [],
            "infra_health": (analysis or {}).get("infra_health"),
            "security_summary": (analysis or {}).get("security_summary"),
            "time_series_analysis": report_context,
            "execution_mode": "REAL",
            "execution_status": execution_status,
            "execution_outcome": outcome,
            "execution_profile": (analysis or {}).get("execution_profile") or safe_profile,
            "execution_artifact_directory": (
                (analysis or {}).get("execution_artifact_directory")
                or state.get("execution_artifact_directory")
            ),
            "execution_artifacts": {
                **(
                    (analysis or {}).get("execution_artifacts")
                    if isinstance((analysis or {}).get("execution_artifacts"), dict)
                    else {}
                ),
                **artifacts,
            },
            "summary": (
                summary
                if execution_status == "failed"
                else (analysis or {}).get("summary") or summary
            ),
            "ready_for_report": True,
        }
        pipeline["analysis"] = pipeline.get("analysis", "completed") + "; made terminal outcome reportable"

    if analysis is not None and execution_status in {"completed", "failed"}:
        analysis["execution_mode"] = "REAL"
        analysis["execution_status"] = execution_status
        analysis["execution_outcome"] = outcome
        analysis["execution_profile"] = safe_profile
        analysis["execution_artifact_directory"] = (
            state.get("execution_artifact_directory")
            or analysis.get("execution_artifact_directory")
        )
        existing_analysis_artifacts = analysis.get("execution_artifacts")
        analysis["execution_artifacts"] = {
            **(existing_analysis_artifacts if isinstance(existing_analysis_artifacts, dict) else {}),
            **(artifact_values if isinstance(artifact_values, dict) else {}),
        }
        state["analysis_result"] = analysis
        if persist_state is not None:
            await persist_state({"analysis_result": analysis})

    await invoke_if_missing(
        "report",
        report_agent,
        "Generate the final PDF report for the current job from its "
        "analysis_result. Include only current-job evidence, run the "
        "report tool sequence, and return the structured report result.",
        "report_result",
    )

    state[pipeline_state_key] = pipeline
    return pipeline

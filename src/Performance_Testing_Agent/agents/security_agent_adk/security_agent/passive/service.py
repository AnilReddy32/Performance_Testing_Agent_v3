"""Runs the passive assessment and shapes its result.

run_passive_checks never raises and never sends a request outside the rules in
target.py and network.py. assess_external_surface builds the complete
SecurityResponse for the automatic, model-free path used by the pipeline.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections.abc import Callable, Mapping
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from security_agent.passive.checks import evaluate, summarize
from security_agent.passive.config import (
    AUTO_OBJECTIVE,
    FOREIGN_ORIGIN,
    TOTAL_TIMEOUT_SECONDS,
    auto_assessment_enabled,
    passive_assessment_enabled,
)
from security_agent.passive.models import Observations
from security_agent.passive.network import BudgetExceeded, PassiveNetwork, RequestBudget
from security_agent.passive.target import (
    PassiveTarget,
    TargetRejected,
    default_resolver,
    looks_like_external_https_target,
    resolve_target,
)
from security_agent.passive.traffic import read_run_traffic

logger = logging.getLogger(__name__)

NETWORK_FACTORY = Callable[[PassiveTarget, RequestBudget], Any]


def _default_network(target: PassiveTarget, budget: RequestBudget) -> PassiveNetwork:
    return PassiveNetwork(target.host, target.addresses, budget=budget)


def _not_found_target(path: str) -> str:
    base = path.split("?", 1)[0].rstrip("/")
    return f"{base}/security-assessment-not-found"


def collect_observations(
    target: PassiveTarget, network: Any, observations: Observations
) -> None:
    """Fill ``observations`` in order; stops quietly if the budget is spent."""
    try:
        observations.tls = network.tls_probe()
        if observations.tls.ok:
            if target.method in {"GET", "HEAD"}:
                primary = network.request(
                    label="primary", method="HEAD", target=target.request_target
                )
                if primary.status in {405, 501}:  # HEAD unsupported: ask with GET
                    primary = network.request(
                        label="primary", method="GET", target=target.request_target
                    )
                observations.primary = primary
            observations.options = network.request(
                label="options",
                method="OPTIONS",
                target=target.request_target,
                headers={
                    "Origin": FOREIGN_ORIGIN,
                    "Access-Control-Request-Method": target.method,
                },
            )
            observations.not_found = network.request(
                label="not_found",
                method="GET",
                target=_not_found_target(target.path),
                read_body=True,
            )
        else:
            observations.skipped_reason = (
                "HTTPS requests were not sent because the TLS handshake did not succeed."
            )
        # Plain HTTP is unencrypted, so only the path goes out: a query string can
        # carry an API key or token that must never cross the network in clear.
        observations.http_redirect = network.request(
            label="http_redirect", method="HEAD", target=target.path, tls=False
        )
    except BudgetExceeded:
        logger.warning("Passive assessment stopped at its request budget.")


def _collect_safely(target: PassiveTarget, network: Any, observations: Observations) -> None:
    try:
        collect_observations(target, network, observations)
    except Exception:  # a probe fault must leave the other checks judgeable
        logger.exception("Passive probing failed unexpectedly")
        if observations.skipped_reason is None:
            observations.skipped_reason = "Probing stopped early because of an internal error."


def _result_shell(state: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "job_id": state.get("job_id") if isinstance(state.get("job_id"), str) else None,
        "test_case_id": state.get("test_case_id"),
        "requests_sent": 0,
        "check_results": [],
        "check_summary": {},
        "assessment_outcome": "not_assessed",
        "authorized": False,
        "limitations": [],
    }


def _blocked(state: Mapping[str, Any], code: str, reason: str, status: str = "blocked") -> dict:
    result = _result_shell(state)
    result.update(status=status, reason_code=code, reason=reason)
    return result


async def run_passive_checks(
    state: Mapping[str, Any],
    *,
    network_factory: NETWORK_FACTORY = _default_network,
    resolver: Callable[[str, int], list[str]] = default_resolver,
) -> dict[str, Any]:
    """Assess the job's external surface. Always returns a result dict."""
    if not passive_assessment_enabled():
        return _blocked(
            state, "passive_assessment_disabled",
            "Passive security assessment is switched off by deployment configuration.",
            status="disabled",
        )
    if not isinstance(state.get("job_id"), str) or not state.get("job_id"):
        return _blocked(state, "no_job", "Passive assessment requires a current job identity.")
    if state.get("execution_status") not in {"completed", "failed"}:
        return _blocked(
            state, "run_not_finished",
            "Passive checks run only after the performance execution has ended, so "
            "they cannot overlap or warm up its measurements.",
        )

    profile = state.get("workload_profile")
    try:
        target = await asyncio.to_thread(
            resolve_target, profile, resolver=resolver
        )
    except TargetRejected as exc:
        return _blocked(state, exc.code, exc.reason)
    except Exception as exc:  # defensive: scope validation must never crash a run
        logger.exception("Passive target validation failed unexpectedly")
        return _blocked(state, "invalid_target", f"The target could not be validated: {type(exc).__name__}.")

    budget = RequestBudget()
    network = network_factory(target, budget)
    gathered = Observations(declared_method=target.method)
    started = datetime.now(timezone.utc)
    deadline_hit = False
    probing = asyncio.create_task(
        asyncio.to_thread(_collect_safely, target, network, gathered)
    )
    try:
        await asyncio.wait_for(asyncio.shield(probing), timeout=TOTAL_TIMEOUT_SECONDS)
    except (TimeoutError, asyncio.TimeoutError):
        deadline_hit = True
        logger.warning("Passive assessment hit its overall deadline; using partial results.")
        # The probing thread cannot be cancelled, so tell the network to break any
        # exchange in flight and send nothing further.
        cancel = getattr(network, "cancel", None)
        if callable(cancel):
            cancel()
    # A probe that outlives the deadline keeps running in its thread, so judge
    # a snapshot that can no longer change underneath the checks.
    observations = replace(gathered)
    try:
        observations.traffic = await asyncio.to_thread(read_run_traffic, state)
    except Exception:
        logger.exception("Reading the run's traffic evidence failed")
        observations.traffic = None
    if deadline_hit and observations.skipped_reason is None:
        observations.skipped_reason = (
            "The assessment deadline passed before this probe finished."
        )

    checks = evaluate(observations)
    summary = summarize(checks)
    primary = observations.primary or observations.options
    result = _result_shell(state)
    limitations = [
        "Passive checks observe what the server returns to a few ordinary requests; they "
        "send no attack payloads and do not prove that internal controls work.",
        "Results describe the externally visible edge, which may be a CDN or WAF in front "
        "of the application.",
        "TLS findings describe the connection made from the machine running this "
        "assessment; a TLS-inspecting proxy on its network path would present its own "
        "certificate (compare the certificate issuer in the evidence).",
    ]
    inconclusive = [c for c in checks if c.verdict == "inconclusive"]
    if inconclusive:
        limitations.append(
            "Inconclusive (not counted as passed or failed): "
            + "; ".join(f"{c.title} - {c.summary}" for c in inconclusive)
        )
    result.update(
        status="completed",
        authorized=True,
        target_origin=target.origin,
        endpoint=target.request_target,
        method=target.method,
        environment=target.environment,
        environment_inferred=target.environment_inferred,
        requests_sent=budget.used,
        tls_connections=1,
        response_status_code=primary.status if primary and primary.received else None,
        elapsed_ms=round(primary.elapsed_ms, 1) if primary and primary.elapsed_ms else None,
        check_results=[c.as_dict() for c in checks],
        check_summary={
            key: summary[key]
            for key in ("total", "assessed", "passed", "failed", "inconclusive")
        },
        assessment_outcome=summary["outcome"],
        status_rollup=summary["status"],
        security_score=summary["security_score"],
        security_score_basis=summary["security_score_basis"],
        limitations=limitations,
        started_at=started.isoformat(),
        finished_at=datetime.now(timezone.utc).isoformat(),
        assessment_id=uuid.uuid4().hex[:12],
    )
    return result


async def assess_external_surface(
    state: Mapping[str, Any],
    *,
    network_factory: NETWORK_FACTORY = _default_network,
    resolver: Callable[[str, int], list[str]] = default_resolver,
) -> dict[str, Any] | None:
    """Model-free automatic assessment; None means "not applicable here".

    Used by the pipeline for every REAL run. It returns None, without sending
    anything, when automatic assessment is off or the target is not an external
    HTTPS API. Otherwise it returns a complete SecurityResponse as a dict.
    """
    # Imported here so this module has no import cycle with the request model,
    # which itself imports the passive configuration.
    from security_agent.models.assessment import AssessmentState
    from security_agent.models.request import build_security_assessment_request
    from security_agent.security.assessment import build_security_response
    from security_agent.security.evaluation import evaluate_configured_controls
    from security_agent.security.profiles import select_profile

    if not (auto_assessment_enabled() and passive_assessment_enabled()):
        return None
    if not looks_like_external_https_target(state.get("workload_profile")):
        return None
    snapshot = dict(state)
    request = build_security_assessment_request(AUTO_OBJECTIVE, snapshot, auto_passive=True)
    try:
        selection = select_profile(snapshot)
    except (OSError, ValueError) as exc:
        selection = {"status": "no_match", "reason": f"The profile registry could not be used: {exc}"}
    evaluation = evaluate_configured_controls(request, selection)
    passive = await run_passive_checks(snapshot, network_factory=network_factory, resolver=resolver)
    response = build_security_response(
        AssessmentState(objective=AUTO_OBJECTIVE, request_context=request),
        evaluation=evaluation,
        passive_result=passive,
    )
    return response.model_dump(mode="json")

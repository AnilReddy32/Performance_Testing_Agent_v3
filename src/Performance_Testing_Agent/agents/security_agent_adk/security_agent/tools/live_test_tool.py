"""Bounded one-request observation of an explicitly scoped API surface."""

import asyncio
from typing import Any
from urllib.parse import urlsplit

from google.adk.tools import ToolContext

from security_agent.config import settings
from security_agent.models.request import is_explicit_live_security_request
from security_agent.passive.target import looks_like_external_https_target
from security_agent.live_testing.executor import HTTPExecutor
from security_agent.live_testing.models import (
    HTTPRequest,
    LiveTestPolicy,
    LiveTestScope,
    LiveTestTarget,
)
from security_agent.live_testing.safety import validate_test_safety
from security_agent.live_testing.scope import (
    build_target_url,
    validate_request_matches_target,
    validate_test_scope,
)
from security_agent.tools.state_utils import snapshot_session_state


_OBSERVED_HEADERS = {
    "strict-transport-security",
    "content-security-policy",
    "x-content-type-options",
    "x-frame-options",
    "referrer-policy",
    "permissions-policy",
    "access-control-allow-origin",
    "cache-control",
    "allow",
}


def _blocked(reason: str, *, job_id: str | None = None) -> dict[str, Any]:
    return {
        "status": "blocked",
        "authorized": False,
        "job_id": job_id,
        "requests_sent": 0,
        "reason": reason,
    }


async def execute_authorized_live_test(
    objective: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Run one bounded HEAD observation using trusted job and deployment scope.

    All target, authorization, path, port, policy, and request values are
    sourced or constrained here. The model cannot supply a URL, HTTP method,
    headers, body, allowlist, or request count.
    """
    state = snapshot_session_state(tool_context.state)
    job_id = state.get("job_id") if isinstance(state.get("job_id"), str) else None
    user_prompt = state.get("test_case_prompt")
    authorization_text = user_prompt if isinstance(user_prompt, str) else objective
    if not is_explicit_live_security_request(authorization_text):
        return {"status": "not_requested", "authorized": False, "job_id": job_id, "requests_sent": 0}

    if not settings.SECURITY_LIVE_TESTS_ENABLED:
        result = _blocked(
            "Live security checks are disabled by trusted deployment configuration.",
            job_id=job_id,
        )
        tool_context.state["security_live_test_result"] = result
        return result

    if not job_id:
        result = _blocked(
            "Live security checks require a current job identity.",
            job_id=job_id,
        )
        tool_context.state["security_live_test_result"] = result
        return result

    profile = state.get("workload_profile")
    profile = profile if isinstance(profile, dict) else {}
    # A missing environment on a public HTTPS target is inferred as
    # external_api instead of blocking the observation.
    profile_environment = profile.get("environment") or (
        "external_api" if looks_like_external_https_target(profile) else None
    )
    target_url = profile.get("target_url")
    endpoint = profile.get("endpoint")
    if not isinstance(target_url, str) or not isinstance(endpoint, str):
        result = _blocked(
            "The trusted workload profile does not provide a target origin and endpoint.",
            job_id=job_id,
        )
        tool_context.state["security_live_test_result"] = result
        return result

    scope_environment = settings.SECURITY_LIVE_ENVIRONMENT or profile_environment
    if not isinstance(scope_environment, str) or not scope_environment.strip():
        result = _blocked("The live-test environment is not configured.", job_id=job_id)
        tool_context.state["security_live_test_result"] = result
        return result

    try:
        origin = urlsplit(target_url)
        if (
            origin.scheme.lower() not in {"http", "https"}
            or not origin.hostname
            or origin.path not in {"", "/"}
            or origin.query
            or origin.fragment
            or origin.username
            or origin.password
        ):
            raise ValueError("trusted target_url must be a clean origin")
        base_url = f"{origin.scheme}://{origin.netloc}"
        endpoint_url = urlsplit(endpoint)
        if (
            endpoint_url.scheme
            or endpoint_url.netloc
            or endpoint_url.fragment
            or not endpoint_url.path.startswith("/")
        ):
            raise ValueError("trusted endpoint must be an absolute path with no URL authority or fragment")
        effective_port = origin.port or (443 if origin.scheme.lower() == "https" else 80)
        if (
            not settings.SECURITY_LIVE_ALLOWED_HOSTS
            and profile_environment != "external_api"
        ):
            raise ValueError(
                "targets outside the external_api environment require an explicit deployment host allowlist"
            )
        if (
            profile_environment == "external_api"
            and origin.scheme.lower() != "https"
        ):
            raise ValueError("external API surface checks require HTTPS")
        # The job's trusted workload profile is the per-run exact target/path
        # allowlist. Optional deployment lists narrow that scope further.
        allowed_hosts = list(settings.SECURITY_LIVE_ALLOWED_HOSTS) or [origin.hostname]
        allowed_paths = list(settings.SECURITY_LIVE_ALLOWED_PATHS) or [endpoint_url.path]
        allowed_ports = list(settings.SECURITY_LIVE_ALLOWED_PORTS) or [effective_port]
        target = LiveTestTarget(
            base_url=base_url,
            # Keep the query from the trusted workload profile. Scope
            # validation pins the request to this exact path and query.
            endpoint=endpoint,
            method="HEAD",
            environment=profile_environment,
        )
    except (TypeError, ValueError) as exc:
        result = _blocked(f"The trusted target is invalid: {exc}", job_id=job_id)
        tool_context.state["security_live_test_result"] = result
        return result

    scope = LiveTestScope(
        authorized=True,
        allowed_hosts=allowed_hosts,
        allowed_paths=allowed_paths,
        allowed_ports=allowed_ports,
        environment=scope_environment,
    )

    scope_result = validate_test_scope(target, scope)
    if not scope_result["allowed"]:
        result = _blocked(scope_result["reason"], job_id=job_id)
        tool_context.state["security_live_test_result"] = result
        return result

    if state.get("execution_status") not in {"completed", "failed"}:
        result = _blocked(
            "Live checks run only after the performance execution has ended, so they cannot overlap or warm up its measurements.",
            job_id=job_id,
        )
        tool_context.state["security_live_test_result"] = result
        return result

    policy = LiveTestPolicy()
    safety_result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
        destructive_test=False,
    )
    if not safety_result["allowed"]:
        result = _blocked(safety_result["reason"], job_id=job_id)
        tool_context.state["security_live_test_result"] = result
        return result

    request = HTTPRequest(method="HEAD", url=build_target_url(target))
    target_result = validate_request_matches_target(target, request.url)
    if not target_result["allowed"]:
        result = _blocked(target_result["reason"], job_id=job_id)
        tool_context.state["security_live_test_result"] = result
        return result

    # A HEAD request observes only response metadata. No load-test runner is
    # started, and the response body is not requested or persisted.
    try:
        execution = await asyncio.wait_for(
            HTTPExecutor(policy=policy).execute(request),
            timeout=policy.timeout_seconds + 1,
        )
    except TimeoutError:
        result = {
            "status": "failed",
            "authorized": True,
            "job_id": job_id,
            "test_case_id": state.get("test_case_id"),
            "target_origin": f"{origin.scheme.lower()}://{origin.netloc.lower()}",
            "endpoint": endpoint,
            "method": "HEAD",
            "environment": profile_environment,
            "requests_sent": 1,
            "error": "The live security request exceeded its hard overall timeout.",
        }
        tool_context.state["security_live_test_result"] = result
        return result
    response = execution.response
    target_origin = f"{origin.scheme.lower()}://{origin.netloc.lower()}"
    result = {
        "status": "completed" if execution.success else "failed",
        "authorized": True,
        "job_id": job_id,
        "test_case_id": state.get("test_case_id"),
        "target_origin": target_origin,
        "endpoint": endpoint,
        "method": "HEAD",
        "environment": profile_environment,
        "requests_sent": 1,
        "response_status_code": response.status_code if response else None,
        "elapsed_ms": response.elapsed_ms if response else None,
        "observed_security_headers": (
            {
                key.lower(): value
                for key, value in response.headers.items()
                if key.lower() in _OBSERVED_HEADERS
            }
            if response
            else {}
        ),
        "error": execution.error,
        "scope": scope_result,
        "safety": safety_result,
        "limitations": [
            "One non-state-changing HEAD request was made; this observation does not test application behavior or prove runtime control effectiveness."
        ],
    }
    tool_context.state["security_live_test_result"] = result
    return result

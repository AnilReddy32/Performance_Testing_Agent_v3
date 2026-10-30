"""Passive results as the SecurityResponse contract, and how the tools reach them."""

import time
from types import SimpleNamespace

import pytest

from security_agent.models.assessment import AssessmentState
from security_agent.models.request import build_security_assessment_request
from security_agent.models.response import SecurityResponse
from security_agent.passive import assess_external_surface, run_passive_checks
from security_agent.passive.models import HttpObservation, TlsObservation
from security_agent.tools import assessment_tool

pytestmark = pytest.mark.asyncio

JOB = "JOB-" + "b" * 32
PUBLIC = ["93.184.216.34"]
HARDENED = {
    "strict-transport-security": "max-age=31536000", "x-content-type-options": "nosniff",
    "x-frame-options": "DENY", "content-security-policy": "default-src 'none'",
    "referrer-policy": "no-referrer", "permissions-policy": "geolocation=()",
    "cache-control": "no-store", "server": "srv",
}


def resolver(host, port):
    return list(PUBLIC)


def reply(label, status=200, headers=None, *, method="HEAD", body=""):
    return HttpObservation(
        label=label, method=method, target="/posts/1", scheme="http" if label == "http_redirect" else "https",
        status=status, headers=tuple((k, v) for k, v in (headers or {}).items()), body=body, elapsed_ms=4.0,
    )


class FakeNetwork:
    """Serves scripted observations and still counts against the real budget."""

    def __init__(self, budget, script, tls=None):
        self.budget, self.script = budget, script
        self.tls = tls or TlsObservation(
            ok=True, version="TLSv1.3", cipher_name="TLS_AES_256_GCM_SHA384", cipher_bits=256,
            subject="api.example.com", issuer="Example CA", san_count=1, not_after=time.time() + 90 * 86400,
        )

    def tls_probe(self):
        return self.tls

    def request(self, *, label, method, target, headers=None, tls=True, read_body=False):
        self.budget.consume()
        return self.script[label]


HARDENED_SCRIPT = {
    "primary": reply("primary", 200, HARDENED),
    "options": reply("options", 204, {"allow": "GET, HEAD, OPTIONS"}, method="OPTIONS"),
    "not_found": reply("not_found", 404, {}, method="GET", body='{"error":"not found"}'),
    "http_redirect": reply("http_redirect", 301, {"location": "https://api.example.com/posts/1"}),
}
WEAK_SCRIPT = {
    **HARDENED_SCRIPT,
    "primary": reply("primary", 200, {"server": "Apache/2.4.41"}),
    "options": reply("options", 200, {
        "allow": "GET, TRACE", "access-control-allow-origin": "https://security-assessment.invalid",
        "access-control-allow-credentials": "true",
    }, method="OPTIONS"),
}


def make_factory(script, tls=None):
    return lambda target, budget: FakeNetwork(budget, script, tls)


def state(**profile_overrides):
    profile = {
        "tool": "k6", "target_url": "https://api.example.com", "endpoint": "/posts/1",
        "method": "GET", "environment": "external_api", "application": "Posts API",
    }
    profile.update(profile_overrides)
    return {
        "job_id": JOB, "test_case_id": "PTC-004", "test_case_name": "Posts check",
        "execution_mode": "REAL", "execution_status": "completed", "workload_profile": profile,
    }


# ------------------------------------------------- the automatic assessment --

@pytest.mark.parametrize("profile", [
    {"environment": "mock_api", "target_url": "http://localhost:8000"},
    {"target_url": "http://api.example.com"},
    {"target_url": "https://127.0.0.1"},
    {"target_url": None},
])
async def test_the_automatic_assessment_does_not_apply_to_local_or_non_https_targets(profile):
    built = []
    result = await assess_external_surface(
        state(**profile), network_factory=lambda t, b: built.append(1), resolver=resolver
    )

    assert result is None and built == []


@pytest.mark.parametrize("variable", ["SECURITY_AUTO_ASSESSMENT_ENABLED", "SECURITY_PASSIVE_ASSESSMENT_ENABLED"])
async def test_either_switch_turns_the_automatic_assessment_off(monkeypatch, variable):
    monkeypatch.setenv(variable, "false")
    built = []

    result = await assess_external_surface(
        state(), network_factory=lambda t, b: built.append(1), resolver=resolver
    )

    assert result is None and built == []


async def test_the_automatic_assessment_returns_a_complete_valid_response():
    result = await assess_external_surface(state(), network_factory=make_factory(HARDENED_SCRIPT), resolver=resolver)

    response = SecurityResponse.model_validate(result)
    assert response.job_id == JOB and response.test_case_id == "PTC-004"
    assert response.status.value == "PASS" and response.security_score == "100%"
    assert response.execution_mode == "REAL" and response.environment == "external_api"
    assert response.requested_controls == ["external_surface"]
    assert response.requested_controls_source == "overall_security_default"
    assert response.assessment_mode == "configuration_and_live"
    assert response.live_testing_requested and response.live_testing_authorized
    assert response.live_testing_status == "completed"
    assert response.assessment_outcome == "partially_assessed"       # rate limiting had no evidence
    assert response.check_summary == {"total": 15, "assessed": 14, "passed": 14, "failed": 0, "inconclusive": 1}
    assert len(response.check_results) == 15
    assert response.profile_match_status == "no_match"                # no invented configuration claims
    control = response.control_results[0]
    assert control.control == "external_surface" and control.assessment_status == "assessed"
    assert control.assessment_basis == "live_observation"
    assert response.coverage == {"requested_count": 1, "assessed_count": 1, "not_assessed_count": 0}
    assert response.assessed_controls == ["external_surface"] and response.not_assessed_controls == []
    assert response.live_test_result["requests_sent"] == 4
    assert response.live_test_result["authorized"] is True
    assert any("no attack payloads" in item for item in response.issues)
    assert not any("single-request" in item for item in response.issues)
    # The caveats and the reason for every inconclusive check reach the report.
    assert any("CDN or WAF" in item for item in response.limitations)
    assert any("TLS-inspecting proxy" in item for item in response.limitations)
    assert any(item.startswith("Inconclusive (not counted as passed or failed):")
               and "Rate-limiting evidence" in item for item in response.limitations)


async def test_failed_checks_become_issues_and_recommendations_and_drive_the_status():
    result = await assess_external_surface(state(), network_factory=make_factory(WEAK_SCRIPT), resolver=resolver)

    response = SecurityResponse.model_validate(result)
    assert response.status.value == "FAIL"                      # reflected origin + credentials is high severity
    assert any("[high] CORS policy for a foreign origin" in issue for issue in response.issues)
    assert any("TRACE" in issue for issue in response.issues)
    assert any("Apache/2.4.41" in issue for issue in response.issues)
    assert response.recommendations
    failed = [c for c in response.check_results if c["verdict"] == "failed"]
    assert failed and all(c["recommendation"] for c in failed)
    assert response.control_results[0].severity == "high"
    assert int(response.security_score.rstrip("%")) < 100


async def test_a_blocked_target_is_not_assessed_and_its_reason_is_not_repeated_endlessly():
    result = await assess_external_surface(
        state(), network_factory=make_factory(HARDENED_SCRIPT),
        resolver=lambda h, p: ["10.0.0.5"],
    )

    response = SecurityResponse.model_validate(result)
    reason = "resolves to a non-public address"
    assert response.status.value == "WARNING" and response.security_score == "N/A"
    assert response.assessment_outcome == "not_assessed" and response.check_results == []
    assert response.live_testing_status == "blocked" and response.live_testing_authorized is False
    assert response.control_results[0].assessment_status == "not_assessed"
    assert response.live_test_result["reason_code"] == "non_public_address"
    assert response.not_assessed_controls == ["external_surface"]
    assert sum(reason in line for line in response.issues) <= 2
    assert sum(reason in line for line in response.limitations) == 1


async def test_all_inconclusive_checks_mean_not_assessed_not_a_pass():
    script = {k: reply(k, 403, {"server": "cloudflare"}) for k in HARDENED_SCRIPT}
    tls = TlsObservation(ok=False, error_kind="timeout", error="timed out")
    result = await assess_external_surface(state(), network_factory=make_factory(script, tls), resolver=resolver)

    response = SecurityResponse.model_validate(result)
    assert response.status.value == "WARNING" and response.security_score == "N/A"
    assert response.assessment_outcome == "not_assessed"
    assert response.control_results[0].assessment_status == "not_assessed"
    assert response.check_summary["assessed"] == 0
    assert "Every passive check was inconclusive" in response.control_results[0].missing_evidence[0]


async def test_a_matching_profile_does_not_widen_the_automatic_assessment():
    demo = {
        "application": "Demo Banking API", "environment": "development",
        "target_url": "https://example.internal", "endpoint": "/users", "method": "GET",
    }
    request = build_security_assessment_request(
        "Automatic assessment", state(**demo), auto_passive=True
    )

    assert request.profile_match_status == "matched"
    assert request.requested_controls == ["external_surface"]
    assert request.passive_assessment_requested is True


# ------------------------------------------------------- the request builder --

@pytest.mark.parametrize("objective,passive", [
    ("Perform the security assessment of this API", True),
    ("Run an active security check after the test", True),
    ("Check authentication", False),
    ("Run a configuration-only security assessment", False),
    ("security assessment without live checks", False),
    ("do not send any probes, security review", False),
])
async def test_an_explicit_request_gets_the_passive_assessment_unless_it_opts_out(objective, passive):
    request = build_security_assessment_request(objective, state())

    assert request.passive_assessment_requested is passive
    assert request.live_testing_requested is passive
    if passive:
        assert "external_surface" in request.requested_controls


async def test_explicit_requests_keep_their_configuration_controls():
    request = build_security_assessment_request("Check authentication and perform a live security check", state())

    assert "authentication" in request.requested_controls and "external_surface" in request.requested_controls
    assert request.passive_assessment_requested is True


async def test_with_passive_off_an_explicit_request_falls_back_to_the_older_observation(monkeypatch):
    monkeypatch.setenv("SECURITY_PASSIVE_ASSESSMENT_ENABLED", "false")
    request = build_security_assessment_request("Run an active security check", state())

    assert request.passive_assessment_requested is False
    assert request.live_testing_requested is True


# ----------------------------------------------------------- the tool path --

def tool_context(**profile_overrides):
    return SimpleNamespace(state=state(**profile_overrides))


async def test_finalization_runs_the_passive_assessment_once_and_not_the_older_probe(monkeypatch):
    calls = {"passive": 0, "old": 0}

    async def fake_passive(session_state):
        calls["passive"] += 1
        return await run_passive_checks(
            session_state, network_factory=make_factory(HARDENED_SCRIPT), resolver=resolver
        )

    async def old_probe(objective, ctx):
        calls["old"] += 1

    monkeypatch.setattr(assessment_tool, "run_passive_checks", fake_passive)
    monkeypatch.setattr(assessment_tool, "execute_authorized_live_test", old_probe)
    ctx = tool_context()
    objective = "Perform a live security assessment"
    request = build_security_assessment_request(objective, ctx.state)
    assessment = AssessmentState(objective=objective, request_context=request).model_dump()

    first = await assessment_tool.finalize_assessment_with_live_observation(assessment, ctx)
    second = await assessment_tool.finalize_assessment_with_live_observation(assessment, ctx)

    assert calls == {"passive": 1, "old": 0}          # idempotent, and no extra HEAD request
    assert first["check_results"] == second["check_results"] and len(first["check_results"]) == 15
    assert first["status"] == "PASS" and first["live_testing_status"] == "completed"
    assert ctx.state["security_passive_result"]["job_id"] == JOB


async def test_finalization_ignores_a_passive_result_that_belongs_to_another_job(monkeypatch):
    async def fake_passive(session_state):
        return await run_passive_checks(
            session_state, network_factory=make_factory(HARDENED_SCRIPT), resolver=resolver
        )

    monkeypatch.setattr(assessment_tool, "run_passive_checks", fake_passive)
    ctx = tool_context()
    ctx.state["security_passive_result"] = {"job_id": "JOB-someone-else", "status": "completed",
                                            "check_results": [{"check_id": "x", "verdict": "passed"}]}
    objective = "Perform a live security assessment"
    assessment = AssessmentState(
        objective=objective, request_context=build_security_assessment_request(objective, ctx.state)
    ).model_dump()

    result = await assessment_tool.finalize_assessment_with_live_observation(assessment, ctx)

    assert ctx.state["security_passive_result"]["job_id"] == JOB
    assert all(c["check_id"] != "x" for c in result["check_results"])


async def test_finalization_without_passive_uses_the_older_observation(monkeypatch):
    monkeypatch.setenv("SECURITY_PASSIVE_ASSESSMENT_ENABLED", "false")
    calls = []

    async def old_probe(objective, ctx):
        calls.append(objective)

    async def no_passive(session_state):
        raise AssertionError("passive must not run when switched off")

    monkeypatch.setattr(assessment_tool, "run_passive_checks", no_passive)
    monkeypatch.setattr(assessment_tool, "execute_authorized_live_test", old_probe)
    ctx = tool_context()
    objective = "Perform a live security assessment"
    assessment = AssessmentState(
        objective=objective, request_context=build_security_assessment_request(objective, ctx.state)
    ).model_dump()

    result = await assessment_tool.finalize_assessment_with_live_observation(assessment, ctx)

    assert calls == [objective] and result["check_results"] == [] and result["assessment_outcome"] is None


async def test_a_configuration_only_request_sends_nothing(monkeypatch):
    async def forbidden(*args, **kwargs):
        raise AssertionError("no live request may be made for a configuration-only request")

    monkeypatch.setattr(assessment_tool, "run_passive_checks", forbidden)
    monkeypatch.setattr(assessment_tool, "execute_authorized_live_test", forbidden)
    ctx = tool_context()
    objective = "Run a configuration-only security assessment"
    assessment = AssessmentState(
        objective=objective, request_context=build_security_assessment_request(objective, ctx.state)
    ).model_dump()

    result = await assessment_tool.finalize_assessment_with_live_observation(assessment, ctx)

    assert result["assessment_mode"] == "configuration_only" and result["check_results"] == []


async def test_a_new_context_request_clears_earlier_passive_state():
    ctx = tool_context()
    ctx.state["security_passive_result"] = {"job_id": JOB}
    ctx.state["security_live_test_result"] = {"job_id": JOB}

    assessment_tool.get_security_assessment_context("Perform a live security assessment", ctx)

    assert ctx.state["security_passive_result"] is None
    assert ctx.state["security_live_test_result"] is None

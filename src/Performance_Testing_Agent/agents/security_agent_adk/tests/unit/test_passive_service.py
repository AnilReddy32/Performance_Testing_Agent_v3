"""The whole passive assessment against real local servers."""

import json
import time

import pytest

pytest.importorskip("cryptography")

from passive_support import (  # noqa: E402
    HOSTNAME,
    LocalServer,
    client_context,
    hardened_router,
    head_unsupported_router,
    make_certificate,
    redirect_to_https,
    vanilla_ssl,
    waf_router,
    weak_router,
)
from security_agent.passive import service  # noqa: E402
from security_agent.passive.network import PassiveNetwork  # noqa: E402

pytestmark = [pytest.mark.usefixtures("vanilla_ssl"), pytest.mark.asyncio]

PUBLIC = ["93.184.216.34"]
JOB = "JOB-" + "a" * 32


@pytest.fixture(scope="module")
def certificate():
    return make_certificate()


def state(**profile_overrides):
    profile = {
        "tool": "k6", "target_url": f"https://{HOSTNAME}", "endpoint": "/posts/1",
        "method": "GET", "environment": "external_api",
    }
    profile.update(profile_overrides)
    return {
        "job_id": JOB, "test_case_id": "PTC-004", "execution_mode": "REAL",
        "execution_status": "completed", "workload_profile": profile,
    }


def resolver(host, port):
    return list(PUBLIC)


def factory(https_server, http_server, certificate, *, trusted=True, timeout=3.0):
    def make(target, budget):
        return PassiveNetwork(
            target.host, ["127.0.0.1"], budget=budget,
            https_port=https_server.port,
            http_port=http_server.port if http_server else 1,
            ssl_context=client_context(certificate[0]) if trusted else None,
            timeout=timeout,
        )
    return make


async def assess(router, certificate, *, http_router=redirect_to_https, st=None, trusted=True):
    with LocalServer(router, tls_material=certificate) as https_server:
        with LocalServer(http_router) as http_server:
            result = await service.run_passive_checks(
                st or state(), network_factory=factory(https_server, http_server, certificate, trusted=trusted),
                resolver=resolver,
            )
            return result, https_server.requests, http_server.requests


def verdicts(result):
    return {c["check_id"]: c["verdict"] for c in result["check_results"]}


async def test_a_hardened_api_passes_every_check_it_can_be_judged_on(certificate):
    result, https_seen, http_seen = await assess(hardened_router, certificate)

    assert result["status"] == "completed" and result["authorized"] is True
    assert result["status_rollup"] == "PASS" and result["security_score"] == "100%"
    got = verdicts(result)
    assert {v for k, v in got.items() if k != "rate_limit_evidence"} == {"passed"}
    assert got["rate_limit_evidence"] == "inconclusive"   # nothing to judge from
    assert result["assessment_outcome"] == "partially_assessed"
    assert result["check_summary"] == {"total": 15, "assessed": 14, "passed": 14, "failed": 0, "inconclusive": 1}
    # Exactly the requests described, and only these.
    assert [(r["method"], r["path"]) for r in https_seen] == [
        ("HEAD", "/posts/1"),
        ("OPTIONS", "/posts/1"),
        ("GET", "/posts/1/security-assessment-not-found"),
    ]
    assert [(r["method"], r["path"]) for r in http_seen] == [("HEAD", "/posts/1")]
    assert result["requests_sent"] == 4


async def test_the_cors_preflight_carries_only_the_reserved_foreign_origin(certificate):
    _, https_seen, _ = await assess(hardened_router, certificate)

    preflight = next(r for r in https_seen if r["method"] == "OPTIONS")
    assert preflight["headers"]["Origin"] == "https://security-assessment.invalid"
    assert preflight["headers"]["Access-Control-Request-Method"] == "GET"
    for request in https_seen:
        assert set(request["headers"]) <= {
            "Host", "User-Agent", "Accept", "Accept-Encoding", "Origin", "Access-Control-Request-Method",
        }


async def test_a_sloppy_api_fails_with_evidence_and_a_blocking_status(certificate):
    result, _, _ = await assess(weak_router, certificate, http_router=lambda m, p, h: (200, {}, "{}"))

    got = verdicts(result)
    assert result["status_rollup"] == "FAIL"           # reflected origin with credentials
    assert got["cors_foreign_origin"] == "failed"
    assert got["http_methods_exposed"] == "failed"
    assert got["error_leakage"] == "failed"
    assert got["https_redirect"] == "failed"
    assert got["header_hsts"] == "failed"
    assert got["header_information_disclosure"] == "failed"
    cors = next(c for c in result["check_results"] if c["check_id"] == "cors_foreign_origin")
    assert cors["severity"] == "high" and cors["recommendation"]
    assert cors["evidence"]["access_control_allow_origin"] == "https://security-assessment.invalid"
    assert int(result["security_score"].rstrip("%")) < 50


async def test_a_gateway_that_answers_403_to_everything_yields_no_http_verdicts(certificate):
    result, _, _ = await assess(waf_router, certificate, http_router=waf_router)

    got = verdicts(result)
    assert got["tls_protocol"] == "passed" and got["tls_certificate"] == "passed"
    http_checks = {k: v for k, v in got.items() if k not in {"tls_protocol", "tls_certificate"}}
    assert set(http_checks.values()) == {"inconclusive"}, http_checks      # never a pass, never a failure
    assert result["check_summary"]["assessed"] == 2
    assert result["assessment_outcome"] == "partially_assessed"
    assert all("HTTP 403" in c["summary"] for c in result["check_results"] if c["check_id"] == "header_hsts")


async def test_head_not_supported_falls_back_to_get_within_the_budget(certificate):
    result, https_seen, _ = await assess(head_unsupported_router, certificate)

    assert [r["method"] for r in https_seen] == ["HEAD", "GET", "OPTIONS", "GET"]
    assert result["requests_sent"] == 5
    assert verdicts(result)["header_hsts"] == "passed"


async def test_an_unsafe_declared_method_is_never_sent_and_uses_options_instead(certificate):
    result, https_seen, _ = await assess(hardened_router, certificate, st=state(method="PUT"))

    assert {r["method"] for r in https_seen} == {"OPTIONS", "GET"}     # no PUT, no HEAD of the resource
    assert next(r for r in https_seen if r["method"] == "OPTIONS")["headers"]["Access-Control-Request-Method"] == "PUT"
    assert result["requests_sent"] == 3
    assert verdicts(result)["header_hsts"] == "passed"                  # present on the OPTIONS reply


async def test_missing_headers_on_an_options_only_observation_are_not_failures(certificate):
    def bare_options(method, path, headers):
        if method == "OPTIONS":
            return 204, {"Allow": "GET, PUT, OPTIONS"}, ""
        return hardened_router(method, path, headers)

    result, _, _ = await assess(bare_options, certificate, st=state(method="POST"))

    got = verdicts(result)
    assert got["header_hsts"] == "inconclusive" and got["header_csp"] == "inconclusive"
    assert got["http_methods_exposed"] == "passed"


async def test_a_bad_certificate_stops_https_probing_after_the_handshake(certificate):
    result, https_seen, http_seen = await assess(hardened_router, certificate, trusted=False)

    got = verdicts(result)
    assert got["tls_certificate"] == "failed" and got["tls_protocol"] == "inconclusive"
    assert https_seen == []                                  # nothing was sent over HTTPS
    assert [r["method"] for r in http_seen] == ["HEAD"]      # the plain-HTTP redirect check still runs
    assert result["requests_sent"] == 1
    assert result["status_rollup"] == "FAIL"
    assert all("TLS handshake did not succeed" in c["summary"]
               for c in result["check_results"] if c["verdict"] == "inconclusive" and c["check_id"].startswith("header_"))


async def test_the_http_request_budget_is_never_exceeded(certificate):
    for router in (hardened_router, weak_router, head_unsupported_router, waf_router):
        result, https_seen, http_seen = await assess(router, certificate)
        assert result["requests_sent"] <= 5
        assert len(https_seen) + len(http_seen) == result["requests_sent"]


async def test_the_runs_own_traffic_is_used_as_rate_limit_evidence(certificate, tmp_path):
    lines = [json.dumps({"type": "Metric", "data": {"name": "http_reqs"}, "metric": "http_reqs"})]
    for status in ["200"] * 90 + ["429"] * 10:
        lines.append(json.dumps({"metric": "http_reqs", "type": "Point",
                                 "data": {"value": 1, "tags": {"status": status, "tls_version": "tls1.3"}}}))
    (tmp_path / "k6_x_raw.json").write_text("\n".join(lines), encoding="utf-8")
    st = state()
    st["execution_artifact_directory"] = str(tmp_path)
    st["execution_artifacts"] = {"job_id": JOB, "artifacts": {"raw_results": "k6_x_raw.json"}}

    result, _, _ = await assess(hardened_router, certificate, st=st)

    rate = next(c for c in result["check_results"] if c["check_id"] == "rate_limit_evidence")
    assert rate["verdict"] == "passed" and "10 of 100" in rate["summary"]
    assert rate["evidence"]["performance_run"]["status_counts"] == {"200": 90, "429": 10}
    assert result["assessment_outcome"] == "assessed"
    assert result["check_summary"]["inconclusive"] == 0


async def test_nothing_is_sent_when_the_switch_is_off(monkeypatch, certificate):
    monkeypatch.setenv("SECURITY_PASSIVE_ASSESSMENT_ENABLED", "false")
    built = []
    result = await service.run_passive_checks(
        state(), network_factory=lambda t, b: built.append(1), resolver=resolver
    )

    assert result["status"] == "disabled" and result["reason_code"] == "passive_assessment_disabled"
    assert result["authorized"] is False and result["requests_sent"] == 0 and built == []


@pytest.mark.parametrize("status", ["running", "not_started", "blocked", "needs_input", None])
async def test_nothing_is_sent_before_the_performance_run_has_ended(status):
    built = []
    st = state()
    st["execution_status"] = status
    result = await service.run_passive_checks(st, network_factory=lambda t, b: built.append(1), resolver=resolver)

    assert result["status"] == "blocked" and result["reason_code"] == "run_not_finished" and built == []


@pytest.mark.parametrize("overrides,code", [
    ({"target_url": "https://localhost"}, "non_public_host"),
    ({"target_url": "http://api.example.com"}, "not_https"),
    ({"target_url": "https://api.example.com:8443"}, "non_standard_port"),
    ({"endpoint": "/a/../b"}, "invalid_endpoint"),
])
async def test_an_out_of_scope_target_is_blocked_without_any_request(overrides, code):
    built = []
    result = await service.run_passive_checks(
        state(**overrides), network_factory=lambda t, b: built.append(1), resolver=resolver
    )

    assert result["status"] == "blocked" and result["reason_code"] == code
    assert result["check_results"] == [] and result["assessment_outcome"] == "not_assessed" and built == []


async def test_a_job_without_an_id_is_blocked():
    st = state()
    st.pop("job_id")

    result = await service.run_passive_checks(st, network_factory=lambda t, b: None, resolver=resolver)

    assert result["reason_code"] == "no_job" and result["job_id"] is None


async def test_a_probe_that_raises_does_not_crash_the_assessment():
    class Exploding:
        def tls_probe(self):
            raise RuntimeError("boom")

    result = await service.run_passive_checks(state(), network_factory=lambda t, b: Exploding(), resolver=resolver)

    assert result["status"] == "completed"
    assert {c["verdict"] for c in result["check_results"]} == {"inconclusive"}
    assert result["assessment_outcome"] == "not_assessed" and result["status_rollup"] == "WARNING"
    assert result["security_score"] == "N/A"


async def test_the_overall_deadline_returns_partial_results(monkeypatch):
    class Slow:
        def tls_probe(self):
            time.sleep(1.5)

    monkeypatch.setattr(service, "TOTAL_TIMEOUT_SECONDS", 0.3)
    started = time.perf_counter()
    result = await service.run_passive_checks(state(), network_factory=lambda t, b: Slow(), resolver=resolver)

    assert time.perf_counter() - started < 1.2
    assert result["status"] == "completed" and result["assessment_outcome"] == "not_assessed"
    assert any("deadline" in c["summary"] for c in result["check_results"])


async def test_every_result_states_its_limits_and_never_claims_a_pentest(certificate):
    result, _, _ = await assess(hardened_router, certificate)

    text = " ".join(result["limitations"]).lower()
    assert "no attack payloads" in text and "cdn or waf" in text
    assert "tls-inspecting" in text or "intercept" in text

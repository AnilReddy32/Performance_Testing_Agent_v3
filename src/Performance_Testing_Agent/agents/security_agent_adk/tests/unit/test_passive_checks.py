"""Verdict logic: every check returns passed, failed or inconclusive, never a guess."""

import time

import pytest

from security_agent.passive import checks
from security_agent.passive.config import FOREIGN_ORIGIN
from security_agent.passive.models import (
    FAILED,
    INCONCLUSIVE,
    PASSED,
    CheckResult,
    HttpObservation,
    Observations,
    TlsObservation,
    TrafficEvidence,
)

HARDENED = {
    "strict-transport-security": "max-age=31536000; includeSubDomains",
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "content-security-policy": "default-src 'none'; frame-ancestors 'none'",
    "referrer-policy": "no-referrer",
    "permissions-policy": "geolocation=()",
    "cache-control": "no-store",
    "server": "srv",
}


def http(status=200, headers=None, *, method="HEAD", body="", label="primary", target="/posts/1"):
    return HttpObservation(
        label=label, method=method, target=target, scheme="https", status=status,
        headers=tuple((k.lower(), v) for k, v in (headers or {}).items()), body=body,
        elapsed_ms=5.0,
    )


def no_response(kind="timeout", label="primary", scheme="https"):
    return HttpObservation(
        label=label, method="HEAD", target="/posts/1", scheme=scheme,
        error_kind=kind, error=f"{kind} happened",
    )


def good_tls(**overrides):
    values = dict(
        ok=True, version="TLSv1.3", cipher_name="TLS_AES_256_GCM_SHA384", cipher_bits=256,
        subject="api.example.com", issuer="Example CA", san_count=2,
        not_after=time.time() + 90 * 86400,
    )
    values.update(overrides)
    return TlsObservation(**values)


def by_id(results):
    return {r.check_id: r for r in results}


def verdicts(results):
    return {r.check_id: r.verdict for r in results}


# ---------------------------------------------------------------------- TLS --

def test_modern_tls_passes_both_tls_checks():
    tls = good_tls()

    assert checks.check_tls_protocol(tls).verdict == PASSED
    assert checks.check_tls_certificate(tls).verdict == PASSED


@pytest.mark.parametrize("version", ["TLSv1.1", "TLSv1", "SSLv3"])
def test_deprecated_protocol_versions_fail_at_high_severity(version):
    result = checks.check_tls_protocol(good_tls(version=version))

    assert result.verdict == FAILED and result.severity == "high"
    assert result.recommendation


@pytest.mark.parametrize("cipher", ["ECDHE-RSA-RC4-SHA", "DES-CBC3-SHA", "AES256-SHA-NULL", "EXP-RC2-CBC-MD5"])
def test_weak_ciphers_fail(cipher):
    assert checks.check_tls_protocol(good_tls(version="TLSv1.2", cipher_name=cipher)).verdict == FAILED


@pytest.mark.parametrize("cipher", ["ECDHE-RSA-AES128-GCM-SHA256", "TLS_CHACHA20_POLY1305_SHA256", "TLS_AES_128_GCM_SHA256"])
def test_strong_ciphers_pass(cipher):
    assert checks.check_tls_protocol(good_tls(version="TLSv1.2", cipher_name=cipher)).verdict == PASSED


def test_a_verification_failure_is_a_certificate_finding_and_hides_the_protocol():
    tls = TlsObservation(ok=False, error_kind="cert_verify", error="x", verify_message="certificate has expired")

    certificate = checks.check_tls_certificate(tls)
    protocol = checks.check_tls_protocol(tls)

    assert certificate.verdict == FAILED and certificate.severity == "high"
    assert "expired" in certificate.summary
    assert protocol.verdict == INCONCLUSIVE and "certificate check" in protocol.summary


@pytest.mark.parametrize("kind", ["timeout", "connection_refused", "connection_error", "handshake"])
def test_an_incomplete_handshake_proves_nothing(kind):
    tls = TlsObservation(ok=False, error_kind=kind, error="boom")

    assert checks.check_tls_protocol(tls).verdict == INCONCLUSIVE
    assert checks.check_tls_certificate(tls).verdict == INCONCLUSIVE


def test_no_handshake_at_all_is_inconclusive():
    assert checks.check_tls_protocol(None).verdict == INCONCLUSIVE
    assert checks.check_tls_certificate(None).verdict == INCONCLUSIVE


def test_a_certificate_close_to_expiry_fails_at_medium_severity():
    result = checks.check_tls_certificate(good_tls(not_after=time.time() + 5 * 86400))

    assert result.verdict == FAILED and result.severity == "medium"
    assert result.evidence["days_until_expiry"] == pytest.approx(5, abs=0.1)


def test_a_certificate_with_unknown_expiry_still_passes_on_verification():
    result = checks.check_tls_certificate(good_tls(not_after=None))

    assert result.verdict == PASSED and result.evidence["days_until_expiry"] is None


# ---------------------------------------------------------- HTTP redirect --

def redirect(status, location=None):
    return http(status, {"Location": location} if location else {}, label="http_redirect")


@pytest.mark.parametrize("status", [301, 302, 303, 307, 308])
def test_http_redirected_to_https_passes(status):
    assert checks.check_https_redirect(redirect(status, "https://api.example.com/posts/1")).verdict == PASSED


@pytest.mark.parametrize("location", ["http://api.example.com/posts/1", "/posts/1", "ftp://x"])
def test_a_redirect_that_does_not_reach_https_fails(location):
    assert checks.check_https_redirect(redirect(301, location)).verdict == FAILED


def test_content_served_over_plain_http_fails():
    assert checks.check_https_redirect(http(200, label="http_redirect")).verdict == FAILED


def test_a_closed_port_80_passes_because_nothing_is_served_in_clear():
    assert checks.check_https_redirect(no_response("connection_refused", "http_redirect", "http")).verdict == PASSED


@pytest.mark.parametrize("obs", [
    http(403, label="http_redirect"), http(404, label="http_redirect"),
    http(405, label="http_redirect"), http(500, label="http_redirect"),
    http(304, label="http_redirect"), redirect(301),
    no_response("timeout", "http_redirect", "http"), no_response("connection_error", "http_redirect", "http"),
    None,
])
def test_anything_that_does_not_show_a_redirect_is_inconclusive(obs):
    assert checks.check_https_redirect(obs).verdict == INCONCLUSIVE


# ---------------------------------------------------------------- headers --

def header_checks(**kwargs):
    return by_id(checks.check_security_headers(Observations(declared_method="GET", **kwargs)))


def test_a_hardened_response_passes_every_header_check():
    results = header_checks(primary=http(200, HARDENED))

    assert set(verdicts(results.values()).values()) == {PASSED}
    assert len(results) == 8 and "header_cookie_attributes" not in results


def test_missing_headers_on_a_successful_head_fail_with_recommendations():
    results = header_checks(primary=http(200, {"content-type": "application/json"}))

    assert results["header_hsts"].verdict == FAILED
    assert results["header_hsts"].severity == "medium"
    assert results["header_x_content_type_options"].verdict == FAILED
    assert results["header_csp"].verdict == FAILED
    assert results["header_cache_control"].severity == "info"
    assert all(r.recommendation for r in results.values() if r.verdict == FAILED)
    assert results["header_information_disclosure"].verdict == PASSED


@pytest.mark.parametrize("status", [401, 403, 404, 405, 408, 429, 500, 502, 503])
def test_no_header_verdict_is_ever_drawn_from_a_denied_missing_or_failing_response(status):
    # Neither a pass nor a failure: a 403/405 must never count as a pass.
    for headers in ({}, HARDENED):
        results = header_checks(primary=http(status, headers))
        assert set(verdicts(results.values()).values()) == {INCONCLUSIVE}
        assert str(status) in results["header_hsts"].summary


def test_a_redirect_response_can_pass_but_its_missing_headers_are_not_failures():
    bare = header_checks(primary=http(301, {"location": "https://x/y"}))
    full = header_checks(primary=http(301, HARDENED))

    assert verdicts(bare.values())["header_hsts"] == INCONCLUSIVE
    assert verdicts(full.values())["header_hsts"] == PASSED


def test_headers_missing_from_an_options_reply_are_not_counted_against_the_target():
    bare = header_checks(options=http(204, {"allow": "GET"}, method="OPTIONS", label="options"))
    full = header_checks(options=http(204, HARDENED, method="OPTIONS", label="options"))

    assert verdicts(bare.values())["header_hsts"] == INCONCLUSIVE
    assert verdicts(full.values())["header_hsts"] == PASSED
    # ...but a header that is present yet weak is still a finding on any 2xx.
    weak = header_checks(options=http(204, {"strict-transport-security": "max-age=60"}, method="OPTIONS"))
    assert verdicts(weak.values())["header_hsts"] == FAILED


def test_the_primary_response_is_preferred_over_options():
    results = header_checks(
        primary=http(200, HARDENED),
        options=http(204, {}, method="OPTIONS"),
    )

    assert results["header_hsts"].verdict == PASSED


def test_no_response_makes_every_header_check_inconclusive_with_the_reason():
    results = header_checks(primary=no_response("timeout"))

    assert set(verdicts(results.values()).values()) == {INCONCLUSIVE}
    assert "timeout" in results["header_hsts"].summary
    assert set(verdicts(header_checks().values()).values()) == {INCONCLUSIVE}


@pytest.mark.parametrize("value,verdict", [
    ("max-age=31536000", PASSED),
    ("max-age=15552000", PASSED),
    ("max-age=15551999", FAILED),
    ("max-age=0", FAILED),
    ("includeSubDomains", FAILED),
    ('max-age="31536000"', PASSED),
])
def test_hsts_strength_is_judged_on_max_age(value, verdict):
    assert header_checks(primary=http(200, {"strict-transport-security": value}))["header_hsts"].verdict == verdict


@pytest.mark.parametrize("name,value,verdict", [
    ("x-content-type-options", "nosniff", PASSED),
    ("x-content-type-options", "sniff", FAILED),
    ("x-frame-options", "SAMEORIGIN", PASSED),
    ("x-frame-options", "ALLOW-FROM https://x", FAILED),
    ("content-security-policy", "frame-ancestors 'self'", PASSED),
    ("content-security-policy", "default-src *", FAILED),
    ("content-security-policy", "script-src 'unsafe-eval'", FAILED),
    ("referrer-policy", "strict-origin-when-cross-origin", PASSED),
    ("referrer-policy", "unsafe-url", FAILED),
    ("referrer-policy", "no-referrer, unsafe-url", FAILED),
    ("cache-control", "private, max-age=60", PASSED),
    ("cache-control", "public, max-age=3600", FAILED),
])
def test_individual_header_values_are_judged(name, value, verdict):
    results = header_checks(primary=http(200, {name: value}))
    check = {
        "x-content-type-options": "header_x_content_type_options",
        "x-frame-options": "header_frame_protection",
        "content-security-policy": "header_csp",
        "referrer-policy": "header_referrer_policy",
        "cache-control": "header_cache_control",
    }[name]
    if name == "content-security-policy" and value.startswith("frame-ancestors"):
        check = "header_frame_protection"
    assert results[check].verdict == verdict


@pytest.mark.parametrize("headers,expected", [
    ({"server": "Apache/2.4.41 (Ubuntu)"}, FAILED),
    ({"server": "nginx/1.18.0"}, FAILED),
    ({"x-powered-by": "Express"}, FAILED),
    ({"x-aspnet-version": "4.0.30319"}, FAILED),
    ({"server": "nginx"}, PASSED),
    ({"server": "cloudflare"}, PASSED),
    ({}, PASSED),
])
def test_technology_disclosure_is_flagged(headers, expected):
    assert header_checks(primary=http(200, headers))["header_information_disclosure"].verdict == expected


def test_cookies_are_checked_only_when_the_response_sets_them():
    insecure = header_checks(primary=http(200, {"set-cookie": "sid=abc; Path=/"}))
    secure = header_checks(primary=http(200, {"set-cookie": "sid=abc; Secure; HttpOnly; SameSite=Lax"}))

    assert insecure["header_cookie_attributes"].verdict == FAILED
    assert "sid is missing Secure, HttpOnly, SameSite" in insecure["header_cookie_attributes"].summary
    assert secure["header_cookie_attributes"].verdict == PASSED


# -------------------------------------------------------------------- CORS --

def preflight(status=204, headers=None):
    return http(status, headers or {}, method="OPTIONS", label="options")


@pytest.mark.parametrize("headers,verdict,severity", [
    ({"access-control-allow-origin": FOREIGN_ORIGIN, "access-control-allow-credentials": "true"}, FAILED, "high"),
    ({"access-control-allow-origin": FOREIGN_ORIGIN}, FAILED, "medium"),
    ({"access-control-allow-origin": "null"}, FAILED, "medium"),
    ({"access-control-allow-origin": "*", "access-control-allow-credentials": "true"}, FAILED, "medium"),
    ({"access-control-allow-origin": "*"}, PASSED, "medium"),
    ({"access-control-allow-origin": "https://app.example.com"}, PASSED, "medium"),
    ({}, PASSED, "medium"),
])
def test_cors_policy_for_a_foreign_origin(headers, verdict, severity):
    result = checks.check_cors(preflight(200, headers))

    assert result.verdict == verdict and result.severity == severity


@pytest.mark.parametrize("obs", [
    preflight(403), preflight(401), preflight(404), preflight(405), preflight(429),
    preflight(500), preflight(301), None, no_response("timeout"),
])
def test_a_preflight_that_was_not_answered_normally_is_inconclusive(obs):
    # Even a 403 that might mean "origin rejected" is not counted as a pass.
    assert checks.check_cors(obs).verdict == INCONCLUSIVE


# ----------------------------------------------------------------- methods --

@pytest.mark.parametrize("allow,verdict", [
    ("GET, HEAD, OPTIONS", PASSED),
    ("GET, POST, PUT, PATCH, DELETE, OPTIONS", PASSED),
    ("GET, TRACE", FAILED),
    ("get,connect", FAILED),
    ("GET, PROPFIND, LOCK", FAILED),
])
def test_advertised_methods_are_judged(allow, verdict):
    assert checks.check_methods(preflight(200, {"allow": allow})).verdict == verdict


@pytest.mark.parametrize("headers,verdict", [
    ({"access-control-allow-methods": "GET,HEAD,PUT,PATCH,POST,DELETE"}, PASSED),
    ({"access-control-allow-methods": "GET, TRACE"}, FAILED),
    ({"allow": "GET", "access-control-allow-methods": "GET, CONNECT"}, FAILED),
    ({"access-control-allow-methods": "*"}, INCONCLUSIVE),
])
def test_methods_are_also_read_from_the_cors_allow_methods_header(headers, verdict):
    result = checks.check_methods(preflight(204, headers))

    assert result.verdict == verdict
    if verdict != INCONCLUSIVE:
        assert "access-control-allow-methods" in result.evidence["listed_in"] or "allow" in result.evidence["listed_in"]


def test_the_certificate_issuer_is_visible_in_the_verdict():
    passed = checks.check_tls_certificate(good_tls(issuer="SSL-SG1-GLOBAL"))
    expiring = checks.check_tls_certificate(good_tls(issuer="SSL-SG1-GLOBAL", not_after=time.time() + 3 * 86400))

    assert "(issuer: SSL-SG1-GLOBAL)" in passed.summary
    assert "(issuer: SSL-SG1-GLOBAL)" in expiring.summary


@pytest.mark.parametrize("obs", [
    preflight(204), preflight(200, {"allow": ""}), preflight(403, {"allow": "GET"}),
    preflight(405, {"allow": "GET"}), preflight(404), preflight(500), None, no_response(),
])
def test_unknown_methods_are_inconclusive_and_a_405_never_passes(obs):
    assert checks.check_methods(obs).verdict == INCONCLUSIVE


# ---------------------------------------------------------- error leakage --

def missing(status, body):
    return http(status, {}, method="GET", body=body, label="not_found",
                target="/posts/security-assessment-not-found")


@pytest.mark.parametrize("body", [
    'Traceback (most recent call last):\n  File "app.py", line 3',
    "java.lang.NullPointerException\n\tat com.acme.Handler.run(Handler.java:42)",
    "System.NullReferenceException: Object reference not set",
    "Error at /var/www/app/src/index.php line 4",
    "C:\\inetpub\\wwwroot\\site\\web.config",
    "SQLSTATE[42000]: Syntax error",
    "You have an error in your SQL syntax near 'x'",
    "ORA-00933: SQL command not properly ended",
    "Whitelabel Error Page",
    "Werkzeug Debugger",
    "at Object.<anonymous> (/srv/app/server.js:10:15)",
])
def test_leaky_error_bodies_fail(body):
    result = checks.check_error_leakage(missing(404, body))

    assert result.verdict == FAILED and result.evidence["signatures"]


@pytest.mark.parametrize("body", [
    '{"error":"not found"}', "", "Not Found", "<html><body>404</body></html>",
    "Cannot GET /posts/security-assessment-not-found",
])
def test_clean_error_bodies_pass(body):
    assert checks.check_error_leakage(missing(404, body)).verdict == PASSED


def test_the_echoed_request_path_is_not_mistaken_for_a_server_path():
    obs = http(404, {}, method="GET", label="not_found", target="/srv/app/security-assessment-not-found",
               body="Cannot GET /srv/app/security-assessment-not-found")

    assert checks.check_error_leakage(obs).verdict == PASSED


@pytest.mark.parametrize("status", [400, 404, 410, 422, 500])
def test_application_error_statuses_are_judged_on_their_content(status):
    assert checks.check_error_leakage(missing(status, "{}")).verdict == PASSED
    assert checks.check_error_leakage(missing(status, "Traceback (most recent call last):")).verdict == FAILED


@pytest.mark.parametrize("status", [200, 204, 301, 401, 403, 405, 429, 502, 503, 504])
def test_other_statuses_do_not_exercise_error_handling_so_never_pass(status):
    assert checks.check_error_leakage(missing(status, "{}")).verdict == INCONCLUSIVE
    assert checks.check_error_leakage(missing(status, "Traceback (most recent call last):")).verdict == INCONCLUSIVE


def test_a_failed_error_probe_is_inconclusive():
    assert checks.check_error_leakage(None).verdict == INCONCLUSIVE
    assert checks.check_error_leakage(no_response()).verdict == INCONCLUSIVE


# ------------------------------------------------------------ rate limiting --

def traffic(**counts):
    total = sum(counts.values())
    return TrafficEvidence(source="run.json", total_requests=total, status_counts={k: v for k, v in counts.items()})


def test_throttling_seen_in_the_performance_run_is_evidence_of_a_limit():
    result = checks.check_rate_limit_evidence(
        Observations(declared_method="GET", traffic=traffic(**{"200": 90, "429": 10}))
    )

    assert result.verdict == PASSED and "10 of 100" in result.summary


def test_rate_limit_headers_are_evidence_too():
    result = checks.check_rate_limit_evidence(
        Observations(declared_method="GET", primary=http(200, {"x-ratelimit-limit": "100"}))
    )

    assert result.verdict == PASSED and "x-ratelimit-limit" in result.summary


def test_no_throttling_at_the_applied_load_never_fails_the_target():
    result = checks.check_rate_limit_evidence(
        Observations(declared_method="GET", traffic=traffic(**{"200": 500}))
    )

    assert result.verdict == INCONCLUSIVE
    assert "does not show that rate limiting is absent" in result.summary


def test_without_any_evidence_rate_limiting_is_inconclusive():
    assert checks.check_rate_limit_evidence(Observations(declared_method="GET")).verdict == INCONCLUSIVE


def test_retry_after_only_counts_on_a_throttled_response():
    on_429 = Observations(declared_method="GET", not_found=http(429, {"retry-after": "30"}, method="GET"))
    on_503 = Observations(declared_method="GET", not_found=http(503, {"retry-after": "30"}, method="GET"))

    assert checks.check_rate_limit_evidence(on_429).verdict == PASSED
    assert checks.check_rate_limit_evidence(on_503).verdict == INCONCLUSIVE


# ------------------------------------------------------------------ rollup --

def result(check_id, verdict, severity):
    return CheckResult(check_id, check_id, "x", verdict, severity, "s")


def test_nothing_assessed_means_warning_and_no_score():
    summary = checks.summarize([result("a", INCONCLUSIVE, "high"), result("b", INCONCLUSIVE, "low")])

    assert (summary["status"], summary["outcome"], summary["security_score"]) == ("WARNING", "not_assessed", "N/A")
    assert summary["assessed"] == 0 and summary["inconclusive"] == 2


def test_everything_passed_is_pass_with_a_full_score():
    summary = checks.summarize([result("a", PASSED, "high"), result("b", PASSED, "low")])

    assert (summary["status"], summary["outcome"], summary["security_score"]) == ("PASS", "assessed", "100%")


@pytest.mark.parametrize("severity,status", [
    ("critical", "FAIL"), ("high", "FAIL"), ("medium", "WARNING"), ("low", "WARNING"), ("info", "PASS"),
])
def test_status_follows_the_worst_failed_check(severity, status):
    assert checks.summarize([result("a", PASSED, "low"), result("b", FAILED, severity)])["status"] == status


def test_inconclusive_checks_never_change_the_status_or_the_score():
    base = [result("a", PASSED, "high"), result("b", FAILED, "medium")]
    with_unknowns = base + [result("c", INCONCLUSIVE, "high"), result("d", INCONCLUSIVE, "high")]

    plain, mixed = checks.summarize(base), checks.summarize(with_unknowns)

    assert (plain["status"], plain["security_score"]) == (mixed["status"], mixed["security_score"])
    assert plain["outcome"] == "assessed" and mixed["outcome"] == "partially_assessed"
    assert mixed["total"] == 4 and mixed["assessed"] == 2 and mixed["inconclusive"] == 2


def test_the_score_is_severity_weighted_over_assessed_checks_only():
    # high passed (5) + medium failed (3) + low passed (1): 6 of 9 points.
    summary = checks.summarize([result("a", PASSED, "high"), result("b", FAILED, "medium"), result("c", PASSED, "low")])

    assert summary["security_score"] == "67%"
    assert "6 of 9" in summary["security_score_basis"]


def test_informational_checks_carry_no_weight():
    only_info = checks.summarize([result("a", FAILED, "info"), result("b", PASSED, "info")])

    assert only_info["security_score"] == "N/A" and only_info["status"] == "PASS"
    assert checks.summarize([result("a", PASSED, "low"), result("b", FAILED, "info")])["security_score"] == "100%"


def test_evaluate_returns_one_unique_verdict_per_check():
    observations = Observations(
        declared_method="GET", tls=good_tls(), primary=http(200, HARDENED),
        options=preflight(204, {"allow": "GET, OPTIONS"}),
        not_found=missing(404, "{}"), http_redirect=redirect(301, "https://api.example.com/"),
    )

    results = checks.evaluate(observations)
    ids = [r.check_id for r in results]

    assert len(ids) == len(set(ids)) == 15  # 16 when the response also sets cookies
    assert {r.verdict for r in results} <= {PASSED, FAILED, INCONCLUSIVE}
    assert verdicts(results)["tls_protocol"] == PASSED
    assert verdicts(results)["rate_limit_evidence"] == INCONCLUSIVE


def test_a_skipped_reason_is_added_to_inconclusive_checks_only():
    observations = Observations(
        declared_method="GET", tls=TlsObservation(ok=False, error_kind="timeout", error="t"),
        skipped_reason="HTTPS requests were not sent.",
    )

    results = checks.evaluate(observations)

    assert all("HTTPS requests were not sent." in r.summary for r in results if r.verdict == INCONCLUSIVE)
    assert not [r for r in results if r.verdict != INCONCLUSIVE]


def test_failed_checks_carry_a_recommendation_and_passed_checks_do_not():
    results = checks.evaluate(Observations(
        declared_method="GET", tls=good_tls(), primary=http(200, {}),
        options=preflight(200, {"allow": "GET, TRACE"}),
    ))

    for r in results:
        assert bool(r.recommendation) == (r.verdict == FAILED)

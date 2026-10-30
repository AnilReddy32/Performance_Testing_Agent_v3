"""Regressions for defects found by an independent review of the passive assessment."""

import asyncio
import ssl
import time

import pytest

pytest.importorskip("cryptography")

from passive_support import (  # noqa: E402
    HOSTNAME,
    LocalServer,
    RawTlsServer,
    client_context,
    hardened_router,
    make_certificate,
    vanilla_ssl,
)
from security_agent.passive import checks, service  # noqa: E402
from security_agent.passive.models import (  # noqa: E402
    FAILED,
    INCONCLUSIVE,
    PASSED,
    HttpObservation,
    Observations,
    TlsObservation,
)
from security_agent.passive.network import PassiveNetwork, RequestBudget  # noqa: E402

pytestmark = pytest.mark.usefixtures("vanilla_ssl")

PUBLIC = ["93.184.216.34"]
JOB = "JOB-" + "d" * 32


@pytest.fixture(scope="module")
def certificate():
    return make_certificate()


def network_for(server, certificate, **kwargs):
    return PassiveNetwork(
        HOSTNAME, ["127.0.0.1"], https_port=server.port,
        ssl_context=client_context(certificate[0]), timeout=kwargs.pop("timeout", 2.0), **kwargs,
    )


def state(**overrides):
    profile = {"tool": "k6", "target_url": f"https://{HOSTNAME}", "endpoint": "/v1/items",
               "method": "GET", "environment": "external_api"}
    profile.update(overrides)
    return {"job_id": JOB, "test_case_id": "PTC-004", "execution_mode": "REAL",
            "execution_status": "completed", "workload_profile": profile}


def reply(status, headers=None, *, method="HEAD", body="", target="/x"):
    return HttpObservation(label="primary", method=method, target=target, scheme="https", status=status,
                           headers=tuple((k, v) for k, v in (headers or {}).items()), body=body)


# ---------------------------------------------- rule: a denied reply never passes --

@pytest.mark.parametrize("status", [401, 403, 404, 405, 500, 502, 503])
def test_rate_limit_headers_on_a_denied_or_failing_reply_are_not_evidence(status):
    obs = Observations(declared_method="GET", primary=reply(status, {"ratelimit-limit": "100"}))

    assert checks.check_rate_limit_evidence(obs).verdict == INCONCLUSIVE


@pytest.mark.parametrize("status", [200, 204, 301])
def test_rate_limit_headers_on_a_normal_reply_are_evidence(status):
    obs = Observations(declared_method="GET", primary=reply(status, {"x-ratelimit-limit": "100"}))

    assert checks.check_rate_limit_evidence(obs).verdict == PASSED


def test_a_429_with_retry_after_is_evidence():
    obs = Observations(declared_method="GET", not_found=reply(429, {"retry-after": "10"}, method="GET"))

    assert checks.check_rate_limit_evidence(obs).verdict == PASSED


def test_a_gateway_that_answers_403_with_rate_limit_headers_cannot_produce_a_clean_pass():
    obs = Observations(
        declared_method="GET",
        tls=TlsObservation(ok=True, version="TLSv1.3", cipher_name="TLS_AES_256_GCM_SHA384", cipher_bits=256,
                           issuer="CA", not_after=time.time() + 90 * 86400),
        primary=reply(403, {"ratelimit-limit": "10"}),
        options=reply(403, {"ratelimit-limit": "10"}, method="OPTIONS"),
        not_found=reply(403, {"ratelimit-limit": "10"}, method="GET"),
    )

    verdicts = {r.check_id: r.verdict for r in checks.evaluate(obs)}

    assert verdicts["rate_limit_evidence"] == INCONCLUSIVE
    assert [k for k, v in verdicts.items() if v == PASSED] == ["tls_protocol", "tls_certificate"]


# ----------------------------------------------------------- header details --

@pytest.mark.parametrize("csp,expected", [
    ("frame-ancestors 'none'", PASSED),
    ("frame-ancestors 'self'", PASSED),
    ("frame-ancestors https://app.example.com", PASSED),
    ("default-src 'none'; frame-ancestors 'self' https://a.example.com", PASSED),
    ("frame-ancestors *", FAILED),
    ("frame-ancestors https:", FAILED),
    ("frame-ancestors 'self' *", FAILED),
    ("default-src 'none'; frame-ancestors data:", FAILED),
    ("default-src 'none'", FAILED),
])
def test_frame_ancestors_only_protects_when_it_does_not_allow_everyone(csp, expected):
    results = {r.check_id: r for r in checks.check_security_headers(
        Observations(declared_method="GET", primary=reply(200, {"content-security-policy": csp})))}

    assert results["header_frame_protection"].verdict == expected


# --------------------------------------------------------- error leakage --

def not_found(status, body, headers=None):
    return HttpObservation(label="not_found", method="GET", target="/api/security-assessment-not-found",
                           scheme="https", status=status, body=body,
                           headers=tuple((headers or {}).items()))


@pytest.mark.parametrize("body", [
    '<nav><a href="/home/index">Home</a> <a href="/usr/">Users</a> <a href="/opt/shop">Shop</a></nav>',
    '<link rel="stylesheet" href="/var/styles">',
    '{"docs":"see /etc/ for details"}',
    "Page not found. Try /home or /srv.",
])
def test_links_and_prose_that_mention_directories_are_not_a_leak(body):
    assert checks.check_error_leakage(not_found(404, body)).verdict == PASSED


@pytest.mark.parametrize("body", [
    "Error in /var/www/app/handlers/items.py at line 12",
    "Cannot open /home/deploy/site/config/settings.yml",
    "at Module._compile (/srv/app/node_modules/x/index.js:12:3)",
    "C:\\inetpub\\wwwroot\\api\\web.config could not be loaded",
])
def test_a_real_server_file_path_is_a_leak(body):
    assert checks.check_error_leakage(not_found(404, body)).verdict == FAILED


@pytest.mark.parametrize("encoding", ["gzip", "br", "deflate", "zstd"])
def test_a_compressed_error_body_cannot_be_judged(encoding):
    result = checks.check_error_leakage(not_found(404, "\x1f\x8b binary", {"content-encoding": encoding}))

    assert result.verdict == INCONCLUSIVE and encoding in result.summary


def test_an_identity_encoded_body_is_scanned_normally():
    result = checks.check_error_leakage(
        not_found(404, "Traceback (most recent call last):", {"content-encoding": "identity"}))

    assert result.verdict == FAILED


def test_an_empty_500_gives_nothing_to_inspect():
    assert checks.check_error_leakage(not_found(500, "")).verdict == INCONCLUSIVE
    assert checks.check_error_leakage(not_found(404, "")).verdict == PASSED      # a normal empty 404


# ---------------------------------------------------------- legacy TLS only --

def test_a_server_that_only_speaks_tls_1_0_or_1_1_fails_the_protocol_check(certificate):
    try:
        server = RawTlsServer(lambda c, r: None, certificate,
                              min_version=ssl.TLSVersion.TLSv1, max_version=ssl.TLSVersion.TLSv1_1)
    except Exception as exc:                      # this OpenSSL build cannot serve legacy TLS
        pytest.skip(f"cannot build a legacy-TLS server here: {exc}")
    with server:
        observation = network_for(server, certificate, timeout=3).tls_probe()

    assert observation.ok is False and observation.error_kind == "legacy_protocol"
    protocol, certificate_check = checks.check_tls_protocol(observation), checks.check_tls_certificate(observation)
    assert protocol.verdict == FAILED and protocol.severity == "high" and protocol.recommendation
    assert certificate_check.verdict == INCONCLUSIVE


def test_other_handshake_failures_are_not_called_legacy():
    observation = TlsObservation(ok=False, error_kind="handshake", error="SSLError: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE]")

    assert checks.check_tls_protocol(observation).verdict == INCONCLUSIVE


# --------------------------------------------- slow or hostile servers --

def drip_forever(connection, request):
    connection.sendall(b"HTTP/1.1 200 OK\r\nX-Pad: ")
    end = time.time() + 20
    while time.time() < end:
        connection.sendall(b"a")
        time.sleep(0.2)


def test_one_request_has_a_hard_wall_clock_limit_even_if_bytes_keep_arriving(certificate):
    with RawTlsServer(drip_forever, certificate) as server:
        network = network_for(server, certificate, timeout=1.0)          # wall clock = 2 s
        started = time.perf_counter()
        observation = network.request(label="primary", method="HEAD", target="/a")
        elapsed = time.perf_counter() - started

    assert observation.status is None and observation.error_kind == "timeout"
    assert elapsed < 5            # without the limit this would run for the full 20 s


def test_cancel_breaks_an_exchange_in_flight_and_refuses_the_next_one(certificate):
    import threading

    with RawTlsServer(drip_forever, certificate) as server:
        network = network_for(server, certificate, timeout=30)           # only cancel can stop it
        threading.Timer(0.5, network.cancel).start()
        started = time.perf_counter()
        first = network.request(label="primary", method="HEAD", target="/a")
        stopped_after = time.perf_counter() - started
        used = network.requests_sent
        second = network.request(label="options", method="OPTIONS", target="/a")

    assert first.error_kind == "cancelled" and stopped_after < 5
    assert second.error_kind == "cancelled"
    assert network.requests_sent == used              # nothing further was sent
    assert network.tls_probe().error_kind == "cancelled"


def test_the_deadline_returns_on_time_and_leaves_no_probe_running(certificate):
    with RawTlsServer(drip_forever, certificate) as server:
        def factory(target, budget):
            return PassiveNetwork(target.host, ["127.0.0.1"], budget=budget, https_port=server.port,
                                  http_port=1, ssl_context=client_context(certificate[0]), timeout=30)

        original = service.TOTAL_TIMEOUT_SECONDS
        service.TOTAL_TIMEOUT_SECONDS = 1.5
        try:
            started = time.perf_counter()
            result = asyncio.run(service.run_passive_checks(
                state(), network_factory=factory, resolver=lambda h, p: list(PUBLIC)))
            took = time.perf_counter() - started
        finally:
            service.TOTAL_TIMEOUT_SECONDS = original
        sent_at_return = len(server.requests)
        time.sleep(1.0)

    assert took < 6                                    # including shutting the worker thread down
    assert result["status"] == "completed"
    # The handshake finished before the server started dripping, so only the two TLS
    # checks can be judged; every HTTP check is inconclusive, not guessed.
    assert result["check_summary"]["assessed"] == 2
    assert result["assessment_outcome"] == "partially_assessed"
    assert len(server.requests) == sent_at_return      # the abandoned probe sent nothing more


def test_a_truncated_chunked_body_keeps_the_status_and_headers_received(certificate):
    def truncated(connection, request):
        connection.sendall(b"HTTP/1.1 404 Not Found\r\nTransfer-Encoding: chunked\r\nServer: srv\r\n\r\n"
                           b"10\r\nTraceback (most r")           # promises 16 bytes, closes early

    with RawTlsServer(truncated, certificate) as server:
        observation = network_for(server, certificate).request(
            label="not_found", method="GET", target="/missing", read_body=True)

    assert observation.status == 404
    assert observation.header("server") == "srv"
    assert observation.body.startswith("Traceback")


def test_a_request_target_that_cannot_be_encoded_is_a_clean_failure_not_a_crash(certificate):
    with LocalServer(hardened_router, tls_material=certificate) as server:
        observation = network_for(server, certificate).request(label="primary", method="HEAD", target="/caf\u00e9")

    assert observation.status is None and observation.error_kind == "invalid_request"


# ---------------------------------------------- failure reporting is order-free --

@pytest.mark.parametrize("order", [(0, 1), (1, 0)])
def test_refused_is_reported_only_when_every_address_refused(order, monkeypatch):
    kinds = {"a": ConnectionRefusedError("refused"), "b": TimeoutError("timed out")}
    addresses = ["a", "b"]
    network = PassiveNetwork(HOSTNAME, [addresses[i] for i in order], timeout=1)

    def connect(self):
        raise kinds[self._address]

    monkeypatch.setattr("security_agent.passive.network._PinnedHTTPConnection.connect", connect)
    observation = network.request(label="http_redirect", method="HEAD", target="/a", tls=False)

    assert observation.error_kind == "timeout"           # never "refused", whatever the order
    assert checks.check_https_redirect(observation).verdict == INCONCLUSIVE


def test_when_every_address_refuses_nothing_is_listening(monkeypatch):
    network = PassiveNetwork(HOSTNAME, ["a", "b"], timeout=1)

    def refuse(self):
        raise ConnectionRefusedError("refused")

    monkeypatch.setattr("security_agent.passive.network._PinnedHTTPConnection.connect", refuse)
    observation = network.request(label="http_redirect", method="HEAD", target="/a", tls=False)

    assert observation.error_kind == "connection_refused"
    assert checks.check_https_redirect(observation).verdict == PASSED


# --------------------------------------------- what goes over plain HTTP --

def test_only_the_path_never_the_query_string_is_sent_in_clear(certificate):
    secret = "/v1/items?api_key=SECRET123&user=bob"

    async def run():
        with LocalServer(hardened_router, tls_material=certificate) as https_server, \
                LocalServer(lambda m, p, h: (301, {"Location": f"https://{HOSTNAME}/"}, "")) as http_server:
            def factory(target, budget):
                return PassiveNetwork(target.host, ["127.0.0.1"], budget=budget, https_port=https_server.port,
                                      http_port=http_server.port, ssl_context=client_context(certificate[0]), timeout=3)
            await service.run_passive_checks(state(endpoint=secret), network_factory=factory,
                                             resolver=lambda h, p: list(PUBLIC))
            return https_server.requests, http_server.requests

    https_seen, http_seen = asyncio.run(run())

    assert [r["path"] for r in http_seen] == ["/v1/items"]                    # no secret in clear
    assert any("SECRET123" in r["path"] for r in https_seen)                  # encrypted requests still carry it
    assert not any("SECRET123" in str(r) for r in http_seen)


def test_a_non_ascii_endpoint_is_sent_percent_encoded_and_fully_assessed(certificate):
    async def run():
        with LocalServer(hardened_router, tls_material=certificate) as https_server, \
                LocalServer(lambda m, p, h: (301, {"Location": f"https://{HOSTNAME}/"}, "")) as http_server:
            def factory(target, budget):
                return PassiveNetwork(target.host, ["127.0.0.1"], budget=budget, https_port=https_server.port,
                                      http_port=http_server.port, ssl_context=client_context(certificate[0]), timeout=3)
            result = await service.run_passive_checks(state(endpoint="/caf\u00e9?q=na\u00efve"),
                                                      network_factory=factory, resolver=lambda h, p: list(PUBLIC))
            return result, https_server.requests

    result, seen = asyncio.run(run())

    assert [r["path"] for r in seen][:2] == ["/caf%C3%A9?q=na%C3%AFve"] * 2
    assert result["check_summary"]["assessed"] >= 13       # not collapsed into "inconclusive"

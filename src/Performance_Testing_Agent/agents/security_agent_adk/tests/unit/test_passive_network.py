"""The network layer against real local sockets: pinning, limits, error kinds."""

import socket
import threading
import time

import pytest

pytest.importorskip("cryptography")

from passive_support import (  # noqa: E402
    HOSTNAME,
    LocalServer,
    client_context,
    free_port,
    hardened_router,
    make_certificate,
    vanilla_ssl,
)
from security_agent.passive.network import (  # noqa: E402
    BudgetExceeded,
    PassiveNetwork,
    RequestBudget,
)


pytestmark = pytest.mark.usefixtures("vanilla_ssl")


@pytest.fixture(scope="module")
def certificate():
    return make_certificate()


def network_for(server, certificate, **kwargs):
    return PassiveNetwork(
        HOSTNAME,
        kwargs.pop("addresses", ["127.0.0.1"]),
        https_port=server.port,
        ssl_context=client_context(certificate[0]),
        timeout=kwargs.pop("timeout", 3.0),
        **kwargs,
    )


def test_tls_probe_reads_version_cipher_and_certificate(certificate):
    with LocalServer(hardened_router, tls_material=certificate) as server:
        observation = network_for(server, certificate).tls_probe()

    assert observation.ok is True
    assert observation.version in {"TLSv1.2", "TLSv1.3"}
    assert observation.cipher_name
    assert observation.subject == HOSTNAME
    assert observation.san_count == 2
    assert 85 < (observation.not_after - time.time()) / 86400 < 91


def test_untrusted_certificate_is_reported_not_ignored(certificate):
    # The default context does not trust the test CA, so verification must fail.
    with LocalServer(hardened_router, tls_material=certificate) as server:
        network = PassiveNetwork(HOSTNAME, ["127.0.0.1"], https_port=server.port, timeout=3)
        observation = network.tls_probe()

    assert observation.ok is False
    assert observation.error_kind == "cert_verify"
    assert "self" in observation.verify_message.lower() or "unable" in observation.verify_message.lower()


def test_expired_certificate_fails_verification():
    expired = make_certificate(expired=True)
    with LocalServer(hardened_router, tls_material=expired) as server:
        observation = network_for(server, expired).tls_probe()

    assert observation.ok is False and observation.error_kind == "cert_verify"
    assert "expired" in observation.verify_message.lower()


def test_hostname_mismatch_fails_verification():
    other = make_certificate(names=("someone-else.example.org",))
    with LocalServer(hardened_router, tls_material=other) as server:
        network = PassiveNetwork(
            HOSTNAME, ["127.0.0.1"], https_port=server.port,
            ssl_context=client_context(other[0]), timeout=3,
        )
        observation = network.tls_probe()

    assert observation.ok is False and observation.error_kind == "cert_verify"
    assert "mismatch" in observation.verify_message.lower() or "match" in observation.verify_message.lower()


def test_head_returns_status_and_lowercased_headers_without_a_body(certificate):
    with LocalServer(hardened_router, tls_material=certificate) as server:
        observation = network_for(server, certificate).request(
            label="primary", method="HEAD", target="/posts/1?x=1"
        )
        seen = server.requests[0]

    assert observation.status == 200 and observation.body == ""
    assert observation.header("strict-transport-security").startswith("max-age=31536000")
    assert observation.header("X-CONTENT-TYPE-OPTIONS") == "nosniff"
    assert seen["method"] == "HEAD" and seen["path"] == "/posts/1?x=1"
    # The request names the host (SNI/Host) even though the IP was pinned.
    assert seen["headers"]["Host"].startswith(HOSTNAME)
    assert "passive" in seen["headers"]["User-Agent"].lower()


def test_get_reads_at_most_one_small_page(certificate):
    def router(method, path, headers):
        return 404, {}, "x" * 100_000

    with LocalServer(router, tls_material=certificate) as server:
        observation = network_for(server, certificate).request(
            label="not_found", method="GET", target="/missing", read_body=True
        )

    assert observation.status == 404
    assert len(observation.body) == 8192


def test_redirects_are_observed_but_never_followed(certificate):
    def router(method, path, headers):
        return 301, {"Location": "https://elsewhere.example.net/x"}, ""

    with LocalServer(router, tls_material=certificate) as server:
        observation = network_for(server, certificate).request(
            label="primary", method="GET", target="/a"
        )
        count = len(server.requests)

    assert observation.status == 301
    assert observation.header("location") == "https://elsewhere.example.net/x"
    assert count == 1


def test_only_safe_methods_and_fixed_headers_are_possible(certificate):
    with LocalServer(hardened_router, tls_material=certificate) as server:
        network = network_for(server, certificate)
        for method in ("POST", "PUT", "DELETE", "PATCH", "TRACE"):
            with pytest.raises(ValueError):
                network.request(label="x", method=method, target="/a")
        with pytest.raises(ValueError):
            network.request(label="x", method="GET", target="/a", headers={"Authorization": "x"})
        with pytest.raises(ValueError):
            network.request(label="x", method="GET", target="http://other/a")
        sent = len(server.requests)

    assert sent == 0
    assert network.requests_sent == 0  # rejected requests do not use the budget


def test_cors_preflight_headers_are_allowed_and_sent(certificate):
    with LocalServer(hardened_router, tls_material=certificate) as server:
        network_for(server, certificate).request(
            label="options", method="OPTIONS", target="/a",
            headers={"Origin": "https://o.invalid", "Access-Control-Request-Method": "PUT"},
        )
        headers = server.requests[0]["headers"]

    assert headers["Origin"] == "https://o.invalid"
    assert headers["Access-Control-Request-Method"] == "PUT"


def test_request_budget_is_a_hard_ceiling(certificate):
    with LocalServer(hardened_router, tls_material=certificate) as server:
        network = network_for(server, certificate, budget=RequestBudget(5))
        for _ in range(5):
            network.request(label="x", method="HEAD", target="/a")
        with pytest.raises(BudgetExceeded):
            network.request(label="x", method="HEAD", target="/a")
        total = len(server.requests)

    assert total == 5 and network.requests_sent == 5


def test_a_refused_connection_is_reported_as_such():
    unused = free_port()
    # Windows reports a refused loopback connection only after about two seconds.
    network = PassiveNetwork(HOSTNAME, ["127.0.0.1"], http_port=unused, timeout=8)
    observation = network.request(label="http", method="HEAD", target="/a", tls=False)

    assert observation.status is None and observation.error_kind == "connection_refused"


def test_a_silent_server_times_out_instead_of_hanging():
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    held = []
    threading.Thread(target=lambda: held.append(listener.accept()), daemon=True).start()
    try:
        network = PassiveNetwork(
            HOSTNAME, ["127.0.0.1"], http_port=listener.getsockname()[1], timeout=0.4
        )
        started = time.perf_counter()
        observation = network.request(label="http", method="HEAD", target="/a", tls=False)
        elapsed = time.perf_counter() - started
    finally:
        listener.close()

    assert observation.error_kind == "timeout"
    assert elapsed < 3


def test_next_address_is_tried_when_the_first_refuses(certificate):
    with LocalServer(hardened_router, tls_material=certificate) as server:
        # 127.0.0.2 is also loopback on most hosts but nothing listens there.
        network = network_for(
            server, certificate, addresses=["127.0.0.2", "127.0.0.1"], timeout=8
        )
        observation = network.request(label="primary", method="HEAD", target="/a")

    assert observation.status == 200
    assert ("127.0.0.2", server.port) in network._dead


def test_plain_http_probe_uses_the_http_port_and_no_tls():
    with LocalServer(lambda m, p, h: (301, {"Location": "https://api.example.com/a"}, "")) as server:
        network = PassiveNetwork(HOSTNAME, ["127.0.0.1"], http_port=server.port, timeout=2)
        observation = network.request(label="http", method="HEAD", target="/a", tls=False)

    assert observation.scheme == "http" and observation.status == 301


def test_an_unreachable_address_is_not_retried_by_every_later_probe():
    network = PassiveNetwork(
        HOSTNAME, ["127.0.0.1"], https_port=free_port(), timeout=8
    )
    first = network.tls_probe()
    started = time.perf_counter()
    later = network.request(label="primary", method="HEAD", target="/a")
    waited = time.perf_counter() - started

    assert first.ok is False and first.error_kind == "connection_refused"
    assert later.status is None and "No reachable address" in later.error
    assert waited < 0.5  # it did not wait out another connection attempt


def test_certificate_details_are_read_from_der_when_getpeercert_is_empty():
    import ssl

    from security_agent.passive.network import _decode_certificate, _peer_certificate

    pem, _ = make_certificate(days_valid=30)
    der = ssl.PEM_cert_to_DER_cert(pem.decode())

    class OsVerifiedSocket:  # what the OS trust store leaves behind: no parsed dict
        def getpeercert(self, binary_form=False):
            return der if binary_form else {}

    decoded = _decode_certificate(der)
    via_socket = _peer_certificate(OsVerifiedSocket())

    for details in (decoded, via_socket):
        assert details["subject"] == ((("commonName", HOSTNAME),),)
        assert 29 < (ssl.cert_time_to_seconds(details["notAfter"]) - time.time()) / 86400 < 31
        assert ("DNS", HOSTNAME) in details["subjectAltName"]


def test_garbage_certificate_bytes_yield_no_details_instead_of_crashing():
    from security_agent.passive.network import _decode_certificate

    assert _decode_certificate(b"not a certificate") == {}


def test_certificate_failures_are_reported_when_the_os_trust_store_is_injected(certificate):
    # Production runs with truststore injected into ssl. A certificate the OS
    # does not trust must still surface as a verification finding, not a crash.
    truststore = pytest.importorskip("truststore")
    with LocalServer(hardened_router, tls_material=certificate) as server:
        truststore.inject_into_ssl()
        try:
            probe = PassiveNetwork(HOSTNAME, ["127.0.0.1"], https_port=server.port, timeout=3).tls_probe()
            request = PassiveNetwork(HOSTNAME, ["127.0.0.1"], https_port=server.port, timeout=3).request(
                label="primary", method="HEAD", target="/a"
            )
        finally:
            truststore.extract_from_ssl()

    assert probe.ok is False and probe.error_kind == "cert_verify"
    assert probe.verify_message
    assert request.status is None and request.error_kind == "tls_certificate"

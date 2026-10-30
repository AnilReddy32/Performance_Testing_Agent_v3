"""Low-level, bounded network access for the passive assessment.

Every connection goes to an address that was resolved once and verified to be
public (see target.py), so a changing DNS answer cannot redirect a probe into a
private network. Only HEAD, GET and OPTIONS are possible; request bodies and
caller-supplied header names outside a fixed list are refused; redirects are
never followed; at most MAX_HTTP_REQUESTS requests are ever sent.
"""

from __future__ import annotations

import http.client
import os
import socket
import ssl
import tempfile
import threading
import time
from collections.abc import Mapping, Sequence
from datetime import datetime, timezone

from security_agent.passive.config import (
    HTTP_PORT,
    HTTPS_PORT,
    MAX_HTTP_REQUESTS,
    MAX_RESPONSE_BYTES,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
)
from security_agent.passive.models import HttpObservation, TlsObservation

_SAFE_METHODS = {"HEAD", "GET", "OPTIONS"}
# The only caller-supplied headers, with the case they are sent in.
_ALLOWED_REQUEST_HEADERS = {
    "origin": "Origin",
    "access-control-request-method": "Access-Control-Request-Method",
    "access-control-request-headers": "Access-Control-Request-Headers",
}


class BudgetExceeded(RuntimeError):
    """More HTTP requests were attempted than the assessment allows."""


class RequestBudget:
    def __init__(self, limit: int = MAX_HTTP_REQUESTS):
        self.limit = limit
        self.used = 0

    def consume(self) -> None:
        if self.used >= self.limit:
            raise BudgetExceeded(
                f"The passive assessment is limited to {self.limit} HTTP requests."
            )
        self.used += 1


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    """HTTPS to a fixed, pre-verified IP while keeping SNI and Host as the name."""

    def __init__(self, host, address, port, timeout, context):
        super().__init__(host, port=port, timeout=timeout, context=context)
        self._address = address

    def connect(self):
        sock = socket.create_connection((self._address, self.port), self.timeout)
        try:
            self.sock = self._context.wrap_socket(sock, server_hostname=self.host)
        except BaseException:
            sock.close()
            raise


class _PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, host, address, port, timeout):
        super().__init__(host, port=port, timeout=timeout)
        self._address = address

    def connect(self):
        self.sock = socket.create_connection((self._address, self.port), self.timeout)


def _clip(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {str(exc)[:160]}"


def _decode_certificate(der: bytes) -> dict:
    """Parse a DER certificate into the shape ssl.getpeercert() returns.

    When Python verifies through the operating system's trust store (as this
    project does for corporate networks), getpeercert() is empty even though
    verification succeeded, so the details are read from the raw certificate.
    """
    try:
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "peer.pem")
            with open(path, "w", encoding="ascii") as handle:
                handle.write(ssl.DER_cert_to_PEM_cert(der))
            decoded = ssl._ssl._test_decode_cert(path)  # type: ignore[attr-defined]
            if decoded:
                return decoded
    except Exception:  # private helper; fall back to cryptography when present
        pass
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID

        certificate = x509.load_der_x509_certificate(der)

        def name(value) -> tuple:
            attributes = value.get_attributes_for_oid(NameOID.COMMON_NAME)
            return (((("commonName", attributes[0].value),),) if attributes else ())

        try:
            names = certificate.extensions.get_extension_for_class(
                x509.SubjectAlternativeName
            ).value.get_values_for_type(x509.DNSName)
        except x509.ExtensionNotFound:
            names = []
        expiry = certificate.not_valid_after_utc
        return {
            "subject": name(certificate.subject),
            "issuer": name(certificate.issuer),
            "notAfter": expiry.strftime("%b %d %H:%M:%S %Y GMT"),
            "subjectAltName": tuple(("DNS", entry) for entry in names),
        }
    except Exception:
        return {}


def _peer_certificate(tls: ssl.SSLSocket) -> dict:
    return tls.getpeercert() or (
        _decode_certificate(der) if (der := tls.getpeercert(binary_form=True)) else {}
    )


def _name(parts: Sequence | None) -> str | None:
    """Pick a readable value out of a certificate subject or issuer."""
    flat = {key: value for rdn in parts or () for key, value in rdn}
    return flat.get("commonName") or flat.get("organizationName")


def _abort(sock) -> None:
    """Break whatever a blocked read or write on this socket is waiting for."""
    if sock is None:
        return
    for action in (lambda: sock.shutdown(socket.SHUT_RDWR), sock.close):
        try:
            action()
        except Exception:
            pass


def _is_legacy_protocol_error(exc: BaseException) -> bool:
    """The server answered a TLS 1.2+ ClientHello with a version alert/hello.

    That is what a server that only speaks TLS 1.0/1.1 (or older) does. It is
    read from the error text because the standard library exposes no code.
    """
    text = f"{exc} {getattr(exc, 'reason', '')}".upper()
    return "PROTOCOL_VERSION" in text or "UNSUPPORTED_PROTOCOL" in text


def _first_failure(failures: list):
    """Report the most informative failure over all addresses tried.

    "Refused" means nothing is listening, which is a claim; any other failure
    (a timeout, a reset) is not. So the result must not depend on the order the
    addresses were tried in: refused is reported only if every address refused.
    """
    other = [f for f in failures if f.error_kind != "connection_refused"]
    return other[0] if other else failures[-1]


class _Watch:
    """A hard wall-clock limit for one exchange, and a handle for cancel().

    Socket timeouts restart on every byte received, so a server that drips data
    could hold one request for as long as it likes. The timer breaks the socket
    after the limit no matter what is arriving.
    """

    def __init__(self, network: "PassiveNetwork", abort):
        self._network = network
        self._abort = abort
        self.fired = threading.Event()
        self._timer = threading.Timer(network._wall_clock, self._expire)
        self._timer.daemon = True

    def _expire(self) -> None:
        self.fired.set()
        self._abort()

    def __enter__(self) -> "_Watch":
        with self._network._lock:
            self._network._active.add(self._abort)
        self._timer.start()
        return self

    def __exit__(self, *exc) -> None:
        self._timer.cancel()
        with self._network._lock:
            self._network._active.discard(self._abort)


class PassiveNetwork:
    """Probes one host through its already-verified addresses."""

    def __init__(
        self,
        host: str,
        addresses: Sequence[str],
        *,
        budget: RequestBudget | None = None,
        https_port: int = HTTPS_PORT,
        http_port: int = HTTP_PORT,
        timeout: float = REQUEST_TIMEOUT_SECONDS,
        ssl_context: ssl.SSLContext | None = None,
    ):
        self._host = host
        self._addresses = tuple(addresses)
        self.budget = budget or RequestBudget()
        self._https_port = https_port
        self._http_port = http_port
        self._timeout = timeout
        self._wall_clock = timeout * 2
        self._ssl_context = ssl_context
        # (address, port) pairs that refused or timed out while connecting. They
        # are skipped for the rest of the assessment so one unreachable address
        # cannot make every probe wait out its timeout again.
        self._dead: set[tuple[str, int]] = set()
        self._cancelled = threading.Event()
        self._lock = threading.Lock()
        self._active: set = set()

    @property
    def requests_sent(self) -> int:
        return self.budget.used

    def cancel(self) -> None:
        """Stop: break any exchange in flight and refuse to start another."""
        self._cancelled.set()
        with self._lock:
            active = list(self._active)
        for abort in active:
            abort()

    def _context(self) -> ssl.SSLContext:
        # Certificate and hostname verification stay on: a failure is a finding.
        if self._ssl_context is None:
            self._ssl_context = ssl.create_default_context()
        return self._ssl_context

    def _candidates(self, port: int) -> list[str]:
        return [a for a in self._addresses if (a, port) not in self._dead]

    def _failure_kind(self, exc: BaseException, watch: _Watch) -> str:
        if self._cancelled.is_set():
            return "cancelled"
        if watch.fired.is_set() or isinstance(exc, TimeoutError):
            return "timeout"
        if isinstance(exc, ConnectionRefusedError):
            return "connection_refused"
        return "connection_error"

    def tls_probe(self) -> TlsObservation:
        if self._cancelled.is_set():
            return TlsObservation(
                ok=False, error_kind="cancelled", error="The assessment deadline passed."
            )
        failures: list[TlsObservation] = []
        for address in self._candidates(self._https_port):
            sock = None
            try:
                sock = socket.create_connection(
                    (address, self._https_port), timeout=self._timeout
                )
                # wrap_socket detaches ``sock``; a duplicate keeps a handle that can
                # still break the connection while the handshake is in progress.
                handle = sock.dup()
            except OSError as exc:
                if sock is not None:
                    sock.close()
                kind = (
                    "timeout" if isinstance(exc, TimeoutError)
                    else "connection_refused" if isinstance(exc, ConnectionRefusedError)
                    else "connection_error"
                )
                if self._cancelled.is_set():
                    kind = "cancelled"
                failures.append(TlsObservation(ok=False, error_kind=kind, error=_clip(exc)))
                self._dead.add((address, self._https_port))
                continue
            watch = _Watch(self, lambda handle=handle: _abort(handle))
            try:
                with watch:
                    with self._context().wrap_socket(
                        sock, server_hostname=self._host
                    ) as tls:
                        version = tls.version()
                        cipher = tls.cipher()
                        certificate = _peer_certificate(tls)
                not_after = certificate.get("notAfter")
                return TlsObservation(
                    ok=True,
                    version=version,
                    cipher_name=cipher[0] if cipher else None,
                    cipher_bits=cipher[2] if cipher else None,
                    subject=_name(certificate.get("subject")),
                    issuer=_name(certificate.get("issuer")),
                    not_after=(
                        ssl.cert_time_to_seconds(not_after) if not_after else None
                    ),
                    san_count=len(certificate.get("subjectAltName", ())),
                )
            except ssl.SSLCertVerificationError as exc:
                detail = (
                    getattr(exc, "verify_message", None)
                    or getattr(exc, "reason", None)
                    or exc
                )
                return TlsObservation(
                    ok=False,
                    error_kind="cert_verify",
                    error=_clip(exc),
                    verify_message=str(detail)[:200],
                )
            except ssl.SSLError as exc:
                if watch.fired.is_set() or self._cancelled.is_set():
                    kind = self._failure_kind(exc, watch)
                elif _is_legacy_protocol_error(exc):
                    kind = "legacy_protocol"
                else:
                    kind = "handshake"
                return TlsObservation(ok=False, error_kind=kind, error=_clip(exc))
            except OSError as exc:
                # Connected, then the handshake itself failed: the address is fine.
                return TlsObservation(
                    ok=False, error_kind=self._failure_kind(exc, watch), error=_clip(exc)
                )
            finally:
                _abort(handle)
                sock.close()
        if failures:
            return _first_failure(failures)
        return TlsObservation(
            ok=False,
            error_kind="cancelled" if self._cancelled.is_set() else "connection_error",
            error="No reachable address remained for this assessment.",
        )

    def request(
        self,
        *,
        label: str,
        method: str,
        target: str,
        headers: Mapping[str, str] | None = None,
        tls: bool = True,
        read_body: bool = False,
    ) -> HttpObservation:
        method = method.upper()
        if method not in _SAFE_METHODS:
            raise ValueError(f"Only HEAD, GET and OPTIONS are permitted, not {method}.")
        if not target.startswith("/"):
            raise ValueError("The request target must be an absolute path.")
        extra = {name.lower(): value for name, value in (headers or {}).items()}
        if not set(extra) <= set(_ALLOWED_REQUEST_HEADERS):
            raise ValueError("Only fixed CORS preflight headers may be sent.")
        request_headers = {
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Encoding": "identity",
            **{_ALLOWED_REQUEST_HEADERS[name]: value for name, value in extra.items()},
        }
        scheme = "https" if tls else "http"
        port = self._https_port if tls else self._http_port
        started = time.perf_counter()

        def failed(kind: str, exc: BaseException | str) -> HttpObservation:
            return HttpObservation(
                label=label, method=method, target=target, scheme=scheme,
                elapsed_ms=(time.perf_counter() - started) * 1000,
                error_kind=kind,
                error=_clip(exc) if isinstance(exc, BaseException) else exc,
            )

        if self._cancelled.is_set():
            return failed("cancelled", "The assessment deadline passed.")
        self.budget.consume()

        failures: list[HttpObservation] = []
        for address in self._candidates(port):
            if self._cancelled.is_set():
                return failed("cancelled", "The assessment deadline passed.")
            if tls:
                connection = _PinnedHTTPSConnection(
                    self._host, address, port, self._timeout, self._context()
                )
            else:
                connection = _PinnedHTTPConnection(
                    self._host, address, port, self._timeout
                )
            watch = _Watch(self, lambda c=connection: _abort(c.sock))
            try:
                with watch:
                    connection.request(method, target, headers=request_headers)
                    response = connection.getresponse()
                    body = b""
                    if read_body and method != "HEAD":
                        # Read at most one small page; the rest is never fetched.
                        try:
                            body = response.read(MAX_RESPONSE_BYTES)
                        except http.client.IncompleteRead as partial:
                            body = partial.partial
                        except (OSError, http.client.HTTPException):
                            body = b""   # keep the status and headers already received
                    return HttpObservation(
                        label=label, method=method, target=target, scheme=scheme,
                        status=response.status,
                        headers=tuple(
                            (name.lower(), value)
                            for name, value in response.getheaders()
                        ),
                        body=body.decode("utf-8", errors="replace"),
                        elapsed_ms=(time.perf_counter() - started) * 1000,
                    )
            except ssl.SSLCertVerificationError as exc:
                return failed("tls_certificate", exc)
            except ssl.SSLError as exc:
                if watch.fired.is_set() or self._cancelled.is_set():
                    return failed(self._failure_kind(exc, watch), exc)
                return failed("tls_error", exc)
            except OSError as exc:
                result = failed(self._failure_kind(exc, watch), exc)
                if connection.sock is not None or self._cancelled.is_set():
                    return result   # connected, then the exchange failed
                failures.append(result)
                self._dead.add((address, port))
            except http.client.HTTPException as exc:
                return failed("protocol_error", exc)
            except (UnicodeError, ValueError) as exc:
                # e.g. a target that cannot be encoded for the request line
                return failed("invalid_request", exc)
            finally:
                connection.close()
        if failures:
            return _first_failure(failures)
        return failed(
            "cancelled" if self._cancelled.is_set() else "connection_error",
            "No reachable address remained for this assessment.",
        )


def days_until(timestamp: float | None, *, now: float | None = None) -> float | None:
    if timestamp is None:
        return None
    current = now if now is not None else datetime.now(timezone.utc).timestamp()
    return (timestamp - current) / 86400

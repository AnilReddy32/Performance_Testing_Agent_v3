"""Test harness: real local HTTPS/HTTP servers with generated certificates.

The passive assessment connects to addresses it was told to use, so a test can
point it at 127.0.0.1 while the certificate and Host name stay those of a public
name. Nothing here touches the network beyond the loopback interface.
"""

from __future__ import annotations

import datetime
import ipaddress
import socket
import ssl
import tempfile
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

HOSTNAME = "api.example.com"

HARDENED_HEADERS = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'none'; frame-ancestors 'none'",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "geolocation=()",
    "Cache-Control": "no-store",
    "Server": "srv",
}


def make_certificate(*, names=(HOSTNAME,), days_valid=90, expired=False):
    """Return (certificate_pem, private_key_pem) for a self-signed CA-style cert."""
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import NameOID

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, names[0])])
    now = datetime.datetime.now(datetime.timezone.utc)
    if expired:
        not_before, not_after = now - datetime.timedelta(days=60), now - datetime.timedelta(days=30)
    else:
        not_before, not_after = now - datetime.timedelta(days=1), now + datetime.timedelta(days=days_valid)
    san = [x509.DNSName(name) for name in names] + [
        x509.IPAddress(ipaddress.ip_address("127.0.0.1"))
    ]
    builder = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(x509.SubjectAlternativeName(san), critical=False)
        .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True, key_cert_sign=True, crl_sign=True,
                content_commitment=False, key_encipherment=True, data_encipherment=False,
                key_agreement=False, encipher_only=False, decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
    )
    certificate = builder.sign(key, hashes.SHA256())
    return (
        certificate.public_bytes(serialization.Encoding.PEM),
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        ),
    )


@pytest.fixture
def vanilla_ssl():
    """Run a test with the standard-library ssl module.

    The application injects the operating system's trust store into ``ssl``
    when its config module is imported (see Performance_Testing_Agent.config).
    That swaps ssl.SSLContext for a class that cannot act as a test server or
    trust a test certificate, so tests build their own contexts without it and
    put it back afterwards.
    """
    try:
        import truststore
    except ImportError:
        yield
        return
    injected = ssl.SSLContext.__module__.startswith("truststore")
    if injected:
        truststore.extract_from_ssl()
    try:
        yield
    finally:
        if injected:
            truststore.inject_into_ssl()


def client_context(certificate_pem: bytes) -> ssl.SSLContext:
    """A client that trusts exactly this certificate and still verifies the name."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cadata=certificate_pem.decode())
    return context


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "srv"
    sys_version = ""

    def log_message(self, *args):  # silence the test output
        pass

    def send_response(self, code, message=None):
        # No automatic Server header: each scenario sets exactly what it wants.
        self.send_response_only(code, message)
        self.send_header("Date", self.date_time_string())

    def _respond(self):
        server = self.server
        server.requests.append(
            {"method": self.command, "path": self.path, "headers": dict(self.headers)}
        )
        status, headers, body = server.router(self.command, self.path, self.headers)
        data = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)

    do_GET = do_HEAD = do_OPTIONS = do_POST = do_PUT = do_DELETE = _respond


class LocalServer:
    """A threaded HTTP or HTTPS server whose behaviour a test supplies."""

    def __init__(self, router, *, tls_material=None):
        self.requests: list[dict] = []
        self.errors: list[str] = []
        self._files = None
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.server.router = router
        self.server.requests = self.requests
        # Keep server-side faults for diagnosis instead of printing them.
        self.server.handle_error = lambda request, client_address: self.errors.append(
            traceback.format_exc()
        )
        if tls_material is not None:
            certificate_pem, key_pem = tls_material
            self._files = tempfile.TemporaryDirectory()
            cert_path = f"{self._files.name}/cert.pem"
            key_path = f"{self._files.name}/key.pem"
            open(cert_path, "wb").write(certificate_pem)
            open(key_path, "wb").write(key_pem)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_path, key_path)
            self.server.socket = context.wrap_socket(self.server.socket, server_side=True)
        self.port = self.server.server_address[1]
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()
        if self._files is not None:
            self._files.cleanup()


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def hardened_router(method, path, headers):
    """A well-configured API: strong headers, safe CORS, clean errors."""
    if path.endswith("/security-assessment-not-found"):
        return 404, {"Content-Type": "application/json", **HARDENED_HEADERS}, '{"error":"not found"}'
    if method == "OPTIONS":
        return 204, {"Allow": "GET, HEAD, OPTIONS", **HARDENED_HEADERS}, ""
    return 200, {"Content-Type": "application/json", **HARDENED_HEADERS}, "{}"


def weak_router(method, path, headers):
    """A sloppy API: no security headers, version leaks, reflected CORS, TRACE, stack traces."""
    leaks = {"Server": "Apache/2.4.41 (Ubuntu)", "X-Powered-By": "PHP/7.4.3"}
    if path.endswith("/security-assessment-not-found"):
        return 404, leaks, 'Traceback (most recent call last):\n  File "/srv/app/main.py", line 9, in handler'
    if method == "OPTIONS":
        return 200, {
            **leaks,
            "Allow": "GET, TRACE, OPTIONS",
            "Access-Control-Allow-Origin": headers.get("Origin", ""),
            "Access-Control-Allow-Credentials": "true",
        }, ""
    return 200, leaks, "{}"


def waf_router(method, path, headers):
    """A gateway that answers every request with 403 and a bare page."""
    return 403, {"Server": "cloudflare"}, "blocked"


def head_unsupported_router(method, path, headers):
    if method == "HEAD":
        return 405, {"Allow": "GET, OPTIONS"}, ""
    return hardened_router(method, path, headers)


def redirect_to_https(method, path, headers):
    return 301, {"Location": f"https://{HOSTNAME}{path}"}, ""


class RawTlsServer:
    """TLS server whose behaviour per connection is ``handler(conn, request_bytes)``.

    For hostile cases the normal HTTP server cannot produce: a response that
    drips forever, a truncated chunked body, a malformed reply.
    """

    def __init__(self, handler, tls_material, *, min_version=None, max_version=None):
        self.handler = handler
        self.requests: list[bytes] = []
        self._files = tempfile.TemporaryDirectory()
        certificate_pem, key_pem = tls_material
        open(f"{self._files.name}/c.pem", "wb").write(certificate_pem)
        open(f"{self._files.name}/k.pem", "wb").write(key_pem)
        self._context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        if min_version is not None:        # e.g. a TLS 1.0/1.1-only server
            self._context.set_ciphers("ALL:@SECLEVEL=0")
            self._context.minimum_version = min_version
            self._context.maximum_version = max_version
        self._context.load_cert_chain(f"{self._files.name}/c.pem", f"{self._files.name}/k.pem")
        self._listener = socket.socket()
        self._listener.bind(("127.0.0.1", 0))
        self._listener.listen(16)
        self.port = self._listener.getsockname()[1]
        self._alive = True
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while self._alive:
            try:
                connection, _ = self._listener.accept()
            except OSError:
                return
            threading.Thread(target=self._serve, args=(connection,), daemon=True).start()

    def _serve(self, connection):
        try:
            connection = self._context.wrap_socket(connection, server_side=True)
            connection.settimeout(30)
            data = b""
            while b"\r\n\r\n" not in data:
                chunk = connection.recv(4096)
                if not chunk:
                    return
                data += chunk
            self.requests.append(data)
            self.handler(connection, data)
        except Exception:
            pass
        finally:
            try:
                connection.close()
            except Exception:
                pass

    def close(self):
        self._alive = False
        self._listener.close()
        self._files.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

"""The security agent's own scope rules for passive assessment.

These do not depend on the load-test host allowlist. A target is accepted when
it is a public HTTPS origin: no credentials, no IP literal, port 443 only, and
every address it resolves to is globally routable. The target always comes from
the job's trusted workload profile, never from prose.
"""

from __future__ import annotations

import ipaddress
import re
import socket
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote, urlsplit

from security_agent.live_testing.scope import _normalized_path
from security_agent.passive.config import (
    HTTPS_PORT,
    MAX_ENDPOINT_LENGTH,
    MAX_RESOLVED_ADDRESSES,
)

_ALLOWED_METHODS = {"GET", "HEAD", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"}
_NON_PUBLIC_SUFFIXES = (
    ".localhost", ".local", ".internal", ".intranet", ".lan", ".home",
    ".corp", ".home.arpa", ".test", ".invalid", ".example", ".onion",
)
EXTERNAL_ENVIRONMENT = "external_api"
_REQUEST_SAFE = "/?&=%:@!$'()*+,;-._~[]"


class TargetRejected(Exception):
    """The target is outside the passive scope; no request was or will be sent."""

    def __init__(self, code: str, reason: str):
        super().__init__(reason)
        self.code = code
        self.reason = reason


@dataclass(frozen=True)
class PassiveTarget:
    host: str
    origin: str
    request_target: str  # path plus query, exactly as in the trusted profile
    path: str
    method: str
    environment: str
    environment_inferred: bool
    addresses: tuple[str, ...]


_DNS_NAME = re.compile(
    r"[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?"
    r"(?:\.[a-z0-9_](?:[a-z0-9_-]{0,61}[a-z0-9_])?)*"
)


def _ascii_hostname(host: str) -> str | None:
    """The host as a plain ASCII DNS name (international names as punycode).

    Anything else (a percent sign, spaces, control characters, empty labels)
    is not a host name and must never reach a Host header, SNI or a resolver.
    """
    try:
        ascii_host = host.encode("idna").decode("ascii").lower()
    except UnicodeError:
        return None
    return ascii_host if len(ascii_host) <= 253 and _DNS_NAME.fullmatch(ascii_host) else None


def _public_hostname(host: str) -> bool:
    if "." not in host or host.endswith("."):
        return False
    return not host.endswith(_NON_PUBLIC_SUFFIXES)


# Internal addresses that look "global" to the standard library.
_EXTRA_NON_PUBLIC = (
    ipaddress.ip_network("168.63.129.16/32"),   # Azure platform/metadata service
    ipaddress.ip_network("fec0::/10"),          # deprecated IPv6 site-local
)
# IPv6 forms that carry an IPv4 address in their low 32 bits (or, for 6to4, bits
# 16-47). A name that resolves to one of these must be judged by that IPv4.
_EMBEDDED_IPV4_PREFIXES = tuple(
    ipaddress.ip_network(prefix)
    for prefix in (
        "::ffff:0:0/96",       # IPv4-mapped
        "::ffff:0:0:0/96",     # IPv4-translated (SIIT)
        "64:ff9b::/96",        # NAT64 well-known prefix
        "::/96",               # deprecated IPv4-compatible
    )
)


def _embedded_ipv4(parsed: ipaddress.IPv6Address) -> ipaddress.IPv4Address | None:
    if parsed.ipv4_mapped is not None:
        return parsed.ipv4_mapped
    if parsed in ipaddress.ip_network("2002::/16"):          # 6to4
        return ipaddress.IPv4Address((int(parsed) >> 80) & 0xFFFFFFFF)
    if parsed in _EMBEDDED_IPV4_PREFIXES[3] and int(parsed) > 1:
        return ipaddress.IPv4Address(int(parsed) & 0xFFFFFFFF)
    if any(parsed in prefix for prefix in _EMBEDDED_IPV4_PREFIXES[1:3]):
        return ipaddress.IPv4Address(int(parsed) & 0xFFFFFFFF)
    return None


def _is_global(address: str) -> bool:
    try:
        parsed = ipaddress.ip_address(address.split("%", 1)[0])
    except ValueError:
        return False
    if any(parsed in network for network in _EXTRA_NON_PUBLIC if network.version == parsed.version):
        return False
    if isinstance(parsed, ipaddress.IPv6Address):
        embedded = _embedded_ipv4(parsed)
        if embedded is not None:
            return _is_global(str(embedded))
    return parsed.is_global


def looks_like_external_https_target(profile: Mapping[str, Any] | None) -> bool:
    """Cheap, network-free test used to decide whether to assess a run at all.

    A declared environment of external_api qualifies; a missing environment is
    inferred from the URL. Any other declared environment (for example a local
    mock) does not. The authoritative checks, including DNS, run later.
    """
    if not isinstance(profile, Mapping):
        return False
    environment = profile.get("environment")
    if isinstance(environment, str) and environment.strip():
        if environment.strip() != EXTERNAL_ENVIRONMENT:
            return False
    target_url = profile.get("target_url")
    if not isinstance(target_url, str) or not target_url.strip():
        return False
    try:
        parsed = urlsplit(target_url.strip())
        host = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError:
        return False
    if parsed.scheme != "https" or not host or port not in (None, HTTPS_PORT):
        return False
    if parsed.username or parsed.password or parsed.path not in {"", "/"} or parsed.query:
        return False
    try:
        ipaddress.ip_address(host)
    except ValueError:
        ascii_host = _ascii_hostname(host)
        return ascii_host is not None and _public_hostname(ascii_host)
    return False


def default_resolver(host: str, port: int) -> list[str]:
    """Resolve once; IPv4 first because it is the most widely reachable."""
    infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    addresses = list(dict.fromkeys(info[4][0] for info in infos))
    addresses.sort(key=lambda address: ":" in address)
    return addresses


def resolve_target(
    profile: Mapping[str, Any] | None,
    *,
    resolver: Callable[[str, int], list[str]] = default_resolver,
) -> PassiveTarget:
    """Validate the trusted profile's target or raise TargetRejected."""
    if not isinstance(profile, Mapping):
        raise TargetRejected("no_target", "The job has no trusted workload profile.")
    target_url = profile.get("target_url")
    endpoint = profile.get("endpoint")
    if not isinstance(target_url, str) or not target_url.strip():
        raise TargetRejected("no_target", "The workload profile has no target URL.")
    if not isinstance(endpoint, str) or not endpoint.strip():
        raise TargetRejected("no_target", "The workload profile has no endpoint.")

    try:
        origin = urlsplit(target_url.strip())
        host = (origin.hostname or "").lower()
        port = origin.port
    except ValueError:
        raise TargetRejected("invalid_target", "The target URL is not valid.") from None
    if origin.scheme != "https":
        raise TargetRejected("not_https", "Passive assessment requires an HTTPS target.")
    if not host:
        raise TargetRejected("invalid_target", "The target URL has no host.")
    if origin.username or origin.password:
        raise TargetRejected(
            "credentials_in_url", "The target URL must not contain credentials."
        )
    if port not in (None, HTTPS_PORT):
        raise TargetRejected(
            "non_standard_port", f"Only port {HTTPS_PORT} is in scope, not {port}."
        )
    if origin.path not in {"", "/"} or origin.query or origin.fragment:
        raise TargetRejected(
            "invalid_target", "The target URL must be a bare origin."
        )
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise TargetRejected(
            "ip_literal", "The target must be a DNS hostname, not an IP address."
        )
    ascii_host = _ascii_hostname(host)
    if ascii_host is None:
        raise TargetRejected(
            "invalid_target", "The target host is not a valid DNS name."
        )
    host = ascii_host
    if not _public_hostname(host):
        raise TargetRejected(
            "non_public_host", f"'{host}' is not a public DNS hostname."
        )

    endpoint_parts = urlsplit(endpoint.strip())
    if (
        endpoint_parts.scheme
        or endpoint_parts.netloc
        or endpoint_parts.fragment
        or not endpoint_parts.path.startswith("/")
        or len(endpoint) > MAX_ENDPOINT_LENGTH
        or _normalized_path(endpoint_parts.path) is None
    ):
        raise TargetRejected(
            "invalid_endpoint",
            "The endpoint must be an absolute path without a host or fragment.",
        )
    # A request line is ASCII; a path like "/café" must go out percent-encoded
    # (existing %XX escapes are kept as they are).
    path = quote(endpoint_parts.path, safe=_REQUEST_SAFE)
    request_target = path + (
        f"?{quote(endpoint_parts.query, safe=_REQUEST_SAFE)}" if endpoint_parts.query else ""
    )

    try:
        addresses = resolver(host, HTTPS_PORT)
    except OSError as exc:
        raise TargetRejected(
            "dns_failure", f"'{host}' did not resolve: {type(exc).__name__}."
        ) from None
    if not addresses:
        raise TargetRejected("dns_failure", f"'{host}' resolved to no addresses.")
    # Every address must be public, because a hostname that also points at an
    # internal address could redirect a probe into the private network.
    if not all(_is_global(address) for address in addresses):
        raise TargetRejected(
            "non_public_address", f"'{host}' resolves to a non-public address."
        )

    method = str(profile.get("method") or "GET").strip().upper()
    if method not in _ALLOWED_METHODS:
        method = "GET"
    declared = profile.get("environment")
    inferred = not (isinstance(declared, str) and declared.strip())
    return PassiveTarget(
        host=host,
        origin=f"https://{host}",
        request_target=request_target,
        path=path,
        method=method,
        environment=EXTERNAL_ENVIRONMENT if inferred else declared.strip(),
        environment_inferred=inferred,
        addresses=tuple(addresses[:MAX_RESOLVED_ADDRESSES]),
    )

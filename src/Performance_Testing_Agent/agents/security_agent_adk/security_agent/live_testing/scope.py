"""Strict target, origin, port, and path validation for live checks."""

from urllib.parse import unquote, urlsplit, urlunsplit

from security_agent.live_testing.models import LiveTestScope, LiveTestTarget


def _normalized_path(value: str) -> str | None:
    if not value.startswith("/") or "\\" in value or any(ord(ch) < 32 for ch in value):
        return None
    lowered = value.lower()
    if "%2f" in lowered or "%5c" in lowered:
        return None
    decoded = unquote(value)
    # Reject nested escapes so a downstream proxy cannot decode the path into
    # a different route after this check.
    if (
        "%" in decoded
        or "\\" in decoded
        or any(ord(ch) < 32 for ch in decoded)
        or any(part in {".", ".."} for part in decoded.split("/"))
    ):
        return None
    return decoded.rstrip("/") or "/"


def _effective_port(parsed) -> int | None:
    try:
        return parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    except ValueError:
        return None


def _base_url_parts(base_url: str):
    parsed = urlsplit(base_url)
    if (
        parsed.scheme.lower() not in {"http", "https"}
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        return None
    if _effective_port(parsed) is None:
        return None
    return parsed


def validate_test_scope(
    target: LiveTestTarget,
    scope: LiveTestScope,
) -> dict:
    """Check that the trusted scope explicitly authorizes this exact target."""
    if not scope.authorized:
        return {"allowed": False, "reason": "Live testing has not been explicitly authorized."}
    if not scope.allowed_hosts:
        return {"allowed": False, "reason": "The live-test host allowlist is empty."}
    if not scope.allowed_paths:
        return {"allowed": False, "reason": "The live-test permitted-path list is empty."}
    if not scope.allowed_ports:
        return {"allowed": False, "reason": "The live-test permitted-port list is empty."}

    base = _base_url_parts(target.base_url)
    if base is None:
        return {
            "allowed": False,
            "reason": "Target must be a clean HTTP(S) origin without credentials, path, query, or fragment.",
        }
    host = base.hostname.lower().rstrip(".")
    allowed_hosts = {
        item.strip().lower().rstrip(".")
        for item in scope.allowed_hosts
        if isinstance(item, str) and item.strip()
    }
    if host not in allowed_hosts:
        return {"allowed": False, "reason": f"Target host '{host}' is outside the authorized scope."}

    port = _effective_port(base)
    if port not in scope.allowed_ports:
        return {"allowed": False, "reason": f"Target port {port} is outside the authorized port scope."}

    if target.environment and target.environment.casefold() != scope.environment.casefold():
        return {"allowed": False, "reason": "Target environment does not match the authorized live-test scope."}

    endpoint = urlsplit(target.endpoint)
    if endpoint.fragment or endpoint.scheme or endpoint.netloc:
        return {"allowed": False, "reason": "Live-test endpoint must be a relative path without a fragment or URL authority."}
    normalized_endpoint = _normalized_path(endpoint.path)
    if normalized_endpoint is None:
        return {"allowed": False, "reason": "Live-test endpoint contains an unsafe or non-canonical path."}

    normalized_allowed_paths = {
        normalized
        for path in scope.allowed_paths
        if isinstance(path, str)
        for normalized in [_normalized_path(path)]
        if normalized is not None
    }
    if normalized_endpoint not in normalized_allowed_paths:
        return {
            "allowed": False,
            "reason": f"Target endpoint '{normalized_endpoint}' is outside the authorized path scope.",
        }

    return {"allowed": True, "reason": "Target origin, port, environment, and exact trusted path are in the authorized scope."}


def build_target_url(target: LiveTestTarget) -> str:
    """Build a request URL from a validated origin and an exact path."""
    parsed = _base_url_parts(target.base_url)
    if parsed is None:
        raise ValueError("Cannot build a live-test URL from an invalid target origin.")
    endpoint = urlsplit(target.endpoint)
    path = _normalized_path(endpoint.path)
    if path is None:
        raise ValueError("Cannot build a live-test URL from an unsafe endpoint path.")
    netloc = parsed.netloc.lower()
    return urlunsplit((parsed.scheme.lower(), netloc, path, endpoint.query, ""))


def validate_request_matches_target(
    target: LiveTestTarget,
    request_url: str,
) -> dict:
    """Ensure the actual request URL stays on the exact approved origin and path."""
    try:
        expected = urlsplit(build_target_url(target))
        actual = urlsplit(request_url)
    except (ValueError, TypeError):
        return {"allowed": False, "reason": "Request URL is invalid."}

    if (
        actual.scheme.lower() != expected.scheme.lower()
        or not actual.hostname
        or actual.username
        or actual.password
        or actual.fragment
        or actual.query != expected.query
    ):
        return {"allowed": False, "reason": "Request URL is not the exact authorized URL."}
    if (
        actual.hostname.lower().rstrip(".") != expected.hostname.lower().rstrip(".")
        or _effective_port(actual) != _effective_port(expected)
    ):
        return {"allowed": False, "reason": "Request URL origin or port does not match the authorized target."}
    if _normalized_path(actual.path) != _normalized_path(expected.path):
        return {"allowed": False, "reason": "Request URL path does not match the authorized target."}
    return {"allowed": True, "reason": "Request URL matches the exact authorized origin, path, and query."}

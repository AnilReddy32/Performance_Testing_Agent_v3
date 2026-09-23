from urllib.parse import urlparse

from security_agent.live_testing.models import LiveTestTarget, LiveTestScope
    

def validate_test_scope(
    target: LiveTestTarget,
    scope: LiveTestScope,
) -> dict:
    """
    Validate that a live-test target is explicitly authorized.

    This function performs authorization-scope validation only.
    It does not make any network requests.
    """

    if not scope.authorized:
        return {
            "allowed": False,
            "reason": "Live testing has not been explicitly authorized.",
        }

    parsed_url = urlparse(target.base_url)

    if parsed_url.scheme not in {"http", "https"}:
        return {
            "allowed": False,
            "reason": "Target URL must use HTTP or HTTPS.",
        }

    if not parsed_url.hostname:
        return {
            "allowed": False,
            "reason": "Target URL does not contain a valid hostname.",
        }

    hostname = parsed_url.hostname.lower()

    allowed_hosts = {
        host.strip().lower()
        for host in scope.allowed_hosts
        if host.strip()
    }

    if hostname not in allowed_hosts:
        return {
            "allowed": False,
            "reason": f"Target host '{hostname}' is outside the authorized scope.",
        }

    if scope.allowed_paths:
        normalized_endpoint = target.endpoint.split("?", 1)[0].rstrip("/") or "/"

        normalized_paths = {
            path.rstrip("/") or "/"
            for path in scope.allowed_paths
            if path.strip()
        }

        if normalized_endpoint not in normalized_paths:
            return {
                "allowed": False,
                "reason": (
                    f"Target endpoint '{normalized_endpoint}' "
                    "is outside the authorized path scope."
                ),
            }

    return {
        "allowed": True,
        "reason": "Target is within the authorized live-testing scope.",
    }

def build_target_url(target: LiveTestTarget) -> str:
    """Build the canonical URL represented by the authorized target."""

    base = target.base_url.rstrip("/")
    endpoint = target.endpoint

    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"

    return f"{base}{endpoint}"


def validate_request_matches_target(
    target: LiveTestTarget,
    request_url: str,
) -> dict:
    """Ensure the executable request matches the authorized target."""

    expected_url = build_target_url(target)

    expected = urlparse(expected_url)
    actual = urlparse(request_url)

    if expected.scheme != actual.scheme:
        return {
            "allowed": False,
            "reason": "Request URL scheme does not match the authorized target.",
        }

    if (expected.hostname or "").lower() != (actual.hostname or "").lower():
        return {
            "allowed": False,
            "reason": "Request URL host does not match the authorized target.",
        }

    expected_path = expected.path.rstrip("/") or "/"
    actual_path = actual.path.rstrip("/") or "/"

    if expected_path != actual_path:
        return {
            "allowed": False,
            "reason": "Request URL path does not match the authorized target.",
        }

    return {
        "allowed": True,
        "reason": "Request URL matches the authorized target.",
    }
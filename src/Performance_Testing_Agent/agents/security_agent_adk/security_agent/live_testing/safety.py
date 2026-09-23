from security_agent.live_testing.models import LiveTestPolicy, LiveTestTarget


STATE_CHANGING_METHODS = {
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
}

SAFE_METHODS = {
    "GET",
    "HEAD",
    "OPTIONS",
}


def validate_test_safety(
    target: LiveTestTarget,
    policy: LiveTestPolicy,
    requested_requests: int,
    destructive_test: bool = False,
) -> dict:
    """
    Validate whether a live security test is permitted by the safety policy.

    This function performs policy validation only.
    It does not make any network requests.
    """

    if requested_requests <= 0:
        return {
            "allowed": False,
            "reason": "Requested request count must be greater than zero.",
        }

    if requested_requests > policy.max_requests:
        return {
            "allowed": False,
            "reason": (
                f"Requested {requested_requests} requests exceeds the "
                f"maximum allowed limit of {policy.max_requests}."
            ),
        }

    method = target.method.upper()

    if method not in SAFE_METHODS and method not in STATE_CHANGING_METHODS:
        return {
            "allowed": False,
            "reason": f"HTTP method '{method}' is not supported by the safety policy.",
        }

    if method in STATE_CHANGING_METHODS:
        if not policy.allow_state_changing_requests:
            return {
                "allowed": False,
                "reason": (
                    f"State-changing HTTP method '{method}' is not permitted "
                    "by the current safety policy."
                ),
            }

    if destructive_test and not policy.allow_destructive_tests:
        return {
            "allowed": False,
            "reason": "Destructive security tests are not permitted by the current safety policy.",
        }

    return {
        "allowed": True,
        "reason": "Live test complies with the configured safety policy.",
    }
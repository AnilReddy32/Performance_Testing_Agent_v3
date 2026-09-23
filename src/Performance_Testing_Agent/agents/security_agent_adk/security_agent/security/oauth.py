from typing import Any


def validate_oauth(
    oauth: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate OAuth security configuration.

    This validator evaluates OAuth configuration evidence.
    It does not perform live OAuth protocol testing.
    """

    if not isinstance(oauth, dict):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "OAuth configuration is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid OAuth configuration."
            ],
        }

    if not oauth.get("enabled"):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "OAuth is not enabled for the application."
            ],
            "recommendations": [
                "Enable OAuth configuration if OAuth authentication "
                "is required."
            ],
        }

    required_fields = {
        "provider": "OAuth provider is not configured.",
        "flow": "OAuth authorization flow is not configured.",
        "token_endpoint_auth_method": (
            "OAuth token endpoint authentication method is not configured."
        ),
    }

    issues: list[str] = []
    recommendations: list[str] = []

    for field, message in required_fields.items():
        value = oauth.get(field)

        if not isinstance(value, str) or not value.strip():
            issues.append(message)
            recommendations.append(
                f"Configure the OAuth '{field}' setting."
            )

    boolean_controls = {
        "redirect_uri_validation": (
            "OAuth redirect URI validation is not enabled."
        ),
        "state_parameter_validation": (
            "OAuth state parameter validation is not enabled."
        ),
        "scope_validation": (
            "OAuth scope validation is not enabled."
        ),
        "pkce_enabled": (
            "OAuth PKCE protection is not enabled."
        ),
    }

    for field, message in boolean_controls.items():
        if oauth.get(field) is not True:
            issues.append(message)
            recommendations.append(
                f"Enable OAuth '{field}'."
            )

    if issues:
        return {
            "status": "FAIL",
            "security_score": "0%",
            "issues": issues,
            "recommendations": recommendations,
        }

    return {
        "status": "PASS",
        "security_score": "100%",
        "issues": [],
        "recommendations": [],
    }
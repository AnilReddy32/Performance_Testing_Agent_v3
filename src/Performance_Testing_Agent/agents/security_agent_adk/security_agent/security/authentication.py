from typing import Any


def validate_authentication(
    authentication: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the application's authentication configuration.

    This function performs deterministic validation based on the
    authentication evidence provided to it.

    Args:
        authentication: Authentication configuration retrieved from
            the application profile.

    Returns:
        Structured authentication assessment.
    """

    if not isinstance(authentication, dict):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "Authentication configuration is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid authentication configuration."
            ],
        }

    if not authentication.get("enabled"):
        return {
            "status": "FAIL",
            "security_score": "0%",
            "issues": [
                "Application authentication is disabled."
            ],
            "recommendations": [
                "Enable authentication for protected application resources."
            ],
        }

    authentication_type = authentication.get("type")

    if not authentication_type:
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "Authentication is enabled, but the authentication type "
                "could not be determined."
            ],
            "recommendations": [
                "Provide the configured authentication mechanism."
            ],
        }

    return {
        "status": "PASS",
        "security_score": "100%",
        "issues": [],
        "recommendations": [],
    }
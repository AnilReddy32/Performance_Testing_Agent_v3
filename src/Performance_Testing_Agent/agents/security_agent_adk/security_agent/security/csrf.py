from typing import Any


def validate_csrf(
    csrf_security: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate CSRF protection configuration.

    This validator evaluates configuration evidence for CSRF
    protection. It does not perform live CSRF attack testing.

    Args:
        csrf_security: CSRF security configuration.

    Returns:
        A dictionary containing status, security score, issues,
        and recommendations.
    """

    if not isinstance(csrf_security, dict):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "CSRF security configuration is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid CSRF security configuration."
            ],
        }

    issues: list[str] = []
    recommendations: list[str] = []

    if csrf_security.get("protection_enabled") is not True:
        issues.append(
            "CSRF protection is not enabled."
        )
        recommendations.append(
            "Enable CSRF protection for state-changing requests."
        )

    if csrf_security.get("csrf_token_validation") is not True:
        issues.append(
            "CSRF token validation is not enabled."
        )
        recommendations.append(
            "Validate CSRF tokens for protected state-changing requests."
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
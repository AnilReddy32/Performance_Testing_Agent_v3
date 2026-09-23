from typing import Any


def validate_jwt(
    authentication: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate JWT security configuration.

    The function evaluates JWT-related configuration using the
    evidence supplied by the application profile.

    Args:
        authentication: Authentication configuration containing
            JWT security settings.

    Returns:
        Structured JWT security assessment.
    """

    if not isinstance(authentication, dict):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "Authentication configuration is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid JWT authentication configuration."
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
                "Enable authentication before relying on JWT-based access control."
            ],
        }

    if authentication.get("type") != "JWT":
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "The configured authentication mechanism is not JWT."
            ],
            "recommendations": [
                "Provide JWT configuration if JWT validation is required."
            ],
        }

    jwt_config = authentication.get("jwt")

    if not isinstance(jwt_config, dict):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "JWT security configuration is unavailable."
            ],
            "recommendations": [
                "Provide the application's JWT validation configuration."
            ],
        }

    checks = {
        "signature_validation": "JWT signature validation is not enabled.",
        "expiration_validation": "JWT expiration validation is not enabled.",
        "issuer_validation": "JWT issuer validation is not enabled.",
        "audience_validation": "JWT audience validation is not enabled.",
        "algorithm_validation": "JWT algorithm validation is not enabled.",
    }

    issues: list[str] = []
    recommendations: list[str] = []

    for field, message in checks.items():
        if jwt_config.get(field) is not True:
            issues.append(message)

    if not jwt_config.get("allowed_algorithms"):
        issues.append(
            "No explicitly allowed JWT signing algorithms are configured."
        )

    if issues:
        for issue in issues:
            recommendations.append(
                f"Address the JWT configuration issue: {issue}"
            )

        score = max(
            0,
            round(
                (
                    (
                        len(checks)
                        + 1
                        - len(issues)
                    )
                    / (len(checks) + 1)
                )
                * 100
            ),
        )

        return {
            "status": "FAIL",
            "security_score": f"{score}%",
            "issues": issues,
            "recommendations": recommendations,
        }

    return {
        "status": "PASS",
        "security_score": "100%",
        "issues": [],
        "recommendations": [],
    }
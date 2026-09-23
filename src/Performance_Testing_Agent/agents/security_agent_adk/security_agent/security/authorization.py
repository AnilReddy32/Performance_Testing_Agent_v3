from typing import Any


def validate_rbac(
    authorization: dict[str, Any],
    endpoints: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Validate Role-Based Access Control configuration.

    Args:
        authorization: Application authorization configuration.
        endpoints: Optional API endpoint configuration used to validate
            endpoint-level authorization requirements.

    Returns:
        Structured RBAC security assessment.
    """

    if not isinstance(authorization, dict):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "Authorization configuration is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid authorization configuration."
            ],
        }

    if not authorization.get("enabled"):
        return {
            "status": "FAIL",
            "security_score": "0%",
            "issues": [
                "Application authorization is disabled."
            ],
            "recommendations": [
                "Enable authorization for protected resources."
            ],
        }

    if authorization.get("type") != "RBAC":
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "The configured authorization mechanism is not RBAC."
            ],
            "recommendations": [
                "Provide RBAC configuration if RBAC validation is required."
            ],
        }

    roles = authorization.get("roles")

    if not isinstance(roles, list) or not roles:
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "No RBAC roles are configured."
            ],
            "recommendations": [
                "Define the application's roles and associated permissions."
            ],
        }

    issues: list[str] = []
    recommendations: list[str] = []

    if authorization.get("role_permission_validation") is not True:
        issues.append(
            "Role-permission validation is not enabled."
        )
        recommendations.append(
            "Enable validation of role-to-permission mappings."
        )

    if endpoints is not None:
        if not isinstance(endpoints, list):
            return {
                "status": "WARNING",
                "security_score": "N/A",
                "issues": [
                    "API endpoint authorization data is invalid."
                ],
                "recommendations": [
                    "Provide valid endpoint authorization configuration."
                ],
            }

        for endpoint in endpoints:
            if not isinstance(endpoint, dict):
                continue

            if endpoint.get("authorization_required") is True:
                allowed_roles = endpoint.get("allowed_roles")

                if not isinstance(allowed_roles, list) or not allowed_roles:
                    path = endpoint.get("path", "unknown endpoint")

                    issues.append(
                        f"Protected endpoint '{path}' does not define "
                        "allowed roles."
                    )

                    recommendations.append(
                        f"Define allowed roles for protected endpoint "
                        f"'{path}'."
                    )

    if issues:
        score = max(
            0,
            round(
                max(
                    0,
                    100 - (len(issues) * 20)
                )
            )
        )

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
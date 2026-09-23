from typing import Any


def validate_api_security(
    endpoints: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Validate API endpoint security configuration.

    This validator evaluates API security configuration evidence.
    It does not perform live HTTP requests or vulnerability testing.

    Args:
        endpoints: List of API endpoint configuration dictionaries.

    Returns:
        A dictionary containing status, security score, issues,
        and recommendations.
    """

    if not isinstance(endpoints, list) or not endpoints:
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "API endpoint security information is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid API endpoint security configuration."
            ],
        }

    issues: list[str] = []
    recommendations: list[str] = []

    for endpoint in endpoints:

        if not isinstance(endpoint, dict):
            issues.append(
                "An API endpoint contains invalid configuration."
            )
            recommendations.append(
                "Ensure every API endpoint has a valid configuration."
            )
            continue

        path = endpoint.get("path")
        method = endpoint.get("method")

        endpoint_name = (
            f"{method} {path}"
            if method and path
            else "Unknown API endpoint"
        )

        # Validate endpoint identity
        if not path:
            issues.append(
                f"{endpoint_name} does not define an endpoint path."
            )
            recommendations.append(
                "Define a valid path for every API endpoint."
            )

        if not method:
            issues.append(
                f"{endpoint_name} does not define an HTTP method."
            )
            recommendations.append(
                "Define an HTTP method for every API endpoint."
            )

        # Authentication requirement
        authentication_required = endpoint.get(
            "authentication_required"
        )

        if authentication_required is None:
            issues.append(
                f"{endpoint_name} does not specify whether authentication is required."
            )
            recommendations.append(
                f"Explicitly define authentication requirements for {endpoint_name}."
            )

        # Authorization consistency
        authorization_required = endpoint.get(
            "authorization_required"
        )

        if authorization_required is True:
            allowed_roles = endpoint.get("allowed_roles")

            if not isinstance(allowed_roles, list) or not allowed_roles:
                issues.append(
                    f"{endpoint_name} requires authorization but does not define allowed roles."
                )
                recommendations.append(
                    f"Define allowed roles for authorized endpoint {endpoint_name}."
                )

        # Authorization should not be configured without authentication
        if (
            authorization_required is True
            and authentication_required is False
        ):
            issues.append(
                f"{endpoint_name} requires authorization while authentication is disabled."
            )
            recommendations.append(
                f"Require authentication before authorization for {endpoint_name}."
            )

        # If authentication is required, the endpoint should explicitly
        # declare its authorization posture.
        if (
            authentication_required is True
            and "authorization_required" not in endpoint
        ):
            issues.append(
                f"{endpoint_name} requires authentication but does not specify its authorization requirement."
            )
            recommendations.append(
                f"Explicitly define authorization requirements for {endpoint_name}."
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
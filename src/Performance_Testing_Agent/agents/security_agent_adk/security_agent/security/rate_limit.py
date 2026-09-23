from typing import Any


def validate_rate_limiting(
    endpoints: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Validate API rate-limiting configuration.

    This validator evaluates rate-limiting configuration evidence
    for API endpoints. It does not perform live traffic generation
    or verify actual runtime enforcement.

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
                "API endpoint information is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid API endpoint information for rate-limit assessment."
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

        rate_limit = endpoint.get("rate_limit")

        # No rate-limit configuration
        if rate_limit is None:
            issues.append(
                f"{endpoint_name} does not have rate-limiting configuration."
            )
            recommendations.append(
                f"Configure rate limiting for {endpoint_name}."
            )
            continue

        # Invalid rate-limit structure
        if not isinstance(rate_limit, dict):
            issues.append(
                f"{endpoint_name} has invalid rate-limiting configuration."
            )
            recommendations.append(
                f"Provide valid rate-limiting configuration for {endpoint_name}."
            )
            continue

        # Rate limiting disabled
        if rate_limit.get("enabled") is not True:
            issues.append(
                f"Rate limiting is disabled for {endpoint_name}."
            )
            recommendations.append(
                f"Enable rate limiting for {endpoint_name}."
            )
            continue

        # Requests-per-minute validation
        requests_per_minute = rate_limit.get(
            "requests_per_minute"
        )

        if requests_per_minute is None:
            issues.append(
                f"{endpoint_name} does not define a requests-per-minute limit."
            )
            recommendations.append(
                f"Define a requests-per-minute limit for {endpoint_name}."
            )
            continue

        if (
            isinstance(requests_per_minute, bool)
            or not isinstance(requests_per_minute, (int, float))
            or requests_per_minute <= 0
        ):
            issues.append(
                f"{endpoint_name} has an invalid requests-per-minute limit."
            )
            recommendations.append(
                f"Configure a positive requests-per-minute limit for {endpoint_name}."
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
from typing import Any


def validate_xss(
    xss_security: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate XSS prevention configuration.

    This validator evaluates configuration evidence for XSS
    prevention. It does not perform live XSS payload testing.

    Args:
        xss_security: XSS security configuration.

    Returns:
        A dictionary containing status, security score, issues,
        and recommendations.
    """

    if not isinstance(xss_security, dict):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "XSS security configuration is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid XSS security configuration."
            ],
        }

    issues: list[str] = []
    recommendations: list[str] = []

    # Input sanitization
    if xss_security.get("input_sanitization") is not True:
        issues.append(
            "Input sanitization is not enabled."
        )
        recommendations.append(
            "Sanitize untrusted input before processing or rendering it."
        )

    # Output encoding
    if xss_security.get("output_encoding") is not True:
        issues.append(
            "Output encoding is not enabled."
        )
        recommendations.append(
            "Apply context-appropriate output encoding when rendering untrusted data."
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
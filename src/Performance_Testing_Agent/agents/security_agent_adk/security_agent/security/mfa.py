from typing import Any


def validate_mfa(
    mfa: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate MFA security configuration.

    This validator evaluates MFA configuration evidence.
    It does not perform live MFA enrollment or authentication testing.
    """

    if not isinstance(mfa, dict):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "MFA configuration is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid MFA configuration."
            ],
        }

    if not mfa.get("enabled"):
        return {
            "status": "FAIL",
            "security_score": "0%",
            "issues": [
                "Multi-factor authentication is disabled."
            ],
            "recommendations": [
                "Enable MFA for accounts and resources requiring "
                "strong authentication."
            ],
        }

    issues: list[str] = []
    recommendations: list[str] = []

    methods = mfa.get("methods")

    if not isinstance(methods, list) or not methods:
        issues.append(
            "No MFA authentication method is configured."
        )
        recommendations.append(
            "Configure at least one approved MFA authentication method."
        )

    if mfa.get("enforcement_enabled") is not True:
        issues.append(
            "MFA enforcement is not enabled."
        )
        recommendations.append(
            "Enable MFA enforcement for users and resources within scope."
        )

    if mfa.get("required_for_admin") is not True:
        issues.append(
            "MFA is not required for administrative accounts."
        )
        recommendations.append(
            "Require MFA for administrative and privileged accounts."
        )

    if mfa.get("recovery_protection") is not True:
        issues.append(
            "MFA recovery protection is not enabled."
        )
        recommendations.append(
            "Protect MFA recovery mechanisms against unauthorized takeover."
        )

    if mfa.get("bypass_protection") is not True:
        issues.append(
            "MFA bypass protection is not enabled."
        )
        recommendations.append(
            "Implement controls preventing unauthorized MFA bypass."
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
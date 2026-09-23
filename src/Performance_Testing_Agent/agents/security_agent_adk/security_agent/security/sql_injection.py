from typing import Any


def validate_sql_injection(
    sql_security: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate SQL injection prevention configuration.

    This validator evaluates configuration evidence for SQL injection
    prevention. It does not perform live SQL injection testing.

    Args:
        sql_security: SQL security configuration.

    Returns:
        A dictionary containing status, security score, issues,
        and recommendations.
    """

    if not isinstance(sql_security, dict):
        return {
            "status": "WARNING",
            "security_score": "N/A",
            "issues": [
                "SQL security configuration is unavailable or invalid."
            ],
            "recommendations": [
                "Provide valid SQL security configuration."
            ],
        }

    issues: list[str] = []
    recommendations: list[str] = []

    # Parameterized queries
    if sql_security.get("parameterized_queries") is not True:
        issues.append(
            "Parameterized queries are not enabled."
        )
        recommendations.append(
            "Use parameterized queries for database operations involving user-controlled input."
        )

    # Prepared statements
    if sql_security.get("prepared_statements") is not True:
        issues.append(
            "Prepared statements are not enabled."
        )
        recommendations.append(
            "Use prepared statements for database operations involving user-controlled input."
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
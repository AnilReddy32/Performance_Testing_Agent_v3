from typing import Any

from security_agent.security.authentication import validate_authentication
from security_agent.security.jwt import validate_jwt
from security_agent.security.authorization import validate_rbac
from security_agent.security.oauth import validate_oauth
from security_agent.security.mfa import validate_mfa
from security_agent.security.api import validate_api_security
from security_agent.security.rate_limit import validate_rate_limiting
from security_agent.security.sql_injection import validate_sql_injection
from security_agent.security.xss import validate_xss
from security_agent.security.csrf import validate_csrf

def assess_authentication(
    authentication_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess application authentication security.

    Use this tool after retrieving authentication configuration
    from the application profile.

    Args:
        authentication_data: Authentication configuration to assess.

    Returns:
        Structured authentication security assessment.
    """

    return validate_authentication(authentication_data)

def assess_jwt(
    authentication_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess JWT security configuration.

    Use this tool when the request specifically requires
    JWT token validation or JWT security assessment.

    Args:
        authentication_data: Authentication configuration containing
            JWT settings.

    Returns:
        Structured JWT security assessment.
    """

    return validate_jwt(authentication_data)


def assess_rbac(
    authorization_data: dict[str, Any],
    endpoints: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Assess application RBAC security.

    Use this tool when the request requires authorization or
    role-based access control validation.

    Args:
        authorization_data: Application RBAC configuration.
        endpoints: Optional API endpoint configuration.

    Returns:
        Structured RBAC security assessment.
    """

    return validate_rbac(
        authorization=authorization_data,
        endpoints=endpoints,
    )

def assess_oauth(
    oauth_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess OAuth security configuration.

    Use this tool when the request specifically requires
    OAuth authentication or OAuth security validation.

    Args:
        oauth_data: OAuth configuration to assess.

    Returns:
        Structured OAuth security assessment.
    """

    return validate_oauth(oauth_data)

def assess_mfa(
    mfa_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess MFA security configuration.

    Use this tool when the request specifically requires
    multi-factor authentication validation.

    Args:
        mfa_data: MFA configuration to assess.

    Returns:
        Structured MFA security assessment.
    """

    return validate_mfa(mfa_data)

def assess_api_security(
    endpoints: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Assess API endpoint security configuration.

    Use this tool after retrieving API endpoint information.
    This performs deterministic validation of endpoint security
    configuration and does not perform live HTTP testing.

    Args:
        endpoints: API endpoint configuration data retrieved
            from the API information tool.

    Returns:
        API security assessment result.
    """
    return validate_api_security(endpoints)

def assess_rate_limiting(
    endpoints: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Assess API rate-limiting configuration.

    Use this tool after retrieving API endpoint information.
    This performs deterministic configuration validation and does
    not perform live traffic or rate-limit enforcement testing.

    Args:
        endpoints: API endpoint configuration data retrieved
            from the API information tool.

    Returns:
        Rate-limiting security assessment result.
    """
    return validate_rate_limiting(endpoints)

def assess_sql_injection(
    sql_security: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess SQL injection prevention configuration.

    Use this tool after retrieving SQL security configuration.
    This performs deterministic configuration validation and does
    not perform live SQL injection testing.

    Args:
        sql_security: SQL security configuration evidence.

    Returns:
        SQL injection security assessment result.
    """
    return validate_sql_injection(sql_security)

def assess_xss(
    xss_security: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess XSS prevention configuration.

    Use this tool after retrieving XSS security configuration.
    This performs deterministic configuration validation and does
    not perform live XSS payload testing.

    Args:
        xss_security: XSS security configuration evidence.

    Returns:
        XSS security assessment result.
    """
    return validate_xss(xss_security)

def assess_csrf(
    csrf_security: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess CSRF protection configuration.

    This performs deterministic configuration validation.
    It does not perform live CSRF attack testing.
    """
    return validate_csrf(csrf_security)
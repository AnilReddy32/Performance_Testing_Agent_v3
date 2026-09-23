from security_agent.live_testing.models import LiveTestTarget, LiveTestScope
from security_agent.live_testing.scope import validate_test_scope


def test_scope_allows_authorized_host_and_path():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/login",
        method="POST",
    )

    scope = LiveTestScope(
        authorized=True,
        allowed_hosts=["staging.example.com"],
        allowed_paths=["/login"],
        environment="staging",
    )

    result = validate_test_scope(target, scope)

    assert result["allowed"] is True


def test_scope_rejects_when_not_authorized():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/login",
        method="POST",
    )

    scope = LiveTestScope(
        authorized=False,
        allowed_hosts=["staging.example.com"],
        allowed_paths=["/login"],
        environment="staging",
    )

    result = validate_test_scope(target, scope)

    assert result["allowed"] is False
    assert "not been explicitly authorized" in result["reason"]


def test_scope_rejects_unauthorized_host():
    target = LiveTestTarget(
        base_url="https://production.example.com",
        endpoint="/login",
        method="POST",
    )

    scope = LiveTestScope(
        authorized=True,
        allowed_hosts=["staging.example.com"],
        allowed_paths=["/login"],
        environment="staging",
    )

    result = validate_test_scope(target, scope)

    assert result["allowed"] is False
    assert "outside the authorized scope" in result["reason"]


def test_scope_rejects_unauthorized_path():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/admin",
        method="GET",
    )

    scope = LiveTestScope(
        authorized=True,
        allowed_hosts=["staging.example.com"],
        allowed_paths=["/login"],
        environment="staging",
    )

    result = validate_test_scope(target, scope)

    assert result["allowed"] is False
    assert "/admin" in result["reason"]


def test_scope_allows_any_path_when_paths_are_not_restricted():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="GET",
    )

    scope = LiveTestScope(
        authorized=True,
        allowed_hosts=["staging.example.com"],
        environment="staging",
    )

    result = validate_test_scope(target, scope)

    assert result["allowed"] is True


def test_scope_rejects_invalid_url_scheme():
    target = LiveTestTarget(
        base_url="ftp://staging.example.com",
        endpoint="/login",
        method="POST",
    )

    scope = LiveTestScope(
        authorized=True,
        allowed_hosts=["staging.example.com"],
        environment="staging",
    )

    result = validate_test_scope(target, scope)

    assert result["allowed"] is False
    assert "HTTP or HTTPS" in result["reason"]


def test_scope_does_not_match_similar_hostname():
    target = LiveTestTarget(
        base_url="https://staging.example.com.attacker.com",
        endpoint="/login",
        method="POST",
    )

    scope = LiveTestScope(
        authorized=True,
        allowed_hosts=["staging.example.com"],
        environment="staging",
    )

    result = validate_test_scope(target, scope)

    assert result["allowed"] is False


def test_scope_handles_query_parameters_in_endpoint():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/login?redirect=/profile",
        method="GET",
    )

    scope = LiveTestScope(
        authorized=True,
        allowed_hosts=["staging.example.com"],
        allowed_paths=["/login"],
        environment="staging",
    )

    result = validate_test_scope(target, scope)

    assert result["allowed"] is True
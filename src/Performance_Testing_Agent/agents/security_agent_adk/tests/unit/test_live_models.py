import pytest
from pydantic import ValidationError

from security_agent.live_testing.models import (
    LiveTestPolicy,
    LiveTestResult,
    LiveTestTarget,
    LiveTestScope,
)


def test_live_test_target_creation():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/login",
        method="POST",
    )

    assert target.base_url == "https://staging.example.com"
    assert target.endpoint == "/login"
    assert target.method == "POST"


def test_live_test_target_rejects_empty_values():
    with pytest.raises(ValidationError):
        LiveTestTarget(
            base_url="",
            endpoint="/login",
            method="POST",
        )


def test_test_scope_defaults():
    scope = LiveTestScope(
        authorized=True,
        environment="staging",
    )

    assert scope.authorized is True
    assert scope.allowed_hosts == []
    assert scope.allowed_paths == []


def test_test_scope_with_explicit_boundary():
    scope = LiveTestScope(
        authorized=True,
        allowed_hosts=["staging.example.com"],
        allowed_paths=["/login", "/users"],
        environment="staging",
    )

    assert "staging.example.com" in scope.allowed_hosts
    assert "/login" in scope.allowed_paths


def test_live_test_policy_defaults():
    policy = LiveTestPolicy()

    assert policy.max_requests == 20
    assert policy.timeout_seconds == 10
    assert policy.allow_state_changing_requests is False
    assert policy.allow_destructive_tests is False


def test_live_test_policy_rejects_invalid_limits():
    with pytest.raises(ValidationError):
        LiveTestPolicy(max_requests=0)

    with pytest.raises(ValidationError):
        LiveTestPolicy(timeout_seconds=0)


def test_live_test_result_creation():
    result = LiveTestResult(
        status="PASS",
        test_name="Authentication Test",
        target="https://staging.example.com/login",
        requests_sent=1,
        evidence=["Authentication challenge returned 401."],
    )

    assert result.status == "PASS"
    assert result.requests_sent == 1
    assert len(result.evidence) == 1
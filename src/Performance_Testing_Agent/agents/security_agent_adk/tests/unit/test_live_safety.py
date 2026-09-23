from security_agent.live_testing.models import LiveTestPolicy, LiveTestTarget
from security_agent.live_testing.safety import validate_test_safety


def test_safe_get_request_is_allowed():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="GET",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is True


def test_head_request_is_allowed():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="HEAD",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is True


def test_options_request_is_allowed():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="OPTIONS",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is True


def test_post_request_is_blocked_by_default():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/login",
        method="POST",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is False
    assert "State-changing" in result["reason"]


def test_state_changing_request_can_be_explicitly_allowed():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/login",
        method="POST",
    )

    policy = LiveTestPolicy(
        allow_state_changing_requests=True,
    )

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is True


def test_put_request_is_blocked_by_default():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users/1",
        method="PUT",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is False


def test_patch_request_is_blocked_by_default():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users/1",
        method="PATCH",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is False


def test_delete_request_is_blocked_by_default():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users/1",
        method="DELETE",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is False


def test_request_count_above_limit_is_blocked():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="GET",
    )

    policy = LiveTestPolicy(max_requests=10)

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=11,
    )

    assert result["allowed"] is False
    assert "exceeds" in result["reason"]


def test_request_count_at_limit_is_allowed():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="GET",
    )

    policy = LiveTestPolicy(max_requests=10)

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=10,
    )

    assert result["allowed"] is True


def test_zero_requests_are_rejected():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="GET",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=0,
    )

    assert result["allowed"] is False
    assert "greater than zero" in result["reason"]


def test_negative_requests_are_rejected():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="GET",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=-1,
    )

    assert result["allowed"] is False


def test_unsupported_http_method_is_rejected():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="TRACE",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is False
    assert "not supported" in result["reason"]


def test_destructive_test_is_blocked_by_default():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="GET",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
        destructive_test=True,
    )

    assert result["allowed"] is False
    assert "Destructive" in result["reason"]


def test_destructive_test_can_be_explicitly_allowed():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="GET",
    )

    policy = LiveTestPolicy(
        allow_destructive_tests=True,
    )

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
        destructive_test=True,
    )

    assert result["allowed"] is True


def test_method_comparison_is_case_insensitive():
    target = LiveTestTarget(
        base_url="https://staging.example.com",
        endpoint="/users",
        method="get",
    )

    policy = LiveTestPolicy()

    result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=1,
    )

    assert result["allowed"] is True
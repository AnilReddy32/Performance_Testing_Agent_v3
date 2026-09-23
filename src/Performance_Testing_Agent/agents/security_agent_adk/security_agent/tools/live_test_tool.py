from typing import Any

from security_agent.live_testing.executor import HTTPExecutor
from security_agent.live_testing.models import (
    HTTPRequest,
    LiveTestPolicy,
    LiveTestScope,
    LiveTestTarget,
)
from security_agent.live_testing.safety import validate_test_safety
from security_agent.live_testing.scope import (
    validate_request_matches_target,
    validate_test_scope,
)


async def execute_authorized_live_test(
    target_data: dict[str, Any],
    scope_data: dict[str, Any],
    policy_data: dict[str, Any],
    request_data: dict[str, Any],
    requested_requests: int = 1,
    destructive_test: bool = False,
) -> dict[str, Any]:
    """
    Execute one authorized and safety-validated live HTTP test.

    The execution order is intentionally fixed:

    1. Validate authorization scope.
    2. Validate safety policy.
    3. Execute the HTTP request.
    """

    target = LiveTestTarget.model_validate(target_data)
    scope = LiveTestScope.model_validate(scope_data)
    policy = LiveTestPolicy.model_validate(policy_data)
    request = HTTPRequest.model_validate(request_data)

    # 1. Scope validation
    scope_result = validate_test_scope(
        target=target,
        scope=scope,
    )

    if not scope_result["allowed"]:
        return {
            "success": False,
            "stage": "scope_validation",
            "result": scope_result,
        }

    # 2. Make sure the actual request matches the authorized target
    request_target_result = validate_request_matches_target(
        target=target,
        request_url=request.url,
    )

    if not request_target_result["allowed"]:
        return {
            "success": False,
            "stage": "target_validation",
            "result": request_target_result,
        }

    # 3. Safety validation
    safety_result = validate_test_safety(
        target=target,
        policy=policy,
        requested_requests=requested_requests,
        destructive_test=destructive_test,
    )

    if not safety_result["allowed"]:
        return {
            "success": False,
            "stage": "safety_validation",
            "result": safety_result,
        }

    # 4. Execute HTTP request
    executor = HTTPExecutor(policy=policy)
    execution_result = await executor.execute(request)
    return {
        "success": execution_result.success,
        "stage": "execution",
        "scope": scope_result,
        "safety": safety_result,
        "execution": execution_result.model_dump(),
    }




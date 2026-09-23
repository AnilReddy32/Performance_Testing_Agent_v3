import httpx
import pytest

from security_agent.tools.live_test_tool import execute_authorized_live_test


@pytest.mark.asyncio
async def test_controlled_live_test_executes_after_scope_and_safety_validation():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"status": "ok"},
        )

    original = httpx.AsyncClient

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            self.client = original(
                *args,
                transport=httpx.MockTransport(handler),
                **kwargs,
            )

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            await self.client.aclose()

        async def request(self, *args, **kwargs):
            return await self.client.request(*args, **kwargs)

    httpx.AsyncClient = MockAsyncClient

    try:
        result = await execute_authorized_live_test(
            target_data={
                "base_url": "https://staging.example.com",
                "endpoint": "/users",
                "method": "GET",
            },
            scope_data={
                "authorized": True,
                "allowed_hosts": ["staging.example.com"],
                "allowed_paths": ["/users"],
                "environment": "staging",
            },
            policy_data={
                "max_requests": 20,
                "timeout_seconds": 10,
                "allow_state_changing_requests": False,
                "allow_destructive_tests": False,
            },
            request_data={
                "method": "GET",
                "url": "https://staging.example.com/users",
            },
        )

        assert result["success"] is True
        assert result["stage"] == "execution"
        assert result["execution"]["success"] is True
        assert result["execution"]["response"]["status_code"] == 200

    finally:
        httpx.AsyncClient = original


@pytest.mark.asyncio
async def test_controlled_live_test_blocks_unauthorized_scope():
    result = await execute_authorized_live_test(
        target_data={
            "base_url": "https://production.example.com",
            "endpoint": "/users",
            "method": "GET",
        },
        scope_data={
            "authorized": True,
            "allowed_hosts": ["staging.example.com"],
            "allowed_paths": ["/users"],
            "environment": "staging",
        },
        policy_data={},
        request_data={
            "method": "GET",
            "url": "https://production.example.com/users",
        },
    )

    assert result["success"] is False
    assert result["stage"] == "scope_validation"


@pytest.mark.asyncio
async def test_controlled_live_test_blocks_unsafe_method():
    result = await execute_authorized_live_test(
        target_data={
            "base_url": "https://staging.example.com",
            "endpoint": "/users",
            "method": "POST",
        },
        scope_data={
            "authorized": True,
            "allowed_hosts": ["staging.example.com"],
            "allowed_paths": ["/users"],
            "environment": "staging",
        },
        policy_data={},
        request_data={
            "method": "POST",
            "url": "https://staging.example.com/users",
        },
    )

    assert result["success"] is False
    assert result["stage"] == "safety_validation"


@pytest.mark.asyncio
async def test_controlled_live_test_blocks_request_to_different_host():
    result = await execute_authorized_live_test(
        target_data={
            "base_url": "https://staging.example.com",
            "endpoint": "/users",
            "method": "GET",
        },
        scope_data={
            "authorized": True,
            "allowed_hosts": ["staging.example.com"],
            "allowed_paths": ["/users"],
            "environment": "staging",
        },
        policy_data={},
        request_data={
            "method": "GET",
            "url": "https://other.example.com/users",
        },
    )

    assert result["success"] is False
    assert result["stage"] == "target_validation"


@pytest.mark.asyncio
async def test_controlled_live_test_blocks_different_path():
    result = await execute_authorized_live_test(
        target_data={
            "base_url": "https://staging.example.com",
            "endpoint": "/users",
            "method": "GET",
        },
        scope_data={
            "authorized": True,
            "allowed_hosts": ["staging.example.com"],
            "allowed_paths": ["/users"],
            "environment": "staging",
        },
        policy_data={},
        request_data={
            "method": "GET",
            "url": "https://staging.example.com/admin",
        },
    )

    assert result["success"] is False
    assert result["stage"] == "target_validation"
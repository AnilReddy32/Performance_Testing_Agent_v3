from unittest import result

import httpx
import pytest

from security_agent.live_testing.executor import HTTPExecutor
from security_agent.live_testing.models import (
    HTTPRequest,
    LiveTestPolicy,
)


@pytest.mark.asyncio
async def test_executor_returns_http_response():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            headers={"content-type": "application/json"},
            json={"status": "ok"},
        )

    policy = LiveTestPolicy()

    executor = HTTPExecutor(policy)

    transport = httpx.MockTransport(handler)

    original_client = httpx.AsyncClient

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            self.client = original_client(
                *args,
                transport=transport,
                **kwargs,
            )

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            await self.client.aclose()

        async def request(self, *args, **kwargs):
            return await self.client.request(*args, **kwargs)

    original = httpx.AsyncClient
    httpx.AsyncClient = MockAsyncClient

    try:
        request = HTTPRequest(
            method="GET",
            url="https://staging.example.com/users",
        )

        result = await executor.execute(request)


        assert result.success is True
        assert result.response is not None
        assert result.response.status_code == 200
        assert result.response.body != ""
        assert result.response.elapsed_ms >= 0

    finally:
        httpx.AsyncClient = original


@pytest.mark.asyncio
async def test_executor_preserves_response_headers():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=401,
            headers={
                "content-type": "application/json",
                "www-authenticate": "Bearer",
            },
            json={"error": "unauthorized"},
        )

    policy = LiveTestPolicy()

    executor = HTTPExecutor(policy)

    transport = httpx.MockTransport(handler)

    original = httpx.AsyncClient

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            self.client = original(
                *args,
                transport=transport,
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
        request = HTTPRequest(
            method="GET",
            url="https://staging.example.com/protected",
        )

        result = await executor.execute(request)


        assert result.success is True
        assert result.response is not None
        assert result.response.status_code == 401
        assert result.response.headers["www-authenticate"] == "Bearer"

    finally:
        httpx.AsyncClient = original


@pytest.mark.asyncio
async def test_executor_uses_configured_timeout():
    captured_timeout = None

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200)

    policy = LiveTestPolicy(timeout_seconds=5)

    executor = HTTPExecutor(policy)

    transport = httpx.MockTransport(handler)

    original = httpx.AsyncClient

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            nonlocal captured_timeout
            captured_timeout = kwargs.get("timeout")

            self.client = original(
                *args,
                transport=transport,
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
        request = HTTPRequest(
            method="GET",
            url="https://staging.example.com/users",
        )

        await executor.execute(request)

        assert captured_timeout == 5

    finally:
        httpx.AsyncClient = original
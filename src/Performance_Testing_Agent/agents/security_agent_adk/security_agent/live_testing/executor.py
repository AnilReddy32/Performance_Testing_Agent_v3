from time import perf_counter
from urllib.parse import urlparse

import httpx

from security_agent.live_testing.models import (
    HTTPExecutionResult,
    HTTPRequest,
    HTTPResponse,
    LiveTestPolicy,
)


class HTTPExecutor:
    """
    Controlled HTTP executor for authorized live security testing.

    This class is intentionally not exposed directly as an ADK tool.
    Requests should reach it through the controlled live-test tool.
    """

    def __init__(self, policy: LiveTestPolicy):
        self.policy = policy

    async def execute(
        self,
        request: HTTPRequest,
    ) -> HTTPExecutionResult:
        """Execute one controlled HTTP request."""

        method = request.method.upper()

        parsed_url = urlparse(request.url)

        if parsed_url.scheme not in {"http", "https"}:
            return HTTPExecutionResult(
                success=False,
                error="Only HTTP and HTTPS URLs are permitted.",
            )

        if not parsed_url.hostname:
            return HTTPExecutionResult(
                success=False,
                error="Request URL does not contain a valid hostname.",
            )

        if parsed_url.username or parsed_url.password:
            return HTTPExecutionResult(
                success=False,
                error="Credentials embedded in request URLs are not permitted.",
            )

        start = perf_counter()

        try:
            async with httpx.AsyncClient(
                timeout=self.policy.timeout_seconds,
                follow_redirects=False,
                trust_env=False,
            ) as client:
                response = await client.request(
                    method=method,
                    url=request.url,
                    headers=request.headers,
                    content=request.body,
                )

                content = await response.aread()

            elapsed_ms = (perf_counter() - start) * 1000

            if len(content) > self.policy.max_response_bytes:
                return HTTPExecutionResult(
                    success=False,
                    error=(
                        "HTTP response exceeded the configured maximum "
                        f"response size of {self.policy.max_response_bytes} bytes."
                    ),
                )

            return HTTPExecutionResult(
                success=True,
                response=HTTPResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=content.decode(
                        response.encoding or "utf-8",
                        errors="replace",
                    ),
                    elapsed_ms=elapsed_ms,
                ),
            )

        except httpx.TimeoutException:
            return HTTPExecutionResult(
                success=False,
                error=(
                    "HTTP request timed out after "
                    f"{self.policy.timeout_seconds} seconds."
                ),
            )

        except httpx.RequestError as exc:
            return HTTPExecutionResult(
                success=False,
                error=f"HTTP request failed: {type(exc).__name__}.",
            )
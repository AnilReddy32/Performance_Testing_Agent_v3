from typing import Any

from pydantic import BaseModel, Field


class LiveTestTarget(BaseModel):
    """Target for an authorized live security test."""

    base_url: str = Field(
        ...,
        min_length=1,
        description="Base URL of the authorized target application.",
    )
    endpoint: str = Field(
        ...,
        min_length=1,
        description="API endpoint path to test.",
    )
    method: str = Field(
        ...,
        min_length=1,
        description="HTTP method to use for the test.",
    )


class LiveTestScope(BaseModel):
    """Explicit authorization boundary for live security testing."""

    authorized: bool = Field(
        ...,
        description="Whether live testing has been explicitly authorized.",
    )
    allowed_hosts: list[str] = Field(
        default_factory=list,
        description="Hosts explicitly authorized for live testing.",
    )
    allowed_paths: list[str] = Field(
        default_factory=list,
        description="Optional paths explicitly authorized for live testing.",
    )
    environment: str = Field(
        ...,
        min_length=1,
        description="Target environment.",
    )


class LiveTestPolicy(BaseModel):
    """Safety limits applied to live security tests."""

    max_requests: int = Field(
        default=20,
        gt=0,
        description="Maximum number of requests permitted for a test.",
    )
    timeout_seconds: int = Field(
        default=10,
        gt=0,
        description="Maximum timeout for an individual request.",
    )
    max_response_bytes: int = Field(
        default=1_000_000,
        gt=0,
        description="Maximum response body size accepted by the executor.",
    )
    allow_state_changing_requests: bool = Field(
        default=False,
        description="Whether state-changing HTTP requests are permitted.",
    )
    allow_destructive_tests: bool = Field(
        default=False,
        description="Whether destructive security tests are permitted.",
    )


class LiveTestResult(BaseModel):
    """Standardized result produced by a live security test."""

    status: str
    test_name: str
    target: str
    requests_sent: int = 0
    evidence: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class HTTPRequest(BaseModel):
    """Controlled HTTP request submitted to the live executor."""

    method: str = Field(..., min_length=1)
    url: str = Field(..., min_length=1)
    headers: dict[str, str] = Field(default_factory=dict)
    body: Any = None


class HTTPResponse(BaseModel):
    """Structured HTTP response evidence."""

    status_code: int
    headers: dict[str, str] = Field(default_factory=dict)
    body: str = ""
    elapsed_ms: float


class HTTPExecutionResult(BaseModel):
    """Structured result of an HTTP execution attempt."""

    success: bool
    response: HTTPResponse | None = None
    error: str | None = None
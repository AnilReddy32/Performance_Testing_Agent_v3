"""Plain data shapes shared by the passive assessment modules."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

PASSED = "passed"
FAILED = "failed"
INCONCLUSIVE = "inconclusive"

# Points a check contributes to the score. Informational checks are reported
# but carry no weight and never change the overall status.
SEVERITY_WEIGHT = {"critical": 8, "high": 5, "medium": 3, "low": 1, "info": 0}
BLOCKING_SEVERITIES = {"critical", "high"}
WARNING_SEVERITIES = {"medium", "low"}


@dataclass(frozen=True)
class CheckResult:
    """One verdict about one aspect of the externally visible surface."""

    check_id: str
    title: str
    category: str
    verdict: str
    severity: str
    summary: str
    evidence: dict[str, Any] = field(default_factory=dict)
    recommendation: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "category": self.category,
            "verdict": self.verdict,
            "severity": self.severity,
            "summary": self.summary,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


@dataclass(frozen=True)
class HttpObservation:
    """What one request returned, or why it returned nothing."""

    label: str
    method: str
    target: str
    scheme: str
    status: int | None = None
    headers: tuple[tuple[str, str], ...] = ()
    body: str = ""
    elapsed_ms: float | None = None
    error_kind: str | None = None
    error: str | None = None

    @property
    def received(self) -> bool:
        return self.status is not None

    def header_values(self, name: str) -> list[str]:
        wanted = name.lower()
        return [value for key, value in self.headers if key == wanted]

    def header(self, name: str) -> str | None:
        values = self.header_values(name)
        return ", ".join(values) if values else None


@dataclass(frozen=True)
class TlsObservation:
    """Result of one TLS handshake with certificate verification enabled."""

    ok: bool
    version: str | None = None
    cipher_name: str | None = None
    cipher_bits: int | None = None
    subject: str | None = None
    issuer: str | None = None
    not_after: float | None = None
    san_count: int | None = None
    error_kind: str | None = None
    error: str | None = None
    verify_message: str | None = None


@dataclass(frozen=True)
class TrafficEvidence:
    """Status-code distribution of the performance run's own requests."""

    source: str
    total_requests: int
    status_counts: dict[str, int]
    tls_versions: tuple[str, ...] = ()
    truncated: bool = False

    @property
    def throttled_requests(self) -> int:
        return self.status_counts.get("429", 0)


@dataclass
class Observations:
    """Everything the probes saw, gathered before any verdict is made."""

    declared_method: str
    tls: TlsObservation | None = None
    primary: HttpObservation | None = None
    options: HttpObservation | None = None
    not_found: HttpObservation | None = None
    http_redirect: HttpObservation | None = None
    traffic: TrafficEvidence | None = None
    skipped_reason: str | None = None

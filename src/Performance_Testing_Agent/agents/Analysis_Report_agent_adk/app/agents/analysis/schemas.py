"""
Schemas for the Analysis Agent.

Three upstream agents feed this agent, each with its OWN shape -- these are
NOT unified into one record type, because they measure fundamentally
different things at different granularities:

- test_execution_agent: one record PER API/endpoint (unchanged from the
  original spec -- MetricRecord below matches it exactly).
- monitoring_agent: ONE snapshot per job (system-level: CPU, memory, DB
  connections, TPS) -- not tied to any single API.
- security_agent: ONE summary per job (pass/fail + score + flat lists of
  issues/recommendations).

AnalysisOutput is what the Report Agent consumes as its input.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Upstream agent input shapes (as given -- do not "unify" these into one
# record, they represent different things)
# ---------------------------------------------------------------------------

class MetricRecord(BaseModel):
    """From test_execution_agent. One per API/endpoint. Unchanged."""
    job_id: str
    application: str
    scenario: str
    api_name: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    p95_response_time: float
    max_response_time: float
    throughput: float
    error_rate: float  # assumed 0-100 (percent); see tools.normalize_error_rate
    http_status: int = 200


class MonitoringResult(BaseModel):
    """From monitoring_agent. ONE snapshot for the whole job (not per-API)."""
    job_id: str = "unknown"
    application: str = "unknown"
    scenario: str = "unknown"
    cpu_usage: float
    memory_usage: float
    db_connections: float
    response_time: float  # monitoring's own view of response time -- may
                           # differ slightly from test_execution's avg_response_time;
                           # we cross-check the two rather than assume they match.
    tps: float
    status: str  # e.g. "OK"
    alerts: List[Any] = Field(default_factory=list)  # item shape not specified -- treated as opaque


class SecurityResult(BaseModel):
    """From security_agent. ONE summary for the whole job."""
    status: str  # PASS | FAIL | WARNING
    security_score: str  # e.g. "100%", "80%" -- kept as the string you gave, not parsed to a number
    issues: List[Any] = Field(default_factory=list)       # item shape not specified -- treated as opaque
    recommendations: List[Any] = Field(default_factory=list)  # item shape not specified -- treated as opaque


class AnalysisInput(BaseModel):
    """What the Orchestrator hands the Analysis Agent: one job's worth of
    data from all three upstream agents. monitoring_result and
    security_result are optional -- the Orchestrator's own diagram says
    invocation is query-driven, not a mandatory sequence, so Analysis
    should still work if one of them didn't run for this job."""
    job_id: str
    application: str
    scenario: str
    test_execution_result: MetricRecord
    monitoring_result: Optional[MonitoringResult] = None
    security_result: Optional[SecurityResult] = None


# ---------------------------------------------------------------------------
# Analysis Agent's own output (== Report Agent's input)
# ---------------------------------------------------------------------------

class DataQualityIssue(BaseModel):
    api_name: Optional[str] = None
    field: str
    issue: str
    severity: str  # warning | critical


class ApiFinding(BaseModel):
    """One per API, derived from test_execution_agent's records."""
    api_name: str
    status: str  # pass | warning | fail
    severity: str  # low | medium | high | critical
    metrics: dict
    anomalies: List[str] = Field(default_factory=list)
    thresholds_breached: List[str] = Field(default_factory=list)
    historical_comparison: Optional[str] = None
    recommendation: Optional[str] = None


class InfraHealthFinding(BaseModel):
    """Derived from monitoring_agent's single job-level snapshot."""
    status: str  # pass | warning | fail (derived here, independent of monitoring's own "status" field)
    monitoring_reported_status: str  # monitoring_agent's own "status" field, passed through as-is
    cpu_usage: float
    memory_usage: float
    db_connections: float
    tps: float
    monitoring_response_time: float
    alerts: List[Any] = Field(default_factory=list)
    anomalies: List[str] = Field(default_factory=list)
    cross_check_note: Optional[str] = None  # e.g. mismatch between monitoring's response_time and test_execution's avg


class SecuritySummary(BaseModel):
    """Passed through from security_agent, largely as-is."""
    status: str  # PASS | FAIL | WARNING (kept exactly as security_agent sent it)
    security_score: str
    issues: List[Any] = Field(default_factory=list)
    recommendations: List[Any] = Field(default_factory=list)


class AnalysisOutput(BaseModel):
    """This is the object handed to the Report Agent as its input."""
    job_id: str
    application: str
    scenario: str

    data_quality_status: str  # valid | invalid
    data_quality_issues: List[DataQualityIssue] = Field(default_factory=list)
    unusable_reason: Optional[str] = None

    overall_status: Optional[str] = None  # pass | warning | fail -- worst of performance/infra/security
    api_findings: List[ApiFinding] = Field(default_factory=list)
    infra_health: Optional[InfraHealthFinding] = None
    security_summary: Optional[SecuritySummary] = None

    summary: Optional[str] = None
    ready_for_report: bool = False

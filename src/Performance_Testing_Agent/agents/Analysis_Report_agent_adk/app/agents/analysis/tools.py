"""
Tools for the Analysis Agent.

As before: every number that matters is computed here in plain Python,
not left to the LLM. The LLM's job is to call these in order, read the
results, add narrative bits informed by RAG context, and call
finalize_analysis() last.

Three separate validation/analysis functions now, one per upstream agent,
because they measure different things at different granularities:
  validate_data_quality / analyze_metrics   <- test_execution_agent (per-API)
  analyze_infra_health                      <- monitoring_agent (per-job snapshot)
  summarize_security                        <- security_agent (per-job summary)
"""

from typing import Any, List, Optional

from .schemas import (
    AnalysisOutput,
    ApiFinding,
    DataQualityIssue,
    InfraHealthFinding,
    SecuritySummary,
)

# ---------------------------------------------------------------------------
# Thresholds -- tune these to your SLAs, or load from app/config.py instead.
# ---------------------------------------------------------------------------
THRESHOLDS = {
    "error_rate_pct": 1.0,
    "p95_avg_ratio": 3.0,
    "max_p95_ratio": 2.0,
    "min_throughput": 1.0,
    "expected_http_status": 200,
    "mismatch_tolerance_pct": 1.0,
    "cpu_usage_pct": 80.0,          # infra: CPU above this -> warning
    "memory_usage_pct": 85.0,       # infra: memory above this -> warning
    "db_connections_max": 200.0,    # infra: connection pool ceiling -- adjust to your real pool size
    "response_time_cross_check_pct": 20.0,  # infra vs test_execution response time disagreement tolerance
}


def _normalize_error_rate(error_rate: float) -> float:
    """error_rate may arrive as a fraction (0.02) or a percent (2.0)."""
    return error_rate * 100 if error_rate <= 1 else error_rate


# ---------------------------------------------------------------------------
# test_execution_agent -> data quality + per-API metric analysis (unchanged logic)
# ---------------------------------------------------------------------------

def validate_data_quality(records: List[dict]) -> dict:
    """Checks each test_execution_agent record for internal consistency.
    Returns {"status": "valid"|"invalid", "issues": [...]}."""
    issues: List[dict] = []

    if not records:
        return {
            "status": "invalid",
            "issues": [{
                "field": "records",
                "issue": "No test_execution records were provided for this job.",
                "severity": "critical",
            }],
        }

    for r in records:
        api = r.get("api_name", "unknown")
        total = r.get("total_requests", 0)
        success = r.get("successful_requests", 0)
        failed = r.get("failed_requests", 0)
        avg = r.get("avg_response_time", 0)
        p95 = r.get("p95_response_time", 0)
        mx = r.get("max_response_time", 0)
        err = r.get("error_rate", 0)

        for field in ("total_requests", "successful_requests", "failed_requests",
                      "avg_response_time", "p95_response_time",
                      "max_response_time", "throughput", "error_rate"):
            if r.get(field, 0) < 0:
                issues.append({"api_name": api, "field": field,
                                "issue": f"{field} is negative ({r.get(field)}).",
                                "severity": "critical"})

        if total == 0:
            issues.append({"api_name": api, "field": "total_requests",
                            "issue": "total_requests is 0 -- no data to analyze for this API.",
                            "severity": "critical"})
            continue

        if success + failed != total:
            issues.append({
                "api_name": api, "field": "total_requests",
                "issue": (f"successful_requests ({success}) + failed_requests "
                          f"({failed}) = {success + failed}, which does not "
                          f"match total_requests ({total})."),
                "severity": "critical",
            })

        expected_err = (failed / total) * 100
        actual_err = _normalize_error_rate(err)
        if abs(expected_err - actual_err) > THRESHOLDS["mismatch_tolerance_pct"]:
            issues.append({
                "api_name": api, "field": "error_rate",
                "issue": (f"Reported error_rate ({actual_err:.2f}%) doesn't match "
                          f"failed/total ({expected_err:.2f}%)."),
                "severity": "warning",
            })

        if p95 < avg:
            issues.append({"api_name": api, "field": "p95_response_time",
                            "issue": f"p95 ({p95}ms) is lower than avg ({avg}ms).",
                            "severity": "warning"})
        if mx < p95:
            issues.append({"api_name": api, "field": "max_response_time",
                            "issue": f"max ({mx}ms) is lower than p95 ({p95}ms).",
                            "severity": "warning"})

    has_critical = any(i["severity"] == "critical" for i in issues)
    return {"status": "invalid" if has_critical else "valid", "issues": issues}


def analyze_metrics(records: List[dict]) -> dict:
    """Runs threshold checks per API from test_execution_agent's records.
    Only call after validate_data_quality() returns status "valid"."""
    findings = []
    for r in records:
        api = r.get("api_name", "unknown")
        avg = r.get("avg_response_time", 0)
        p95 = r.get("p95_response_time", 0)
        mx = r.get("max_response_time", 0)
        throughput = r.get("throughput", 0)
        err = _normalize_error_rate(r.get("error_rate", 0))
        status_code = r.get("http_status", 200)

        anomalies = []
        breached = []

        if err > THRESHOLDS["error_rate_pct"]:
            anomalies.append(f"Error rate {err:.2f}% exceeds {THRESHOLDS['error_rate_pct']}% threshold.")
            breached.append("error_rate")

        if avg > 0 and p95 / avg > THRESHOLDS["p95_avg_ratio"]:
            anomalies.append(
                f"p95 ({p95}ms) is {p95/avg:.1f}x the average ({avg}ms) -- "
                f"wide latency variance / possible tail contention."
            )
            breached.append("p95_avg_ratio")

        if p95 > 0 and mx / p95 > THRESHOLDS["max_p95_ratio"]:
            anomalies.append(
                f"Max response time ({mx}ms) is {mx/p95:.1f}x p95 ({p95}ms) -- "
                f"outlier spikes present."
            )
            breached.append("max_p95_ratio")

        if throughput < THRESHOLDS["min_throughput"]:
            anomalies.append(f"Throughput {throughput} req/s is below the "
                              f"{THRESHOLDS['min_throughput']} req/s floor.")
            breached.append("min_throughput")

        if status_code != THRESHOLDS["expected_http_status"]:
            anomalies.append(f"Unexpected HTTP status {status_code} "
                              f"(expected {THRESHOLDS['expected_http_status']}).")
            breached.append("http_status")

        if not breached:
            severity, status = "low", "pass"
        elif "error_rate" in breached or "http_status" in breached:
            severity, status = ("critical" if err > THRESHOLDS["error_rate_pct"] * 5 else "high"), "fail"
        elif len(breached) >= 2:
            severity, status = "high", "warning"
        else:
            severity, status = "medium", "warning"

        findings.append({
            "api_name": api,
            "status": status,
            "severity": severity,
            "metrics": {
                "total_requests": r.get("total_requests"),
                "successful_requests": r.get("successful_requests"),
                "failed_requests": r.get("failed_requests"),
                "avg_response_time": avg, "p95_response_time": p95,
                "max_response_time": mx, "throughput": throughput,
                "error_rate_pct": round(err, 2), "http_status": status_code,
            },
            "anomalies": anomalies,
            "thresholds_breached": breached,
        })
    return {"findings": findings}


# ---------------------------------------------------------------------------
# monitoring_agent -> infra health analysis (NEW)
# ---------------------------------------------------------------------------

def analyze_infra_health(monitoring_result: dict, test_execution_avg_response_time: Optional[float] = None) -> dict:
    """
    Analyzes monitoring_agent's single job-level snapshot. Also cross-checks
    monitoring's own response_time against test_execution's avg_response_time
    -- these come from different measurement points (infra vs. client-side),
    so a big disagreement is itself worth flagging, not silently trusted.

    test_execution_avg_response_time: pass the average of avg_response_time
    across all API records for this job (compute it yourself from the
    test_execution records, or pass None to skip the cross-check).
    """
    cpu = monitoring_result.get("cpu_usage", 0)
    mem = monitoring_result.get("memory_usage", 0)
    db_conn = monitoring_result.get("db_connections", 0)
    tps = monitoring_result.get("tps", 0)
    mon_response_time = monitoring_result.get("response_time", 0)
    mon_status = monitoring_result.get("status", "unknown")
    alerts = monitoring_result.get("alerts", [])

    anomalies = []
    if cpu > THRESHOLDS["cpu_usage_pct"]:
        anomalies.append(f"CPU usage {cpu}% exceeds {THRESHOLDS['cpu_usage_pct']}% threshold.")
    if mem > THRESHOLDS["memory_usage_pct"]:
        anomalies.append(f"Memory usage {mem}% exceeds {THRESHOLDS['memory_usage_pct']}% threshold.")
    if db_conn > THRESHOLDS["db_connections_max"]:
        anomalies.append(f"DB connections {db_conn} exceeds pool ceiling of {THRESHOLDS['db_connections_max']}.")
    if alerts:
        anomalies.append(f"{len(alerts)} monitoring alert(s) reported: {alerts}")

    cross_check_note = None
    if test_execution_avg_response_time is not None and test_execution_avg_response_time > 0:
        diff_pct = abs(mon_response_time - test_execution_avg_response_time) / test_execution_avg_response_time * 100
        if diff_pct > THRESHOLDS["response_time_cross_check_pct"]:
            cross_check_note = (
                f"monitoring_agent's response_time ({mon_response_time}ms) disagrees with "
                f"test_execution_agent's avg_response_time ({test_execution_avg_response_time}ms) "
                f"by {diff_pct:.0f}% -- worth checking measurement points/clock sync."
            )

    if any("exceeds" in a for a in anomalies) and (cpu > THRESHOLDS["cpu_usage_pct"] or mem > THRESHOLDS["memory_usage_pct"]):
        status = "fail" if (cpu > 95 or mem > 95) else "warning"
    elif anomalies:
        status = "warning"
    else:
        status = "pass"

    return {
        "status": status,
        "monitoring_reported_status": mon_status,
        "cpu_usage": cpu, "memory_usage": mem, "db_connections": db_conn,
        "tps": tps, "monitoring_response_time": mon_response_time,
        "alerts": alerts, "anomalies": anomalies, "cross_check_note": cross_check_note,
    }


# ---------------------------------------------------------------------------
# security_agent -> pass-through summary (NEW)
# ---------------------------------------------------------------------------

def summarize_security(security_result: dict) -> dict:
    """
    Mostly a pass-through -- security_agent already did the analysis, this
    agent's job is just to fold its verdict into the overall job status,
    not to re-judge security findings itself.
    """
    return {
        "status": security_result.get("status", "unknown"),
        "security_score": security_result.get("security_score", "unknown"),
        "issues": security_result.get("issues", []),
        "recommendations": security_result.get("recommendations", []),
    }


# ---------------------------------------------------------------------------
# RAG historical/knowledge lookup (unchanged interface)
# ---------------------------------------------------------------------------

def retrieve_historical_context(
    application: str, scenario: str, api_name: str, anomaly_text: Optional[str] = None
) -> dict:
    """Pulls comparable historical runs + relevant SLA/runbook/postmortem
    content from app/rag/. Wrapped in try/except so the agent still works
    if RAG is unreachable -- degrades to threshold-only analysis."""
    try:
        from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.rag.retriever import retrieve_context
        result = retrieve_context(
            application=application, scenario=scenario, api_name=api_name,
            anomaly_text=anomaly_text, top_k=5,
        )
        return {"available": True, "context": result}
    except Exception as e:  # noqa: BLE001
        return {
            "available": False,
            "context": None,
            "note": f"RAG context unavailable ({e.__class__.__name__}); "
                    f"proceeding on static thresholds only.",
        }


# ---------------------------------------------------------------------------
# Final assembly -- combines all three upstream dimensions
# ---------------------------------------------------------------------------

def finalize_analysis(
    job_id: str,
    application: str,
    scenario: str,
    quality_report: dict,
    findings: Optional[List[dict]] = None,
    infra_health: Optional[dict] = None,
    security_summary: Optional[dict] = None,
    summary: str = "",
    test_case_prompt: Optional[str] = None,
) -> dict:
    """
    Assembles and VALIDATES the final AnalysisOutput. Overall status is the
    WORST of: performance (api_findings), infra health, and security -- a
    security FAIL should not be hidden by a clean performance run, and vice
    versa. Call this last, and return its result as your final answer.

    test_case_prompt: the user's original request text, passed through
    unmodified so the Report Agent can include it in the final report.
    """
    findings = findings or []

    if quality_report["status"] == "invalid":
        critical_issues = [i["issue"] for i in quality_report["issues"] if i["severity"] == "critical"]
        output = AnalysisOutput(
            job_id=job_id, application=application, scenario=scenario,
            test_case_prompt=test_case_prompt,
            data_quality_status="invalid",
            data_quality_issues=[DataQualityIssue(**i) for i in quality_report["issues"]],
            unusable_reason="; ".join(critical_issues) or "Data failed quality validation.",
            ready_for_report=False,
        )
        return output.model_dump()

    api_findings = [ApiFinding(**f) for f in findings]

    status_rank = {"pass": 0, "warning": 1, "fail": 2}
    statuses = [f.status for f in api_findings]
    worst = max((status_rank.get(s, 0) for s in statuses), default=0)

    infra_obj = None
    if infra_health:
        infra_obj = InfraHealthFinding(**infra_health)
        worst = max(worst, status_rank.get(infra_obj.status, 0))

    security_obj = None
    if security_summary:
        security_obj = SecuritySummary(**security_summary)
        sec_status = security_obj.status.lower()
        sec_rank = {"pass": 0, "warning": 1, "fail": 2}.get(sec_status, 1)  # unknown security status -> treat as warning, not silently pass
        worst = max(worst, sec_rank)

    overall = {0: "pass", 1: "warning", 2: "fail"}[worst]

    output = AnalysisOutput(
        job_id=job_id, application=application, scenario=scenario,
        test_case_prompt=test_case_prompt,
        data_quality_status="valid",
        data_quality_issues=[DataQualityIssue(**i) for i in quality_report["issues"]],
        overall_status=overall,
        api_findings=api_findings,
        infra_health=infra_obj,
        security_summary=security_obj,
        summary=summary,
        ready_for_report=True,
    )
    return output.model_dump()





















# """
# Tools for the Analysis Agent.

# As before: every number that matters is computed here in plain Python,
# not left to the LLM. The LLM's job is to call these in order, read the
# results, add narrative bits informed by RAG context, and call
# finalize_analysis() last.

# Three separate validation/analysis functions now, one per upstream agent,
# because they measure different things at different granularities:
#   validate_data_quality / analyze_metrics   <- test_execution_agent (per-API)
#   analyze_infra_health                      <- monitoring_agent (per-job snapshot)
#   summarize_security                        <- security_agent (per-job summary)
# """

# from typing import Any, List, Optional

# from .schemas import (
#     AnalysisOutput,
#     ApiFinding,
#     DataQualityIssue,
#     InfraHealthFinding,
#     SecuritySummary,
# )

# # ---------------------------------------------------------------------------
# # Thresholds -- tune these to your SLAs, or load from app/config.py instead.
# # ---------------------------------------------------------------------------
# THRESHOLDS = {
#     "error_rate_pct": 1.0,
#     "p95_avg_ratio": 3.0,
#     "max_p95_ratio": 2.0,
#     "min_throughput": 1.0,
#     "expected_http_status": 200,
#     "mismatch_tolerance_pct": 1.0,
#     "cpu_usage_pct": 80.0,          # infra: CPU above this -> warning
#     "memory_usage_pct": 85.0,       # infra: memory above this -> warning
#     "db_connections_max": 200.0,    # infra: connection pool ceiling -- adjust to your real pool size
#     "response_time_cross_check_pct": 20.0,  # infra vs test_execution response time disagreement tolerance
# }


# def _normalize_error_rate(error_rate: float) -> float:
#     """error_rate may arrive as a fraction (0.02) or a percent (2.0)."""
#     return error_rate * 100 if error_rate <= 1 else error_rate


# # ---------------------------------------------------------------------------
# # test_execution_agent -> data quality + per-API metric analysis (unchanged logic)
# # ---------------------------------------------------------------------------

# def validate_data_quality(records: List[dict]) -> dict:
#     """Checks each test_execution_agent record for internal consistency.
#     Returns {"status": "valid"|"invalid", "issues": [...]}."""
#     issues: List[dict] = []

#     if not records:
#         return {
#             "status": "invalid",
#             "issues": [{
#                 "field": "records",
#                 "issue": "No test_execution records were provided for this job.",
#                 "severity": "critical",
#             }],
#         }

#     for r in records:
#         api = r.get("api_name", "unknown")
#         total = r.get("total_requests", 0)
#         success = r.get("successful_requests", 0)
#         failed = r.get("failed_requests", 0)
#         avg = r.get("avg_response_time", 0)
#         p95 = r.get("p95_response_time", 0)
#         mx = r.get("max_response_time", 0)
#         err = r.get("error_rate", 0)

#         for field in ("total_requests", "successful_requests", "failed_requests",
#                       "avg_response_time", "p95_response_time",
#                       "max_response_time", "throughput", "error_rate"):
#             if r.get(field, 0) < 0:
#                 issues.append({"api_name": api, "field": field,
#                                 "issue": f"{field} is negative ({r.get(field)}).",
#                                 "severity": "critical"})

#         if total == 0:
#             issues.append({"api_name": api, "field": "total_requests",
#                             "issue": "total_requests is 0 -- no data to analyze for this API.",
#                             "severity": "critical"})
#             continue

#         if success + failed != total:
#             issues.append({
#                 "api_name": api, "field": "total_requests",
#                 "issue": (f"successful_requests ({success}) + failed_requests "
#                           f"({failed}) = {success + failed}, which does not "
#                           f"match total_requests ({total})."),
#                 "severity": "critical",
#             })

#         expected_err = (failed / total) * 100
#         actual_err = _normalize_error_rate(err)
#         if abs(expected_err - actual_err) > THRESHOLDS["mismatch_tolerance_pct"]:
#             issues.append({
#                 "api_name": api, "field": "error_rate",
#                 "issue": (f"Reported error_rate ({actual_err:.2f}%) doesn't match "
#                           f"failed/total ({expected_err:.2f}%)."),
#                 "severity": "warning",
#             })

#         if p95 < avg:
#             issues.append({"api_name": api, "field": "p95_response_time",
#                             "issue": f"p95 ({p95}ms) is lower than avg ({avg}ms).",
#                             "severity": "warning"})
#         if mx < p95:
#             issues.append({"api_name": api, "field": "max_response_time",
#                             "issue": f"max ({mx}ms) is lower than p95 ({p95}ms).",
#                             "severity": "warning"})

#     has_critical = any(i["severity"] == "critical" for i in issues)
#     return {"status": "invalid" if has_critical else "valid", "issues": issues}


# def analyze_metrics(records: List[dict]) -> dict:
#     """Runs threshold checks per API from test_execution_agent's records.
#     Only call after validate_data_quality() returns status "valid"."""
#     findings = []
#     for r in records:
#         api = r.get("api_name", "unknown")
#         avg = r.get("avg_response_time", 0)
#         p95 = r.get("p95_response_time", 0)
#         mx = r.get("max_response_time", 0)
#         throughput = r.get("throughput", 0)
#         err = _normalize_error_rate(r.get("error_rate", 0))
#         status_code = r.get("http_status", 200)

#         anomalies = []
#         breached = []

#         if err > THRESHOLDS["error_rate_pct"]:
#             anomalies.append(f"Error rate {err:.2f}% exceeds {THRESHOLDS['error_rate_pct']}% threshold.")
#             breached.append("error_rate")

#         if avg > 0 and p95 / avg > THRESHOLDS["p95_avg_ratio"]:
#             anomalies.append(
#                 f"p95 ({p95}ms) is {p95/avg:.1f}x the average ({avg}ms) -- "
#                 f"wide latency variance / possible tail contention."
#             )
#             breached.append("p95_avg_ratio")

#         if p95 > 0 and mx / p95 > THRESHOLDS["max_p95_ratio"]:
#             anomalies.append(
#                 f"Max response time ({mx}ms) is {mx/p95:.1f}x p95 ({p95}ms) -- "
#                 f"outlier spikes present."
#             )
#             breached.append("max_p95_ratio")

#         if throughput < THRESHOLDS["min_throughput"]:
#             anomalies.append(f"Throughput {throughput} req/s is below the "
#                               f"{THRESHOLDS['min_throughput']} req/s floor.")
#             breached.append("min_throughput")

#         if status_code != THRESHOLDS["expected_http_status"]:
#             anomalies.append(f"Unexpected HTTP status {status_code} "
#                               f"(expected {THRESHOLDS['expected_http_status']}).")
#             breached.append("http_status")

#         if not breached:
#             severity, status = "low", "pass"
#         elif "error_rate" in breached or "http_status" in breached:
#             severity, status = ("critical" if err > THRESHOLDS["error_rate_pct"] * 5 else "high"), "fail"
#         elif len(breached) >= 2:
#             severity, status = "high", "warning"
#         else:
#             severity, status = "medium", "warning"

#         findings.append({
#             "api_name": api,
#             "status": status,
#             "severity": severity,
#             "metrics": {
#                 "avg_response_time": avg, "p95_response_time": p95,
#                 "max_response_time": mx, "throughput": throughput,
#                 "error_rate_pct": round(err, 2), "http_status": status_code,
#             },
#             "anomalies": anomalies,
#             "thresholds_breached": breached,
#         })
#     return {"findings": findings}


# # ---------------------------------------------------------------------------
# # monitoring_agent -> infra health analysis (NEW)
# # ---------------------------------------------------------------------------

# def analyze_infra_health(monitoring_result: dict, test_execution_avg_response_time: Optional[float] = None) -> dict:
#     """
#     Analyzes monitoring_agent's single job-level snapshot. Also cross-checks
#     monitoring's own response_time against test_execution's avg_response_time
#     -- these come from different measurement points (infra vs. client-side),
#     so a big disagreement is itself worth flagging, not silently trusted.

#     test_execution_avg_response_time: pass the average of avg_response_time
#     across all API records for this job (compute it yourself from the
#     test_execution records, or pass None to skip the cross-check).
#     """
#     cpu = monitoring_result.get("cpu_usage", 0)
#     mem = monitoring_result.get("memory_usage", 0)
#     db_conn = monitoring_result.get("db_connections", 0)
#     tps = monitoring_result.get("tps", 0)
#     mon_response_time = monitoring_result.get("response_time", 0)
#     mon_status = monitoring_result.get("status", "unknown")
#     alerts = monitoring_result.get("alerts", [])

#     anomalies = []
#     if cpu > THRESHOLDS["cpu_usage_pct"]:
#         anomalies.append(f"CPU usage {cpu}% exceeds {THRESHOLDS['cpu_usage_pct']}% threshold.")
#     if mem > THRESHOLDS["memory_usage_pct"]:
#         anomalies.append(f"Memory usage {mem}% exceeds {THRESHOLDS['memory_usage_pct']}% threshold.")
#     if db_conn > THRESHOLDS["db_connections_max"]:
#         anomalies.append(f"DB connections {db_conn} exceeds pool ceiling of {THRESHOLDS['db_connections_max']}.")
#     if alerts:
#         anomalies.append(f"{len(alerts)} monitoring alert(s) reported: {alerts}")

#     cross_check_note = None
#     if test_execution_avg_response_time is not None and test_execution_avg_response_time > 0:
#         diff_pct = abs(mon_response_time - test_execution_avg_response_time) / test_execution_avg_response_time * 100
#         if diff_pct > THRESHOLDS["response_time_cross_check_pct"]:
#             cross_check_note = (
#                 f"monitoring_agent's response_time ({mon_response_time}ms) disagrees with "
#                 f"test_execution_agent's avg_response_time ({test_execution_avg_response_time}ms) "
#                 f"by {diff_pct:.0f}% -- worth checking measurement points/clock sync."
#             )

#     if any("exceeds" in a for a in anomalies) and (cpu > THRESHOLDS["cpu_usage_pct"] or mem > THRESHOLDS["memory_usage_pct"]):
#         status = "fail" if (cpu > 95 or mem > 95) else "warning"
#     elif anomalies:
#         status = "warning"
#     else:
#         status = "pass"

#     return {
#         "status": status,
#         "monitoring_reported_status": mon_status,
#         "cpu_usage": cpu, "memory_usage": mem, "db_connections": db_conn,
#         "tps": tps, "monitoring_response_time": mon_response_time,
#         "alerts": alerts, "anomalies": anomalies, "cross_check_note": cross_check_note,
#     }


# # ---------------------------------------------------------------------------
# # security_agent -> pass-through summary (NEW)
# # ---------------------------------------------------------------------------

# def summarize_security(security_result: dict) -> dict:
#     """
#     Mostly a pass-through -- security_agent already did the analysis, this
#     agent's job is just to fold its verdict into the overall job status,
#     not to re-judge security findings itself.
#     """
#     return {
#         "status": security_result.get("status", "unknown"),
#         "security_score": security_result.get("security_score", "unknown"),
#         "issues": security_result.get("issues", []),
#         "recommendations": security_result.get("recommendations", []),
#     }


# # ---------------------------------------------------------------------------
# # RAG historical/knowledge lookup (unchanged interface)
# # ---------------------------------------------------------------------------

# def retrieve_historical_context(
#     application: str, scenario: str, api_name: str, anomaly_text: Optional[str] = None
# ) -> dict:
#     """Pulls comparable historical runs + relevant SLA/runbook/postmortem
#     content from app/rag/. Wrapped in try/except so the agent still works
#     if RAG is unreachable -- degrades to threshold-only analysis."""
#     try:
#         from app.rag.retriever import retrieve_context
#         result = retrieve_context(
#             application=application, scenario=scenario, api_name=api_name,
#             anomaly_text=anomaly_text, top_k=5,
#         )
#         return {"available": True, "context": result}
#     except Exception as e:  # noqa: BLE001
#         return {
#             "available": False,
#             "context": None,
#             "note": f"RAG context unavailable ({e.__class__.__name__}); "
#                     f"proceeding on static thresholds only.",
#         }


# # ---------------------------------------------------------------------------
# # Final assembly -- combines all three upstream dimensions
# # ---------------------------------------------------------------------------

# def finalize_analysis(
#     job_id: str,
#     application: str,
#     scenario: str,
#     quality_report: dict,
#     findings: Optional[List[dict]] = None,
#     infra_health: Optional[dict] = None,
#     security_summary: Optional[dict] = None,
#     summary: str = "",
# ) -> dict:
#     """
#     Assembles and VALIDATES the final AnalysisOutput. Overall status is the
#     WORST of: performance (api_findings), infra health, and security -- a
#     security FAIL should not be hidden by a clean performance run, and vice
#     versa. Call this last, and return its result as your final answer.
#     """
#     findings = findings or []

#     if quality_report["status"] == "invalid":
#         critical_issues = [i["issue"] for i in quality_report["issues"] if i["severity"] == "critical"]
#         output = AnalysisOutput(
#             job_id=job_id, application=application, scenario=scenario,
#             data_quality_status="invalid",
#             data_quality_issues=[DataQualityIssue(**i) for i in quality_report["issues"]],
#             unusable_reason="; ".join(critical_issues) or "Data failed quality validation.",
#             ready_for_report=False,
#         )
#         return output.model_dump()

#     api_findings = [ApiFinding(**f) for f in findings]

#     status_rank = {"pass": 0, "warning": 1, "fail": 2}
#     statuses = [f.status for f in api_findings]
#     worst = max((status_rank.get(s, 0) for s in statuses), default=0)

#     infra_obj = None
#     if infra_health:
#         infra_obj = InfraHealthFinding(**infra_health)
#         worst = max(worst, status_rank.get(infra_obj.status, 0))

#     security_obj = None
#     if security_summary:
#         security_obj = SecuritySummary(**security_summary)
#         sec_status = security_obj.status.lower()
#         sec_rank = {"pass": 0, "warning": 1, "fail": 2}.get(sec_status, 1)  # unknown security status -> treat as warning, not silently pass
#         worst = max(worst, sec_rank)

#     overall = {0: "pass", 1: "warning", 2: "fail"}[worst]

#     output = AnalysisOutput(
#         job_id=job_id, application=application, scenario=scenario,
#         data_quality_status="valid",
#         data_quality_issues=[DataQualityIssue(**i) for i in quality_report["issues"]],
#         overall_status=overall,
#         api_findings=api_findings,
#         infra_health=infra_obj,
#         security_summary=security_obj,
#         summary=summary,
#         ready_for_report=True,
#     )
#     return output.model_dump()





# """
# Tools for the Analysis Agent.

# As before: every number that matters is computed here in plain Python,
# not left to the LLM. The LLM's job is to call these in order, read the
# results, add narrative bits informed by RAG context, and call
# finalize_analysis() last.

# Three separate validation/analysis functions now, one per upstream agent,
# because they measure different things at different granularities:
#   validate_data_quality / analyze_metrics   <- test_execution_agent (per-API)
#   analyze_infra_health                      <- monitoring_agent (per-job snapshot)
#   summarize_security                        <- security_agent (per-job summary)
# """

# from typing import Any, List, Optional

# from .schemas import (
#     AnalysisOutput,
#     ApiFinding,
#     DataQualityIssue,
#     InfraHealthFinding,
#     SecuritySummary,
# )

# # ---------------------------------------------------------------------------
# # Thresholds -- tune these to your SLAs, or load from app/config.py instead.
# # ---------------------------------------------------------------------------
# THRESHOLDS = {
#     "error_rate_pct": 1.0,
#     "p95_avg_ratio": 3.0,
#     "max_p95_ratio": 2.0,
#     "min_throughput": 1.0,
#     "expected_http_status": 200,
#     "mismatch_tolerance_pct": 1.0,
#     "cpu_usage_pct": 80.0,          # infra: CPU above this -> warning
#     "memory_usage_pct": 85.0,       # infra: memory above this -> warning
#     "db_connections_max": 200.0,    # infra: connection pool ceiling -- adjust to your real pool size
#     "response_time_cross_check_pct": 20.0,  # infra vs test_execution response time disagreement tolerance
# }


# def _normalize_error_rate(error_rate: float) -> float:
#     """error_rate may arrive as a fraction (0.02) or a percent (2.0)."""
#     return error_rate * 100 if error_rate <= 1 else error_rate


# # ---------------------------------------------------------------------------
# # test_execution_agent -> data quality + per-API metric analysis (unchanged logic)
# # ---------------------------------------------------------------------------

# def validate_data_quality(records: List[dict]) -> dict:
#     """Checks each test_execution_agent record for internal consistency.
#     Returns {"status": "valid"|"invalid", "issues": [...]}."""
#     issues: List[dict] = []

#     if not records:
#         return {
#             "status": "invalid",
#             "issues": [{
#                 "field": "records",
#                 "issue": "No test_execution records were provided for this job.",
#                 "severity": "critical",
#             }],
#         }

#     for r in records:
#         api = r.get("api_name", "unknown")
#         total = r.get("total_requests", 0)
#         success = r.get("successful_requests", 0)
#         failed = r.get("failed_requests", 0)
#         avg = r.get("avg_response_time", 0)
#         p95 = r.get("p95_response_time", 0)
#         mx = r.get("max_response_time", 0)
#         err = r.get("error_rate", 0)

#         for field in ("total_requests", "successful_requests", "failed_requests",
#                       "avg_response_time", "p95_response_time",
#                       "max_response_time", "throughput", "error_rate"):
#             if r.get(field, 0) < 0:
#                 issues.append({"api_name": api, "field": field,
#                                 "issue": f"{field} is negative ({r.get(field)}).",
#                                 "severity": "critical"})

#         if total == 0:
#             issues.append({"api_name": api, "field": "total_requests",
#                             "issue": "total_requests is 0 -- no data to analyze for this API.",
#                             "severity": "critical"})
#             continue

#         if success + failed != total:
#             issues.append({
#                 "api_name": api, "field": "total_requests",
#                 "issue": (f"successful_requests ({success}) + failed_requests "
#                           f"({failed}) = {success + failed}, which does not "
#                           f"match total_requests ({total})."),
#                 "severity": "critical",
#             })

#         expected_err = (failed / total) * 100
#         actual_err = _normalize_error_rate(err)
#         if abs(expected_err - actual_err) > THRESHOLDS["mismatch_tolerance_pct"]:
#             issues.append({
#                 "api_name": api, "field": "error_rate",
#                 "issue": (f"Reported error_rate ({actual_err:.2f}%) doesn't match "
#                           f"failed/total ({expected_err:.2f}%)."),
#                 "severity": "warning",
#             })

#         if p95 < avg:
#             issues.append({"api_name": api, "field": "p95_response_time",
#                             "issue": f"p95 ({p95}ms) is lower than avg ({avg}ms).",
#                             "severity": "warning"})
#         if mx < p95:
#             issues.append({"api_name": api, "field": "max_response_time",
#                             "issue": f"max ({mx}ms) is lower than p95 ({p95}ms).",
#                             "severity": "warning"})

#     has_critical = any(i["severity"] == "critical" for i in issues)
#     return {"status": "invalid" if has_critical else "valid", "issues": issues}


# def analyze_metrics(records: List[dict]) -> dict:
#     """Runs threshold checks per API from test_execution_agent's records.
#     Only call after validate_data_quality() returns status "valid"."""
#     findings = []
#     for r in records:
#         api = r.get("api_name", "unknown")
#         avg = r.get("avg_response_time", 0)
#         p95 = r.get("p95_response_time", 0)
#         mx = r.get("max_response_time", 0)
#         throughput = r.get("throughput", 0)
#         err = _normalize_error_rate(r.get("error_rate", 0))
#         status_code = r.get("http_status", 200)

#         anomalies = []
#         breached = []

#         if err > THRESHOLDS["error_rate_pct"]:
#             anomalies.append(f"Error rate {err:.2f}% exceeds {THRESHOLDS['error_rate_pct']}% threshold.")
#             breached.append("error_rate")

#         if avg > 0 and p95 / avg > THRESHOLDS["p95_avg_ratio"]:
#             anomalies.append(
#                 f"p95 ({p95}ms) is {p95/avg:.1f}x the average ({avg}ms) -- "
#                 f"wide latency variance / possible tail contention."
#             )
#             breached.append("p95_avg_ratio")

#         if p95 > 0 and mx / p95 > THRESHOLDS["max_p95_ratio"]:
#             anomalies.append(
#                 f"Max response time ({mx}ms) is {mx/p95:.1f}x p95 ({p95}ms) -- "
#                 f"outlier spikes present."
#             )
#             breached.append("max_p95_ratio")

#         if throughput < THRESHOLDS["min_throughput"]:
#             anomalies.append(f"Throughput {throughput} req/s is below the "
#                               f"{THRESHOLDS['min_throughput']} req/s floor.")
#             breached.append("min_throughput")

#         if status_code != THRESHOLDS["expected_http_status"]:
#             anomalies.append(f"Unexpected HTTP status {status_code} "
#                               f"(expected {THRESHOLDS['expected_http_status']}).")
#             breached.append("http_status")

#         if not breached:
#             severity, status = "low", "pass"
#         elif "error_rate" in breached or "http_status" in breached:
#             severity, status = ("critical" if err > THRESHOLDS["error_rate_pct"] * 5 else "high"), "fail"
#         elif len(breached) >= 2:
#             severity, status = "high", "warning"
#         else:
#             severity, status = "medium", "warning"

#         findings.append({
#             "api_name": api,
#             "status": status,
#             "severity": severity,
#             "metrics": {
#                 "avg_response_time": avg, "p95_response_time": p95,
#                 "max_response_time": mx, "throughput": throughput,
#                 "error_rate_pct": round(err, 2), "http_status": status_code,
#             },
#             "anomalies": anomalies,
#             "thresholds_breached": breached,
#         })
#     return {"findings": findings}


# # ---------------------------------------------------------------------------
# # monitoring_agent -> infra health analysis (NEW)
# # ---------------------------------------------------------------------------

# def analyze_infra_health(monitoring_result: dict, test_execution_avg_response_time: Optional[float] = None) -> dict:
#     """
#     Analyzes monitoring_agent's single job-level snapshot. Also cross-checks
#     monitoring's own response_time against test_execution's avg_response_time
#     -- these come from different measurement points (infra vs. client-side),
#     so a big disagreement is itself worth flagging, not silently trusted.

#     test_execution_avg_response_time: pass the average of avg_response_time
#     across all API records for this job (compute it yourself from the
#     test_execution records, or pass None to skip the cross-check).
#     """
#     cpu = monitoring_result.get("cpu_usage", 0)
#     mem = monitoring_result.get("memory_usage", 0)
#     db_conn = monitoring_result.get("db_connections", 0)
#     tps = monitoring_result.get("tps", 0)
#     mon_response_time = monitoring_result.get("response_time", 0)
#     mon_status = monitoring_result.get("status", "unknown")
#     alerts = monitoring_result.get("alerts", [])

#     anomalies = []
#     if cpu > THRESHOLDS["cpu_usage_pct"]:
#         anomalies.append(f"CPU usage {cpu}% exceeds {THRESHOLDS['cpu_usage_pct']}% threshold.")
#     if mem > THRESHOLDS["memory_usage_pct"]:
#         anomalies.append(f"Memory usage {mem}% exceeds {THRESHOLDS['memory_usage_pct']}% threshold.")
#     if db_conn > THRESHOLDS["db_connections_max"]:
#         anomalies.append(f"DB connections {db_conn} exceeds pool ceiling of {THRESHOLDS['db_connections_max']}.")
#     if alerts:
#         anomalies.append(f"{len(alerts)} monitoring alert(s) reported: {alerts}")

#     cross_check_note = None
#     if test_execution_avg_response_time is not None and test_execution_avg_response_time > 0:
#         diff_pct = abs(mon_response_time - test_execution_avg_response_time) / test_execution_avg_response_time * 100
#         if diff_pct > THRESHOLDS["response_time_cross_check_pct"]:
#             cross_check_note = (
#                 f"monitoring_agent's response_time ({mon_response_time}ms) disagrees with "
#                 f"test_execution_agent's avg_response_time ({test_execution_avg_response_time}ms) "
#                 f"by {diff_pct:.0f}% -- worth checking measurement points/clock sync."
#             )

#     if any("exceeds" in a for a in anomalies) and (cpu > THRESHOLDS["cpu_usage_pct"] or mem > THRESHOLDS["memory_usage_pct"]):
#         status = "fail" if (cpu > 95 or mem > 95) else "warning"
#     elif anomalies:
#         status = "warning"
#     else:
#         status = "pass"

#     return {
#         "status": status,
#         "monitoring_reported_status": mon_status,
#         "cpu_usage": cpu, "memory_usage": mem, "db_connections": db_conn,
#         "tps": tps, "monitoring_response_time": mon_response_time,
#         "alerts": alerts, "anomalies": anomalies, "cross_check_note": cross_check_note,
#     }


# # ---------------------------------------------------------------------------
# # security_agent -> pass-through summary (NEW)
# # ---------------------------------------------------------------------------

# def summarize_security(security_result: dict) -> dict:
#     """
#     Mostly a pass-through -- security_agent already did the analysis, this
#     agent's job is just to fold its verdict into the overall job status,
#     not to re-judge security findings itself.
#     """
#     return {
#         "status": security_result.get("status", "unknown"),
#         "security_score": security_result.get("security_score", "unknown"),
#         "issues": security_result.get("issues", []),
#         "recommendations": security_result.get("recommendations", []),
#     }


# # ---------------------------------------------------------------------------
# # RAG historical/knowledge lookup (unchanged interface)
# # ---------------------------------------------------------------------------

# def retrieve_historical_context(
#     application: str, scenario: str, api_name: str, anomaly_text: Optional[str] = None
# ) -> dict:
#     """Pulls comparable historical runs + relevant SLA/runbook/postmortem
#     content from app/rag/. Wrapped in try/except so the agent still works
#     if RAG is unreachable -- degrades to threshold-only analysis."""
#     try:
#         from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.rag.retriever import retrieve_context
#         result = retrieve_context(
#             application=application, scenario=scenario, api_name=api_name,
#             anomaly_text=anomaly_text, top_k=5,
#         )
#         return {"available": True, "context": result}
#     except Exception as e:  # noqa: BLE001
#         return {
#             "available": False,
#             "context": None,
#             "note": f"RAG context unavailable ({e.__class__.__name__}); "
#                     f"proceeding on static thresholds only.",
#         }


# # ---------------------------------------------------------------------------
# # Final assembly -- combines all three upstream dimensions
# # ---------------------------------------------------------------------------

# def finalize_analysis(
#     job_id: str,
#     application: str,
#     scenario: str,
#     quality_report: dict,
#     findings: Optional[List[dict]] = None,
#     infra_health: Optional[dict] = None,
#     security_summary: Optional[dict] = None,
#     summary: str = "",
# ) -> dict:
#     """
#     Assembles and VALIDATES the final AnalysisOutput. Overall status is the
#     WORST of: performance (api_findings), infra health, and security -- a
#     security FAIL should not be hidden by a clean performance run, and vice
#     versa. Call this last, and return its result as your final answer.
#     """
#     findings = findings or []

#     if quality_report["status"] == "invalid":
#         critical_issues = [i["issue"] for i in quality_report["issues"] if i["severity"] == "critical"]
#         output = AnalysisOutput(
#             job_id=job_id, application=application, scenario=scenario,
#             data_quality_status="invalid",
#             data_quality_issues=[DataQualityIssue(**i) for i in quality_report["issues"]],
#             unusable_reason="; ".join(critical_issues) or "Data failed quality validation.",
#             ready_for_report=False,
#         )
#         return output.model_dump()

#     api_findings = [ApiFinding(**f) for f in findings]

#     status_rank = {"pass": 0, "warning": 1, "fail": 2}
#     statuses = [f.status for f in api_findings]
#     worst = max((status_rank.get(s, 0) for s in statuses), default=0)

#     infra_obj = None
#     if infra_health:
#         infra_obj = InfraHealthFinding(**infra_health)
#         worst = max(worst, status_rank.get(infra_obj.status, 0))

#     security_obj = None
#     if security_summary:
#         security_obj = SecuritySummary(**security_summary)
#         sec_status = security_obj.status.lower()
#         sec_rank = {"pass": 0, "warning": 1, "fail": 2}.get(sec_status, 1)  # unknown security status -> treat as warning, not silently pass
#         worst = max(worst, sec_rank)

#     overall = {0: "pass", 1: "warning", 2: "fail"}[worst]

#     output = AnalysisOutput(
#         job_id=job_id, application=application, scenario=scenario,
#         data_quality_status="valid",
#         data_quality_issues=[DataQualityIssue(**i) for i in quality_report["issues"]],
#         overall_status=overall,
#         api_findings=api_findings,
#         infra_health=infra_obj,
#         security_summary=security_obj,
#         summary=summary,
#         ready_for_report=True,
#     )
#     return output.model_dump()





















# # """
# # Tools for the Analysis Agent.

# # As before: every number that matters is computed here in plain Python,
# # not left to the LLM. The LLM's job is to call these in order, read the
# # results, add narrative bits informed by RAG context, and call
# # finalize_analysis() last.

# # Three separate validation/analysis functions now, one per upstream agent,
# # because they measure different things at different granularities:
# #   validate_data_quality / analyze_metrics   <- test_execution_agent (per-API)
# #   analyze_infra_health                      <- monitoring_agent (per-job snapshot)
# #   summarize_security                        <- security_agent (per-job summary)
# # """

# # from typing import Any, List, Optional

# # from .schemas import (
# #     AnalysisOutput,
# #     ApiFinding,
# #     DataQualityIssue,
# #     InfraHealthFinding,
# #     SecuritySummary,
# # )

# # # ---------------------------------------------------------------------------
# # # Thresholds -- tune these to your SLAs, or load from app/config.py instead.
# # # ---------------------------------------------------------------------------
# # THRESHOLDS = {
# #     "error_rate_pct": 1.0,
# #     "p95_avg_ratio": 3.0,
# #     "max_p95_ratio": 2.0,
# #     "min_throughput": 1.0,
# #     "expected_http_status": 200,
# #     "mismatch_tolerance_pct": 1.0,
# #     "cpu_usage_pct": 80.0,          # infra: CPU above this -> warning
# #     "memory_usage_pct": 85.0,       # infra: memory above this -> warning
# #     "db_connections_max": 200.0,    # infra: connection pool ceiling -- adjust to your real pool size
# #     "response_time_cross_check_pct": 20.0,  # infra vs test_execution response time disagreement tolerance
# # }


# # def _normalize_error_rate(error_rate: float) -> float:
# #     """error_rate may arrive as a fraction (0.02) or a percent (2.0)."""
# #     return error_rate * 100 if error_rate <= 1 else error_rate


# # # ---------------------------------------------------------------------------
# # # test_execution_agent -> data quality + per-API metric analysis (unchanged logic)
# # # ---------------------------------------------------------------------------

# # def validate_data_quality(records: List[dict]) -> dict:
# #     """Checks each test_execution_agent record for internal consistency.
# #     Returns {"status": "valid"|"invalid", "issues": [...]}."""
# #     issues: List[dict] = []

# #     if not records:
# #         return {
# #             "status": "invalid",
# #             "issues": [{
# #                 "field": "records",
# #                 "issue": "No test_execution records were provided for this job.",
# #                 "severity": "critical",
# #             }],
# #         }

# #     for r in records:
# #         api = r.get("api_name", "unknown")
# #         total = r.get("total_requests", 0)
# #         success = r.get("successful_requests", 0)
# #         failed = r.get("failed_requests", 0)
# #         avg = r.get("avg_response_time", 0)
# #         p95 = r.get("p95_response_time", 0)
# #         mx = r.get("max_response_time", 0)
# #         err = r.get("error_rate", 0)

# #         for field in ("total_requests", "successful_requests", "failed_requests",
# #                       "avg_response_time", "p95_response_time",
# #                       "max_response_time", "throughput", "error_rate"):
# #             if r.get(field, 0) < 0:
# #                 issues.append({"api_name": api, "field": field,
# #                                 "issue": f"{field} is negative ({r.get(field)}).",
# #                                 "severity": "critical"})

# #         if total == 0:
# #             issues.append({"api_name": api, "field": "total_requests",
# #                             "issue": "total_requests is 0 -- no data to analyze for this API.",
# #                             "severity": "critical"})
# #             continue

# #         if success + failed != total:
# #             issues.append({
# #                 "api_name": api, "field": "total_requests",
# #                 "issue": (f"successful_requests ({success}) + failed_requests "
# #                           f"({failed}) = {success + failed}, which does not "
# #                           f"match total_requests ({total})."),
# #                 "severity": "critical",
# #             })

# #         expected_err = (failed / total) * 100
# #         actual_err = _normalize_error_rate(err)
# #         if abs(expected_err - actual_err) > THRESHOLDS["mismatch_tolerance_pct"]:
# #             issues.append({
# #                 "api_name": api, "field": "error_rate",
# #                 "issue": (f"Reported error_rate ({actual_err:.2f}%) doesn't match "
# #                           f"failed/total ({expected_err:.2f}%)."),
# #                 "severity": "warning",
# #             })

# #         if p95 < avg:
# #             issues.append({"api_name": api, "field": "p95_response_time",
# #                             "issue": f"p95 ({p95}ms) is lower than avg ({avg}ms).",
# #                             "severity": "warning"})
# #         if mx < p95:
# #             issues.append({"api_name": api, "field": "max_response_time",
# #                             "issue": f"max ({mx}ms) is lower than p95 ({p95}ms).",
# #                             "severity": "warning"})

# #     has_critical = any(i["severity"] == "critical" for i in issues)
# #     return {"status": "invalid" if has_critical else "valid", "issues": issues}


# # def analyze_metrics(records: List[dict]) -> dict:
# #     """Runs threshold checks per API from test_execution_agent's records.
# #     Only call after validate_data_quality() returns status "valid"."""
# #     findings = []
# #     for r in records:
# #         api = r.get("api_name", "unknown")
# #         avg = r.get("avg_response_time", 0)
# #         p95 = r.get("p95_response_time", 0)
# #         mx = r.get("max_response_time", 0)
# #         throughput = r.get("throughput", 0)
# #         err = _normalize_error_rate(r.get("error_rate", 0))
# #         status_code = r.get("http_status", 200)

# #         anomalies = []
# #         breached = []

# #         if err > THRESHOLDS["error_rate_pct"]:
# #             anomalies.append(f"Error rate {err:.2f}% exceeds {THRESHOLDS['error_rate_pct']}% threshold.")
# #             breached.append("error_rate")

# #         if avg > 0 and p95 / avg > THRESHOLDS["p95_avg_ratio"]:
# #             anomalies.append(
# #                 f"p95 ({p95}ms) is {p95/avg:.1f}x the average ({avg}ms) -- "
# #                 f"wide latency variance / possible tail contention."
# #             )
# #             breached.append("p95_avg_ratio")

# #         if p95 > 0 and mx / p95 > THRESHOLDS["max_p95_ratio"]:
# #             anomalies.append(
# #                 f"Max response time ({mx}ms) is {mx/p95:.1f}x p95 ({p95}ms) -- "
# #                 f"outlier spikes present."
# #             )
# #             breached.append("max_p95_ratio")

# #         if throughput < THRESHOLDS["min_throughput"]:
# #             anomalies.append(f"Throughput {throughput} req/s is below the "
# #                               f"{THRESHOLDS['min_throughput']} req/s floor.")
# #             breached.append("min_throughput")

# #         if status_code != THRESHOLDS["expected_http_status"]:
# #             anomalies.append(f"Unexpected HTTP status {status_code} "
# #                               f"(expected {THRESHOLDS['expected_http_status']}).")
# #             breached.append("http_status")

# #         if not breached:
# #             severity, status = "low", "pass"
# #         elif "error_rate" in breached or "http_status" in breached:
# #             severity, status = ("critical" if err > THRESHOLDS["error_rate_pct"] * 5 else "high"), "fail"
# #         elif len(breached) >= 2:
# #             severity, status = "high", "warning"
# #         else:
# #             severity, status = "medium", "warning"

# #         findings.append({
# #             "api_name": api,
# #             "status": status,
# #             "severity": severity,
# #             "metrics": {
# #                 "avg_response_time": avg, "p95_response_time": p95,
# #                 "max_response_time": mx, "throughput": throughput,
# #                 "error_rate_pct": round(err, 2), "http_status": status_code,
# #             },
# #             "anomalies": anomalies,
# #             "thresholds_breached": breached,
# #         })
# #     return {"findings": findings}


# # # ---------------------------------------------------------------------------
# # # monitoring_agent -> infra health analysis (NEW)
# # # ---------------------------------------------------------------------------

# # def analyze_infra_health(monitoring_result: dict, test_execution_avg_response_time: Optional[float] = None) -> dict:
# #     """
# #     Analyzes monitoring_agent's single job-level snapshot. Also cross-checks
# #     monitoring's own response_time against test_execution's avg_response_time
# #     -- these come from different measurement points (infra vs. client-side),
# #     so a big disagreement is itself worth flagging, not silently trusted.

# #     test_execution_avg_response_time: pass the average of avg_response_time
# #     across all API records for this job (compute it yourself from the
# #     test_execution records, or pass None to skip the cross-check).
# #     """
# #     cpu = monitoring_result.get("cpu_usage", 0)
# #     mem = monitoring_result.get("memory_usage", 0)
# #     db_conn = monitoring_result.get("db_connections", 0)
# #     tps = monitoring_result.get("tps", 0)
# #     mon_response_time = monitoring_result.get("response_time", 0)
# #     mon_status = monitoring_result.get("status", "unknown")
# #     alerts = monitoring_result.get("alerts", [])

# #     anomalies = []
# #     if cpu > THRESHOLDS["cpu_usage_pct"]:
# #         anomalies.append(f"CPU usage {cpu}% exceeds {THRESHOLDS['cpu_usage_pct']}% threshold.")
# #     if mem > THRESHOLDS["memory_usage_pct"]:
# #         anomalies.append(f"Memory usage {mem}% exceeds {THRESHOLDS['memory_usage_pct']}% threshold.")
# #     if db_conn > THRESHOLDS["db_connections_max"]:
# #         anomalies.append(f"DB connections {db_conn} exceeds pool ceiling of {THRESHOLDS['db_connections_max']}.")
# #     if alerts:
# #         anomalies.append(f"{len(alerts)} monitoring alert(s) reported: {alerts}")

# #     cross_check_note = None
# #     if test_execution_avg_response_time is not None and test_execution_avg_response_time > 0:
# #         diff_pct = abs(mon_response_time - test_execution_avg_response_time) / test_execution_avg_response_time * 100
# #         if diff_pct > THRESHOLDS["response_time_cross_check_pct"]:
# #             cross_check_note = (
# #                 f"monitoring_agent's response_time ({mon_response_time}ms) disagrees with "
# #                 f"test_execution_agent's avg_response_time ({test_execution_avg_response_time}ms) "
# #                 f"by {diff_pct:.0f}% -- worth checking measurement points/clock sync."
# #             )

# #     if any("exceeds" in a for a in anomalies) and (cpu > THRESHOLDS["cpu_usage_pct"] or mem > THRESHOLDS["memory_usage_pct"]):
# #         status = "fail" if (cpu > 95 or mem > 95) else "warning"
# #     elif anomalies:
# #         status = "warning"
# #     else:
# #         status = "pass"

# #     return {
# #         "status": status,
# #         "monitoring_reported_status": mon_status,
# #         "cpu_usage": cpu, "memory_usage": mem, "db_connections": db_conn,
# #         "tps": tps, "monitoring_response_time": mon_response_time,
# #         "alerts": alerts, "anomalies": anomalies, "cross_check_note": cross_check_note,
# #     }


# # # ---------------------------------------------------------------------------
# # # security_agent -> pass-through summary (NEW)
# # # ---------------------------------------------------------------------------

# # def summarize_security(security_result: dict) -> dict:
# #     """
# #     Mostly a pass-through -- security_agent already did the analysis, this
# #     agent's job is just to fold its verdict into the overall job status,
# #     not to re-judge security findings itself.
# #     """
# #     return {
# #         "status": security_result.get("status", "unknown"),
# #         "security_score": security_result.get("security_score", "unknown"),
# #         "issues": security_result.get("issues", []),
# #         "recommendations": security_result.get("recommendations", []),
# #     }


# # # ---------------------------------------------------------------------------
# # # RAG historical/knowledge lookup (unchanged interface)
# # # ---------------------------------------------------------------------------

# # def retrieve_historical_context(
# #     application: str, scenario: str, api_name: str, anomaly_text: Optional[str] = None
# # ) -> dict:
# #     """Pulls comparable historical runs + relevant SLA/runbook/postmortem
# #     content from app/rag/. Wrapped in try/except so the agent still works
# #     if RAG is unreachable -- degrades to threshold-only analysis."""
# #     try:
# #         from app.rag.retriever import retrieve_context
# #         result = retrieve_context(
# #             application=application, scenario=scenario, api_name=api_name,
# #             anomaly_text=anomaly_text, top_k=5,
# #         )
# #         return {"available": True, "context": result}
# #     except Exception as e:  # noqa: BLE001
# #         return {
# #             "available": False,
# #             "context": None,
# #             "note": f"RAG context unavailable ({e.__class__.__name__}); "
# #                     f"proceeding on static thresholds only.",
# #         }


# # # ---------------------------------------------------------------------------
# # # Final assembly -- combines all three upstream dimensions
# # # ---------------------------------------------------------------------------

# # def finalize_analysis(
# #     job_id: str,
# #     application: str,
# #     scenario: str,
# #     quality_report: dict,
# #     findings: Optional[List[dict]] = None,
# #     infra_health: Optional[dict] = None,
# #     security_summary: Optional[dict] = None,
# #     summary: str = "",
# # ) -> dict:
# #     """
# #     Assembles and VALIDATES the final AnalysisOutput. Overall status is the
# #     WORST of: performance (api_findings), infra health, and security -- a
# #     security FAIL should not be hidden by a clean performance run, and vice
# #     versa. Call this last, and return its result as your final answer.
# #     """
# #     findings = findings or []

# #     if quality_report["status"] == "invalid":
# #         critical_issues = [i["issue"] for i in quality_report["issues"] if i["severity"] == "critical"]
# #         output = AnalysisOutput(
# #             job_id=job_id, application=application, scenario=scenario,
# #             data_quality_status="invalid",
# #             data_quality_issues=[DataQualityIssue(**i) for i in quality_report["issues"]],
# #             unusable_reason="; ".join(critical_issues) or "Data failed quality validation.",
# #             ready_for_report=False,
# #         )
# #         return output.model_dump()

# #     api_findings = [ApiFinding(**f) for f in findings]

# #     status_rank = {"pass": 0, "warning": 1, "fail": 2}
# #     statuses = [f.status for f in api_findings]
# #     worst = max((status_rank.get(s, 0) for s in statuses), default=0)

# #     infra_obj = None
# #     if infra_health:
# #         infra_obj = InfraHealthFinding(**infra_health)
# #         worst = max(worst, status_rank.get(infra_obj.status, 0))

# #     security_obj = None
# #     if security_summary:
# #         security_obj = SecuritySummary(**security_summary)
# #         sec_status = security_obj.status.lower()
# #         sec_rank = {"pass": 0, "warning": 1, "fail": 2}.get(sec_status, 1)  # unknown security status -> treat as warning, not silently pass
# #         worst = max(worst, sec_rank)

# #     overall = {0: "pass", 1: "warning", 2: "fail"}[worst]

# #     output = AnalysisOutput(
# #         job_id=job_id, application=application, scenario=scenario,
# #         data_quality_status="valid",
# #         data_quality_issues=[DataQualityIssue(**i) for i in quality_report["issues"]],
# #         overall_status=overall,
# #         api_findings=api_findings,
# #         infra_health=infra_obj,
# #         security_summary=security_obj,
# #         summary=summary,
# #         ready_for_report=True,
# #     )
# #     return output.model_dump()

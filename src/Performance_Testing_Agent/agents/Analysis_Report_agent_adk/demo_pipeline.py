"""
Runs the Analysis -> Report pipeline using ONLY the deterministic tools
(no LLM, no ADK runtime needed) so you can sanity-check the data
contracts and file output before wiring the real agents into your
orchestrator.
 
Uses realistic sample data matching the real output shapes of
test_execution_agent, monitoring_agent, and security_agent.
 
Usage:
    python demo_pipeline.py
"""
import json
import sys
import os
 
sys.path.insert(0, os.path.dirname(__file__))
 
from app.agents.analysis.tools import (
    validate_data_quality, analyze_metrics, analyze_infra_health,
    summarize_security, finalize_analysis,
)
from app.agents.report.tools import build_report_sections, finalize_report
 
# --- Sample input, matching test_execution_agent's exact schema -----------
test_execution_results = [
    {
        "job_id": "JOB-1001", "application": "ANZ-Payments", "scenario": "peak_load",
        "api_name": "POST /payments", "total_requests": 10000,
        "successful_requests": 9820, "failed_requests": 180,
        "avg_response_time": 210.0, "p95_response_time": 890.0,
        "max_response_time": 2100.0, "throughput": 45.2,
        "error_rate": 1.8, "http_status": 200,
    },
    {
        "job_id": "JOB-1001", "application": "ANZ-Payments", "scenario": "peak_load",
        "api_name": "GET /accounts/{id}", "total_requests": 15000,
        "successful_requests": 14995, "failed_requests": 5,
        "avg_response_time": 60.0, "p95_response_time": 130.0,
        "max_response_time": 200.0, "throughput": 120.0,
        "error_rate": 0.03, "http_status": 200,
    },
]
 
# --- Sample input, matching monitoring_agent's exact schema ----------------
monitoring_result = {
    "job_id": "JOB-1001", "application": "ANZ-Payments", "scenario": "peak_load",
    "cpu_usage": 61.67, "memory_usage": 66.08, "db_connections": 151.92,
    "response_time": 466.25, "tps": 156.92, "status": "OK", "alerts": [],
}
 
# --- Sample input, matching security_agent's exact schema ------------------
security_result = {
    "status": "WARNING", "security_score": "80%",
    "issues": ["JWT expiry not enforced on retry endpoint"],
    "recommendations": ["Reject retried requests with expired JWTs at the gateway"],
}
 
# --- Step 1: test_execution_agent -> data quality + per-API metrics --------
quality = validate_data_quality(test_execution_results)
print("Data quality:", quality["status"])
 
if quality["status"] == "valid":
    findings = analyze_metrics(test_execution_results)["findings"]
 
    # --- Step 2: monitoring_agent -> infra health (cross-checked against test_execution) ---
    avg_rt = sum(r["avg_response_time"] for r in test_execution_results) / len(test_execution_results)
    infra = analyze_infra_health(monitoring_result, test_execution_avg_response_time=avg_rt)
    print("Infra status:", infra["status"])
 
    # --- Step 3: security_agent -> pass-through summary ---
    security = summarize_security(security_result)
    print("Security status:", security["status"])
 
    analysis_result = finalize_analysis(
        job_id="JOB-1001", application="ANZ-Payments", scenario="peak_load",
        quality_report=quality, findings=findings, infra_health=infra, security_summary=security,
        summary="Peak load run shows the payments API breaching the 1% error-rate "
                 "threshold with a heavy latency tail; account lookups are healthy. "
                 "Infra is within limits; one open security issue on JWT retry handling.",
    )
else:
    analysis_result = finalize_analysis(
        job_id="JOB-1001", application="ANZ-Payments", scenario="peak_load",
        quality_report=quality,
    )
 
print("\n--- AnalysisOutput (this is the Report Agent's input) ---")
print(json.dumps(analysis_result, indent=2))
 
# --- Step 4: Report Agent's tools -------------------------------------------
section_result = build_report_sections(
    job_id=analysis_result["job_id"],
    application=analysis_result["application"],
    scenario=analysis_result["scenario"],
    data_quality_status=analysis_result["data_quality_status"],
    unusable_reason=analysis_result.get("unusable_reason"),
    overall_status=analysis_result.get("overall_status"),
    api_findings=analysis_result.get("api_findings", []),
    infra_health=analysis_result.get("infra_health"),
    security_summary=analysis_result.get("security_summary"),
    summary=analysis_result.get("summary", ""),
)
 
report_result = finalize_report(
    job_id=analysis_result["job_id"],
    application=analysis_result["application"],
    scenario=analysis_result["scenario"],
    overall_status=analysis_result.get("overall_status"),
    sections=section_result["sections"],
    rejected=section_result["rejected"],
    requested_format="both",
)
 
print("\n--- ReportOutput ---")
print(json.dumps(report_result, indent=2))
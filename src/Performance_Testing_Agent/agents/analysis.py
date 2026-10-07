# """
# Analysis Agent -- reads test_execution_result, monitoring_result, and
# security_result from shared session state (written there by the other
# agents earlier in the same conversation), analyzes them, and writes
# analysis_result back to state. No arguments on the tool function, matching
# the convention already used by monitoring.py / report.py, so the LLM never
# has to retype numbers as tool-call arguments.

# Self-contained on purpose (no imports from a separate `app` package): the
# Test Execution Agent's own app.agent module is loaded via a sys.path
# insert that claims the top-level name `app`, and this project cannot also
# have a second, different `app` package without the two colliding. Keeping
# this file flat avoids that collision entirely.

# Schema note: test_execution_result's shape is guaranteed by
# app/analysis_agent/handoff.py's validate_analysis_payload() before it ever
# reaches session state -- in particular error_rate is already guaranteed to
# be a 0-100 percentage, never a raw fraction. The checks below re-verify
# this defensively (cheap, and protects against that validation ever
# changing upstream) but do not need to guess at error_rate's units.
# """

# from google.adk.agents import LlmAgent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.tools import ToolContext

# from ..config import LITELLM_MODEL_NAME, TEMPERATURE

# # Matches app/analysis_agent/handoff.py::EXPECTED_ANALYSIS_KEYS exactly --
# # used here to recognize whether test_execution_result actually IS a
# # performance-test payload, as opposed to a script/test-data/environment-prep
# # result or a rejection message (see tool_executor.py -- handle_test_request
# # can return any of several different shapes depending on what the user asked
# # the Test Execution Agent for).
# EXPECTED_TEST_EXECUTION_KEYS = {
#     "job_id", "application", "scenario", "api_name",
#     "total_requests", "successful_requests", "failed_requests",
#     "avg_response_time", "p95_response_time", "max_response_time",
#     "throughput", "error_rate", "http_status",
# }

# THRESHOLDS = {
#     "error_rate_pct": 1.0,
#     "p95_avg_ratio": 3.0,
#     "max_p95_ratio": 2.0,
#     "min_throughput": 1.0,
#     "expected_http_status": 200,
#     "cpu_usage_pct": 80.0,
#     "memory_usage_pct": 85.0,
#     "db_connections_max": 200.0,
#     "response_time_cross_check_pct": 20.0,
# }


# def _validate_test_execution_record(record: dict) -> dict:
#     """Defensive re-check of the record already validated by
#     handoff.py::validate_analysis_payload. Returns {"status": "valid"|"invalid", "issues": [...]}."""
#     issues = []
#     total = record.get("total_requests", 0)
#     success = record.get("successful_requests", 0)
#     failed = record.get("failed_requests", 0)

#     if total == 0:
#         issues.append("total_requests is 0 -- no data to analyze.")
#     elif success + failed != total:
#         issues.append(
#             f"successful_requests ({success}) + failed_requests ({failed}) "
#             f"!= total_requests ({total})."
#         )

#     for field in ("avg_response_time", "p95_response_time", "max_response_time",
#                   "throughput", "error_rate"):
#         if record.get(field, 0) < 0:
#             issues.append(f"{field} is negative ({record.get(field)}).")

#     return {"status": "invalid" if issues else "valid", "issues": issues}


# def _analyze_api_metrics(record: dict) -> dict:
#     """Threshold checks for one API record. error_rate is guaranteed to
#     already be a 0-100 percentage by handoff.py's validation, so no
#     normalization is needed here."""
#     avg = record.get("avg_response_time", 0)
#     p95 = record.get("p95_response_time", 0)
#     mx = record.get("max_response_time", 0)
#     throughput = record.get("throughput", 0)
#     err = record.get("error_rate", 0)
#     status_code = record.get("http_status", 200)

#     anomalies, breached = [], []

#     if err > THRESHOLDS["error_rate_pct"]:
#         anomalies.append(f"Error rate {err:.2f}% exceeds {THRESHOLDS['error_rate_pct']}% threshold.")
#         breached.append("error_rate")

#     if avg > 0 and p95 / avg > THRESHOLDS["p95_avg_ratio"]:
#         anomalies.append(f"p95 ({p95}ms) is {p95/avg:.1f}x the average ({avg}ms) -- wide latency variance.")
#         breached.append("p95_avg_ratio")

#     if p95 > 0 and mx / p95 > THRESHOLDS["max_p95_ratio"]:
#         anomalies.append(f"Max response time ({mx}ms) is {mx/p95:.1f}x p95 ({p95}ms) -- outlier spikes.")
#         breached.append("max_p95_ratio")

#     if throughput < THRESHOLDS["min_throughput"]:
#         anomalies.append(f"Throughput {throughput} req/s is below the {THRESHOLDS['min_throughput']} req/s floor.")
#         breached.append("min_throughput")

#     if status_code != THRESHOLDS["expected_http_status"]:
#         anomalies.append(f"Unexpected HTTP status {status_code}.")
#         breached.append("http_status")

#     if not breached:
#         severity, status = "low", "pass"
#     elif "error_rate" in breached or "http_status" in breached:
#         severity, status = ("critical" if err > THRESHOLDS["error_rate_pct"] * 5 else "high"), "fail"
#     elif len(breached) >= 2:
#         severity, status = "high", "warning"
#     else:
#         severity, status = "medium", "warning"

#     return {
#         "api_name": record.get("api_name", "unknown"),
#         "status": status, "severity": severity,
#         "metrics": {
#             "avg_response_time": avg, "p95_response_time": p95, "max_response_time": mx,
#             "throughput": throughput, "error_rate_pct": round(err, 2), "http_status": status_code,
#         },
#         "anomalies": anomalies, "thresholds_breached": breached,
#     }


# def _analyze_infra_health(monitoring_result: dict, test_execution_avg_response_time: float | None) -> dict:
#     cpu = monitoring_result.get("cpu_usage", 0)
#     mem = monitoring_result.get("memory_usage", 0)
#     db_conn = monitoring_result.get("db_connections", 0)
#     tps = monitoring_result.get("tps", 0)
#     mon_rt = monitoring_result.get("response_time", 0)
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
#     if test_execution_avg_response_time and test_execution_avg_response_time > 0:
#         diff_pct = abs(mon_rt - test_execution_avg_response_time) / test_execution_avg_response_time * 100
#         if diff_pct > THRESHOLDS["response_time_cross_check_pct"]:
#             cross_check_note = (
#                 f"monitoring's response_time ({mon_rt}ms) disagrees with test_execution's "
#                 f"avg_response_time ({test_execution_avg_response_time}ms) by {diff_pct:.0f}%."
#             )

#     if (cpu > THRESHOLDS["cpu_usage_pct"] or mem > THRESHOLDS["memory_usage_pct"]):
#         status = "fail" if (cpu > 95 or mem > 95) else "warning"
#     elif anomalies:
#         status = "warning"
#     else:
#         status = "pass"

#     return {
#         "status": status, "monitoring_reported_status": mon_status,
#         "cpu_usage": cpu, "memory_usage": mem, "db_connections": db_conn,
#         "tps": tps, "monitoring_response_time": mon_rt,
#         "alerts": alerts, "anomalies": anomalies, "cross_check_note": cross_check_note,
#     }


# def run_analysis(tool_context: ToolContext) -> dict:
#     """Analyzes performance-test, infra-monitoring, and security results
#     already collected earlier in this conversation. Takes no arguments --
#     reads test_execution_result, monitoring_result, and security_result
#     directly from shared session state, so it should only be called after
#     at least a performance test has actually been run. Stores its result
#     under "analysis_result"."""

#     print("===== Analysis Agent: run_analysis =====")

#     test_execution_result = tool_context.state.get("test_execution_result")
#     monitoring_result = tool_context.state.get("monitoring_result")
#     security_result = tool_context.state.get("security_result")

#     # Guard: test_execution_result might be from script/test-data/environment
#     # generation, or a rejection -- NOT real performance metrics. Only proceed
#     # if it actually has the shape handoff.py guarantees for a real test run.
#     if not test_execution_result or not EXPECTED_TEST_EXECUTION_KEYS.issubset(test_execution_result.keys()):
#         result = {
#             "status": "error",
#             "message": (
#                 "No valid performance test execution results were found in "
#                 "session state to analyze. Run an actual performance test "
#                 "(not just script generation, test-data generation, or "
#                 "environment preparation) before requesting analysis."
#             ),
#         }
#         tool_context.state["analysis_result"] = result
#         return result

#     quality = _validate_test_execution_record(test_execution_result)

#     if quality["status"] == "invalid":
#         result = {
#             "status": "rejected",
#             "data_quality_status": "invalid",
#             "unusable_reason": "; ".join(quality["issues"]),
#         }
#         tool_context.state["analysis_result"] = result
#         return result

#     api_finding = _analyze_api_metrics(test_execution_result)

#     status_rank = {"pass": 0, "warning": 1, "fail": 2}
#     worst = status_rank.get(api_finding["status"], 0)

#     infra_finding = None
#     if monitoring_result:
#         infra_finding = _analyze_infra_health(
#             monitoring_result, test_execution_result.get("avg_response_time")
#         )
#         worst = max(worst, status_rank.get(infra_finding["status"], 0))

#     security_summary = None
#     if security_result:
#         security_summary = {
#             "status": security_result.get("status", "unknown"),
#             "security_score": security_result.get("security_score", "unknown"),
#             "issues": security_result.get("issues", []),
#             "recommendations": security_result.get("recommendations", []),
#         }
#         sec_rank = {"pass": 0, "warning": 1, "fail": 2}.get(security_summary["status"].lower(), 1)
#         worst = max(worst, sec_rank)

#     overall_status = {0: "pass", 1: "warning", 2: "fail"}[worst]

#     result = {
#         "status": "Completed",
#         "data_quality_status": "valid",
#         "overall_status": overall_status,
#         "api_finding": api_finding,
#         "infra_health": infra_finding,
#         "security_summary": security_summary,
#     }

#     tool_context.state["analysis_result"] = result
#     return result


# analysis_agent = LlmAgent(
#     name="analysis_agent",
#     model=LiteLlm(
#         model=LITELLM_MODEL_NAME,
#         temperature=TEMPERATURE,
#     ),
#     mode="single_turn",  # call-and-return, like an ADK workflow node, not a sticky chat transfer
#     instruction=(
#         "You are the Analysis Agent for a Banking AI Performance Testing "
#         "System. Whenever you are asked for root cause analysis, "
#         "bottleneck detection, performance recommendations, SLA validation, "
#         "or historical comparison, call run_analysis (it takes no arguments "
#         "-- it reads prior results itself) and report back its exact "
#         "results. If it returns status 'error', tell the user a "
#         "performance test needs to be run first."
#     ),
#     description=(
#         "Analyzes previously collected test-execution, monitoring, and "
#         "security results to detect bottlenecks and recommend fixes."
#     ),
#     tools=[run_analysis],
# )
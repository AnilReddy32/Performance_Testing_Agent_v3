"""
Report Agent -- reads analysis_result (and the underlying test_execution/
monitoring/security results, for full detail) from shared session state,
generates a TXT/PDF report file, and writes report_result back to state.

Self-contained on purpose, same reasoning as analysis.py: avoids creating
a second top-level `app` package that would collide with Test Execution
Agent's own app.agent module (loaded via sys.path insert in orchestrator/agent.py).

RAG knowledge-base ingestion (closing the loop so this run becomes future
historical context) is intentionally NOT included yet -- that depends on
a separate module tree (app/rag/) that needs the same collision-safe
treatment applied to it first. This is a deliberate scope cut, not an
oversight; see the surrounding conversation for why.
"""

import os
from datetime import datetime, timezone

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext

from ..config import LITELLM_MODEL_NAME, TEMPERATURE, REPORT_PATH


def _build_sections(analysis_result: dict) -> list[dict]:
    if analysis_result.get("status") == "error":
        return [{
            "title": "Report Not Generated -- No Analysis Available",
            "content": analysis_result.get("message", "Analysis has not been run yet."),
        }]

    if analysis_result.get("data_quality_status") == "invalid":
        return [{
            "title": "Report Not Generated -- Invalid Data",
            "content": f"Reason: {analysis_result.get('unusable_reason', 'Data failed quality validation.')}",
        }]

    sections = []
    overall_status = analysis_result.get("overall_status", "unknown")
    api = analysis_result.get("api_finding", {})

    sections.append({
        "title": "Executive Summary",
        "content": f"Overall Result: {overall_status.upper()}\nAPI: {api.get('api_name', 'unknown')}",
    })

    if api:
        m = api.get("metrics", {})
        lines = [
            f"Status: {api['status'].upper()} / {api['severity']}",
            f"avg={m.get('avg_response_time')}ms  p95={m.get('p95_response_time')}ms  "
            f"max={m.get('max_response_time')}ms  throughput={m.get('throughput')} req/s  "
            f"error_rate={m.get('error_rate_pct')}%  http_status={m.get('http_status')}",
        ]
        lines += [f"- {a}" for a in api.get("anomalies", [])]
        sections.append({"title": "Performance Findings (Test Execution)", "content": "\n".join(lines)})

    infra = analysis_result.get("infra_health")
    if infra:
        lines = [
            f"Status: {infra['status'].upper()} (monitoring reported: {infra.get('monitoring_reported_status')})",
            f"CPU={infra.get('cpu_usage')}%  Memory={infra.get('memory_usage')}%  "
            f"DB connections={infra.get('db_connections')}  TPS={infra.get('tps')}",
        ]
        lines += [f"- {a}" for a in infra.get("anomalies", [])]
        if infra.get("cross_check_note"):
            lines.append(f"Cross-check: {infra['cross_check_note']}")
        sections.append({"title": "Infrastructure Health (Monitoring)", "content": "\n".join(lines)})

    security = analysis_result.get("security_summary")
    if security:
        lines = [f"Status: {security.get('status')}   Score: {security.get('security_score')}"]
        issues = security.get("issues", [])
        recs = security.get("recommendations", [])
        lines.append("Issues:" if issues else "Issues: none reported.")
        lines += [f"  - {i}" for i in issues]
        if recs:
            lines.append("Recommendations:")
            lines += [f"  - {r}" for r in recs]
        sections.append({"title": "Security Findings (Security Agent)", "content": "\n".join(lines)})

    return sections


def _render_txt_report(job_id: str, sections: list[dict]) -> str:
    os.makedirs(REPORT_PATH, exist_ok=True)
    path = os.path.join(REPORT_PATH, f"{job_id}_report.txt")
    with open(path, "w", encoding="utf-8") as f:
        for s in sections:
            f.write(f"{s['title']}\n{'=' * len(s['title'])}\n{s['content']}\n\n")
    return path


def generate_report(tool_context: ToolContext) -> dict:
    """Generates the final consolidated performance testing report file.
    Takes no arguments -- reads analysis_result (and test_execution_result
    for the job_id) from shared session state, so it should only be called
    LAST, after run_analysis has already produced a result. Stores its
    result under "report_result"."""

    print("===== Report Agent: generate_report =====")

    analysis_result = tool_context.state.get("analysis_result")
    test_execution_result = tool_context.state.get("test_execution_result") or {}
    job_id = test_execution_result.get("job_id", "unknown_job")

    if not analysis_result:
        result = {
            "status": "error",
            "message": "No analysis_result found in session state. Run analysis before requesting a report.",
        }
        tool_context.state["report_result"] = result
        return result

    sections = _build_sections(analysis_result)
    file_path = _render_txt_report(job_id, sections)

    result = {
        "status": "Generated",
        "file_path": file_path,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "test_execution": tool_context.state.get("test_execution_result"),
            "monitoring": tool_context.state.get("monitoring_result"),
            "security": tool_context.state.get("security_result"),
            "analysis": analysis_result,
        },
    }

    tool_context.state["report_result"] = result
    return result


report_agent = LlmAgent(
    name="report_agent",
    model=LiteLlm(
        model=LITELLM_MODEL_NAME,
        temperature=TEMPERATURE,
    ),
    mode="single_turn",  # call-and-return, like an ADK workflow node, not a sticky chat transfer
    instruction=(
        "You are the Report Agent for a Banking AI Performance Testing "
        "System. Whenever a report, summary, or final results are "
        "requested, call generate_report (it takes no arguments -- it "
        "reads prior results itself) and report back its exact results. "
        "If it returns status 'error', tell the user analysis needs to be "
        "run first."
    ),
    description=(
        "Generates the final consolidated report from whatever "
        "test-execution, monitoring, security, and analysis results were "
        "collected earlier in the conversation."
    ),
    tools=[generate_report],
)
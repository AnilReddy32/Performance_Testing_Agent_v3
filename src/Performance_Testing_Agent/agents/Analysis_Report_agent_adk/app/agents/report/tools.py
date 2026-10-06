"""
Tools for the Report Agent.

Renders THREE dimensions from AnalysisOutput: per-API performance
findings (api_findings), infra health (infra_health, from monitoring_agent),
and security (security_summary, from security_agent, passed through mostly
as-is since security_agent already did the judging).

CHANGE (this version): render_txt_report / render_pdf_report always write
the real file to local disk (REPORTS_DIR, e.g. "data/reports/JOB-123_report.pdf")
FIRST - that write always happens and is never skipped. Registering the
same file as an ADK artifact (for a clickable download in the ADK web
UI) is now a best-effort SECOND step wrapped in try/except: if it fails
(e.g. Windows' 260-character path limit inside ADK's file-based artifact
service - see WinError 206 in earlier logs), that failure is caught and
logged, and the function still returns successfully with the local path.
This guarantees a real PDF/TXT file always ends up in the project folder
regardless of whether the artifact-storage backend cooperates on this
machine.
"""

import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from google.adk.tools import ToolContext
from google.genai import types as genai_types

from .schemas import ReportOutput, ReportSection

logger = logging.getLogger(__name__)

# Anchored to this file's own location, not the current working directory -
# a bare relative "data/reports" resolves differently depending on whether
# adk web was launched from the project root or from src/. Anchoring one
# level higher (to src/) keeps reports inside src/data/reports, matching
# where the project already expects them. Walking up from this file
# (report/tools.py) to src/:
#   report -> agents -> app -> Analysis_Report_agent_adk -> agents
#   -> Performance_Testing_Agent -> src
_SRC_ROOT = Path(__file__).resolve().parents[6]
_DEFAULT_REPORTS_DIR = str(_SRC_ROOT / "data" / "reports")

REPORTS_DIR = os.environ.get("REPORTS_DIR", _DEFAULT_REPORTS_DIR)


def build_report_sections(
    job_id: str,
    application: str,
    scenario: str,
    data_quality_status: str,
    unusable_reason: Optional[str],
    overall_status: Optional[str],
    api_findings: List[dict],
    infra_health: Optional[dict],
    security_summary: Optional[dict],
    summary: str,
) -> dict:
    """Builds the ordered list of report sections. Returns
    {"sections": [...], "rejected": bool}."""
    sections: List[dict] = []

    if data_quality_status == "invalid":
        sections.append({
            "title": "Report Not Generated -- Invalid Data",
            "content": (
                f"Job {job_id} for application '{application}' "
                f"(scenario: {scenario}) could not be analyzed.\n\n"
                f"Reason: {unusable_reason or 'Data failed quality validation.'}\n\n"
                f"Action required: re-run the test or correct the source data, "
                f"then resubmit to the Analysis Agent."
            ),
        })
        return {"sections": sections, "rejected": True}

    sections.append({
        "title": "Executive Summary",
        "content": (
            f"Application: {application}\n"
            f"Scenario: {scenario}\n"
            f"Job ID: {job_id}\n"
            f"Overall Result: {(overall_status or 'unknown').upper()}\n\n"
            f"{summary or 'No summary provided.'}"
        ),
    })

    if api_findings:
        lines = []
        for f in api_findings:
            m = f.get("metrics", {})
            lines.append(
                f"- {f.get('api_name', 'Unknown API')} "
                f"[{str(f.get('status', 'unknown')).upper()} / {f.get('severity', 'unknown')}]\n"
                f"    avg={m.get('avg_response_time')}ms  "
                f"p95={m.get('p95_response_time')}ms  "
                f"max={m.get('max_response_time')}ms  "
                f"throughput={m.get('throughput')} req/s  "
                f"error_rate={m.get('error_rate_pct')}%  "
                f"http_status={m.get('http_status')}"
            )
            for a in f.get("anomalies", []):
                lines.append(f"    * {a}")
            if f.get("historical_comparison"):
                lines.append(f"    history: {f['historical_comparison']}")
            if f.get("recommendation"):
                lines.append(f"    recommendation: {f['recommendation']}")
        sections.append({"title": "Per-API Findings (Test Execution)", "content": "\n".join(lines)})
    else:
        sections.append({"title": "Per-API Findings (Test Execution)", "content": "No per-API findings were produced."})

    if infra_health:
        lines = [
            f"Status: {infra_health['status'].upper()} "
            f"(monitoring_agent reported: {infra_health.get('monitoring_reported_status', 'unknown')})",
            f"CPU usage: {infra_health.get('cpu_usage')}%   "
            f"Memory usage: {infra_health.get('memory_usage')}%   "
            f"DB connections: {infra_health.get('db_connections')}   "
            f"TPS: {infra_health.get('tps')}   "
            f"Response time (monitoring): {infra_health.get('monitoring_response_time')}ms",
        ]
        for a in infra_health.get("anomalies", []):
            lines.append(f"- {a}")
        if infra_health.get("cross_check_note"):
            lines.append(f"Cross-check: {infra_health['cross_check_note']}")
        if infra_health.get("alerts"):
            lines.append(f"Monitoring alerts: {infra_health['alerts']}")
        sections.append({"title": "Infrastructure Health (Monitoring)", "content": "\n".join(lines)})

    if security_summary:
        lines = [
            f"Status: {security_summary.get('status', 'unknown')}   "
            f"Security score: {security_summary.get('security_score', 'unknown')}",
        ]
        issues = security_summary.get("issues", [])
        recs = security_summary.get("recommendations", [])
        if issues:
            lines.append("Issues:")
            lines.extend(f"  - {i}" for i in issues)
        else:
            lines.append("Issues: none reported.")
        if recs:
            lines.append("Recommendations:")
            lines.extend(f"  - {r}" for r in recs)
        sections.append({"title": "Security Findings (Security Agent)", "content": "\n".join(lines)})

    fail_or_warn = [f for f in api_findings if f.get("status") in ("fail", "warning")]
    next_steps = [f"- {f.get('api_name', 'Unknown API')}: {f.get('recommendation') or 'Investigate flagged anomalies above.'}"
                  for f in fail_or_warn]
    if infra_health and infra_health.get("status") in ("fail", "warning"):
        next_steps.append("- Infrastructure: review CPU/memory/DB connection anomalies above.")
    if security_summary and str(security_summary.get("status", "")).upper() in ("FAIL", "WARNING"):
        next_steps.append("- Security: address the issues/recommendations listed above before next deployment.")

    sections.append({
        "title": "Recommended Next Steps",
        "content": "\n".join(next_steps) if next_steps else "All dimensions passed -- no action required.",
    })

    return {"sections": sections, "rejected": False}


async def _save_artifact_best_effort(
    tool_context: ToolContext,
    artifact_filename: str,
    data: bytes,
    mime_type: str,
) -> bool:
    """Tries to register a file as a real downloadable ADK artifact.
    Returns True on success, False on any failure (logged, never raised) -
    e.g. Windows path-length limits inside ADK's file-based artifact
    service. The caller always has the local disk file regardless of
    what this returns."""
    try:
        part = genai_types.Part.from_bytes(data=data, mime_type=mime_type)
        await tool_context.save_artifact(filename=artifact_filename, artifact=part)
        return True
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "Could not register '%s' as an ADK artifact (%s: %s) - the "
            "file was still written to local disk in %s and remains "
            "available there.",
            artifact_filename, e.__class__.__name__, e, REPORTS_DIR,
        )
        return False


async def render_txt_report(job_id: str, sections: List[dict], tool_context: ToolContext) -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    local_path = os.path.join(REPORTS_DIR, f"{job_id}_report.txt")
    text = ""
    for s in sections:
        text += f"{s['title']}\n{'=' * len(s['title'])}\n{s['content']}\n\n"

    # Local file is always written first - this is the guaranteed deliverable.
    with open(local_path, "w", encoding="utf-8") as f:
        f.write(text)

    artifact_filename = f"{job_id}_report.txt"
    saved = await _save_artifact_best_effort(
        tool_context, artifact_filename, text.encode("utf-8"), "text/plain"
    )

    # If the artifact registration failed, report the real local path
    # instead of an artifact filename that doesn't actually exist as a
    # download - the caller should always get something that genuinely
    # points at a file that exists.
    return artifact_filename if saved else local_path


async def render_pdf_report(job_id: str, sections: List[dict], tool_context: ToolContext) -> str:
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    os.makedirs(REPORTS_DIR, exist_ok=True)
    local_path = os.path.join(REPORTS_DIR, f"{job_id}_report.pdf")

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(local_path, pagesize=LETTER,
                             topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    story = []
    for s in sections:
        story.append(Paragraph(s["title"], styles["Heading2"]))
        for line in s["content"].split("\n"):
            story.append(Paragraph(line if line.strip() else "&nbsp;", styles["Normal"]))
        story.append(Spacer(1, 0.2 * inch))

    # Local PDF is always written first - this is the guaranteed deliverable.
    doc.build(story)

    with open(local_path, "rb") as f:
        pdf_bytes = f.read()

    artifact_filename = f"{job_id}_report.pdf"
    saved = await _save_artifact_best_effort(
        tool_context, artifact_filename, pdf_bytes, "application/pdf"
    )

    return artifact_filename if saved else local_path


def ingest_report_to_knowledge_base(analysis_result: dict) -> dict:
    """Closes the loop: pushes this job's analysis into the RAG knowledge
    base so the NEXT run's Analysis Agent can compare against it. Call
    LAST, after finalize_report. Non-fatal if it fails."""
    try:
        from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.rag.ingest import ingest_historical_run
        result = ingest_historical_run(analysis_result)
        return {"knowledge_base_updated": True, **result}
    except Exception as e:  # noqa: BLE001
        return {"knowledge_base_updated": False, "error": str(e)}


async def finalize_report(
    job_id: str,
    application: str,
    scenario: str,
    overall_status: Optional[str],
    sections: List[dict],
    rejected: bool,
    tool_context: ToolContext,
    requested_format: str = "pdf",
) -> dict:
    """Renders the requested file format(s) and returns a validated
    ReportOutput dict. Call last.

    file_path holds either the ARTIFACT'S filename (e.g.
    "JOB-123_report.pdf", downloadable from the ADK web UI's Artifacts
    panel) if artifact registration succeeded, or the real local disk
    path (e.g. "data/reports/JOB-123_report.pdf") if it didn't - either
    way it points at a file that actually exists.
    """
    # Guard against an empty/missing job_id (e.g. a rejected/invalid-data
    # report with no real job to attach to) - without this, the artifact
    # filename becomes a bare "_report.txt"/"_report.pdf" (leading
    # underscore, no id), which is a degenerate filename some artifact
    # storage backends choke on.
    if not job_id:
        job_id = f"UNKNOWN-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

    fmt = "txt" if rejected else requested_format
    file_path = None

    if fmt in ("txt", "both"):
        file_path = await render_txt_report(job_id, sections, tool_context)
    if fmt in ("pdf", "both") and not rejected:
        file_path = await render_pdf_report(job_id, sections, tool_context)

    output = ReportOutput(
        job_id=job_id, application=application, scenario=scenario,
        overall_status=overall_status, report_format=fmt, file_path=file_path,
        generated_at=datetime.now(timezone.utc).isoformat(),
        sections=[ReportSection(**s) for s in sections], rejected=rejected,
    )
    return output.model_dump()







# """
# Tools for the Report Agent.

# Renders THREE dimensions from AnalysisOutput: per-API performance
# findings (api_findings), infra health (infra_health, from monitoring_agent),
# and security (security_summary, from security_agent, passed through mostly
# as-is since security_agent already did the judging).

# CHANGE (this version): render_txt_report / render_pdf_report always write
# the real file to local disk (REPORTS_DIR, e.g. "data/reports/JOB-123_report.pdf")
# FIRST - that write always happens and is never skipped. Registering the
# same file as an ADK artifact (for a clickable download in the ADK web
# UI) is now a best-effort SECOND step wrapped in try/except: if it fails
# (e.g. Windows' 260-character path limit inside ADK's file-based artifact
# service - see WinError 206 in earlier logs), that failure is caught and
# logged, and the function still returns successfully with the local path.
# This guarantees a real PDF/TXT file always ends up in the project folder
# regardless of whether the artifact-storage backend cooperates on this
# machine.
# """

# import logging
# import os
# from datetime import datetime, timezone
# from pathlib import Path
# from typing import List, Optional

# from google.adk.tools import ToolContext
# from google.genai import types as genai_types

# from .schemas import ReportOutput, ReportSection

# logger = logging.getLogger(__name__)

# # Anchored to this file's own location, not the current working directory -
# # a bare relative "data/reports" resolves differently depending on whether
# # adk web was launched from the project root or from src/. Anchoring one
# # level higher (to src/) keeps reports inside src/data/reports, matching
# # where the project already expects them. Walking up from this file
# # (report/tools.py) to src/:
# #   report -> agents -> app -> Analysis_Report_agent_adk -> agents
# #   -> Performance_Testing_Agent -> src
# _SRC_ROOT = Path(__file__).resolve().parents[6]
# _DEFAULT_REPORTS_DIR = str(_SRC_ROOT / "data" / "reports")

# REPORTS_DIR = os.environ.get("REPORTS_DIR", _DEFAULT_REPORTS_DIR)


# def build_report_sections(
#     job_id: str,
#     application: str,
#     scenario: str,
#     data_quality_status: str,
#     unusable_reason: Optional[str],
#     overall_status: Optional[str],
#     api_findings: List[dict],
#     infra_health: Optional[dict],
#     security_summary: Optional[dict],
#     summary: str,
# ) -> dict:
#     """Builds the ordered list of report sections. Returns
#     {"sections": [...], "rejected": bool}."""
#     sections: List[dict] = []

#     if data_quality_status == "invalid":
#         sections.append({
#             "title": "Report Not Generated -- Invalid Data",
#             "content": (
#                 f"Job {job_id} for application '{application}' "
#                 f"(scenario: {scenario}) could not be analyzed.\n\n"
#                 f"Reason: {unusable_reason or 'Data failed quality validation.'}\n\n"
#                 f"Action required: re-run the test or correct the source data, "
#                 f"then resubmit to the Analysis Agent."
#             ),
#         })
#         return {"sections": sections, "rejected": True}

#     sections.append({
#         "title": "Executive Summary",
#         "content": (
#             f"Application: {application}\n"
#             f"Scenario: {scenario}\n"
#             f"Job ID: {job_id}\n"
#             f"Overall Result: {(overall_status or 'unknown').upper()}\n\n"
#             f"{summary or 'No summary provided.'}"
#         ),
#     })

#     if api_findings:
#         lines = []
#         for f in api_findings:
#             m = f.get("metrics", {})
#             lines.append(
#                 f"- {f.get('api_name', 'Unknown API')} "
#                 f"[{str(f.get('status', 'unknown')).upper()} / {f.get('severity', 'unknown')}]\n"
#                 f"    avg={m.get('avg_response_time')}ms  "
#                 f"p95={m.get('p95_response_time')}ms  "
#                 f"max={m.get('max_response_time')}ms  "
#                 f"throughput={m.get('throughput')} req/s  "
#                 f"error_rate={m.get('error_rate_pct')}%  "
#                 f"http_status={m.get('http_status')}"
#             )
#             for a in f.get("anomalies", []):
#                 lines.append(f"    * {a}")
#             if f.get("historical_comparison"):
#                 lines.append(f"    history: {f['historical_comparison']}")
#             if f.get("recommendation"):
#                 lines.append(f"    recommendation: {f['recommendation']}")
#         sections.append({"title": "Per-API Findings (Test Execution)", "content": "\n".join(lines)})
#     else:
#         sections.append({"title": "Per-API Findings (Test Execution)", "content": "No per-API findings were produced."})

#     if infra_health:
#         lines = [
#             f"Status: {infra_health['status'].upper()} "
#             f"(monitoring_agent reported: {infra_health.get('monitoring_reported_status', 'unknown')})",
#             f"CPU usage: {infra_health.get('cpu_usage')}%   "
#             f"Memory usage: {infra_health.get('memory_usage')}%   "
#             f"DB connections: {infra_health.get('db_connections')}   "
#             f"TPS: {infra_health.get('tps')}   "
#             f"Response time (monitoring): {infra_health.get('monitoring_response_time')}ms",
#         ]
#         for a in infra_health.get("anomalies", []):
#             lines.append(f"- {a}")
#         if infra_health.get("cross_check_note"):
#             lines.append(f"Cross-check: {infra_health['cross_check_note']}")
#         if infra_health.get("alerts"):
#             lines.append(f"Monitoring alerts: {infra_health['alerts']}")
#         sections.append({"title": "Infrastructure Health (Monitoring)", "content": "\n".join(lines)})

#     if security_summary:
#         lines = [
#             f"Status: {security_summary.get('status', 'unknown')}   "
#             f"Security score: {security_summary.get('security_score', 'unknown')}",
#         ]
#         issues = security_summary.get("issues", [])
#         recs = security_summary.get("recommendations", [])
#         if issues:
#             lines.append("Issues:")
#             lines.extend(f"  - {i}" for i in issues)
#         else:
#             lines.append("Issues: none reported.")
#         if recs:
#             lines.append("Recommendations:")
#             lines.extend(f"  - {r}" for r in recs)
#         sections.append({"title": "Security Findings (Security Agent)", "content": "\n".join(lines)})

#     fail_or_warn = [f for f in api_findings if f.get("status") in ("fail", "warning")]
#     next_steps = [f"- {f.get('api_name', 'Unknown API')}: {f.get('recommendation') or 'Investigate flagged anomalies above.'}"
#                   for f in fail_or_warn]
#     if infra_health and infra_health.get("status") in ("fail", "warning"):
#         next_steps.append("- Infrastructure: review CPU/memory/DB connection anomalies above.")
#     if security_summary and str(security_summary.get("status", "")).upper() in ("FAIL", "WARNING"):
#         next_steps.append("- Security: address the issues/recommendations listed above before next deployment.")

#     sections.append({
#         "title": "Recommended Next Steps",
#         "content": "\n".join(next_steps) if next_steps else "All dimensions passed -- no action required.",
#     })

#     return {"sections": sections, "rejected": False}


# async def _save_artifact_best_effort(
#     tool_context: ToolContext,
#     artifact_filename: str,
#     data: bytes,
#     mime_type: str,
# ) -> bool:
#     """Tries to register a file as a real downloadable ADK artifact.
#     Returns True on success, False on any failure (logged, never raised) -
#     e.g. Windows path-length limits inside ADK's file-based artifact
#     service. The caller always has the local disk file regardless of
#     what this returns."""
#     try:
#         part = genai_types.Part.from_bytes(data=data, mime_type=mime_type)
#         await tool_context.save_artifact(filename=artifact_filename, artifact=part)
#         return True
#     except Exception as e:  # noqa: BLE001
#         logger.warning(
#             "Could not register '%s' as an ADK artifact (%s: %s) - the "
#             "file was still written to local disk in %s and remains "
#             "available there.",
#             artifact_filename, e.__class__.__name__, e, REPORTS_DIR,
#         )
#         return False


# async def render_txt_report(job_id: str, sections: List[dict], tool_context: ToolContext) -> str:
#     os.makedirs(REPORTS_DIR, exist_ok=True)
#     local_path = os.path.join(REPORTS_DIR, f"{job_id}_report.txt")
#     text = ""
#     for s in sections:
#         text += f"{s['title']}\n{'=' * len(s['title'])}\n{s['content']}\n\n"

#     # Local file is always written first - this is the guaranteed deliverable.
#     with open(local_path, "w", encoding="utf-8") as f:
#         f.write(text)

#     artifact_filename = f"{job_id}_report.txt"
#     saved = await _save_artifact_best_effort(
#         tool_context, artifact_filename, text.encode("utf-8"), "text/plain"
#     )

#     # If the artifact registration failed, report the real local path
#     # instead of an artifact filename that doesn't actually exist as a
#     # download - the caller should always get something that genuinely
#     # points at a file that exists.
#     return artifact_filename if saved else local_path


# async def render_pdf_report(job_id: str, sections: List[dict], tool_context: ToolContext) -> str:
#     from reportlab.lib.pagesizes import LETTER
#     from reportlab.lib.styles import getSampleStyleSheet
#     from reportlab.lib.units import inch
#     from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

#     os.makedirs(REPORTS_DIR, exist_ok=True)
#     local_path = os.path.join(REPORTS_DIR, f"{job_id}_report.pdf")

#     styles = getSampleStyleSheet()
#     doc = SimpleDocTemplate(local_path, pagesize=LETTER,
#                              topMargin=0.75 * inch, bottomMargin=0.75 * inch)
#     story = []
#     for s in sections:
#         story.append(Paragraph(s["title"], styles["Heading2"]))
#         for line in s["content"].split("\n"):
#             story.append(Paragraph(line if line.strip() else "&nbsp;", styles["Normal"]))
#         story.append(Spacer(1, 0.2 * inch))

#     # Local PDF is always written first - this is the guaranteed deliverable.
#     doc.build(story)

#     with open(local_path, "rb") as f:
#         pdf_bytes = f.read()

#     artifact_filename = f"{job_id}_report.pdf"
#     saved = await _save_artifact_best_effort(
#         tool_context, artifact_filename, pdf_bytes, "application/pdf"
#     )

#     return artifact_filename if saved else local_path


# def ingest_report_to_knowledge_base(analysis_result: dict) -> dict:
#     """Closes the loop: pushes this job's analysis into the RAG knowledge
#     base so the NEXT run's Analysis Agent can compare against it. Call
#     LAST, after finalize_report. Non-fatal if it fails."""
#     try:
#         from app.rag.ingest import ingest_historical_run
#         result = ingest_historical_run(analysis_result)
#         return {"knowledge_base_updated": True, **result}
#     except Exception as e:  # noqa: BLE001
#         return {"knowledge_base_updated": False, "error": str(e)}


# async def finalize_report(
#     job_id: str,
#     application: str,
#     scenario: str,
#     overall_status: Optional[str],
#     sections: List[dict],
#     rejected: bool,
#     tool_context: ToolContext,
#     requested_format: str = "pdf",
# ) -> dict:
#     """Renders the requested file format(s) and returns a validated
#     ReportOutput dict. Call last.

#     file_path holds either the ARTIFACT'S filename (e.g.
#     "JOB-123_report.pdf", downloadable from the ADK web UI's Artifacts
#     panel) if artifact registration succeeded, or the real local disk
#     path (e.g. "data/reports/JOB-123_report.pdf") if it didn't - either
#     way it points at a file that actually exists.
#     """
#     # Guard against an empty/missing job_id (e.g. a rejected/invalid-data
#     # report with no real job to attach to) - without this, the artifact
#     # filename becomes a bare "_report.txt"/"_report.pdf" (leading
#     # underscore, no id), which is a degenerate filename some artifact
#     # storage backends choke on.
#     if not job_id:
#         job_id = f"UNKNOWN-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

#     fmt = "txt" if rejected else requested_format
#     file_path = None

#     if fmt in ("txt", "both"):
#         file_path = await render_txt_report(job_id, sections, tool_context)
#     if fmt in ("pdf", "both") and not rejected:
#         file_path = await render_pdf_report(job_id, sections, tool_context)

#     output = ReportOutput(
#         job_id=job_id, application=application, scenario=scenario,
#         overall_status=overall_status, report_format=fmt, file_path=file_path,
#         generated_at=datetime.now(timezone.utc).isoformat(),
#         sections=[ReportSection(**s) for s in sections], rejected=rejected,
#     )
#     return output.model_dump()
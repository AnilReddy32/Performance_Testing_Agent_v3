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
import math
import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
from xml.sax.saxutils import escape

from google.adk.tools import ToolContext
from google.genai import types as genai_types

from Performance_Testing_Agent.execution_context import (
    artifact_directory_reference,
    resolve_artifact_directory,
)

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


def _format_count(value) -> str:
    """Formats a request count with thousands separators, or returns a
    placeholder if the count wasn't available."""
    if value is None:
        return "n/a"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def _passive_check_lines(security_summary: dict) -> list:
    """One line per passive check verdict, with the totals; empty when none ran."""
    check_results = security_summary.get("check_results")
    if not isinstance(check_results, list) or not check_results:
        return []
    totals = security_summary.get("check_summary")
    totals = totals if isinstance(totals, dict) else {}
    lines = [
        "Passive external-surface checks "
        f"({totals.get('assessed', '?')} of {totals.get('total', len(check_results))} assessed; "
        f"{totals.get('passed', '?')} passed, {totals.get('failed', '?')} failed, "
        f"{totals.get('inconclusive', '?')} inconclusive; "
        f"outcome: {security_summary.get('assessment_outcome', 'unknown')}):"
    ]
    for item in check_results:
        if isinstance(item, dict):
            lines.append(
                f"  - [{str(item.get('verdict', 'unknown')).upper()}] "
                f"{item.get('title', item.get('check_id', 'check'))} "
                f"({item.get('severity', 'unknown')}): {item.get('summary', '')}"
            )
    return lines


def _display_live_security_status(security_summary: Optional[dict]) -> str:
    """Map internal live-check states to the four report-facing labels."""
    if not security_summary:
        return "not requested"
    value = security_summary.get("live_testing_status")
    if value in {"completed", "failed", "not_requested", "not_assessed"}:
        return value.replace("_", " ")
    if value in {"blocked", "not_run"}:
        return "not assessed"
    if security_summary.get("live_testing_requested"):
        return "not assessed"
    return "not requested"


def _build_agent_activity_rows(
    application: str,
    scenario: str,
    api_findings: List[dict],
    infra_health: Optional[dict],
    security_summary: Optional[dict],
    summary: str,
    requested_format: str,
) -> list:
    """
    Returns [(agent_name, summary_text), ...] - one row per agent in the
    pipeline. This is the single source of truth for "what each agent
    did"; both the PDF table and the plain-text fallback are built from
    these same rows, so the two renderings can never drift apart.
    """
    rows = []

    if api_findings:
        te_blocks = []
        for f in api_findings:
            m = f.get("metrics", {})
            percentiles = m.get("latency_percentiles_ms")
            percentile_summary = (
                "\nLatency percentiles (ms): "
                + ", ".join(
                    f"{name}={percentiles[name]}"
                    for name in ("p50", "p90", "p95", "p99")
                    if isinstance(percentiles, dict) and name in percentiles
                )
                if isinstance(percentiles, dict) and percentiles
                else ""
            )
            te_blocks.append(
                f"Load test executed on {f.get('api_name', 'Unknown API')} "
                f"({application} - {scenario}).\n"
                f"Results: {_format_count(m.get('total_requests'))} total requests, "
                f"{_format_count(m.get('successful_requests'))} successful, "
                f"{_format_count(m.get('failed_requests'))} failed.\n"
                f"Avg response time: {m.get('avg_response_time')} ms; "
                f"95th percentile: {m.get('p95_response_time')} ms; "
                f"Max: {m.get('max_response_time')} ms.\n"
                f"Throughput: {m.get('throughput')} TPS; "
                f"Error rate: {m.get('error_rate_pct')}%."
                f"{percentile_summary}"
            )
        rows.append(("Test Execution", "\n\n".join(te_blocks)))
    else:
        rows.append(("Test Execution", "No test execution data was available for this job."))

    if infra_health:
        db_connections = infra_health.get("db_connections")
        cpu_peak = infra_health.get("cpu_peak_usage")
        memory_peak = infra_health.get("memory_peak_usage")
        if infra_health.get("monitoring_reported_status") == "UNAVAILABLE":
            mon_text = "Monitoring unavailable; no metrics were substituted."
            if infra_health.get("data_source"):
                mon_text += f" {infra_health['data_source']}."
            if infra_health.get("anomalies"):
                mon_text += " " + "; ".join(infra_health["anomalies"])
        else:
            cpu_summary = f"{infra_health.get('cpu_usage')}% average"
            memory_summary = f"{infra_health.get('memory_usage')}% average"
            if cpu_peak is not None:
                cpu_summary += f", {cpu_peak}% peak"
            if memory_peak is not None:
                memory_summary += f", {memory_peak}% peak"
            mon_text = (
                f"CPU usage: {cpu_summary}; "
                f"memory: {memory_summary}; "
                f"DB connections: {db_connections if db_connections is not None else 'not collected'}, "
                f"TPS: {infra_health.get('tps')}, "
                f"Response time: {infra_health.get('monitoring_response_time')} ms.\n"
            )
            if infra_health.get("data_source"):
                mon_text += f"Data source and scope: {infra_health['data_source']}.\n"
            provenance = infra_health.get("measurement_provenance", {})
            if provenance:
                mon_text += "Measurement provenance: " + "; ".join(
                    f"{metric}={details.get('data_source') or details.get('status', 'unknown')} "
                    f"({details.get('measurement_scope') or details.get('reason', 'scope unavailable')})"
                    for metric, details in provenance.items()
                ) + ".\n"
            mon_text += (
                f"Alerts triggered: {infra_health['alerts']}"
                if infra_health.get("alerts") else "No alerts triggered."
            )
    else:
        mon_text = "Monitoring was not run for this job."
    rows.append(("Monitoring", mon_text))

    if security_summary:
        sec_lines = [
            f"Status: {security_summary.get('status', 'UNKNOWN')}.",
            f"Security score: {security_summary.get('security_score', 'N/A')}.",
            f"Live security check: {_display_live_security_status(security_summary)}.",
        ]
        if security_summary.get("security_score_basis"):
            sec_lines.append(f"Security score basis: {security_summary['security_score_basis']}")
        for issue in security_summary.get("issues", []):
            sec_lines.append(f"Issue: {issue}")
        if security_summary.get("coverage"):
            sec_lines.append(f"Control coverage: {security_summary['coverage']}")
        if security_summary.get("control_results"):
            sec_lines.append("Control assessment evidence:")
            for item in security_summary["control_results"]:
                if isinstance(item, dict):
                    sec_lines.append(
                        "  - " + str(item.get("control", "control"))
                        + ": " + str(item.get("assessment_status", "unknown"))
                        + "; basis=" + str(item.get("assessment_basis", "not stated"))
                        + "; evidence=" + str(item.get("evidence_references", []))
                    )
        # The summary table gets the totals only; the full per-check list is in
        # the "Security Findings" section.
        sec_lines.extend(line.rstrip(":") for line in _passive_check_lines(security_summary)[:1])
        if security_summary.get("evidence_references"):
            sec_lines.append(
                "Evidence references: " + ", ".join(map(str, security_summary["evidence_references"]))
            )
        if security_summary.get("limitations"):
            sec_lines.append("Assessment limitations:")
            sec_lines.extend(f"  - {item}" for item in security_summary["limitations"])
        recommendations = security_summary.get("recommendations", [])
        if recommendations:
            sec_lines.append(f"Recommendation: {recommendations[0]}")
        sec_text = "\n".join(sec_lines)
    else:
        sec_text = "Security assessment: not requested for this job.\nLive security check: not requested."
    rows.append(("Security Validation", sec_text))

    rows.append(("Analysis", summary or "No analysis summary was provided."))

    # PDF is ALWAYS generated now (see finalize_report) regardless of what
    # requested_format literally says - so the label reflects that actual
    # guarantee, not just the raw requested value, to avoid this row ever
    # saying "text report" when a PDF was also produced.
    format_label = "PDF and text" if requested_format in ("txt", "both") else "PDF"
    rows.append((
        "Reporting",
        f"A {format_label} report was generated, including all findings, "
        f"recommendations, and an executive summary.",
    ))

    return rows


def _build_agent_activity_summary(
    application: str,
    scenario: str,
    api_findings: List[dict],
    infra_health: Optional[dict],
    security_summary: Optional[dict],
    summary: str,
    requested_format: str,
) -> str:
    """Flat numbered text version of the same rows _build_agent_activity_rows
    produces - used for TXT reports."""
    rows = _build_agent_activity_rows(
        application, scenario, api_findings, infra_health,
        security_summary, summary, requested_format,
    )
    lines = []
    for i, (agent, text) in enumerate(rows, start=1):
        lines.append(f"{i}. {agent}:")
        for line in text.split("\n"):
            lines.append(f"   - {line}" if line.strip() else "")
        lines.append("")
    return "\n".join(lines).rstrip()


def _package_native_execution_artifacts(
    job_id: str,
    execution_mode: Optional[str],
    execution_artifacts: Optional[dict[str, str]],
    tool: str | None = None,
) -> dict[str, str]:
    """Package native report and raw result files unless the runner did so."""
    if (execution_mode or "").upper() != "REAL":
        return {}
    artifacts = execution_artifacts or {}
    native_name = artifacts.get("native_report")
    raw_name = artifacts.get("raw_results")
    if not native_name and not raw_name:
        return {}

    job_directory = resolve_artifact_directory(job_id, tool=tool)
    source_paths: dict[str, Path] = {}
    for artifact_key, artifact_name in (
        ("native_report", native_name),
        ("raw_results", raw_name),
    ):
        if not artifact_name:
            continue
        relative_path = Path(artifact_name)
        if (
            relative_path.is_absolute()
            or relative_path.as_posix() != artifact_name
            or any(part in {"", ".", ".."} for part in relative_path.parts)
        ):
            raise ValueError(
                f"Execution artifact '{artifact_key}' must be a safe job-local path."
            )
        source_path = (job_directory / relative_path).resolve()
        if not source_path.is_relative_to(job_directory) or not source_path.is_file():
            raise ValueError(
                f"Execution artifact '{artifact_key}' is missing or outside "
                "the current job directory."
            )
        source_paths[artifact_key] = source_path

    references = {
        artifact_key: source_paths[artifact_key].relative_to(job_directory).as_posix()
        for artifact_key, source_path in source_paths.items()
    }
    existing_archive = artifacts.get("native_report_archive")
    if existing_archive:
        archive_path = (job_directory / existing_archive).resolve()
        if (
            archive_path.is_relative_to(job_directory)
            and archive_path.is_file()
            and not archive_path.is_symlink()
        ):
            references["native_report_archive"] = archive_path.relative_to(job_directory).as_posix()
            return references
    if len(source_paths) != 2:
        return references

    archive_path = job_directory / f"{job_id}_native_report.zip"
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{job_id}_native_report_",
            suffix=".tmp",
            dir=job_directory,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
        with zipfile.ZipFile(
            temporary_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            native_path = source_paths["native_report"]
            if native_path.is_dir():
                for report_file in native_path.rglob("*"):
                    if report_file.is_file():
                        archive.write(
                            report_file,
                            arcname=(Path("native_report") / report_file.relative_to(native_path)).as_posix(),
                        )
            else:
                archive.write(native_path, arcname=f"native_report/{native_path.name}")
            archive.write(
                source_paths["raw_results"],
                arcname=f"raw_results/{raw_name}",
            )
        temporary_path.replace(archive_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    references["native_report_archive"] = archive_path.name
    return references


def _artifact_download_url(job_id: str, artifact_key: str) -> str:
    base_url = os.getenv("ARTIFACT_PUBLIC_BASE_URL", "").rstrip("/")
    relative_url = f"/artifacts/{job_id}/{artifact_key}"
    return f"{base_url}{relative_url}" if base_url else relative_url


def _artifact_link(label: str, url: str) -> str:
    href = escape(url, {'"': "&quot;"})
    return f'<link href="{href}">{escape(label)}</link>'


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
    test_case_prompt: Optional[str] = None,
    requested_format: str = "pdf",
    time_series_analysis: Optional[dict] = None,
    execution_mode: Optional[str] = None,
    execution_profile: Optional[dict] = None,
    execution_artifact_directory: Optional[str] = None,
    execution_artifacts: Optional[dict[str, str]] = None,
    execution_status: Optional[str] = None,
    execution_outcome: Optional[dict] = None,
) -> dict:
    """Builds the ordered list of report sections. Returns
    {"sections": [...], "rejected": bool}.

    test_case_prompt: the user's original request text, if available -
    rendered as the very first section.
    """
    sections: List[dict] = []

    if security_summary and security_summary.get("job_id") != job_id:
        security_summary = None
    if (
        security_summary is None
        and isinstance(execution_outcome, dict)
        and execution_outcome.get("job_id") == job_id
    ):
        candidate_security = execution_outcome.get("security_result")
        if isinstance(candidate_security, dict) and candidate_security.get("job_id") == job_id:
            security_summary = candidate_security
    if security_summary is None and isinstance(execution_outcome, dict):
        if execution_outcome.get("job_id") == job_id and execution_outcome.get("security_requested") is True:
            security_summary = {
                "job_id": job_id,
                "status": "NOT ASSESSED",
                "security_score": "N/A",
                "issues": ["A matching job-scoped security result was unavailable."],
                "recommendations": [],
                "live_testing_requested": False,
                "live_testing_status": "not_assessed",
                "limitations": ["No matching job-scoped security result was available to this report."],
            }

    if test_case_prompt:
        sections.append({
            "title": "Test Case / Original Request",
            "content": test_case_prompt,
        })

    terminal_real_run = (
        (execution_mode or "").upper() == "REAL"
        and execution_status in {"completed", "failed"}
    )
    if data_quality_status == "invalid" and not terminal_real_run:
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

    if terminal_real_run:
        outcome = execution_outcome or {}
        outcome_lines = [
            f"Execution status: {execution_status.upper()}",
            f"Runner status: {outcome.get('runner_status', 'unknown')}",
        ]
        if outcome.get("message"):
            outcome_lines.append(f"Outcome details: {escape(str(outcome['message']))}")
        for field, label in (
            ("exit_code", "Process exit code"),
            ("thresholds_passed", "Thresholds passed"),
            ("threshold_failures", "Threshold failures"),
            ("blocked_reasons", "Execution restrictions"),
        ):
            if outcome.get(field) not in (None, [], {}):
                outcome_lines.append(f"{label}: {escape(str(outcome[field]))}")
        if data_quality_status == "invalid":
            outcome_lines.append(
                "Performance measurements were unavailable or failed quality validation; "
                f"reason: {escape(str(unusable_reason or 'not provided'))}"
            )
        for result_key, label, reported_summary in (
            ("monitoring_result", "Available monitoring input", infra_health),
            ("security_result", "Available security input", security_summary),
        ):
            result = outcome.get(result_key)
            if reported_summary is None and isinstance(result, dict):
                visible_fields = (
                    "status", "monitoring_reported_status", "cpu_usage",
                    "memory_usage", "db_connections", "tps",
                    "monitoring_response_time", "security_score", "alerts",
                    "anomalies", "issues", "recommendations", "message",
                )
                details = [
                    f"{field}={escape(str(result[field]))}"
                    for field in visible_fields
                    if field in result and result[field] not in (None, [], {})
                ]
                if details:
                    outcome_lines.append(f"{label}: " + "; ".join(details))
        sections.append({
            "title": "REAL Execution Outcome",
            "content": "\n".join(outcome_lines),
        })

    chart_series = (
        time_series_analysis.get("series", [])
        if isinstance(time_series_analysis, dict)
        and time_series_analysis.get("status") == "analyzed"
        and time_series_analysis.get("execution_mode") == "REAL"
        and isinstance(time_series_analysis.get("series"), list)
        else []
    )
    charts = []
    for metric, title, unit in (
        ("avg_response_time_ms", "Response latency over time", "ms"),
        ("throughput_rps", "Throughput over time", "requests/second"),
        ("cpu_avg_percent", "Load-generator host CPU over time", "%"),
    ):
        points = [
            {
                "elapsed_seconds": point.get("elapsed_seconds"),
                "value": point.get(metric),
            }
            for point in chart_series
            if isinstance(point, dict)
            and isinstance(point.get("elapsed_seconds"), (int, float))
            and isinstance(point.get(metric), (int, float))
        ]
        if points:
            charts.append(
                {
                    "title": title,
                    "unit": unit,
                    "points": points,
                    "data_source": (
                        "psutil load-generator host"
                        if metric == "cpu_avg_percent"
                        else (
                            "JMeter client-observed HTTP traffic"
                            if "jmeter" in str((execution_profile or {}).get("tool", "")).lower()
                            else "k6 client-observed HTTP traffic"
                        )
                    ),
                }
            )

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

    packaged_references = _package_native_execution_artifacts(
        job_id,
        execution_mode,
        execution_artifacts,
        tool=(execution_profile or {}).get("tool"),
    )
    report_artifacts = dict(execution_artifacts or {})
    report_artifacts.update(packaged_references)
    report_artifact_directory = execution_artifact_directory
    if (execution_mode or "").upper() == "REAL":
        report_artifact_directory = artifact_directory_reference(
            job_id,
            tool=(execution_profile or {}).get("tool"),
        )
    execution_lines = [
        f"Execution mode: {(execution_mode or 'UNKNOWN').upper()}",
    ]
    if execution_profile:
        execution_lines.append("Workload profile:")
        execution_lines.extend(
            f"  - {field}: {value}"
            for field, value in execution_profile.items()
        )
    else:
        execution_lines.append("Workload profile: not recorded.")
    if report_artifact_directory:
        execution_lines.append(
            f"Artifact directory: {report_artifact_directory}"
        )
    artifact_references = report_artifacts
    if artifact_references:
        execution_lines.append("Artifact references:")
        for artifact_name, artifact_path in sorted(artifact_references.items()):
            if report_artifact_directory and not os.path.isabs(artifact_path):
                reference = os.path.join(
                    report_artifact_directory,
                    artifact_path,
                ).replace(os.sep, "/")
            else:
                reference = artifact_path
            if artifact_name in {
                "native_report",
                "raw_results",
                "native_report_archive",
            }:
                tool_name = str((execution_profile or {}).get("tool", "")).lower()
                is_jmeter = "jmeter" in tool_name
                label = {
                    "native_report": "Native JMeter HTML dashboard" if is_jmeter else "Native k6 HTML report",
                    "raw_results": "Raw JMeter results (JTL)" if is_jmeter else "Raw k6 results (JSON)",
                    "native_report_archive": (
                        "JMeter dashboard + raw JTL ZIP" if is_jmeter else "Native report + raw results ZIP"
                    ),
                }[artifact_name]
                artifact_url = _artifact_download_url(job_id, artifact_name)
                execution_lines.append(
                    f"  - {_artifact_link(label, artifact_url)}"
                )
            else:
                execution_lines.append(f"  - {artifact_name}: {reference}")
        if packaged_references:
            execution_lines.append(
                "The interactive native HTML dashboard is linked as a separate "
                "artifact and is not embedded in this PDF."
            )
        if (
            (execution_mode or "").upper() == "REAL"
            and "native_report_archive" not in packaged_references
        ):
            execution_lines.append(
                "Native report package unavailable: the execution manifest "
                "does not contain both the native report and raw results."
            )
    else:
        execution_lines.append("Artifact references: none recorded.")
    sections.append(
        {
            "title": "Execution Profile and Artifacts",
            "content": "\n".join(execution_lines),
        }
    )
    if charts:
        sections.append(
            {
                "title": "Time-Series Charts (REAL Measurements)",
                "content": (
                    "Charts show measured values in five-second aligned "
                    "buckets. Host CPU is from the load-generator machine, "
                    "not the target."
                ),
                "charts": charts,
            }
        )
    elif (execution_mode or "").upper() == "SIMULATED":
        sections.append(
            {
                "title": "Time-Series Charts",
                "content": (
                    "No time-series graphs are available: simulated runs do "
                    "not produce measured time-series data."
                ),
            }
        )

    activity_rows = _build_agent_activity_rows(
        application, scenario, api_findings, infra_health,
        security_summary, summary, requested_format,
    )
    sections.append({
        "title": "Agent Activity Summary",
        "content": _build_agent_activity_summary(
            application, scenario, api_findings, infra_health,
            security_summary, summary, requested_format,
        ),
        # table_rows is used ONLY by render_pdf_report to draw a real
        # table for this section; render_txt_report ignores it.
        "table_rows": [("Agent", "Summary")] + activity_rows,
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
            f"Security result job ID: {security_summary.get('job_id', 'unavailable')}.",
            f"Live security check: {_display_live_security_status(security_summary)}.",
        ]
        if security_summary.get("security_score_basis"):
            lines.append(f"Security score basis: {security_summary['security_score_basis']}")
        issues = security_summary.get("issues", [])
        recs = security_summary.get("recommendations", [])
        if issues:
            lines.append("Issues:")
            lines.extend(f"  - {i}" for i in issues)
        else:
            lines.append("Issues: none reported.")
        if security_summary.get("coverage"):
            lines.append(f"Control coverage: {security_summary['coverage']}")
        for field, label in (
            ("requested_controls", "Requested controls"),
            ("assessed_controls", "Assessed controls"),
            ("not_assessed_controls", "Not assessed controls"),
        ):
            if security_summary.get(field):
                lines.append(f"{label}: {', '.join(map(str, security_summary[field]))}")
        control_results = security_summary.get("control_results", [])
        if control_results:
            lines.append("Control evidence and provenance:")
            for item in control_results:
                if not isinstance(item, dict):
                    continue
                lines.append(
                    "  - {control}: {result}; basis={basis}; evidence fields={fields}; references={refs}".format(
                        control=item.get("control", "unknown"),
                        result=item.get("assessment_status", "unknown"),
                        basis=item.get("assessment_basis", "not stated"),
                        fields=item.get("evidence_fields", []),
                        refs=item.get("evidence_references", []),
                    )
                )
        lines.extend(_passive_check_lines(security_summary))
        if security_summary.get("evidence_references"):
            lines.append("Evidence references: " + ", ".join(map(str, security_summary["evidence_references"])))
        live_result = security_summary.get("live_test_result")
        if isinstance(live_result, dict):
            observation = [
                f"Live observation: {live_result.get('method', 'unknown')} "
                f"{live_result.get('endpoint', 'unknown endpoint')}; "
                f"HTTP {live_result.get('response_status_code', 'unavailable')}; "
                f"elapsed {live_result.get('elapsed_ms', 'unavailable')} ms; "
                f"requests sent {live_result.get('requests_sent', 'unknown')}.",
            ]
            headers = live_result.get("observed_security_headers")
            if isinstance(headers, dict) and headers:
                observation.append("Observed response headers (observations only):")
                observation.extend(f"  - {name}: {value}" for name, value in headers.items())
            lines.extend(observation)
        if security_summary.get("limitations"):
            lines.append("Assessment limitations:")
            lines.extend(f"  - {item}" for item in security_summary["limitations"])
        if recs:
            lines.append("Recommendations:")
            lines.extend(f"  - {r}" for r in recs)
        sections.append({"title": "Security Findings (Security Agent)", "content": "\n".join(lines)})
    else:
        sections.append({
            "title": "Security Findings (Security Agent)",
            "content": "Security assessment: not requested for this job.\nLive security check: not requested.",
        })

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
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Flowable,
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
    )

    class TimeSeriesChart(Flowable):
        def __init__(self, chart: dict):
            super().__init__()
            self.title = str(chart["title"])
            self.unit = str(chart["unit"])
            self.data_source = str(chart["data_source"])
            self.points = [
                (float(point["elapsed_seconds"]), float(point["value"]))
                for point in chart["points"][:1000]
                if isinstance(point, dict)
                and isinstance(point.get("elapsed_seconds"), (int, float))
                and isinstance(point.get("value"), (int, float))
                and math.isfinite(float(point["elapsed_seconds"]))
                and math.isfinite(float(point["value"]))
            ]
            self.width = 450
            self.height = 190

        def wrap(self, available_width, available_height):
            self.width = min(450, available_width)
            return self.width, self.height

        def draw(self):
            if not self.points:
                return
            canvas = self.canv
            left, right, bottom, top = 48, self.width - 12, 35, self.height - 25
            x_values = [point[0] for point in self.points]
            y_values = [point[1] for point in self.points]
            x_min, x_max = min(x_values), max(x_values)
            y_min, y_max = min(0.0, min(y_values)), max(y_values)
            if x_min == x_max:
                x_max = x_min + 1
            if y_min == y_max:
                y_max = y_min + 1

            canvas.saveState()
            canvas.setFont("Helvetica-Bold", 10)
            canvas.drawString(left, self.height - 13, self.title)
            canvas.setFont("Helvetica", 7)
            canvas.setFillColor(colors.HexColor("#555555"))
            canvas.drawRightString(right, self.height - 13, self.data_source)
            canvas.setStrokeColor(colors.HexColor("#cccccc"))
            canvas.setLineWidth(0.5)
            for tick in range(5):
                y = bottom + (top - bottom) * tick / 4
                value = y_min + (y_max - y_min) * tick / 4
                canvas.line(left, y, right, y)
                canvas.setFont("Helvetica", 7)
                canvas.drawRightString(left - 5, y - 2, f"{value:.2f}")
            canvas.setStrokeColor(colors.HexColor("#334e68"))
            canvas.setLineWidth(1.5)
            mapped_points = [
                (
                    left + (x - x_min) / (x_max - x_min) * (right - left),
                    bottom + (y - y_min) / (y_max - y_min) * (top - bottom),
                )
                for x, y in self.points
            ]
            if len(mapped_points) == 1:
                x, y = mapped_points[0]
                canvas.circle(x, y, 2, stroke=1, fill=1)
            else:
                path = canvas.beginPath()
                path.moveTo(*mapped_points[0])
                for x, y in mapped_points[1:]:
                    path.lineTo(x, y)
                canvas.drawPath(path)
            canvas.setStrokeColor(colors.black)
            canvas.setLineWidth(0.7)
            canvas.line(left, bottom, left, top)
            canvas.line(left, bottom, right, bottom)
            canvas.setFont("Helvetica", 7)
            canvas.drawString(left, 17, f"Elapsed time (s); values in {self.unit}")
            canvas.drawRightString(right, 17, f"{x_min:g} - {x_max:g} s")
            canvas.restoreState()

    os.makedirs(REPORTS_DIR, exist_ok=True)
    local_path = os.path.join(REPORTS_DIR, f"{job_id}_report.pdf")

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(local_path, pagesize=LETTER,
                             topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    story = []
    for s in sections:
        story.append(Paragraph(s["title"], styles["Heading2"]))

        table_rows = s.get("table_rows")
        if table_rows:
            table_data = []
            for row_index, row in enumerate(table_rows):
                cell_style = styles["Heading4"] if row_index == 0 else styles["Normal"]
                table_data.append([
                    Paragraph(str(cell).replace("\n", "<br/>"), cell_style)
                    for cell in row
                ])
            table = Table(table_data, colWidths=[1.4 * inch, 5.6 * inch], repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ]))
            story.append(table)
        else:
            for line in s["content"].split("\n"):
                story.append(Paragraph(line if line.strip() else "&nbsp;", styles["Normal"]))

        for chart in s.get("charts", []):
            story.append(Spacer(1, 0.1 * inch))
            story.append(TimeSeriesChart(chart))

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

    # Business rule: a PDF must ALWAYS be generated for a real (non-rejected)
    # report, regardless of what requested_format was passed in.
    # requested_format only controls whether a TXT copy is ALSO produced
    # alongside the PDF - it can no longer suppress the PDF entirely.
    want_txt = requested_format in ("txt", "both")

    file_path = None
    fmt = "txt"  # unchanged default for rejected reports

    if rejected:
        file_path = await render_txt_report(job_id, sections, tool_context)
    else:
        if want_txt:
            await render_txt_report(job_id, sections, tool_context)
        file_path = await render_pdf_report(job_id, sections, tool_context)
        fmt = "both" if want_txt else "pdf"

    report_artifacts: dict[str, str] = {}
    workload_profile = tool_context.state.get("workload_profile")
    execution_tool = (
        workload_profile.get("tool")
        if isinstance(workload_profile, dict)
        else None
    )
    if not rejected and job_id.startswith("JOB-"):
        local_pdf = Path(REPORTS_DIR) / f"{job_id}_report.pdf"
        if local_pdf.is_file():
            job_directory = resolve_artifact_directory(job_id, tool=execution_tool)
            job_directory.mkdir(parents=True, exist_ok=True)
            consolidated_pdf = job_directory / f"{job_id}_report.pdf"
            shutil.copy2(local_pdf, consolidated_pdf)
            report_artifacts["consolidated_report"] = consolidated_pdf.name
        native_archive = (
            resolve_artifact_directory(job_id, tool=execution_tool)
            / f"{job_id}_native_report.zip"
        )
        if native_archive.is_file():
            report_artifacts["native_report_archive"] = native_archive.name

    output = ReportOutput(
        job_id=job_id, application=application, scenario=scenario,
        overall_status=overall_status, report_format=fmt, file_path=file_path,
        generated_at=datetime.now(timezone.utc).isoformat(),
        sections=[ReportSection(**s) for s in sections], rejected=rejected,
        artifacts=report_artifacts,
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
#         from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.rag.ingest import ingest_historical_run
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







# # """
# # Tools for the Report Agent.

# # Renders THREE dimensions from AnalysisOutput: per-API performance
# # findings (api_findings), infra health (infra_health, from monitoring_agent),
# # and security (security_summary, from security_agent, passed through mostly
# # as-is since security_agent already did the judging).

# # CHANGE (this version): render_txt_report / render_pdf_report always write
# # the real file to local disk (REPORTS_DIR, e.g. "data/reports/JOB-123_report.pdf")
# # FIRST - that write always happens and is never skipped. Registering the
# # same file as an ADK artifact (for a clickable download in the ADK web
# # UI) is now a best-effort SECOND step wrapped in try/except: if it fails
# # (e.g. Windows' 260-character path limit inside ADK's file-based artifact
# # service - see WinError 206 in earlier logs), that failure is caught and
# # logged, and the function still returns successfully with the local path.
# # This guarantees a real PDF/TXT file always ends up in the project folder
# # regardless of whether the artifact-storage backend cooperates on this
# # machine.
# # """

# # import logging
# # import os
# # from datetime import datetime, timezone
# # from pathlib import Path
# # from typing import List, Optional

# # from google.adk.tools import ToolContext
# # from google.genai import types as genai_types

# # from .schemas import ReportOutput, ReportSection

# # logger = logging.getLogger(__name__)

# # # Anchored to this file's own location, not the current working directory -
# # # a bare relative "data/reports" resolves differently depending on whether
# # # adk web was launched from the project root or from src/. Anchoring one
# # # level higher (to src/) keeps reports inside src/data/reports, matching
# # # where the project already expects them. Walking up from this file
# # # (report/tools.py) to src/:
# # #   report -> agents -> app -> Analysis_Report_agent_adk -> agents
# # #   -> Performance_Testing_Agent -> src
# # _SRC_ROOT = Path(__file__).resolve().parents[6]
# # _DEFAULT_REPORTS_DIR = str(_SRC_ROOT / "data" / "reports")

# # REPORTS_DIR = os.environ.get("REPORTS_DIR", _DEFAULT_REPORTS_DIR)


# # def build_report_sections(
# #     job_id: str,
# #     application: str,
# #     scenario: str,
# #     data_quality_status: str,
# #     unusable_reason: Optional[str],
# #     overall_status: Optional[str],
# #     api_findings: List[dict],
# #     infra_health: Optional[dict],
# #     security_summary: Optional[dict],
# #     summary: str,
# # ) -> dict:
# #     """Builds the ordered list of report sections. Returns
# #     {"sections": [...], "rejected": bool}."""
# #     sections: List[dict] = []

# #     if data_quality_status == "invalid":
# #         sections.append({
# #             "title": "Report Not Generated -- Invalid Data",
# #             "content": (
# #                 f"Job {job_id} for application '{application}' "
# #                 f"(scenario: {scenario}) could not be analyzed.\n\n"
# #                 f"Reason: {unusable_reason or 'Data failed quality validation.'}\n\n"
# #                 f"Action required: re-run the test or correct the source data, "
# #                 f"then resubmit to the Analysis Agent."
# #             ),
# #         })
# #         return {"sections": sections, "rejected": True}

# #     sections.append({
# #         "title": "Executive Summary",
# #         "content": (
# #             f"Application: {application}\n"
# #             f"Scenario: {scenario}\n"
# #             f"Job ID: {job_id}\n"
# #             f"Overall Result: {(overall_status or 'unknown').upper()}\n\n"
# #             f"{summary or 'No summary provided.'}"
# #         ),
# #     })

# #     if api_findings:
# #         lines = []
# #         for f in api_findings:
# #             m = f.get("metrics", {})
# #             lines.append(
# #                 f"- {f.get('api_name', 'Unknown API')} "
# #                 f"[{str(f.get('status', 'unknown')).upper()} / {f.get('severity', 'unknown')}]\n"
# #                 f"    avg={m.get('avg_response_time')}ms  "
# #                 f"p95={m.get('p95_response_time')}ms  "
# #                 f"max={m.get('max_response_time')}ms  "
# #                 f"throughput={m.get('throughput')} req/s  "
# #                 f"error_rate={m.get('error_rate_pct')}%  "
# #                 f"http_status={m.get('http_status')}"
# #             )
# #             for a in f.get("anomalies", []):
# #                 lines.append(f"    * {a}")
# #             if f.get("historical_comparison"):
# #                 lines.append(f"    history: {f['historical_comparison']}")
# #             if f.get("recommendation"):
# #                 lines.append(f"    recommendation: {f['recommendation']}")
# #         sections.append({"title": "Per-API Findings (Test Execution)", "content": "\n".join(lines)})
# #     else:
# #         sections.append({"title": "Per-API Findings (Test Execution)", "content": "No per-API findings were produced."})

# #     if infra_health:
# #         lines = [
# #             f"Status: {infra_health['status'].upper()} "
# #             f"(monitoring_agent reported: {infra_health.get('monitoring_reported_status', 'unknown')})",
# #             f"CPU usage: {infra_health.get('cpu_usage')}%   "
# #             f"Memory usage: {infra_health.get('memory_usage')}%   "
# #             f"DB connections: {infra_health.get('db_connections')}   "
# #             f"TPS: {infra_health.get('tps')}   "
# #             f"Response time (monitoring): {infra_health.get('monitoring_response_time')}ms",
# #         ]
# #         for a in infra_health.get("anomalies", []):
# #             lines.append(f"- {a}")
# #         if infra_health.get("cross_check_note"):
# #             lines.append(f"Cross-check: {infra_health['cross_check_note']}")
# #         if infra_health.get("alerts"):
# #             lines.append(f"Monitoring alerts: {infra_health['alerts']}")
# #         sections.append({"title": "Infrastructure Health (Monitoring)", "content": "\n".join(lines)})

# #     if security_summary:
# #         lines = [
# #             f"Status: {security_summary.get('status', 'unknown')}   "
# #             f"Security score: {security_summary.get('security_score', 'unknown')}",
# #         ]
# #         issues = security_summary.get("issues", [])
# #         recs = security_summary.get("recommendations", [])
# #         if issues:
# #             lines.append("Issues:")
# #             lines.extend(f"  - {i}" for i in issues)
# #         else:
# #             lines.append("Issues: none reported.")
# #         if recs:
# #             lines.append("Recommendations:")
# #             lines.extend(f"  - {r}" for r in recs)
# #         sections.append({"title": "Security Findings (Security Agent)", "content": "\n".join(lines)})

# #     fail_or_warn = [f for f in api_findings if f.get("status") in ("fail", "warning")]
# #     next_steps = [f"- {f.get('api_name', 'Unknown API')}: {f.get('recommendation') or 'Investigate flagged anomalies above.'}"
# #                   for f in fail_or_warn]
# #     if infra_health and infra_health.get("status") in ("fail", "warning"):
# #         next_steps.append("- Infrastructure: review CPU/memory/DB connection anomalies above.")
# #     if security_summary and str(security_summary.get("status", "")).upper() in ("FAIL", "WARNING"):
# #         next_steps.append("- Security: address the issues/recommendations listed above before next deployment.")

# #     sections.append({
# #         "title": "Recommended Next Steps",
# #         "content": "\n".join(next_steps) if next_steps else "All dimensions passed -- no action required.",
# #     })

# #     return {"sections": sections, "rejected": False}


# # async def _save_artifact_best_effort(
# #     tool_context: ToolContext,
# #     artifact_filename: str,
# #     data: bytes,
# #     mime_type: str,
# # ) -> bool:
# #     """Tries to register a file as a real downloadable ADK artifact.
# #     Returns True on success, False on any failure (logged, never raised) -
# #     e.g. Windows path-length limits inside ADK's file-based artifact
# #     service. The caller always has the local disk file regardless of
# #     what this returns."""
# #     try:
# #         part = genai_types.Part.from_bytes(data=data, mime_type=mime_type)
# #         await tool_context.save_artifact(filename=artifact_filename, artifact=part)
# #         return True
# #     except Exception as e:  # noqa: BLE001
# #         logger.warning(
# #             "Could not register '%s' as an ADK artifact (%s: %s) - the "
# #             "file was still written to local disk in %s and remains "
# #             "available there.",
# #             artifact_filename, e.__class__.__name__, e, REPORTS_DIR,
# #         )
# #         return False


# # async def render_txt_report(job_id: str, sections: List[dict], tool_context: ToolContext) -> str:
# #     os.makedirs(REPORTS_DIR, exist_ok=True)
# #     local_path = os.path.join(REPORTS_DIR, f"{job_id}_report.txt")
# #     text = ""
# #     for s in sections:
# #         text += f"{s['title']}\n{'=' * len(s['title'])}\n{s['content']}\n\n"

# #     # Local file is always written first - this is the guaranteed deliverable.
# #     with open(local_path, "w", encoding="utf-8") as f:
# #         f.write(text)

# #     artifact_filename = f"{job_id}_report.txt"
# #     saved = await _save_artifact_best_effort(
# #         tool_context, artifact_filename, text.encode("utf-8"), "text/plain"
# #     )

# #     # If the artifact registration failed, report the real local path
# #     # instead of an artifact filename that doesn't actually exist as a
# #     # download - the caller should always get something that genuinely
# #     # points at a file that exists.
# #     return artifact_filename if saved else local_path


# # async def render_pdf_report(job_id: str, sections: List[dict], tool_context: ToolContext) -> str:
# #     from reportlab.lib.pagesizes import LETTER
# #     from reportlab.lib.styles import getSampleStyleSheet
# #     from reportlab.lib.units import inch
# #     from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# #     os.makedirs(REPORTS_DIR, exist_ok=True)
# #     local_path = os.path.join(REPORTS_DIR, f"{job_id}_report.pdf")

# #     styles = getSampleStyleSheet()
# #     doc = SimpleDocTemplate(local_path, pagesize=LETTER,
# #                              topMargin=0.75 * inch, bottomMargin=0.75 * inch)
# #     story = []
# #     for s in sections:
# #         story.append(Paragraph(s["title"], styles["Heading2"]))
# #         for line in s["content"].split("\n"):
# #             story.append(Paragraph(line if line.strip() else "&nbsp;", styles["Normal"]))
# #         story.append(Spacer(1, 0.2 * inch))

# #     # Local PDF is always written first - this is the guaranteed deliverable.
# #     doc.build(story)

# #     with open(local_path, "rb") as f:
# #         pdf_bytes = f.read()

# #     artifact_filename = f"{job_id}_report.pdf"
# #     saved = await _save_artifact_best_effort(
# #         tool_context, artifact_filename, pdf_bytes, "application/pdf"
# #     )

# #     return artifact_filename if saved else local_path


# # def ingest_report_to_knowledge_base(analysis_result: dict) -> dict:
# #     """Closes the loop: pushes this job's analysis into the RAG knowledge
# #     base so the NEXT run's Analysis Agent can compare against it. Call
# #     LAST, after finalize_report. Non-fatal if it fails."""
# #     try:
# #         from app.rag.ingest import ingest_historical_run
# #         result = ingest_historical_run(analysis_result)
# #         return {"knowledge_base_updated": True, **result}
# #     except Exception as e:  # noqa: BLE001
# #         return {"knowledge_base_updated": False, "error": str(e)}


# # async def finalize_report(
# #     job_id: str,
# #     application: str,
# #     scenario: str,
# #     overall_status: Optional[str],
# #     sections: List[dict],
# #     rejected: bool,
# #     tool_context: ToolContext,
# #     requested_format: str = "pdf",
# # ) -> dict:
# #     """Renders the requested file format(s) and returns a validated
# #     ReportOutput dict. Call last.

# #     file_path holds either the ARTIFACT'S filename (e.g.
# #     "JOB-123_report.pdf", downloadable from the ADK web UI's Artifacts
# #     panel) if artifact registration succeeded, or the real local disk
# #     path (e.g. "data/reports/JOB-123_report.pdf") if it didn't - either
# #     way it points at a file that actually exists.
# #     """
# #     # Guard against an empty/missing job_id (e.g. a rejected/invalid-data
# #     # report with no real job to attach to) - without this, the artifact
# #     # filename becomes a bare "_report.txt"/"_report.pdf" (leading
# #     # underscore, no id), which is a degenerate filename some artifact
# #     # storage backends choke on.
# #     if not job_id:
# #         job_id = f"UNKNOWN-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"

# #     fmt = "txt" if rejected else requested_format
# #     file_path = None

# #     if fmt in ("txt", "both"):
# #         file_path = await render_txt_report(job_id, sections, tool_context)
# #     if fmt in ("pdf", "both") and not rejected:
# #         file_path = await render_pdf_report(job_id, sections, tool_context)

# #     output = ReportOutput(
# #         job_id=job_id, application=application, scenario=scenario,
# #         overall_status=overall_status, report_format=fmt, file_path=file_path,
# #         generated_at=datetime.now(timezone.utc).isoformat(),
# #         sections=[ReportSection(**s) for s in sections], rejected=rejected,
# #     )
# #     return output.model_dump()

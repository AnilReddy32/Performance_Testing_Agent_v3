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

import csv
import json
import math
from pathlib import Path
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any, List, Optional

from google.adk.tools import ToolContext

from Performance_Testing_Agent.execution_context import (
    artifact_directory_reference,
    resolve_artifact_directory,
)

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
    "timeseries_latency_degradation_pct": 20.0,
    "timeseries_error_rate_increase_pct_points": 1.0,
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


def _pearson_correlation(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 3:
        return None
    left_mean = mean(left)
    right_mean = mean(right)
    left_variance = sum((value - left_mean) ** 2 for value in left)
    right_variance = sum((value - right_mean) ** 2 for value in right)
    if left_variance == 0 or right_variance == 0:
        return None
    covariance = sum(
        (left_value - left_mean) * (right_value - right_mean)
        for left_value, right_value in zip(left, right)
    )
    return round(covariance / math.sqrt(left_variance * right_variance), 4)


def _read_aligned_time_series(
    path: Path,
    run_started_at: datetime,
) -> list[dict[str, Any]]:
    required_fields = {
        "timestamp",
        "elapsed_seconds",
        "bucket_duration_seconds",
        "requests",
        "successful_requests",
        "failed_requests",
        "avg_response_time_ms",
        "throughput_rps",
        "cpu_avg_percent",
        "cpu_peak_percent",
        "memory_avg_percent",
        "memory_peak_percent",
        "execution_data_source",
        "execution_measurement_scope",
        "monitoring_data_source",
        "monitoring_measurement_scope",
        "target_resource_metrics",
    }
    rows: list[dict[str, Any]] = []
    with path.open("r", newline="", encoding="utf-8") as series_file:
        reader = csv.DictReader(series_file)
        if not required_fields.issubset(reader.fieldnames or []):
            raise ValueError("The aligned time-series CSV is missing required fields.")
        for row_number, raw in enumerate(reader, start=2):
            if (
                raw.get("execution_data_source") != "k6"
                or raw.get("execution_measurement_scope")
                != "load_generator_observed_http_traffic"
                or raw.get("target_resource_metrics") != "false"
            ):
                raise ValueError(
                    f"Aligned time-series row {row_number} has invalid execution provenance."
                )
            if raw.get("monitoring_data_source") and (
                raw.get("monitoring_data_source") != "psutil"
                or raw.get("monitoring_measurement_scope") != "load_generator_host"
            ):
                raise ValueError(
                    f"Aligned time-series row {row_number} has invalid monitoring provenance."
                )

            def number(field: str, *, optional: bool = False) -> float | None:
                value = raw.get(field, "")
                if optional and value == "":
                    return None
                try:
                    parsed = float(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(
                        f"Aligned time-series row {row_number} has invalid {field}."
                    ) from exc
                if not math.isfinite(parsed):
                    raise ValueError(
                        f"Aligned time-series row {row_number} has non-finite {field}."
                    )
                return parsed

            elapsed = number("elapsed_seconds")
            duration = number("bucket_duration_seconds")
            requests = number("requests")
            successful = number("successful_requests")
            failed = number("failed_requests")
            if (
                elapsed is None
                or duration is None
                or requests is None
                or successful is None
                or failed is None
                or elapsed < 0
                or duration <= 0
                or min(requests, successful, failed) < 0
                or requests != int(requests)
                or successful != int(successful)
                or failed != int(failed)
                or successful + failed != requests
            ):
                raise ValueError(
                    f"Aligned time-series row {row_number} contains invalid request counts."
                )
            try:
                timestamp = datetime.fromisoformat(raw["timestamp"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"Aligned time-series row {row_number} has an invalid timestamp."
                ) from exc
            if (
                timestamp.tzinfo is None
                or timestamp.utcoffset() != timedelta(0)
                or abs((timestamp - run_started_at).total_seconds() - elapsed) > 0.001
            ):
                raise ValueError(
                    f"Aligned time-series row {row_number} timestamp is not UTC-aligned "
                    "to the run start."
                )
            if duration > 5 or (
                rows
                and (
                    rows[-1]["bucket_duration_seconds"] != 5
                    or abs(
                        elapsed
                        - (
                            rows[-1]["elapsed_seconds"]
                            + rows[-1]["bucket_duration_seconds"]
                        )
                    )
                    > 0.001
                )
            ) or (not rows and elapsed != 0):
                raise ValueError(
                    f"Aligned time-series row {row_number} is out of bucket order "
                    "or has an invalid duration."
                )
            latency = number("avg_response_time_ms", optional=True)
            throughput = number("throughput_rps", optional=True)
            cpu = number("cpu_avg_percent", optional=True)
            memory = number("memory_avg_percent", optional=True)
            cpu_peak = number("cpu_peak_percent", optional=True)
            memory_peak = number("memory_peak_percent", optional=True)
            if latency is not None and latency < 0:
                raise ValueError("Latency values cannot be negative.")
            if throughput is not None and throughput < 0:
                raise ValueError("Throughput values cannot be negative.")
            expected_throughput = requests / duration
            if throughput is None or not math.isclose(
                throughput,
                expected_throughput,
                rel_tol=1e-6,
                abs_tol=1e-6,
            ):
                raise ValueError(
                    f"Aligned time-series row {row_number} has inconsistent throughput."
                )
            for resource_value in (cpu, memory, cpu_peak, memory_peak):
                if resource_value is not None and not 0 <= resource_value <= 100:
                    raise ValueError("Host resource percentages must be between 0 and 100.")
            error_rate = failed / requests * 100 if requests else None
            rows.append(
                {
                    "elapsed_seconds": elapsed,
                    "bucket_duration_seconds": duration,
                    "requests": int(requests),
                    "successful_requests": int(successful),
                    "failed_requests": int(failed),
                    "avg_response_time_ms": latency,
                    "throughput_rps": throughput,
                    "error_rate_pct": error_rate,
                    "cpu_avg_percent": cpu,
                    "cpu_peak_percent": cpu_peak,
                    "memory_avg_percent": memory,
                    "memory_peak_percent": memory_peak,
                }
            )
    if not rows:
        raise ValueError("The aligned time-series CSV contains no data rows.")
    return rows


def _execution_report_context(
    state: dict[str, Any],
    job_id: str,
    execution_mode: str,
) -> dict[str, Any]:
    profile = state.get("workload_profile")
    profile_fields = (
        "tool",
        "target_url",
        "endpoint",
        "method",
        "users",
        "max_rps",
        "duration_seconds",
        "ramp_up_seconds",
        "expected_status_code",
        "expected_response_time_ms",
        "p95_threshold_ms",
    )
    execution_profile = (
        {
            field: profile[field]
            for field in profile_fields
            if profile.get(field) is not None
        }
        if isinstance(profile, dict)
        else None
    )

    execution_artifacts: dict[str, str] = {}
    manifest = state.get("execution_artifacts")
    if (
        isinstance(manifest, dict)
        and manifest.get("job_id") == job_id
        and manifest.get("execution_mode") == execution_mode
    ):
        raw_artifacts = manifest.get("artifacts")
        if isinstance(raw_artifacts, dict):
            execution_artifacts = {
                key: value
                for key, value in raw_artifacts.items()
                if isinstance(key, str)
                and isinstance(value, str)
                and value.strip()
            }
    try:
        artifact_directory = artifact_directory_reference(job_id)
    except ValueError:
        artifact_directory = None

    return {
        "execution_profile": execution_profile,
        "execution_artifact_directory": artifact_directory,
        "execution_artifacts": execution_artifacts,
    }


def analyze_timeseries(tool_context: ToolContext) -> dict:
    """Compute deterministic trends from this job's aligned time-series artifact."""
    state = tool_context.state
    job_id_value = state.get("job_id")
    job_id = job_id_value if isinstance(job_id_value, str) else "unknown"
    execution_mode = str(state.get("execution_mode", "SIMULATED")).upper()
    report_context = _execution_report_context(
        state,
        job_id,
        execution_mode,
    )
    if execution_mode not in {"REAL", "SIMULATED"}:
        return {
            "status": "unavailable",
            "job_id": job_id,
            "execution_mode": execution_mode,
            **report_context,
            "provenance": {
                "execution_mode": execution_mode,
                "time_series": {
                    "status": "unavailable",
                    "data_source": None,
                    "measurement_scope": None,
                    "target_resource_metrics": False,
                },
            },
            "findings": [],
            "reason": "The execution mode is not recognized.",
        }
    unavailable_reason = (
        "Deterministic time-series analysis requires an aligned REAL "
        "execution artifact."
        if execution_mode != "REAL"
        else "The REAL aligned time series is unavailable."
    )
    unavailable_provenance: dict[str, Any] = {
        "execution_mode": execution_mode,
        "time_series": {
            "status": (
                "simulated_estimate"
                if execution_mode == "SIMULATED"
                else "unavailable"
            ),
            "data_source": (
                "simulated_estimate"
                if execution_mode == "SIMULATED"
                else None
            ),
            "measurement_scope": (
                "simulated_estimate"
                if execution_mode == "SIMULATED"
                else None
            ),
            "target_resource_metrics": False,
        },
        "note": (
            "No time-series measurements are generated for SIMULATED runs."
            if execution_mode == "SIMULATED"
            else "REAL execution does not fall back to simulated measurements."
        ),
    }
    unavailable: dict[str, Any] = {
        "status": "unavailable",
        "job_id": job_id,
        "execution_mode": execution_mode,
        **report_context,
        "provenance": unavailable_provenance,
        "findings": [],
    }
    if execution_mode != "REAL":
        return {
            **unavailable,
            "reason": unavailable_reason,
        }

    manifest = state.get("execution_artifacts")
    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    series_name = (
        artifacts.get("aligned_time_series")
        if isinstance(artifacts, dict)
        else None
    )
    metadata_name = (
        artifacts.get("measurement_metadata")
        if isinstance(artifacts, dict)
        else None
    )
    if (
        not isinstance(job_id_value, str)
        or not isinstance(manifest, dict)
        or manifest.get("job_id") != job_id
        or manifest.get("execution_mode") != "REAL"
        or not isinstance(series_name, str)
        or not isinstance(metadata_name, str)
    ):
        return {
            **unavailable,
            "reason": "The REAL job has no matching aligned time-series artifacts.",
        }

    metadata: dict[str, Any]
    try:
        job_directory = resolve_artifact_directory(job_id)
        series_path = (job_directory / series_name).resolve()
        metadata_path = (job_directory / metadata_name).resolve()
        if (
            series_path.parent != job_directory
            or metadata_path.parent != job_directory
            or not series_path.is_file()
            or not metadata_path.is_file()
        ):
            raise ValueError("The aligned time-series artifacts are missing or outside the job directory.")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        shared_schema = metadata.get("shared_time_series") if isinstance(metadata, dict) else None
        if (
            not isinstance(metadata, dict)
            or metadata.get("job_id") != job_id
            or not isinstance(shared_schema, dict)
            or shared_schema.get("schema_version") != "1.0"
            or shared_schema.get("bucket_seconds") != 5
            or shared_schema.get("alignment_origin") != "k6_run_window.started_at"
        ):
            raise ValueError("The aligned time-series metadata does not match schema 1.0.")
        run_window = metadata.get("k6_run_window")
        run_started_at_value = (
            run_window.get("started_at")
            if isinstance(run_window, dict)
            else None
        )
        if not isinstance(run_started_at_value, str):
            raise ValueError("The aligned time-series metadata has no k6 start time.")
        run_started_at = datetime.fromisoformat(run_started_at_value)
        if (
            run_started_at.tzinfo is None
            or run_started_at.utcoffset() != timedelta(0)
        ):
            raise ValueError("The k6 start time must be timezone-aware UTC.")
        rows = _read_aligned_time_series(series_path, run_started_at)
    except (OSError, UnicodeError, ValueError, csv.Error, json.JSONDecodeError) as exc:
        return {
            **unavailable,
            "reason": f"Aligned time-series analysis could not read valid data: {exc}",
        }

    measured_rows = [
        row for row in rows if row["avg_response_time_ms"] is not None
    ]
    if not measured_rows:
        return {
            **unavailable,
            "reason": "The aligned time series contains no latency observations.",
        }
    source_metadata = metadata.get("sources", {})
    runtime_source = (
        source_metadata.get("runtime_samples")
        if isinstance(source_metadata, dict)
        else None
    )
    monitoring_has_samples = any(
        row["cpu_avg_percent"] is not None
        or row["memory_avg_percent"] is not None
        for row in rows
    )
    monitoring_status = (
        runtime_source.get("status")
        if isinstance(runtime_source, dict)
        else ("available" if monitoring_has_samples else "unavailable")
    )
    if isinstance(runtime_source, dict) and (
        runtime_source.get("data_source") != "psutil"
        or runtime_source.get("measurement_scope") != "load_generator_host"
        or runtime_source.get("target_resource_metrics") is not False
        or monitoring_status not in {
            "available",
            "partial",
            "unavailable",
            "no_samples",
        }
    ):
        return {
            **unavailable,
            "reason": "The runtime sample provenance metadata is invalid.",
        }
    provenance = {
        "execution_mode": "REAL",
        "time_series": {
            "status": "measured",
            "data_source": "k6",
            "measurement_scope": "load_generator_observed_http_traffic",
            "target_resource_metrics": False,
        },
        "monitoring": {
            "status": monitoring_status,
            "data_source": "psutil" if monitoring_has_samples else None,
            "measurement_scope": (
                "load_generator_host" if monitoring_has_samples else None
            ),
            "target_resource_metrics": False,
        },
        "workload_profile": {
            "status": "trusted_session_state",
            "data_source": "workload_profile",
            "measurement_scope": "configured_test_load",
        },
    }
    finding_provenance = {
        "execution_mode": "REAL",
        "data_sources": ["k6"],
    }

    latency_values = [row["avg_response_time_ms"] for row in measured_rows]
    assert all(value is not None for value in latency_values)
    latency_start = float(latency_values[0])
    latency_end = float(latency_values[-1])
    latency_change_pct = (
        (latency_end - latency_start) / latency_start * 100
        if latency_start > 0
        else None
    )
    rates = [row for row in rows if row["error_rate_pct"] is not None]
    rising_error_buckets = [
        {
            "elapsed_seconds": current["elapsed_seconds"],
            "previous_error_rate_pct": previous["error_rate_pct"],
            "error_rate_pct": current["error_rate_pct"],
            "increase_percentage_points": round(
                current["error_rate_pct"] - previous["error_rate_pct"],
                4,
            ),
            "requests": current["requests"],
            "throughput_rps": current["throughput_rps"],
        }
        for previous, current in zip(
            rates,
            rates[1:],
        )
        if current["error_rate_pct"] > previous["error_rate_pct"]
    ]
    first_rising_error = (
        rising_error_buckets[0]["elapsed_seconds"]
        if rising_error_buckets
        else None
    )

    latency_cpu_pairs = [
        (row["avg_response_time_ms"], row["cpu_avg_percent"])
        for row in rows
        if row["avg_response_time_ms"] is not None
        and row["cpu_avg_percent"] is not None
    ]
    latency_memory_pairs = [
        (row["avg_response_time_ms"], row["memory_avg_percent"])
        for row in rows
        if row["avg_response_time_ms"] is not None
        and row["memory_avg_percent"] is not None
    ]
    latency_cpu_correlation = _pearson_correlation(
        [pair[0] for pair in latency_cpu_pairs],
        [pair[1] for pair in latency_cpu_pairs],
    )
    latency_memory_correlation = _pearson_correlation(
        [pair[0] for pair in latency_memory_pairs],
        [pair[1] for pair in latency_memory_pairs],
    )

    profile = state.get("workload_profile")
    ramp_up_seconds = (
        profile.get("ramp_up_seconds", 0)
        if isinstance(profile, dict)
        else 0
    )
    if (
        isinstance(ramp_up_seconds, bool)
        or not isinstance(ramp_up_seconds, (int, float))
        or not math.isfinite(float(ramp_up_seconds))
        or ramp_up_seconds < 0
    ):
        return {
            **unavailable,
            "reason": "The workload profile has an invalid ramp_up_seconds value.",
        }
    ramp_up_seconds = float(ramp_up_seconds)
    ramp_rows = [
        row for row in measured_rows
        if row["elapsed_seconds"] + row["bucket_duration_seconds"]
        <= ramp_up_seconds
    ]
    post_ramp_rows = [
        row for row in measured_rows
        if row["elapsed_seconds"] >= ramp_up_seconds
    ]
    ramp_latency = (
        mean(float(row["avg_response_time_ms"]) for row in ramp_rows)
        if ramp_rows
        else None
    )
    post_ramp_latency = (
        mean(float(row["avg_response_time_ms"]) for row in post_ramp_rows)
        if post_ramp_rows
        else None
    )
    ramp_error_rates = [
        row["error_rate_pct"] for row in ramp_rows
        if row["error_rate_pct"] is not None
    ]
    post_ramp_error_rates = [
        row["error_rate_pct"] for row in post_ramp_rows
        if row["error_rate_pct"] is not None
    ]
    ramp_error_rate = mean(ramp_error_rates) if ramp_error_rates else None
    post_ramp_error_rate = (
        mean(post_ramp_error_rates) if post_ramp_error_rates else None
    )
    post_ramp_latency_change_pct = (
        (post_ramp_latency - ramp_latency) / ramp_latency * 100
        if ramp_latency is not None and ramp_latency > 0 and post_ramp_latency is not None
        else None
    )
    post_ramp_error_increase_pp = (
        post_ramp_error_rate - ramp_error_rate
        if ramp_error_rate is not None and post_ramp_error_rate is not None
        else None
    )
    latency_degraded = (
        post_ramp_latency_change_pct is not None
        and post_ramp_latency_change_pct
        > THRESHOLDS["timeseries_latency_degradation_pct"]
    )
    errors_degraded = (
        post_ramp_error_increase_pp is not None
        and post_ramp_error_increase_pp
        > THRESHOLDS["timeseries_error_rate_increase_pct_points"]
    )
    post_ramp_degraded = latency_degraded or errors_degraded

    requests = [row["requests"] for row in rows]
    throughput_values = [
        row["throughput_rps"] for row in rows
        if row["throughput_rps"] is not None
    ]
    total_requests = sum(requests)
    total_failed = sum(row["failed_requests"] for row in rows)
    observed_load_rows = [
        row for row in rows if row["throughput_rps"] is not None
    ]
    first_throughput = (
        float(observed_load_rows[0]["throughput_rps"])
        if observed_load_rows
        else None
    )
    last_throughput = (
        float(observed_load_rows[-1]["throughput_rps"])
        if observed_load_rows
        else None
    )
    load_change_pct = (
        (last_throughput - first_throughput) / first_throughput * 100
        if first_throughput is not None
        and last_throughput is not None
        and first_throughput > 0
        else None
    )
    overall_error_rate = (
        total_failed / total_requests * 100
        if total_requests
        else None
    )
    findings = []
    if latency_change_pct is not None and latency_change_pct > 0:
        findings.append(
            {
                "category": "latency_trend",
                "severity": "warning" if latency_change_pct > 20 else "info",
                **finding_provenance,
                "message": (
                    f"Bucket-average latency increased {latency_change_pct:.2f}% "
                    "from the first to the last observed bucket."
                ),
            }
        )
    if rising_error_buckets:
        first_error_rate = rising_error_buckets[0]["error_rate_pct"]
        first_error_increase = rising_error_buckets[0][
            "increase_percentage_points"
        ]
        first_error_load = rising_error_buckets[0]["throughput_rps"]
        findings.append(
            {
                "category": "error_trend",
                "severity": (
                    "warning"
                    if first_error_increase
                    > THRESHOLDS[
                        "timeseries_error_rate_increase_pct_points"
                    ]
                    else "info"
                ),
                **finding_provenance,
                "message": (
                    f"Error rate first increased at elapsed second "
                    f"{first_rising_error} to {first_error_rate:.2f}% at "
                    f"{first_error_load:.4f} requests/second."
                ),
            }
        )
    if post_ramp_degraded:
        findings.append(
            {
                "category": "post_ramp_degradation",
                "severity": "warning",
                "execution_mode": "REAL",
                "data_sources": ["k6", "workload_profile"],
                "message": (
                    "Post-ramp latency or error rate exceeded the configured "
                    "degradation comparison threshold."
                ),
            }
        )

    return {
        "status": "analyzed",
        "job_id": job_id,
        "execution_mode": "REAL",
        **report_context,
        "provenance": provenance,
        "schema_version": shared_schema["schema_version"],
        "bucket_seconds": shared_schema["bucket_seconds"],
        "bucket_count": len(rows),
        "series": [
            {
                "elapsed_seconds": row["elapsed_seconds"],
                "avg_response_time_ms": row["avg_response_time_ms"],
                "throughput_rps": row["throughput_rps"],
                "cpu_avg_percent": row["cpu_avg_percent"],
            }
            for row in rows
        ],
        "latency": {
            "first_observed_bucket_avg_ms": latency_start,
            "last_observed_bucket_avg_ms": latency_end,
            "change_percentage": (
                round(latency_change_pct, 4)
                if latency_change_pct is not None
                else None
            ),
        },
        "errors": {
            "total_requests": total_requests,
            "failed_requests": total_failed,
            "overall_error_rate_pct": (
                round(overall_error_rate, 4)
                if overall_error_rate is not None
                else None
            ),
            "first_rising_error_elapsed_seconds": first_rising_error,
            "rising_error_buckets": rising_error_buckets,
        },
        "load": {
            "first_bucket_throughput_rps": first_throughput,
            "last_bucket_throughput_rps": last_throughput,
            "throughput_change_percentage": (
                round(load_change_pct, 4)
                if load_change_pct is not None
                else None
            ),
            "peak_requests_per_bucket": max(requests),
            "peak_throughput_rps": (
                round(max(throughput_values), 4)
                if throughput_values
                else None
            ),
            "average_throughput_rps": (
                round(mean(throughput_values), 4)
                if throughput_values
                else None
            ),
        },
        "resource_correlation": {
            "latency_vs_load_generator_cpu_pearson": latency_cpu_correlation,
            "latency_vs_load_generator_memory_pearson": latency_memory_correlation,
            "cpu_paired_buckets": len(latency_cpu_pairs),
            "memory_paired_buckets": len(latency_memory_pairs),
            "interpretation": (
                "Correlations are descriptive associations with host-wide "
                "load-generator resources; they do not establish target "
                "resource behavior or causation."
            ),
        },
        "degradation_after_ramp_up": {
            "ramp_up_seconds": ramp_up_seconds,
            "ramp_up_latency_avg_ms": (
                round(ramp_latency, 4) if ramp_latency is not None else None
            ),
            "post_ramp_latency_avg_ms": (
                round(post_ramp_latency, 4)
                if post_ramp_latency is not None
                else None
            ),
            "post_ramp_latency_change_pct": (
                round(post_ramp_latency_change_pct, 4)
                if post_ramp_latency_change_pct is not None
                else None
            ),
            "ramp_up_error_rate_pct": (
                round(ramp_error_rate, 4)
                if ramp_error_rate is not None
                else None
            ),
            "post_ramp_error_rate_pct": (
                round(post_ramp_error_rate, 4)
                if post_ramp_error_rate is not None
                else None
            ),
            "post_ramp_error_increase_percentage_points": (
                round(post_ramp_error_increase_pp, 4)
                if post_ramp_error_increase_pp is not None
                else None
            ),
            "degraded": (
                post_ramp_degraded
                if ramp_rows and post_ramp_rows
                else None
            ),
            "comparison_status": (
                "compared"
                if ramp_rows and post_ramp_rows
                else "insufficient_ramp_or_post_ramp_data"
            ),
        },
        "thresholds": {
            "latency_degradation_pct": THRESHOLDS[
                "timeseries_latency_degradation_pct"
            ],
            "error_rate_increase_percentage_points": THRESHOLDS[
                "timeseries_error_rate_increase_pct_points"
            ],
        },
        "findings": findings,
    }


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
    if cpu is not None and cpu > THRESHOLDS["cpu_usage_pct"]:
        anomalies.append(f"CPU usage {cpu}% exceeds {THRESHOLDS['cpu_usage_pct']}% threshold.")
    if mem is not None and mem > THRESHOLDS["memory_usage_pct"]:
        anomalies.append(f"Memory usage {mem}% exceeds {THRESHOLDS['memory_usage_pct']}% threshold.")
    if db_conn is not None and db_conn > THRESHOLDS["db_connections_max"]:
        anomalies.append(f"DB connections {db_conn} exceeds pool ceiling of {THRESHOLDS['db_connections_max']}.")
    if alerts:
        anomalies.append(f"{len(alerts)} monitoring alert(s) reported: {alerts}")

    cross_check_note = None
    if (
        mon_response_time is not None
        and test_execution_avg_response_time is not None
        and test_execution_avg_response_time > 0
    ):
        diff_pct = abs(mon_response_time - test_execution_avg_response_time) / test_execution_avg_response_time * 100
        if diff_pct > THRESHOLDS["response_time_cross_check_pct"]:
            cross_check_note = (
                f"monitoring_agent's response_time ({mon_response_time}ms) disagrees with "
                f"test_execution_agent's avg_response_time ({test_execution_avg_response_time}ms) "
                f"by {diff_pct:.0f}% -- worth checking measurement points/clock sync."
            )

    if mon_status == "UNAVAILABLE":
        anomalies.append("Monitoring data was unavailable for this job.")
        status = "warning"
    elif any("exceeds" in a for a in anomalies) and (
        (cpu is not None and cpu > THRESHOLDS["cpu_usage_pct"])
        or (mem is not None and mem > THRESHOLDS["memory_usage_pct"])
    ):
        status = "fail" if (
            (cpu is not None and cpu > 95)
            or (mem is not None and mem > 95)
        ) else "warning"
    elif anomalies:
        status = "warning"
    else:
        status = "pass"

    return {
        "status": status,
        "monitoring_reported_status": mon_status,
        "cpu_usage": cpu,
        "cpu_peak_usage": monitoring_result.get("cpu_peak_usage"),
        "memory_usage": mem,
        "memory_peak_usage": monitoring_result.get("memory_peak_usage"),
        "db_connections": db_conn,
        "tps": tps, "monitoring_response_time": mon_response_time,
        "alerts": alerts, "anomalies": anomalies, "cross_check_note": cross_check_note,
        "data_source": monitoring_result.get("data_source"),
        "measurement_provenance": monitoring_result.get(
            "measurement_provenance", {}
        ),
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
    time_series_analysis: Optional[dict] = None,
) -> dict:
    """
    Assembles and VALIDATES the final AnalysisOutput. Overall status is the
    WORST of: performance (api_findings), infra health, security, and
    actionable time-series findings. A security FAIL should not be hidden by
    a clean performance run, and vice versa. Call this last, and return its
    result as your final answer.

    test_case_prompt: the user's original request text, passed through
    unmodified so the Report Agent can include it in the final report.
    """
    findings = findings or []
    execution_context: dict[str, Any] = {
        "execution_mode": None,
        "execution_profile": None,
        "execution_artifact_directory": None,
        "execution_artifacts": {},
    }
    if (
        isinstance(time_series_analysis, dict)
        and time_series_analysis.get("job_id") == job_id
        and time_series_analysis.get("execution_mode")
        in {"REAL", "SIMULATED"}
    ):
        execution_context["execution_mode"] = time_series_analysis[
            "execution_mode"
        ]
        profile = time_series_analysis.get("execution_profile")
        if isinstance(profile, dict):
            execution_context["execution_profile"] = profile
        artifact_directory = time_series_analysis.get(
            "execution_artifact_directory"
        )
        if isinstance(artifact_directory, str):
            execution_context["execution_artifact_directory"] = (
                artifact_directory
            )
        artifacts = time_series_analysis.get("execution_artifacts")
        if isinstance(artifacts, dict):
            execution_context["execution_artifacts"] = {
                key: value
                for key, value in artifacts.items()
                if isinstance(key, str) and isinstance(value, str)
            }

    if quality_report["status"] == "invalid":
        critical_issues = [i["issue"] for i in quality_report["issues"] if i["severity"] == "critical"]
        output = AnalysisOutput(
            job_id=job_id, application=application, scenario=scenario,
            test_case_prompt=test_case_prompt,
            data_quality_status="invalid",
            data_quality_issues=[DataQualityIssue(**i) for i in quality_report["issues"]],
            unusable_reason="; ".join(critical_issues) or "Data failed quality validation.",
            time_series_analysis=time_series_analysis,
            **execution_context,
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

    if time_series_analysis and time_series_analysis.get("status") == "analyzed":
        severity_rank = {"info": 0, "warning": 1, "fail": 2}
        time_series_rank = max(
            (
                severity_rank.get(
                    str(finding.get("severity", "warning")).lower(),
                    1,
                )
                for finding in time_series_analysis.get("findings", [])
                if isinstance(finding, dict)
            ),
            default=0,
        )
        worst = max(worst, time_series_rank)

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
        time_series_analysis=time_series_analysis,
        **execution_context,
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

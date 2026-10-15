import csv
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext

from Performance_Testing_Agent.config import LITELLM_MODEL_NAME
from Performance_Testing_Agent.execution_context import (
    resolve_artifact_directory,
)

from .metric_simulator import simulate_monitoring_metrics


def _unavailable_real_metrics(
    *,
    job_id: str,
    application: str,
    scenario: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "job_id": job_id,
        "application": application,
        "scenario": scenario,
        "status": "UNAVAILABLE",
        "execution_mode": "REAL",
        "data_source": "REAL monitoring samples unavailable",
        "measurement_provenance": {},
        "cpu_usage": None,
        "cpu_peak_usage": None,
        "memory_usage": None,
        "memory_peak_usage": None,
        "db_connections": None,
        "response_time": None,
        "tps": None,
        "alerts": [],
        "message": reason,
    }


def _collect_real_monitoring_metrics(
    state: dict[str, Any],
) -> dict[str, Any]:
    execution_value = state.get("test_execution_result")
    execution = execution_value if isinstance(execution_value, dict) else None
    job_id = str(state.get("job_id") or "unknown")
    application = (
        str(execution.get("application") or "unknown")
        if execution
        else "unknown"
    )
    scenario = (
        str(execution.get("scenario") or "unknown")
        if execution
        else "unknown"
    )

    if state.get("execution_status") != "completed" or execution is None:
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason="No completed REAL test execution is available for monitoring.",
        )
    if execution.get("job_id") != job_id:
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason="The REAL execution result does not match the current job.",
        )

    manifest = state.get("execution_artifacts")
    artifacts = manifest.get("artifacts") if isinstance(manifest, dict) else None
    if (
        not isinstance(manifest, dict)
        or manifest.get("job_id") != job_id
        or manifest.get("execution_mode") != "REAL"
    ):
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason="The REAL execution artifact manifest does not match this job.",
        )
    samples_name = artifacts.get("monitoring_samples") if isinstance(artifacts, dict) else None
    if not isinstance(samples_name, str) or not samples_name:
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason="The REAL execution artifact manifest has no monitoring sample file.",
        )
    metadata_name = (
        artifacts.get("measurement_metadata")
        if isinstance(artifacts, dict)
        else None
    )
    if not isinstance(metadata_name, str) or not metadata_name:
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason="The REAL execution artifact manifest has no measurement metadata.",
        )

    try:
        job_directory = resolve_artifact_directory(job_id)
        samples_path = (job_directory / samples_name).resolve()
        metadata_path = (job_directory / metadata_name).resolve()
        if (
            samples_path.parent != job_directory
            or not samples_path.is_file()
        ):
            raise ValueError(
                "The monitoring sample path is missing or outside the job directory."
            )
        if metadata_path.parent != job_directory or not metadata_path.is_file():
            raise ValueError(
                "The measurement metadata path is missing or outside the job directory."
            )
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        sources = metadata.get("sources") if isinstance(metadata, dict) else None
        runtime_source = (
            sources.get("runtime_samples") if isinstance(sources, dict) else None
        )
        if (
            not isinstance(metadata, dict)
            or
            metadata.get("job_id") != job_id
            or not isinstance(runtime_source, dict)
            or runtime_source.get("data_source") != "psutil"
            or runtime_source.get("measurement_scope") != "load_generator_host"
            or runtime_source.get("target_resource_metrics") is not False
        ):
            raise ValueError(
                "Measurement metadata does not match the REAL host sample artifact."
            )

        cpu_values: list[float] = []
        memory_values: list[float] = []
        with samples_path.open("r", newline="", encoding="utf-8") as samples_file:
            reader = csv.DictReader(samples_file)
            required_fields = {
                "timestamp",
                "cpu_percent",
                "memory_percent",
                "measurement_scope",
                "data_source",
                "target_resource_metric",
            }
            if not required_fields.issubset(reader.fieldnames or []):
                raise ValueError("The REAL monitoring sample CSV has an invalid header.")
            for row in reader:
                if (
                    row.get("measurement_scope") != "load_generator_host"
                    or row.get("data_source") != "psutil"
                    or row.get("target_resource_metric") != "false"
                ):
                    raise ValueError(
                        "The monitoring CSV contains untrusted or mislabeled samples."
                    )
                timestamp_value = row.get("timestamp")
                if not timestamp_value:
                    raise ValueError(
                        "The monitoring CSV contains a missing timestamp."
                    )
                timestamp = datetime.fromisoformat(
                    timestamp_value.replace("Z", "+00:00")
                )
                if timestamp.tzinfo is None:
                    raise ValueError(
                        "The monitoring CSV contains a timezone-naive timestamp."
                    )
                cpu = float(row["cpu_percent"])
                memory = float(row["memory_percent"])
                if (
                    not math.isfinite(cpu)
                    or not math.isfinite(memory)
                    or not 0 <= cpu <= 100
                    or not 0 <= memory <= 100
                ):
                    raise ValueError(
                        "The REAL monitoring CSV contains invalid CPU or memory values."
                    )
                cpu_values.append(cpu)
                memory_values.append(memory)
    except (OSError, UnicodeError, ValueError, csv.Error) as exc:
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason=f"REAL monitoring samples could not be read: {exc}",
        )

    if not cpu_values or len(cpu_values) != len(memory_values):
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason="The REAL monitoring sample CSV contains no complete CPU/memory samples.",
        )
    if runtime_source.get("sample_count") != len(cpu_values):
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason="The REAL sample count does not match the measurement metadata.",
        )
    sample_status = runtime_source.get("status")
    if sample_status not in {"available", "partial"}:
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason="Measurement metadata marks the REAL host samples unavailable.",
        )

    average_cpu = round(sum(cpu_values) / len(cpu_values), 2)
    peak_cpu = round(max(cpu_values), 2)
    average_memory = round(sum(memory_values) / len(memory_values), 2)
    peak_memory = round(max(memory_values), 2)
    response_time = execution.get("avg_response_time")
    throughput = execution.get("throughput")
    if (
        isinstance(response_time, bool)
        or not isinstance(response_time, (int, float))
        or not math.isfinite(float(response_time))
        or isinstance(throughput, bool)
        or not isinstance(throughput, (int, float))
        or not math.isfinite(float(throughput))
    ):
        return _unavailable_real_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            reason="The REAL execution result is missing valid latency/throughput metrics.",
        )

    alerts = []
    if peak_cpu > 85:
        alerts.append("High load-generator host CPU usage")
    if peak_memory > 80:
        alerts.append("High load-generator host memory usage")
    if response_time > 1000:
        alerts.append("High client-observed response time")
    if peak_cpu > 95 or peak_memory > 95:
        status = "CRITICAL"
    elif alerts:
        status = "WARNING"
    else:
        status = "OK"

    return {
        "job_id": job_id,
        "application": application,
        "scenario": scenario,
        "status": status,
        "execution_mode": "REAL",
        "data_source": (
            (
                "REAL (partial): psutil load-generator host samples and "
                "k6 client-observed metrics"
                if sample_status == "partial"
                else "REAL: psutil load-generator host samples and "
                "k6 client-observed metrics"
            )
        ),
        "sampling_status": sample_status,
        "sampling_error": runtime_source.get("sampling_error"),
        "measurement_provenance": {
            "cpu_usage": {
                "data_source": "psutil",
                "measurement_scope": "load_generator_host",
                "statistic": "average_percent",
                "target_resource_metric": False,
            },
            "cpu_peak_usage": {
                "data_source": "psutil",
                "measurement_scope": "load_generator_host",
                "statistic": "peak_percent",
                "target_resource_metric": False,
            },
            "memory_usage": {
                "data_source": "psutil",
                "measurement_scope": "load_generator_host",
                "statistic": "average_percent",
                "target_resource_metric": False,
            },
            "memory_peak_usage": {
                "data_source": "psutil",
                "measurement_scope": "load_generator_host",
                "statistic": "peak_percent",
                "target_resource_metric": False,
            },
            "response_time": {
                "data_source": "k6",
                "measurement_scope": "load_generator_observed_http_traffic",
                "statistic": "average_ms",
                "target_resource_metric": False,
            },
            "tps": {
                "data_source": "k6",
                "measurement_scope": "load_generator_observed_http_traffic",
                "statistic": "requests_per_second",
                "target_resource_metric": False,
            },
            "db_connections": {
                "data_source": None,
                "measurement_scope": None,
                "target_resource_metric": False,
                "status": "not_collected",
                "reason": "No target-specific database telemetry provider is configured.",
            },
        },
        "sample_count": len(cpu_values),
        "cpu_usage": average_cpu,
        "cpu_peak_usage": peak_cpu,
        "memory_usage": average_memory,
        "memory_peak_usage": peak_memory,
        "db_connections": None,
        "response_time": float(response_time),
        "tps": float(throughput),
        "alerts": alerts,
    }


def collect_monitoring_metrics(tool_context: ToolContext) -> dict:
    """Collects infrastructure/performance monitoring metrics (CPU,
    memory, DB connections, response time, TPS) for this job. REAL
    executions consume their timestamped runtime sample artifact. All
    other modes use the existing labeled simulator. Stores the result
    under "monitoring_result" for downstream agents."""

    state = tool_context.state
    if str(state.get("execution_mode", "SIMULATED")).upper() == "REAL":
        result = _collect_real_monitoring_metrics(state)
    else:
        result = simulate_monitoring_metrics(state.get("test_execution_result"))
        result.update(
            {
                "execution_mode": "SIMULATED",
                "measurement_scope": "simulated_estimate",
                "measurement_provenance": {
                    metric: {
                        "data_source": result.get("data_source"),
                        "measurement_scope": "simulated_estimate",
                        "target_resource_metric": False,
                    }
                    for metric in (
                        "cpu_usage",
                        "memory_usage",
                        "db_connections",
                        "response_time",
                        "tps",
                    )
                },
            }
        )

    state["monitoring_result"] = result

    return result


# ============================================================
# Monitoring Agent -- single local tool, no arguments, reads prior
# results itself and writes its own result straight to session state
# (same convention test_execution_agent's run_test_execution_adk uses).
#
# The orchestrator wraps this agent in AgentTool. ToolContext state changes
# are forwarded into the parent session by the wrapper.
#
# output_key removed: the old version had both output_key="monitoring_result"
# AND an MCP tool -- output_key makes ADK auto-store this agent's own
# final TEXT answer into session.state["monitoring_result"] after it
# runs, which would silently overwrite the clean, structured dict that
# collect_monitoring_metrics already wrote there directly via
# tool_context.state, with whatever text the LLM happened to answer
# with. Since the tool now writes the structured result itself, nothing
# else should be allowed to overwrite it afterward.
# ============================================================

monitoring_agent = Agent(

    name="monitoring_agent",

    model=LiteLlm(model=LITELLM_MODEL_NAME),

    description=(
        "Collects infrastructure and performance monitoring metrics "
        "(CPU, Memory, DB Connections, Response Time, TPS) for this job."
    ),

    instruction="""
You are the Monitoring Agent of the ANZ Performance Testing system.

Whenever you are asked about CPU, memory, database connections,
response time, API latency, TPS, resource utilization, or to
"process", "analyze", "check", or "monitor" a scenario, call
collect_monitoring_metrics and report its exact results. REAL mode reads
the run's timestamped host samples and labels them as load-generator
measurements, not target-resource metrics. SIMULATED mode retains the
existing simulator and must identify every estimate as SIMULATED. If a
REAL sample is missing or invalid, report monitoring as unavailable; never
substitute simulated data. Do not invent or alter values returned by the
tool.
""",

    tools=[
        collect_monitoring_metrics,
    ],
)
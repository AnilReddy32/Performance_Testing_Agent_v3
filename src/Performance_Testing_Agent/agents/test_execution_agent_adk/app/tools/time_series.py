"""Shared time-series format and alignment for REAL execution artifacts."""

from __future__ import annotations

import csv
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


TIME_SERIES_SCHEMA_VERSION = "1.0"
TIME_SERIES_BUCKET_SECONDS = 5
TIME_SERIES_FIELDS = (
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
)


def _parse_timestamp(value: str, source: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{source} contains an invalid timestamp.") from exc
    if timestamp.tzinfo is None:
        raise ValueError(f"{source} timestamp must include a timezone.")
    return timestamp.astimezone(timezone.utc)


def _finite_number(value: str, field: str, source: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{source} contains an invalid {field} value.") from exc
    if not math.isfinite(number):
        raise ValueError(f"{source} contains a non-finite {field} value.")
    return number


def _read_execution_buckets(
    path: Path,
    run_started_at: datetime,
) -> dict[int, dict[str, Any]]:
    buckets: dict[int, dict[str, Any]] = {}
    with path.open("r", newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        required = {
            "timestamp",
            "requests",
            "successful_requests",
            "failed_requests",
            "avg_response_time_ms",
        }
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Execution time series is missing required columns.")
        for row in reader:
            timestamp = _parse_timestamp(row["timestamp"], "Execution time series")
            elapsed = (timestamp - run_started_at).total_seconds()
            if elapsed < 0:
                raise ValueError("Execution sample precedes the run start.")
            bucket_index = int(elapsed // TIME_SERIES_BUCKET_SECONDS)
            requests = int(_finite_number(row["requests"], "requests", "Execution time series"))
            successful = int(
                _finite_number(
                    row["successful_requests"],
                    "successful_requests",
                    "Execution time series",
                )
            )
            failed = int(
                _finite_number(
                    row["failed_requests"],
                    "failed_requests",
                    "Execution time series",
                )
            )
            average_latency: float | str = (
                ""
                if row.get("avg_response_time_ms", "") == ""
                else _finite_number(
                    row["avg_response_time_ms"],
                    "avg_response_time_ms",
                    "Execution time series",
                )
            )
            throughput = _finite_number(
                row["throughput_rps"],
                "throughput_rps",
                "Execution time series",
            )
            if (
                min(requests, successful, failed) < 0
                or successful + failed != requests
                or (average_latency != "" and average_latency < 0)
                or throughput < 0
            ):
                raise ValueError("Execution time series contains inconsistent metrics.")
            if bucket_index in buckets:
                raise ValueError("Execution time series has duplicate aligned buckets.")
            buckets[bucket_index] = {
                "requests": requests,
                "successful_requests": successful,
                "failed_requests": failed,
                "avg_response_time_ms": average_latency,
                "throughput_rps": throughput,
            }
    return buckets


def _read_monitoring_buckets(
    path: Path,
    run_started_at: datetime,
    run_finished_at: datetime,
) -> dict[int, dict[str, float]]:
    buckets: dict[int, dict[str, Any]] = {}
    with path.open("r", newline="", encoding="utf-8") as input_file:
        reader = csv.DictReader(input_file)
        required = {
            "timestamp",
            "cpu_percent",
            "memory_percent",
            "measurement_scope",
            "data_source",
            "target_resource_metric",
        }
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("Monitoring samples are missing required columns.")
        for row in reader:
            timestamp = _parse_timestamp(row["timestamp"], "Monitoring samples")
            if not run_started_at <= timestamp <= run_finished_at:
                continue
            if (
                row["measurement_scope"] != "load_generator_host"
                or row["data_source"] != "psutil"
                or row["target_resource_metric"] != "false"
            ):
                raise ValueError("Monitoring samples have invalid measurement provenance.")
            cpu = _finite_number(row["cpu_percent"], "cpu_percent", "Monitoring samples")
            memory = _finite_number(
                row["memory_percent"],
                "memory_percent",
                "Monitoring samples",
            )
            if not 0 <= cpu <= 100 or not 0 <= memory <= 100:
                raise ValueError("Monitoring samples contain out-of-range percentages.")
            elapsed = (timestamp - run_started_at).total_seconds()
            bucket_index = int(elapsed // TIME_SERIES_BUCKET_SECONDS)
            bucket = buckets.setdefault(
                bucket_index,
                {
                    "cpu": [],
                    "memory": [],
                },
            )
            bucket["cpu"].append(cpu)
            bucket["memory"].append(memory)

    return {
        bucket_index: {
            "cpu_avg_percent": sum(values["cpu"]) / len(values["cpu"]),
            "cpu_peak_percent": max(values["cpu"]),
            "memory_avg_percent": sum(values["memory"]) / len(values["memory"]),
            "memory_peak_percent": max(values["memory"]),
        }
        for bucket_index, values in buckets.items()
    }


def write_aligned_time_series(
    *,
    execution_time_series_path: Path,
    monitoring_samples_path: Path,
    output_path: Path,
    run_started_at: datetime,
    run_finished_at: datetime,
    execution_data_source: str = "k6",
) -> int:
    """Write one fixed-width elapsed-time grid with explicit per-source scope.

    UTC timestamps are converted to offsets from the execution start, then floored into
    half-open five-second windows [start, end). Missing execution counts are
    zero; latency and monitoring fields remain empty when no observation
    exists. The final window is shortened to the actual run end.
    """
    if run_started_at.tzinfo is None or run_finished_at.tzinfo is None:
        raise ValueError("Time-series alignment requires timezone-aware run times.")
    if execution_data_source not in {"k6", "jmeter"}:
        raise ValueError("Unsupported REAL execution time-series source.")
    start = run_started_at.astimezone(timezone.utc)
    finish = run_finished_at.astimezone(timezone.utc)
    duration_seconds = (finish - start).total_seconds()
    if duration_seconds <= 0:
        raise ValueError("The REAL execution run window must have positive duration.")

    execution_buckets = _read_execution_buckets(execution_time_series_path, start)
    monitoring_buckets = _read_monitoring_buckets(
        monitoring_samples_path,
        start,
        finish,
    )
    bucket_count = math.ceil(duration_seconds / TIME_SERIES_BUCKET_SECONDS)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=TIME_SERIES_FIELDS)
        writer.writeheader()
        for bucket_index in range(bucket_count):
            elapsed = bucket_index * TIME_SERIES_BUCKET_SECONDS
            bucket_start = start + timedelta(seconds=elapsed)
            bucket_duration = min(
                TIME_SERIES_BUCKET_SECONDS,
                duration_seconds - elapsed,
            )
            recorded_bucket_duration = round(bucket_duration, 6)
            execution_values = execution_buckets.get(bucket_index, {})
            monitoring_values = monitoring_buckets.get(bucket_index, {})
            requests = execution_values.get("requests", 0)
            throughput = (
                requests / recorded_bucket_duration
                if requests and recorded_bucket_duration > 0
                else 0.0 if requests == 0 else ""
            )
            writer.writerow(
                {
                    "timestamp": bucket_start.isoformat(),
                    "elapsed_seconds": elapsed,
                    "bucket_duration_seconds": recorded_bucket_duration,
                    "requests": requests,
                    "successful_requests": execution_values.get(
                        "successful_requests",
                        0,
                    ),
                    "failed_requests": execution_values.get("failed_requests", 0),
                    "avg_response_time_ms": execution_values.get(
                        "avg_response_time_ms",
                        "",
                    ),
                    "throughput_rps": throughput,
                    "cpu_avg_percent": monitoring_values.get("cpu_avg_percent", ""),
                    "cpu_peak_percent": monitoring_values.get("cpu_peak_percent", ""),
                    "memory_avg_percent": monitoring_values.get(
                        "memory_avg_percent",
                        "",
                    ),
                    "memory_peak_percent": monitoring_values.get(
                        "memory_peak_percent",
                        "",
                    ),
                    "execution_data_source": execution_data_source,
                    "execution_measurement_scope": (
                        "load_generator_observed_http_traffic"
                    ),
                    "monitoring_data_source": (
                        "psutil" if monitoring_values else ""
                    ),
                    "monitoring_measurement_scope": (
                        "load_generator_host" if monitoring_values else ""
                    ),
                    "target_resource_metrics": "false",
                }
            )
    return bucket_count


__all__ = [
    "TIME_SERIES_BUCKET_SECONDS",
    "TIME_SERIES_FIELDS",
    "TIME_SERIES_SCHEMA_VERSION",
    "write_aligned_time_series",
]

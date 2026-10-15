"""Run trusted REAL k6 scripts and persist machine-readable artifacts."""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Performance_Testing_Agent.execution_context import (
    WorkloadProfile,
    resolve_artifact_directory,
    validate_real_profile,
)

from app.tools.k6_template import build_real_k6_script
from app.tools.result_formatter import EXPECTED_KEYS
from app.tools.runtime_sampler import RuntimeMetricsSampler
from app.tools.time_series import (
    TIME_SERIES_BUCKET_SECONDS,
    TIME_SERIES_SCHEMA_VERSION,
    write_aligned_time_series,
)


_K6_THRESHOLD_FAILURE_EXIT_CODE = 99
_TIME_SERIES_BUCKET_SECONDS = TIME_SERIES_BUCKET_SECONDS


def _measurement_sources(sample_result: dict[str, Any]) -> dict[str, Any]:
    sample_count = int(sample_result["sample_count"])
    sampling_error = sample_result.get("sampling_error")
    if sampling_error:
        sampling_status = "partial" if sample_count else "unavailable"
    else:
        sampling_status = "available" if sample_count else "no_samples"
    return {
        "runtime_samples": {
            "status": sampling_status,
            "data_source": "psutil",
            "measurement_scope": "load_generator_host",
            "target_resource_metrics": False,
            "sample_count": sample_count,
            "sample_interval_seconds": sample_result[
                "sample_interval_seconds"
            ],
            "sampler_started_at": sample_result["sampler_started_at"],
            "sampler_stopped_at": sample_result["sampler_stopped_at"],
            "metrics": ["cpu_percent", "memory_percent"],
            "not_collected": {
                "database_connections": (
                    "No target-specific database telemetry provider is configured."
                )
            },
            "sampling_error": sampling_error,
        },
        "k6_time_series": {
            "data_source": "k6 raw JSON point samples",
            "measurement_scope": "load_generator_observed_http_traffic",
            "target_resource_metrics": False,
            "metrics": [
                "requests",
                "successful_requests",
                "failed_requests",
                "avg_response_time_ms",
                "throughput_rps",
            ],
        },
    }


def _artifact_name(script_path: Path, suffix: str) -> str:
    return f"{script_path.stem}_{suffix}"


def _child_environment(target_url: str) -> dict[str, str]:
    allowed_environment = {
        "PATH",
        "HOME",
        "TMPDIR",
        "TMP",
        "TEMP",
        "LANG",
        "LC_ALL",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
    }
    environment = {
        key: value
        for key, value in os.environ.items()
        if key in allowed_environment
    }
    environment["BASE_URL"] = target_url.rstrip("/")
    environment.update(
        {
            "K6_WEB_DASHBOARD": "true",
            "K6_WEB_DASHBOARD_EXPORT": "",
            "K6_WEB_DASHBOARD_HOST": "127.0.0.1",
            "K6_WEB_DASHBOARD_PORT": "-1",
            "K6_WEB_DASHBOARD_OPEN": "false",
            "K6_WEB_DASHBOARD_PERIOD": "1s",
            "K6_NO_USAGE_REPORT": "true",
        }
    )
    return environment


def _write_runner_log(path: Path, sections: list[tuple[str, str]]) -> None:
    path.write_text(
        "".join(f"===== {name} =====\n{text}\n" for name, text in sections),
        encoding="utf-8",
    )


def _read_summary_metrics(summary: dict[str, Any]) -> dict[str, Any]:
    metrics = summary.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("k6 summary is missing its metrics object.")
    return metrics


def _metric_value(
    summary_metrics: dict[str, Any],
    metric_name: str,
    value_name: str,
) -> float:
    metric = summary_metrics.get(metric_name)
    values = metric.get("values") if isinstance(metric, dict) else None
    if not isinstance(values, dict) and isinstance(metric, dict):
        values = metric
    value = values.get(value_name) if isinstance(values, dict) else None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"k6 summary is missing {metric_name}.values.{value_name}."
        )
    numeric_value = float(value)
    if not math.isfinite(numeric_value) or numeric_value < 0:
        raise ValueError(
            f"k6 summary contains an invalid {metric_name}.values.{value_name}."
        )
    return numeric_value


def _parse_sample_time(value: Any) -> float:
    if not isinstance(value, str):
        raise ValueError("k6 raw sample is missing its timestamp.")
    normalized = value.replace("Z", "+00:00")
    try:
        timestamp = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError("k6 raw sample has an invalid timestamp.") from exc
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.timestamp()


def _read_raw_samples(
    raw_results_path: Path,
    run_started_at: datetime,
) -> tuple[int, int, int, dict[int, dict[str, Any]], Counter[int]]:
    total_requests = 0
    failed_requests = 0
    response_count = 0
    buckets: dict[int, dict[str, Any]] = {}
    status_codes: Counter[int] = Counter()

    with raw_results_path.open("r", encoding="utf-8") as raw_file:
        for line_number, line in enumerate(raw_file, start=1):
            if not line.strip():
                continue
            try:
                sample = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"k6 raw output contains invalid JSON on line {line_number}."
                ) from exc
            if not isinstance(sample, dict):
                raise ValueError(
                    f"k6 raw output line {line_number} is not a JSON object."
                )

            metric_name = sample.get("metric")
            data = sample.get("data")
            if (
                sample.get("type") != "Point"
                or metric_name
                not in {"http_reqs", "http_req_failed", "http_req_duration"}
                or not isinstance(data, dict)
            ):
                continue
            timestamp = _parse_sample_time(data.get("time"))
            elapsed_seconds = timestamp - run_started_at.timestamp()
            if elapsed_seconds < 0:
                raise ValueError("k6 raw sample precedes the k6 run start.")
            bucket_index = int(elapsed_seconds // _TIME_SERIES_BUCKET_SECONDS)
            bucket = buckets.setdefault(
                bucket_index,
                {
                    "start": bucket_index * _TIME_SERIES_BUCKET_SECONDS,
                    "requests": 0,
                    "failed_requests": 0,
                    "latency_total": 0.0,
                    "latency_count": 0,
                },
            )
            sample_value = data.get("value")

            if metric_name == "http_reqs":
                total_requests += 1
                bucket["requests"] += 1
                tags = data.get("tags")
                status_value = tags.get("status") if isinstance(tags, dict) else None
                try:
                    if status_value is not None:
                        status_codes[int(status_value)] += 1
                except (TypeError, ValueError):
                    raise ValueError(
                        f"k6 raw output contains an invalid HTTP status: {status_value!r}."
                    )
            elif metric_name == "http_req_failed":
                if isinstance(sample_value, (int, float)) and sample_value > 0:
                    failed_requests += 1
                    bucket["failed_requests"] += 1
            elif metric_name == "http_req_duration":
                if (
                    isinstance(sample_value, bool)
                    or not isinstance(sample_value, (int, float))
                    or not math.isfinite(float(sample_value))
                    or sample_value < 0
                ):
                    raise ValueError(
                        "k6 raw output contains an invalid response-time sample."
                    )
                bucket["latency_total"] += float(sample_value)
                bucket["latency_count"] += 1
                response_count += 1

    if total_requests < 1:
        raise ValueError("k6 completed without recording any HTTP requests.")
    if response_count != total_requests:
        raise ValueError(
            "k6 raw output request and response-time sample counts do not match."
        )
    if failed_requests > total_requests:
        raise ValueError("k6 raw output has more failures than requests.")
    return total_requests, failed_requests, response_count, buckets, status_codes


def _write_time_series(
    path: Path,
    buckets: dict[int, dict[str, Any]],
    run_started_at: datetime,
) -> None:
    if not buckets:
        raise ValueError("k6 raw output contains no time-series samples.")
    with path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=[
                "timestamp",
                "elapsed_seconds",
                "requests",
                "successful_requests",
                "failed_requests",
                "avg_response_time_ms",
                "throughput_rps",
            ],
        )
        writer.writeheader()
        for bucket_index in sorted(buckets):
            bucket = buckets[bucket_index]
            requests = int(bucket["requests"])
            failed = int(bucket["failed_requests"])
            elapsed_seconds = int(bucket["start"])
            timestamp = run_started_at.timestamp() + elapsed_seconds
            writer.writerow(
                {
                    "timestamp": datetime.fromtimestamp(
                        timestamp,
                        tz=timezone.utc,
                    ).isoformat(),
                    "elapsed_seconds": elapsed_seconds,
                    "requests": requests,
                    "successful_requests": requests - failed,
                    "failed_requests": failed,
                    "avg_response_time_ms": (
                        bucket["latency_total"] / bucket["latency_count"]
                        if bucket["latency_count"]
                        else 0.0
                    ),
                    "throughput_rps": (
                        requests / _TIME_SERIES_BUCKET_SECONDS
                    ),
                }
            )


def _thresholds_passed(return_code: int) -> bool:
    if return_code == 0:
        return True
    if return_code == _K6_THRESHOLD_FAILURE_EXIT_CODE:
        return False
    raise ValueError(
        f"Cannot determine threshold status from k6 exit code {return_code}."
    )


def _normalized_metrics(
    *,
    job_id: str,
    application: str,
    scenario: str,
    api_name: str,
    summary: dict[str, Any],
    raw_results_path: Path,
    time_series_path: Path,
    run_started_at: datetime,
) -> dict[str, Any]:
    summary_metrics = _read_summary_metrics(summary)
    total_requests, failed_requests, _, buckets, statuses = _read_raw_samples(
        raw_results_path,
        run_started_at,
    )
    summary_count = _metric_value(summary_metrics, "http_reqs", "count")
    if int(summary_count) != total_requests:
        raise ValueError(
            "k6 raw output request count does not match the summary export."
        )

    result = {
        "job_id": job_id,
        "application": application,
        "scenario": scenario,
        "api_name": api_name,
        "total_requests": total_requests,
        "successful_requests": total_requests - failed_requests,
        "failed_requests": failed_requests,
        "avg_response_time": _metric_value(
            summary_metrics,
            "http_req_duration",
            "avg",
        ),
        "p95_response_time": _metric_value(
            summary_metrics,
            "http_req_duration",
            "p(95)",
        ),
        "max_response_time": _metric_value(
            summary_metrics,
            "http_req_duration",
            "max",
        ),
        "throughput": _metric_value(summary_metrics, "http_reqs", "rate"),
        "error_rate": failed_requests / total_requests * 100,
        "http_status": statuses.most_common(1)[0][0] if statuses else 0,
    }
    if set(result) != EXPECTED_KEYS:
        raise ValueError("Normalized k6 metrics violate the 13-field contract.")
    _write_time_series(time_series_path, buckets, run_started_at)
    return result


def run_real_k6_test(
    *,
    job_id: str,
    profile_data: dict[str, Any],
    artifact_directory: str,
    script_path: str,
    test_case_id: str | None,
    application: str,
    scenario: str,
    api_name: str,
) -> dict[str, Any]:
    """Validate and run the prepared deterministic k6 script."""
    artifacts: dict[str, str] = {}
    artifact_paths: dict[str, Path] = {}
    try:
        profile = WorkloadProfile.model_validate(profile_data)
        preflight = validate_real_profile(profile)
        if preflight["status"] != "ready":
            raise ValueError(
                "REAL k6 execution preflight failed: "
                + "; ".join(
                    preflight.get("blocked_reasons")
                    or preflight.get("missing_inputs")
                    or ["unknown preflight failure"]
                )
            )
        if profile.credentials_ref != "none":
            raise ValueError(
                "REAL k6 credentials are not supported until a configured "
                "secret-reference provider is available; use credentials_ref='none' "
                "only for an unauthenticated target."
            )
        assert profile.max_rps is not None
        job_directory = resolve_artifact_directory(job_id)
        supplied_directory = Path(artifact_directory).expanduser().resolve()
        if supplied_directory != job_directory:
            raise ValueError(
                "The supplied artifact directory does not match this job."
            )
        resolved_script = Path(script_path).expanduser().resolve()
        if resolved_script.parent != job_directory or not resolved_script.is_file():
            raise ValueError(
                "The prepared k6 script must be a file inside this job's artifact directory."
            )
        expected_script = build_real_k6_script(
            profile.model_dump(mode="json"),
            test_case_id=test_case_id,
        )
        if resolved_script.read_text(encoding="utf-8") != expected_script:
            raise ValueError(
                "The prepared k6 script no longer matches the reviewed template."
            )
        executable = shutil.which("k6")
        if executable is None:
            raise FileNotFoundError(
                "k6 executable was not found on PATH; install k6 to run REAL tests."
            )
        assert profile.target_url is not None
        job_directory.mkdir(parents=True, exist_ok=True)

        raw_path = job_directory / _artifact_name(resolved_script, "raw.json")
        summary_path = job_directory / _artifact_name(resolved_script, "summary.json")
        report_path = job_directory / _artifact_name(
            resolved_script,
            "native_report.html",
        )
        time_series_path = job_directory / _artifact_name(
            resolved_script,
            "time_series.csv",
        )
        aligned_time_series_path = job_directory / _artifact_name(
            resolved_script,
            "aligned_time_series.csv",
        )
        normalized_path = job_directory / _artifact_name(
            resolved_script,
            "normalized_metrics.json",
        )
        runtime_samples_path = job_directory / _artifact_name(
            resolved_script,
            "runtime_samples.csv",
        )
        measurement_metadata_path = job_directory / _artifact_name(
            resolved_script,
            "measurement_metadata.json",
        )
        log_path = job_directory / _artifact_name(resolved_script, "runner.log")
        artifact_paths = {
            "generated_script": resolved_script,
            "raw_results": raw_path,
            "k6_summary": summary_path,
            "normalized_metrics": normalized_path,
            "time_series": time_series_path,
            "aligned_time_series": aligned_time_series_path,
            "monitoring_samples": runtime_samples_path,
            "measurement_metadata": measurement_metadata_path,
            "native_report": report_path,
            "runner_log": log_path,
        }
        artifacts["generated_script"] = resolved_script.name
        environment = _child_environment(profile.target_url)
        environment["K6_WEB_DASHBOARD_EXPORT"] = str(report_path)

        inspect_result = subprocess.run(
            [
                executable,
                "inspect",
                "--include-system-env-vars=false",
                "-e",
                f"BASE_URL={profile.target_url.rstrip('/')}",
                str(resolved_script),
            ],
            cwd=job_directory,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        log_sections = [
            ("k6 inspect stdout", inspect_result.stdout or ""),
            ("k6 inspect stderr", inspect_result.stderr or ""),
        ]
        if inspect_result.returncode != 0:
            _write_runner_log(log_path, log_sections)
            raise RuntimeError(
                "k6 inspect rejected the prepared script: "
                + (inspect_result.stderr or inspect_result.stdout or "no details")
            )

        sampler = RuntimeMetricsSampler(runtime_samples_path)
        sampler.start()
        run_started_at = datetime.now(timezone.utc)
        try:
            run_result = subprocess.run(
                [
                    executable,
                    "run",
                    "--rps",
                    str(profile.max_rps),
                    "--include-system-env-vars=false",
                    "--out",
                    f"json={raw_path}",
                    "--summary-export",
                    str(summary_path),
                    "--summary-mode",
                    "full",
                    "--summary-time-unit",
                    "ms",
                    "-e",
                    f"BASE_URL={profile.target_url.rstrip('/')}",
                    str(resolved_script),
                ],
                cwd=job_directory,
                env=environment,
                capture_output=True,
                text=True,
                timeout=profile.duration_seconds + 120,
                check=False,
            )
        finally:
            run_finished_at = datetime.now(timezone.utc)
            sample_result = sampler.stop()
            measurement_sources = _measurement_sources(sample_result)
            measurement_metadata_path.write_text(
                json.dumps(
                    {
                        "job_id": job_id,
                        "k6_run_window": {
                            "started_at": run_started_at.isoformat(),
                            "finished_at": run_finished_at.isoformat(),
                        },
                        "shared_time_series": {
                            "schema_version": TIME_SERIES_SCHEMA_VERSION,
                            "bucket_seconds": TIME_SERIES_BUCKET_SECONDS,
                            "alignment_origin": "k6_run_window.started_at",
                            "alignment_rule": (
                                "Timestamp each source in UTC, compute elapsed "
                                "time from k6 start, then floor into half-open "
                                "five-second windows."
                            ),
                        },
                        "sources": measurement_sources,
                    },
                    indent=2,
                    allow_nan=False,
                )
                + "\n",
                encoding="utf-8",
            )
            artifacts["monitoring_samples"] = runtime_samples_path.name
            artifacts["measurement_metadata"] = measurement_metadata_path.name
        log_sections.extend(
            [
                ("k6 run stdout", run_result.stdout or ""),
                ("k6 run stderr", run_result.stderr or ""),
            ]
        )
        _write_runner_log(log_path, log_sections)

        for key, path in artifact_paths.items():
            if path.is_file():
                artifacts[key] = path.name

        if run_result.returncode not in {0, _K6_THRESHOLD_FAILURE_EXIT_CODE}:
            raise RuntimeError(
                f"k6 run failed with exit code {run_result.returncode}; "
                "see runner log for details."
            )
        if not raw_path.is_file() or not summary_path.is_file():
            raise RuntimeError(
                "k6 did not produce both raw JSON output and a summary export."
            )
        if not report_path.is_file() or report_path.stat().st_size == 0:
            raise RuntimeError("k6 did not produce its native HTML report.")

        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        metrics = _normalized_metrics(
            job_id=job_id,
            application=application,
            scenario=scenario,
            api_name=api_name,
            summary=summary,
            raw_results_path=raw_path,
            time_series_path=time_series_path,
            run_started_at=run_started_at,
        )
        if not time_series_path.is_file():
            raise RuntimeError("k6 time-series output was not produced.")
        shared_bucket_count = write_aligned_time_series(
            execution_time_series_path=time_series_path,
            monitoring_samples_path=runtime_samples_path,
            output_path=aligned_time_series_path,
            run_started_at=run_started_at,
            run_finished_at=run_finished_at,
        )
        normalized_document = {
            "execution_mode": "REAL",
            "thresholds_passed": _thresholds_passed(run_result.returncode),
            "workload_profile": {
                "users": profile.users,
                "max_rps": profile.max_rps,
                "duration_seconds": profile.duration_seconds,
                "ramp_up_seconds": profile.ramp_up_seconds,
            },
            "measurement_sources": measurement_sources,
            "shared_time_series": {
                "schema_version": TIME_SERIES_SCHEMA_VERSION,
                "bucket_seconds": TIME_SERIES_BUCKET_SECONDS,
                "bucket_count": shared_bucket_count,
                "alignment_origin": "k6_run_window.started_at",
                "artifact": aligned_time_series_path.name,
            },
            "metrics": metrics,
        }
        normalized_path.write_text(
            json.dumps(normalized_document, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        artifacts.update(
            {
                "normalized_metrics": normalized_path.name,
                "time_series": time_series_path.name,
                "aligned_time_series": aligned_time_series_path.name,
            }
        )
        return {
            "status": "completed",
            "message": (
                "REAL k6 execution completed. Threshold breaches, if any, "
                "are retained as performance findings."
            ),
            "job_id": job_id,
            "execution_mode": "REAL",
            "thresholds_passed": normalized_document["thresholds_passed"],
            "metrics": metrics,
            "measurement_sources": measurement_sources,
            "artifacts": artifacts,
        }
    except (
        FileNotFoundError,
        OSError,
        RuntimeError,
        ValueError,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
    ) as exc:
        for key, path in artifact_paths.items():
            if path.is_file():
                artifacts[key] = path.name
        return {
            "status": "failed",
            "message": str(exc),
            "job_id": job_id,
            "execution_mode": "REAL",
            "artifacts": artifacts,
        }


__all__ = ["run_real_k6_test"]

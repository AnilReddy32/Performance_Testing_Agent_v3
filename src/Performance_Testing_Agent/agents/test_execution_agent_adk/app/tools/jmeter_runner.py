"""Execute a trusted JMeter plan and normalize its real JTL results."""

from __future__ import annotations

import csv
import json
import math
import os
import re
import shlex
import shutil
import signal
import statistics
import subprocess
import tempfile
import time
import uuid
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Performance_Testing_Agent.execution_context import (
    WorkloadProfile,
    artifact_root_directory,
    resolve_artifact_directory,
    validate_real_profile,
)

from app.tools.jmeter_template import (
    build_real_jmeter_plan,
    validate_real_jmeter_plan,
)
from app.tools.runtime_sampler import RuntimeMetricsSampler
from app.tools.time_series import (
    TIME_SERIES_BUCKET_SECONDS,
    TIME_SERIES_SCHEMA_VERSION,
    write_aligned_time_series,
)
from app.tools.result_formatter import EXPECTED_KEYS


_RUN_TIMEOUT_GRACE_SECONDS = 120
_PROCESS_CLEANUP_GRACE_SECONDS = 5
_JAVA_CHECK_TIMEOUT_SECONDS = 10
_PROPERTY_NAME = re.compile(r"[A-Z_][A-Z0-9_]*\Z")


class _CommandTimeout(RuntimeError):
    def __init__(self, command: list[str], stdout: str, stderr: str):
        super().__init__("Command exceeded its bounded timeout.")
        self.command = command
        self.stdout = stdout
        self.stderr = stderr


def _decode_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _terminate_process_tree(process: subprocess.Popen[str]) -> None:
    """Stop the process group, escalating to a hard kill if it will not exit."""
    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGTERM)
        else:
            process.terminate()
    except ProcessLookupError:
        return
    except OSError:
        process.terminate()

    try:
        process.wait(timeout=_PROCESS_CLEANUP_GRACE_SECONDS)
        return
    except subprocess.TimeoutExpired:
        pass

    try:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
    except ProcessLookupError:
        return
    except OSError:
        process.kill()
    process.wait()


def _run_command(
    command: list[str],
    *,
    cwd: Path,
    environment: dict[str, str],
    timeout_seconds: int,
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        start_new_session=(os.name == "posix"),
        creationflags=(
            subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        ),
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        _terminate_process_tree(process)
        stdout, stderr = process.communicate()
        raise _CommandTimeout(
            command,
            _decode_output(stdout if stdout else exc.stdout),
            _decode_output(stderr if stderr else exc.stderr),
        ) from exc
    except BaseException:
        _terminate_process_tree(process)
        process.communicate()
        raise
    return subprocess.CompletedProcess(
        args=command,
        returncode=process.returncode,
        stdout=stdout,
        stderr=stderr,
    )


##------------------
# def _child_environment() -> dict[str, str]:
#     allowed_names = {
#         "PATH",
#         "HOME",
#         "JAVA_HOME",
#         "JRE_HOME",
#         "JMETER_HOME",
#         "TMPDIR",
#         "TMP",
#         "TEMP",
#         "LANG",
#         "LC_ALL",
#         "SSL_CERT_FILE",
#         "SSL_CERT_DIR",
#         # Required on Windows: subprocess.Popen launches .BAT files through
#         # cmd.exe, which needs SystemRoot (e.g. C:\Windows) to locate system
#         # DLLs and bootstrap the process at all - without it, the process
#         # can fail immediately with no stdout/stderr output and exit code 1,
#         # before the target program (JMeter) ever gets a chance to run or log
#         # anything. COMSPEC (the path to cmd.exe itself) is included for the
#         # same reason.
#         "SystemRoot",
#         "COMSPEC",
#     }
#     return {
#         name: value
#         for name, value in os.environ.items()
#         if name in allowed_names
#     }



def _child_environment() -> dict[str, str]:
    allowed_names = {
        "PATH",
        "HOME",
        "JAVA_HOME",
        "JRE_HOME",
        "JMETER_HOME",
        "TMPDIR",
        "TMP",
        "TEMP",
        "LANG",
        "LC_ALL",
        "SSL_CERT_FILE",
        "SSL_CERT_DIR",
        "SystemRoot",
        "COMSPEC",
    }
    allowed_upper = {name.upper() for name in allowed_names}
    return {
        name: value
        for name, value in os.environ.items()
        if name.upper() in allowed_upper
    }

##$--------------
def _escape_java_property(value: str) -> str:
    escaped: list[str] = []
    for index, character in enumerate(value):
        codepoint = ord(character)
        if character == "\\":
            escaped.append("\\\\")
        elif character == "\n":
            escaped.append("\\n")
        elif character == "\r":
            escaped.append("\\r")
        elif character == "\t":
            escaped.append("\\t")
        elif character == "\f":
            escaped.append("\\f")
        elif character in "=:#!" or (character == " " and index == 0):
            escaped.append("\\" + character)
        elif codepoint < 0x20 or codepoint > 0x7E:
            if codepoint <= 0xFFFF:
                escaped.append(f"\\u{codepoint:04x}")
            else:
                adjusted = codepoint - 0x10000
                high = 0xD800 + (adjusted >> 10)
                low = 0xDC00 + (adjusted & 0x3FF)
                escaped.extend((f"\\u{high:04x}", f"\\u{low:04x}"))
        else:
            escaped.append(character)
    return "".join(escaped)


def _write_private_jmeter_properties(
    header_env: dict[str, str] | None,
) -> str | None:
    properties: list[tuple[str, str]] = []
    for environment_name in sorted(set((header_env or {}).values())):
        if not _PROPERTY_NAME.fullmatch(environment_name):
            raise ValueError(
                "JMeter header references must be uppercase environment names."
            )
        secret_value = os.environ.get(environment_name)
        if secret_value is None or secret_value == "":
            raise ValueError(
                "Required request-header environment variable "
                f"{environment_name} is not set."
            )
        properties.append((environment_name, secret_value))

    if not properties:
        return None

    descriptor, path = tempfile.mkstemp(
        prefix="real-jmeter-properties-",
        suffix=".properties",
    )
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="ascii", newline="\n") as handle:
            for name, value in properties:
                handle.write(f"{name}={_escape_java_property(value)}\n")
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        Path(path).unlink(missing_ok=True)
        raise
    return path


def _write_log(path: Path, sections: list[tuple[str, str]]) -> None:
    content = "".join(
        f"===== {title} =====\n{body.rstrip()}\n\n"
        for title, body in sections
    )
    path.write_text(content, encoding="utf-8")
    try:
        path.chmod(0o600)
    except OSError:
        pass


def _prepare_private_output(path: Path) -> None:
    if path.is_symlink():
        raise ValueError(f"JMeter output path cannot be a symbolic link: {path.name}.")
    if path.exists():
        if not path.is_file():
            raise ValueError(f"JMeter output path is not a regular file: {path.name}.")
        path.unlink()


def _read_jtl(
    path: Path,
    profile: WorkloadProfile,
) -> tuple[dict[str, Any], list[str], dict[str, float]]:
    assert profile.expected_status_code is not None
    assert profile.p95_threshold_ms is not None

    durations: list[float] = []
    statuses: Counter[int] = Counter()
    failed_requests = 0
    total_requests = 0
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"timeStamp", "elapsed", "responseCode", "success"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(
                "JMeter JTL output is missing required CSV fields: "
                + ", ".join(sorted(required))
                + "."
            )
        for line_number, row in enumerate(reader, start=2):
            if not row or not any(value for value in row.values() if value):
                continue
            total_requests += 1
            try:
                elapsed_ms = float(row["elapsed"])
            except (TypeError, ValueError) as exc:
                raise ValueError(
                    f"JMeter JTL has an invalid elapsed time on line {line_number}."
                ) from exc
            if not math.isfinite(elapsed_ms) or elapsed_ms < 0:
                raise ValueError(
                    f"JMeter JTL has an invalid elapsed time on line {line_number}."
                )
            durations.append(elapsed_ms)

            try:
                status_code = int(row["responseCode"])
            except (TypeError, ValueError):
                status_code = 0
            if status_code:
                statuses[status_code] += 1
            sample_success = (row.get("success") or "").strip().lower() == "true"
            if not sample_success or status_code != profile.expected_status_code:
                failed_requests += 1

    if total_requests == 0:
        raise ValueError("JMeter completed without recording any HTTP requests.")

    ordered = sorted(durations)
    def percentile(percent: float) -> float:
        index = max(0, math.ceil(percent * len(ordered)) - 1)
        return ordered[index]

    p95 = percentile(0.95)
    result = {
        "total_requests": total_requests,
        "successful_requests": total_requests - failed_requests,
        "failed_requests": failed_requests,
        "avg_response_time": statistics.fmean(durations),
        "p95_response_time": p95,
        "max_response_time": max(durations),
        "error_rate": failed_requests / total_requests * 100,
        "http_status": statuses.most_common(1)[0][0] if statuses else 0,
    }
    failure_reasons: list[str] = []
    if failed_requests:
        failure_reasons.append(
            f"{failed_requests} of {total_requests} requests failed or returned "
            f"a status other than {profile.expected_status_code}."
        )
    if p95 > profile.p95_threshold_ms:
        failure_reasons.append(
            f"p95 response time {p95:.2f} ms exceeded the configured threshold "
            f"of {profile.p95_threshold_ms} ms."
        )
    latency_percentiles = {
        "p50": percentile(0.50),
        "p90": percentile(0.90),
        "p95": p95,
        "p99": percentile(0.99),
    }
    return result, failure_reasons, latency_percentiles


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
            "sample_interval_seconds": sample_result["sample_interval_seconds"],
            "sampler_started_at": sample_result["sampler_started_at"],
            "sampler_stopped_at": sample_result["sampler_stopped_at"],
            "metrics": ["cpu_percent", "memory_percent"],
            "sampling_error": sampling_error,
        },
        "jmeter_time_series": {
            "data_source": "JMeter raw JTL sample rows",
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


def _write_jmeter_time_series(
    *,
    jtl_path: Path,
    output_path: Path,
    run_started_at: datetime,
    run_finished_at: datetime,
    profile: WorkloadProfile,
) -> int:
    duration = (run_finished_at - run_started_at).total_seconds()
    if duration <= 0:
        raise ValueError("JMeter run window must have positive duration.")
    bucket_count = math.ceil(duration / TIME_SERIES_BUCKET_SECONDS)
    buckets: dict[int, dict[str, float]] = {}
    start_epoch = run_started_at.timestamp()
    with jtl_path.open("r", newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        for row_number, row in enumerate(reader, start=2):
            if not row or not any(value for value in row.values() if value):
                continue
            try:
                sample_epoch = float(row["timeStamp"]) / 1000.0
                elapsed_ms = float(row["elapsed"])
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"JMeter JTL has an invalid sample timestamp or elapsed time on line {row_number}."
                ) from exc
            elapsed = sample_epoch - start_epoch
            if not math.isfinite(elapsed) or not math.isfinite(elapsed_ms) or elapsed_ms < 0:
                raise ValueError(f"JMeter JTL has invalid timing data on line {row_number}.")
            if elapsed < -1.0 or elapsed > duration + 1.0:
                raise ValueError("JMeter JTL sample falls outside the current run window.")
            elapsed = min(max(elapsed, 0.0), max(duration - 1e-9, 0.0))
            bucket_index = min(
                int(elapsed // TIME_SERIES_BUCKET_SECONDS),
                bucket_count - 1,
            )
            bucket = buckets.setdefault(
                bucket_index,
                {"requests": 0, "failed": 0, "latency_total": 0.0},
            )
            bucket["requests"] += 1
            bucket["latency_total"] += elapsed_ms
            try:
                status_code = int(row.get("responseCode") or 0)
            except (TypeError, ValueError):
                status_code = 0
            if (
                (row.get("success") or "").strip().lower() != "true"
                or status_code != profile.expected_status_code
            ):
                bucket["failed"] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output_file:
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
        for bucket_index in range(bucket_count):
            bucket = buckets.get(
                bucket_index,
                {"requests": 0, "failed": 0, "latency_total": 0.0},
            )
            elapsed = bucket_index * TIME_SERIES_BUCKET_SECONDS
            bucket_duration = min(TIME_SERIES_BUCKET_SECONDS, duration - elapsed)
            requests = int(bucket["requests"])
            failed = int(bucket["failed"])
            writer.writerow({
                "timestamp": datetime.fromtimestamp(
                    start_epoch + elapsed,
                    tz=timezone.utc,
                ).isoformat(),
                "elapsed_seconds": elapsed,
                "requests": requests,
                "successful_requests": requests - failed,
                "failed_requests": failed,
                "avg_response_time_ms": (
                    bucket["latency_total"] / requests if requests else ""
                ),
                "throughput_rps": requests / bucket_duration,
            })
    return bucket_count


def _generate_native_dashboard(
    *,
    executable: str,
    result_path: Path,
    job_directory: Path,
    job_id: str,
    environment: dict[str, str],
    timeout_seconds: int,
    sections: list[tuple[str, str]],
) -> dict[str, str]:
    """Generate JMeter's dashboard, retain a browsable job copy and ZIP package."""
    report_root = artifact_root_directory("jmeter")
    report_root.mkdir(parents=True, exist_ok=True)
    if report_root.is_symlink():
        raise ValueError("JMeter native report root cannot be a symbolic link.")
    expected_job_directory = report_root / job_id
    if Path(job_directory).resolve() != expected_job_directory.resolve():
        raise ValueError("JMeter dashboard job directory does not match its tool root.")
    job_directory = expected_job_directory
    if job_directory.is_symlink():
        raise ValueError("JMeter job artifact directory cannot be a symbolic link.")
    job_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    if job_directory.resolve().parent != report_root.resolve():
        raise ValueError("JMeter job directory must remain under its report root.")
    destination = job_directory / "jmeter_native_report"
    if destination.is_symlink():
        raise ValueError("JMeter native report directory cannot be a symbolic link.")

    staging_parent = Path(tempfile.mkdtemp(prefix=f".{job_id}_dashboard_", dir=job_directory))
    staging_output = staging_parent / "dashboard"
    dashboard_log = staging_parent / "jmeter_dashboard.log"
    try:
        command = [
            executable,
            "-g",
            str(result_path),
            "-o",
            str(staging_output),
            "-j",
            str(dashboard_log),
        ]
        sections.append(("JMeter dashboard command", shlex.join(command)))
        try:
            generated = _run_command(
                command,
                cwd=job_directory,
                environment=environment,
                timeout_seconds=timeout_seconds,
            )
        except _CommandTimeout as exc:
            sections.extend([
                ("Dashboard stdout before timeout", exc.stdout),
                ("Dashboard stderr before timeout", exc.stderr),
                ("Dashboard exit status", "timed out; process group terminated"),
            ])
            raise RuntimeError("JMeter native dashboard generation exceeded its bounded timeout.") from exc
        sections.extend([
            ("Dashboard stdout", generated.stdout or ""),
            ("Dashboard stderr", generated.stderr or ""),
            ("Dashboard exit status", str(generated.returncode)),
        ])
        index = staging_output / "index.html"
        if generated.returncode != 0 or not index.is_file() or index.stat().st_size == 0:
            raise RuntimeError(
                f"JMeter dashboard generation failed with exit code {generated.returncode}; "
                "see the runner log."
            )

        backup = job_directory / f".jmeter_native_report_previous_{uuid.uuid4().hex}"
        if destination.exists():
            if not destination.is_dir():
                raise ValueError("Existing JMeter report destination is not a directory.")
            os.replace(destination, backup)
        try:
            os.replace(staging_output, destination)
        except Exception:
            if backup.exists() and not destination.exists():
                os.replace(backup, destination)
            raise
        if backup.exists():
            shutil.rmtree(backup)

        report_stem = result_path.stem.removesuffix("_results")
        report_stem = re.sub(r"[^A-Za-z0-9._-]+", "_", report_stem).strip("._-")
        if not report_stem:
            report_stem = job_id
        entrypoint_path = job_directory / f"{report_stem}_native_report.html"
        index_html = (destination / "index.html").read_text(encoding="utf-8")
        entrypoint_html, replacements = re.subn(
            r"<head(?:\s[^>]*)?>",
            lambda match: f'{match.group(0)}\n    <base href="jmeter_native_report/">',
            index_html,
            count=1,
            flags=re.IGNORECASE,
        )
        if replacements != 1:
            raise RuntimeError("JMeter dashboard index has no valid head element.")
        temporary_entrypoint = job_directory / f".{report_stem}_{uuid.uuid4().hex}.tmp"
        try:
            temporary_entrypoint.write_text(entrypoint_html, encoding="utf-8")
            temporary_entrypoint.chmod(0o600)
            os.replace(temporary_entrypoint, entrypoint_path)
        finally:
            temporary_entrypoint.unlink(missing_ok=True)

        archive_name = f"{job_id}_jmeter_native_report.zip"
        archive_path = job_directory / archive_name
        temporary_archive = job_directory / f".{job_id}_jmeter_report_{uuid.uuid4().hex}.tmp"
        try:
            with zipfile.ZipFile(
                temporary_archive, "w", compression=zipfile.ZIP_DEFLATED
            ) as archive:
                for file_path in sorted(destination.rglob("*")):
                    if file_path.is_file():
                        archive.write(
                            file_path,
                            arcname=(Path("jmeter_native_report") / file_path.relative_to(destination)).as_posix(),
                        )
                archive.write(
                    result_path,
                    arcname=(Path("raw_results") / result_path.name).as_posix(),
                )
            os.replace(temporary_archive, archive_path)
        finally:
            temporary_archive.unlink(missing_ok=True)
        archive_path.chmod(0o600)
        return {
            "native_report": "jmeter_native_report/index.html",
            "native_report_archive": archive_path.name,
            "native_report_entrypoint": entrypoint_path.name,
        }
    finally:
        shutil.rmtree(staging_parent, ignore_errors=True)


def run_real_jmeter_test(
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
    """Run an approved generated JMX plan and retain raw and normalized results."""
    artifacts: dict[str, str] = {}
    artifact_paths: dict[str, Path] = {}
    sections: list[tuple[str, str]] = []
    temporary_properties: str | None = None
    exit_code: int | None = None
    command: list[str] = []
    run_started_at: datetime | None = None
    run_finished_at: datetime | None = None

    try:
        profile = WorkloadProfile.model_validate(profile_data)
        preflight = validate_real_profile(profile)
        if preflight["status"] != "ready":
            raise ValueError(
                "REAL JMeter execution preflight failed: "
                + "; ".join(
                    preflight.get("blocked_reasons")
                    or preflight.get("missing_inputs")
                    or ["unknown preflight failure"]
                )
            )

        artifact_root = artifact_root_directory("jmeter")
        candidate_directory = artifact_root / job_id
        if candidate_directory.is_symlink():
            raise ValueError("The JMeter job artifact directory cannot be a symbolic link.")
        job_directory = resolve_artifact_directory(job_id, tool="jmeter")
        supplied_directory = Path(artifact_directory).expanduser().resolve()
        if supplied_directory != job_directory:
            raise ValueError("The supplied artifact directory does not match this job.")
        supplied_script = Path(script_path).expanduser()
        if supplied_script.is_symlink():
            raise ValueError("The prepared JMeter plan cannot be a symbolic link.")
        resolved_script = supplied_script.resolve()
        if resolved_script.parent != job_directory or not resolved_script.is_file():
            raise ValueError(
                "The prepared JMeter plan must be a file inside this job's artifact directory."
            )
        expected_plan = build_real_jmeter_plan(
            profile.model_dump(mode="json"),
            test_case_id=test_case_id,
        )
        plan_content = resolved_script.read_text(encoding="utf-8")
        validate_real_jmeter_plan(plan_content, profile.model_dump(mode="json"), test_case_id)
        if plan_content != expected_plan:
            raise ValueError(
                "The prepared JMeter plan no longer matches the reviewed template."
            )

        job_directory.mkdir(parents=True, exist_ok=True, mode=0o700)
        if job_directory.is_symlink() or job_directory.resolve() != job_directory:
            raise ValueError("The JMeter job artifact directory is not safe.")

        result_path = job_directory / f"{resolved_script.stem}_results.jtl"
        jmeter_log_path = job_directory / f"{resolved_script.stem}_jmeter.log"
        runner_log_path = job_directory / f"{resolved_script.stem}_runner.log"
        normalized_path = job_directory / f"{resolved_script.stem}_normalized_metrics.json"
        time_series_path = job_directory / f"{resolved_script.stem}_time_series.csv"
        aligned_time_series_path = job_directory / f"{resolved_script.stem}_aligned_time_series.csv"
        runtime_samples_path = job_directory / f"{resolved_script.stem}_runtime_samples.csv"
        measurement_metadata_path = job_directory / f"{resolved_script.stem}_measurement_metadata.json"
        artifact_paths = {
            "generated_script": resolved_script,
            "raw_results": result_path,
            "jmeter_log": jmeter_log_path,
            "runner_log": runner_log_path,
            "normalized_metrics": normalized_path,
            "time_series": time_series_path,
            "aligned_time_series": aligned_time_series_path,
            "monitoring_samples": runtime_samples_path,
            "measurement_metadata": measurement_metadata_path,
        }
        artifacts["generated_script"] = resolved_script.name
        for path in (
            result_path,
            jmeter_log_path,
            normalized_path,
            time_series_path,
            aligned_time_series_path,
            runtime_samples_path,
            measurement_metadata_path,
        ):
            _prepare_private_output(path)

        executable = shutil.which("jmeter")
        if executable is None:
            raise FileNotFoundError(
                "JMeter executable was not found on PATH; install Apache JMeter to run REAL tests."
            )
        java_executable = shutil.which("java")
        if java_executable is None:
            raise FileNotFoundError(
                "Java executable was not found on PATH; install a supported Java runtime to run JMeter."
            )

        child_environment = _child_environment()
        java_check = _run_command(
            [java_executable, "-version"],
            cwd=job_directory,
            environment=child_environment,
            timeout_seconds=_JAVA_CHECK_TIMEOUT_SECONDS,
        )
        java_version_output = (java_check.stdout or "") + (java_check.stderr or "")
        sections.append(("Java executable", java_executable))
        sections.append(("Java version check", java_version_output))
        if java_check.returncode != 0:
            raise RuntimeError(
                f"Java version check failed with exit code {java_check.returncode}."
            )

        temporary_properties = _write_private_jmeter_properties(profile.header_env)
        command = [
            executable,
            "-n",
            "-f",
            "-t",
            str(resolved_script),
            "-l",
            str(result_path),
            "-j",
            str(jmeter_log_path),
            "-Jjmeter.save.saveservice.output_format=csv",
            "-Jjmeter.save.saveservice.print_field_names=true",
            "-Jjmeter.save.saveservice.timestamp_format=ms",
            "-Jjmeter.save.saveservice.response_data=false",
            "-Jjmeter.save.saveservice.requestHeaders=false",
            "-Jjmeter.save.saveservice.responseHeaders=false",
            "-Jjmeter.save.saveservice.url=true",
        ]
        if temporary_properties:
            command.extend(["-q", temporary_properties])

        sections.append(("Resolved JMeter executable", executable))
        sections.append(("JMeter command", shlex.join(command)))
        run_preflight = validate_real_profile(profile)
        if run_preflight["status"] != "ready":
            raise ValueError(
                "REAL JMeter execution preflight failed immediately before run: "
                + "; ".join(
                    run_preflight.get("blocked_reasons")
                    or run_preflight.get("missing_inputs")
                    or ["unknown preflight failure"]
                )
            )

        timeout_seconds = profile.duration_seconds + _RUN_TIMEOUT_GRACE_SECONDS
        sampler = RuntimeMetricsSampler(runtime_samples_path)
        sampler.start()
        run_started_at = datetime.now(timezone.utc)
        monotonic_start = time.monotonic()
        try:
            run_result = _run_command(
                command,
                cwd=job_directory,
                environment=child_environment,
                timeout_seconds=timeout_seconds,
            )
            exit_code = run_result.returncode
            sections.extend(
                [
                    ("JMeter stdout", run_result.stdout or ""),
                    ("JMeter stderr", run_result.stderr or ""),
                    ("JMeter exit status", str(exit_code)),
                    ("JMeter timeout seconds", str(timeout_seconds)),
                ]
            )
        except _CommandTimeout as exc:
            sections.extend(
                [
                    ("JMeter stdout before timeout", exc.stdout),
                    ("JMeter stderr before timeout", exc.stderr),
                    ("JMeter exit status", "timed out; process group terminated"),
                    ("JMeter timeout seconds", str(timeout_seconds)),
                ]
            )
            raise RuntimeError(
                f"JMeter exceeded its bounded timeout of {timeout_seconds} seconds; "
                "the JMeter process group was terminated."
            ) from exc
        finally:
            run_finished_at = datetime.now(timezone.utc)
            run_elapsed_seconds = max(time.monotonic() - monotonic_start, 0.001)
            sample_result = sampler.stop()
            measurement_sources = _measurement_sources(sample_result)

        if exit_code != 0:
            raise RuntimeError(
                f"JMeter failed with exit code {exit_code}; see the runner and JMeter logs."
            )
        if not result_path.is_file() or result_path.stat().st_size == 0:
            raise RuntimeError("JMeter completed without producing a non-empty JTL file.")
        result_path.chmod(0o600)
        if jmeter_log_path.is_file():
            jmeter_log_path.chmod(0o600)

        metrics, failure_reasons, latency_percentiles = _read_jtl(result_path, profile)
        assert run_elapsed_seconds is not None
        metrics.update(
            {
                "job_id": job_id,
                "application": application,
                "scenario": scenario,
                "api_name": api_name,
                "throughput": metrics["total_requests"] / run_elapsed_seconds,
            }
        )
        if set(metrics) != EXPECTED_KEYS:
            raise ValueError("Normalized JMeter metrics violate the 13-field contract.")

        assert run_started_at is not None and run_finished_at is not None
        source_bucket_count = _write_jmeter_time_series(
            jtl_path=result_path,
            output_path=time_series_path,
            run_started_at=run_started_at,
            run_finished_at=run_finished_at,
            profile=profile,
        )
        shared_bucket_count = write_aligned_time_series(
            execution_time_series_path=time_series_path,
            monitoring_samples_path=runtime_samples_path,
            output_path=aligned_time_series_path,
            run_started_at=run_started_at,
            run_finished_at=run_finished_at,
            execution_data_source="jmeter",
        )
        measurement_metadata_path.write_text(
            json.dumps(
                {
                    "job_id": job_id,
                    "jmeter_run_window": {
                        "started_at": run_started_at.isoformat(),
                        "finished_at": run_finished_at.isoformat(),
                    },
                    "shared_time_series": {
                        "schema_version": TIME_SERIES_SCHEMA_VERSION,
                        "bucket_seconds": TIME_SERIES_BUCKET_SECONDS,
                        "alignment_origin": "jmeter_run_window.started_at",
                        "alignment_rule": (
                            "UTC timestamps converted to elapsed offsets from JMeter start, "
                            "then floored into half-open five-second windows."
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
        measurement_metadata_path.chmod(0o600)
        for measurement_path in (
            runtime_samples_path,
            time_series_path,
            aligned_time_series_path,
        ):
            if measurement_path.is_file():
                measurement_path.chmod(0o600)

        thresholds_passed = not failure_reasons
        normalized_document = {
            "execution_mode": "REAL",
            "thresholds_passed": thresholds_passed,
            "threshold_failures": failure_reasons,
            "runner": {
                "name": "Apache JMeter",
                "executable": executable,
                "java_executable": java_executable,
                "exit_code": exit_code,
                "timeout_seconds": timeout_seconds,
                "started_at": run_started_at.isoformat() if run_started_at else None,
                "finished_at": run_finished_at.isoformat() if run_finished_at else None,
            },
            "workload_profile": {
                "users": profile.users,
                "max_rps": profile.max_rps,
                "duration_seconds": profile.duration_seconds,
                "ramp_up_seconds": profile.ramp_up_seconds,
            },
            "latency_percentiles_ms": latency_percentiles,
            "measurement_sources": measurement_sources,
            "jmeter_run_window": {
                "started_at": run_started_at.isoformat(),
                "finished_at": run_finished_at.isoformat(),
            },
            "shared_time_series": {
                "schema_version": TIME_SERIES_SCHEMA_VERSION,
                "bucket_seconds": TIME_SERIES_BUCKET_SECONDS,
                "bucket_count": shared_bucket_count,
                "source_bucket_count": source_bucket_count,
                "alignment_origin": "jmeter_run_window.started_at",
                "artifact": aligned_time_series_path.name,
            },
            "metrics": metrics,
        }
        normalized_path.write_text(
            json.dumps(normalized_document, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        normalized_path.chmod(0o600)
        artifacts.update(
            _generate_native_dashboard(
                executable=executable,
                result_path=result_path,
                job_directory=job_directory,
                job_id=job_id,
                environment=child_environment,
                timeout_seconds=timeout_seconds,
                sections=sections,
            )
        )
        _write_log(runner_log_path, sections)
        artifacts.update(
            {key: path.name for key, path in artifact_paths.items() if path.is_file()}
        )
        return {
            "status": "completed",
            "message": (
                "REAL JMeter execution completed. "
                + (
                    "Configured thresholds passed."
                    if thresholds_passed
                    else "One or more configured thresholds failed; see threshold_failures."
                )
            ),
            "job_id": job_id,
            "execution_mode": "REAL",
            "exit_code": exit_code,
            "thresholds_passed": thresholds_passed,
            "threshold_failures": failure_reasons,
            "metrics": metrics,
            "latency_percentiles_ms": latency_percentiles,
            "measurement_sources": measurement_sources,
            "artifacts": artifacts,
        }
    except (
        FileNotFoundError,
        OSError,
        RuntimeError,
        ValueError,
        csv.Error,
        json.JSONDecodeError,
        subprocess.SubprocessError,
    ) as exc:
        if isinstance(exc, _CommandTimeout):
            sections.extend(
                [
                    ("Command stdout before timeout", exc.stdout),
                    ("Command stderr before timeout", exc.stderr),
                    ("Command exit status", "timed out; process group terminated"),
                ]
            )
        sections.append(("Runner outcome", str(exc)))
        if artifact_paths.get("runner_log"):
            _write_log(artifact_paths["runner_log"], sections)
        for key in (
            "raw_results",
            "jmeter_log",
            "normalized_metrics",
            "time_series",
            "aligned_time_series",
            "monitoring_samples",
            "measurement_metadata",
        ):
            output_path = artifact_paths.get(key)
            if output_path is not None and output_path.is_file():
                try:
                    output_path.chmod(0o600)
                except OSError:
                    pass
        artifacts.update(
            {key: path.name for key, path in artifact_paths.items() if path.is_file()}
        )
        return {
            "status": "failed",
            "message": str(exc),
            "job_id": job_id,
            "execution_mode": "REAL",
            "exit_code": exit_code,
            "artifacts": artifacts,
        }
    finally:
        if temporary_properties:
            Path(temporary_properties).unlink(missing_ok=True)


__all__ = ["run_real_jmeter_test"]
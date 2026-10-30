from __future__ import annotations

import ipaddress
import os
import re
import socket
import uuid
from pathlib import Path
from typing import Any, Literal
from urllib.parse import unquote, urlsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError


ExecutionMode = Literal["REAL", "SIMULATED"]
ArtifactKey = Literal[
    "generated_script",
    "test_data",
    "environment",
    "raw_results",
    "k6_summary",
    "jmeter_log",
    "normalized_metrics",
    "time_series",
    "aligned_time_series",
    "monitoring_samples",
    "measurement_metadata",
    "native_report",
    "native_report_archive",
    "native_report_entrypoint",
    "runner_log",
    "consolidated_report",
]
ExecutionStatus = Literal[
    "not_started",
    "needs_input",
    "blocked",
    "prepared",
    "running",
    "completed",
    "failed",
]
PreflightStatus = Literal[
    "not_required",
    "needs_input",
    "blocked",
    "rejected",
    "ready",
]

_PROFILE_FIELD_NAMES = (
    "tool",
    "target_url",
    "environment",
    "endpoint",
    "method",
    "users",
    "max_rps",
    "duration_seconds",
    "ramp_up_seconds",
    "p95_threshold_ms",
    "expected_status_code",
    "credentials_ref",
)
_BODY_METHODS = {"POST", "PUT", "PATCH"}
_K6_TASK_PATTERN = re.compile(
    r"\bk6\b.*\b(?:test|testing|script|scenario|workload|load|run|execute|"
    r"generate|create|prepare)\b|\b(?:test|testing|script|scenario|workload|"
    r"load|run|execute|generate|create|prepare)\b.*\bk6\b",
    re.IGNORECASE | re.DOTALL,
)
_JMETER_TASK_PATTERN = re.compile(
    r"\bjmeter\b.{0,160}\b(?:run|execute|perform|start|launch|generate|"
    r"create|prepare|write|test|testing)\b|\b(?:run|execute|perform|"
    r"start|launch|generate|create|prepare|write|test|testing)\b"
    r".{0,160}\bjmeter\b",
    re.IGNORECASE | re.DOTALL,
)
_SIMULATED_TOOL_TASK_PATTERN = re.compile(
    r"\bgatling\b.*\b(?:test|testing|script|scenario|workload|load|run|"
    r"execute|generate|create|prepare)\b|\b(?:test|testing|script|"
    r"scenario|workload|load|run|execute|generate|create|prepare)\b.*"
    r"\bgatling\b",
    re.IGNORECASE | re.DOTALL,
)
_CATALOG_TEST_CASE_ID_PATTERN = re.compile(r"\b(?:PTC|WTC)-\d{3}\b", re.I)
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_K6_ARTIFACTS_ROOT = (
    _PROJECT_ROOT / "src" / "generated_scripts" / "k6 native reports"
)
_DEFAULT_JMETER_ARTIFACTS_ROOT = (
    _PROJECT_ROOT / "src" / "generated_scripts" / "Jmeter native reports"
)
_DEFAULT_ARTIFACTS_ROOT = _DEFAULT_K6_ARTIFACTS_ROOT
_JOB_ID_PATTERN = re.compile(r"JOB-[0-9a-f]{32}")


class WorkloadProfile(BaseModel):
    """Validated, non-secret inputs required to define a test workload."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )

    tool: Literal["k6", "jmeter", "gatling"] | None = None
    target_url: str | None = None
    environment: Literal["mock_api", "external_api"] | None = None
    endpoint: str | None = None
    method: Literal["GET", "POST", "PUT", "PATCH", "DELETE"] | None = None
    payload_template: dict[str, Any] | list[Any] | None = None
    header_env: dict[str, str] | None = None
    expected_status_code: int | None = Field(default=None, ge=100, le=599)
    users: int | None = Field(default=None, ge=1)
    max_rps: int | None = Field(default=None, ge=1)
    duration_seconds: int | None = Field(default=None, ge=1)
    ramp_up_seconds: int | None = Field(default=None, ge=1)
    expected_response_time_ms: int | None = Field(default=None, ge=1)
    p95_threshold_ms: int | None = Field(default=None, ge=1)
    credentials_ref: str | None = None


class ExecutionArtifactManifest(BaseModel):
    """Stable artifact-key contract shared by runners, reports, and callers."""

    job_id: str
    execution_mode: ExecutionMode
    artifacts: dict[ArtifactKey, str] = Field(default_factory=dict)


class ExecutionPreflight(BaseModel):
    status: PreflightStatus
    missing_inputs: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)


class ExecutionJobContext(BaseModel):
    job_id: str
    execution_mode: ExecutionMode
    workload_profile: WorkloadProfile | None = None
    execution_preflight: ExecutionPreflight
    execution_status: ExecutionStatus
    execution_artifact_directory: str
    execution_artifacts: ExecutionArtifactManifest
    execution_source_id: str | None = None
    test_case_id: str | None = None
    test_case_name: str | None = None
    application: str | None = None


class ExecutionJobResult(BaseModel):
    """Structured execution-stage result; paths are relative to the job folder."""

    job_id: str
    execution_mode: ExecutionMode
    status: ExecutionStatus
    message: str
    missing_inputs: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
    artifacts: dict[ArtifactKey, str] = Field(default_factory=dict)


def real_execution_gate(state: dict[str, Any]) -> dict[str, Any]:
    """Return a fail-closed REAL-mode response without invoking any runner."""
    job_id = state.get("job_id")
    if not isinstance(job_id, str) or not job_id:
        raise ValueError("REAL execution context is missing a valid job_id.")

    preflight = state.get("execution_preflight")
    if not isinstance(preflight, dict):
        preflight = {}
    preflight_status = preflight.get("status")

    if preflight_status == "needs_input":
        missing_inputs = preflight.get("missing_inputs")
        if (
            not isinstance(missing_inputs, list)
            or not missing_inputs
            or not all(isinstance(item, str) and item for item in missing_inputs)
        ):
            raise ValueError("REAL execution preflight has invalid missing_inputs.")
        result = ExecutionJobResult(
            job_id=job_id,
            execution_mode="REAL",
            status="needs_input",
            message=(
                "Real execution was not started. Provide the missing "
                "workload profile values: "
                + ", ".join(missing_inputs)
                + "."
            ),
            missing_inputs=missing_inputs,
        )
    else:
        blocked_reasons = preflight.get("blocked_reasons")
        if not isinstance(blocked_reasons, list) or not all(
            isinstance(reason, str) for reason in blocked_reasons
        ):
            blocked_reasons = []
        if preflight_status == "ready":
            blocked_reasons = [
                "A ready REAL preflight must include a valid workload profile."
            ]
        elif preflight_status not in {"blocked", "rejected"}:
            blocked_reasons = [
                "Real execution preflight is missing or invalid."
            ]
        elif not blocked_reasons:
            blocked_reasons = [
                "REAL execution preflight was blocked without a reason."
            ]
        result = ExecutionJobResult(
            job_id=job_id,
            execution_mode="REAL",
            status="blocked",
            message=(
                "Real execution was not started. "
                "No simulated fallback was run."
            ),
            blocked_reasons=blocked_reasons,
        )
    return result.model_dump(mode="json")


def _catalog_profile_data(test_case: dict[str, Any]) -> dict[str, Any]:
    """Adapt the existing flat performance-test catalog to the profile schema."""
    profile = test_case.get("workload_profile")
    if profile is not None:
        if not isinstance(profile, dict):
            raise ValueError("workload_profile must be an object.")
        return profile

    raw_method = test_case.get("method")
    return {
        "tool": test_case.get("tool"),
        "target_url": test_case.get("target_url"),
        "environment": test_case.get("environment"),
        "endpoint": test_case.get("endpoint"),
        "method": (
            raw_method.strip().upper()
            if isinstance(raw_method, str) and raw_method.strip()
            else None
        ),
        "payload_template": test_case.get("payload_template"),
        "header_env": test_case.get("header_env"),
        "expected_status_code": test_case.get(
            "expected_status_code",
            test_case.get("expected_status"),
        ),
        "users": test_case.get("users", test_case.get("virtual_users")),
        "max_rps": test_case.get("max_rps"),
        "duration_seconds": test_case.get(
            "duration_seconds",
            test_case.get("duration"),
        ),
        "ramp_up_seconds": test_case.get(
            "ramp_up_seconds",
            test_case.get("ramp_up"),
        ),
        "expected_response_time_ms": test_case.get(
            "expected_response_time_ms"
        ),
        "p95_threshold_ms": test_case.get("p95_threshold_ms"),
        "credentials_ref": test_case.get("credentials_ref"),
    }


def workload_profile_from_test_case(
    test_case: dict[str, Any],
) -> WorkloadProfile:
    """Return a typed profile, retaining missing fields for input requests."""
    try:
        return WorkloadProfile.model_validate(_catalog_profile_data(test_case))
    except ValidationError as exc:
        raise ValueError(f"Invalid workload profile: {exc}") from exc


def missing_profile_inputs(profile: WorkloadProfile | None) -> list[str]:
    if profile is None:
        return list(_PROFILE_FIELD_NAMES) + ["payload_template"]

    missing = [
        field
        for field in _PROFILE_FIELD_NAMES
        if getattr(profile, field) is None
        or (
            isinstance(getattr(profile, field), str)
            and not getattr(profile, field).strip()
        )
    ]
    if profile.method in _BODY_METHODS and profile.payload_template is None:
        missing.append("payload_template")
    return missing


def is_k6_test_request(request: str) -> bool:
    """Identify requests to create or run k6 performance-test workloads."""
    return bool(_K6_TASK_PATTERN.search(request))


def is_jmeter_test_request(request: str) -> bool:
    """Identify JMeter workload tasks that require REAL-mode preflight."""
    return bool(_JMETER_TASK_PATTERN.search(request))


_TOOL_NEGATION = re.compile(
    r"\b(?:not|no|never|without|avoid|except|excluding|skip|don't|dont|"
    r"instead\s+of|rather\s+than)\b",
    re.IGNORECASE,
)


def _only_named_tool(request: str) -> str | None:
    """The one runner a request names, if it names exactly one without negating it.

    Whatever runner the prompt names is the runner used, whatever the catalog
    case defaults to. The explicit phrasings in requested_execution_tool ("using
    JMeter", "k6 runner") are narrower than the ways people name a runner, so
    "Run PTC-003 in JMeter", "using Apache JMeter" or just "PTC-003 JMeter" left
    the case on its catalog tool (and a JMeter request was then blocked for a
    tool mismatch). A negated mention ("no JMeter") does not count. Two runners
    named, or none, stay unselected.
    """
    named = {
        tool
        for tool, name in (("k6", "k6"), ("jmeter", "jmeter"))
        for match in re.finditer(rf"\b{name}\b", request, re.IGNORECASE)
        if not _TOOL_NEGATION.search(request[max(0, match.start() - 40): match.start()])
    }
    return next(iter(named)) if len(named) == 1 else None


def requested_execution_tool(request: str) -> str | None:
    """Return an explicitly requested real runner, if the request names one."""
    k6_selected = bool(
        re.search(
            r"\bk6\s+(?:test|script|plan|runner)\b|"
            r"\b(?:using|with|via|through|use)\s+(?:the\s+)?k6\b",
            request,
            re.IGNORECASE,
        )
    )
    jmeter_selected = bool(
        re.search(
            r"\bjmeter\s+(?:test|script|plan|runner)\b|"
            r"\b(?:using|with|via|through|use)\s+(?:the\s+)?jmeter\b",
            request,
            re.IGNORECASE,
        )
    )
    requested = {
        tool
        for tool, matches in (
            ("k6", k6_selected),
            ("jmeter", jmeter_selected),
        )
        if matches
    }
    if len(requested) > 1:
        raise ValueError(
            "Select either k6 or JMeter for one test case execution."
        )
    return next(iter(requested), None) or _only_named_tool(request)


def is_explicit_execution_request(request: str) -> bool:
    """Return true only for an affirmative request to start a test run."""
    if re.search(
        r"\b(?:do not|don't|never|without|avoid|no need to|not)\b"
        r"[^.!?,;\n]{0,80}\b(?:run|execute|perform|start|launch)\b",
        request,
        re.IGNORECASE,
    ):
        return False
    pattern = re.compile(
        r"\b(?:please\s+)?(?:run|execute|perform|start|launch)\b"
        r"[^.!?,;\n]{0,80}\b(?:test|script|scenario|workload|it|this|"
        r"jmeter|k6|gatling|"
        r"against|now|PTC-\d{3}|WTC-\d{3})\b",
        re.IGNORECASE,
    )
    for match in pattern.finditer(request):
        prefix = request[: match.start()]
        if re.search(
            r"\b(?:can|could|would|will|might|should)\s*$",
            prefix,
            re.IGNORECASE,
        ):
            continue
        return True
    return False


def is_simulated_tool_request(request: str) -> bool:
    """Identify Gatling workload requests that remain on the simulated path."""
    return bool(_SIMULATED_TOOL_TASK_PATTERN.search(request))


def extract_catalog_test_case_id(request: str) -> str | None:
    """Return the single explicit catalog ID in a request, if present."""
    test_case_ids = {
        match.group(0).upper()
        for match in _CATALOG_TEST_CASE_ID_PATTERN.finditer(request)
    }
    if len(test_case_ids) > 1:
        raise ValueError(
            "A request can select only one catalog test case at a time."
        )
    return next(iter(test_case_ids), None)


def _configured_positive_int(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a positive integer.") from exc
    if value < 1:
        raise ValueError(f"{name} must be a positive integer.")
    return value


def _enabled_by_configuration() -> bool:
    raw_value = os.getenv("REAL_EXECUTION_ENABLED", "false").strip().lower()
    if raw_value not in {"true", "false", "1", "0", "yes", "no"}:
        raise ValueError(
            "REAL_EXECUTION_ENABLED must be one of true/false, 1/0, or yes/no."
        )
    return raw_value in {"true", "1", "yes"}


def _allowed_hosts() -> set[str]:
    configured = os.getenv(
        "REAL_EXECUTION_ALLOWED_HOSTS",
        "localhost,127.0.0.1",
    )
    return {
        host.strip().lower().rstrip(".")
        for host in configured.split(",")
        if host.strip()
    }


def _allowed_ports() -> set[int]:
    configured = os.getenv("REAL_EXECUTION_ALLOWED_PORTS", "8000")
    ports: set[int] = set()
    for raw_port in configured.split(","):
        try:
            port = int(raw_port.strip())
        except ValueError as exc:
            raise ValueError(
                "REAL_EXECUTION_ALLOWED_PORTS must contain comma-separated ports."
            ) from exc
        if not 1 <= port <= 65535:
            raise ValueError("Allowed ports must be between 1 and 65535.")
        ports.add(port)
    return ports


def _external_targets_enabled() -> bool:
    raw_value = os.getenv("REAL_EXECUTION_EXTERNAL_TARGETS_ENABLED", "false")
    normalized = raw_value.strip().lower()
    if normalized not in {"true", "false", "1", "0", "yes", "no"}:
        raise ValueError(
            "REAL_EXECUTION_EXTERNAL_TARGETS_ENABLED must be one of "
            "true/false, 1/0, or yes/no."
        )
    return normalized in {"true", "1", "yes"}


def _resolve_target_addresses(host: str, port: int) -> tuple[set[str], str | None]:
    try:
        resolved = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError as exc:
        return set(), f"Could not resolve allowed target host '{host}': {exc}."
    addresses = {entry[4][0].split("%", 1)[0] for entry in resolved}
    if not addresses:
        return set(), f"Target host '{host}' resolved to no addresses."
    return addresses, None


def validate_target_url(
    target_url: str,
    *,
    environment: str = "mock_api",
) -> list[str]:
    """Validate an approved local or external origin and its DNS addresses."""
    errors: list[str] = []
    try:
        parsed = urlsplit(target_url)
        hostname = parsed.hostname
        port = parsed.port
    except ValueError:
        return ["target_url is not a valid URL."]

    if not hostname:
        errors.append("target_url must include a hostname.")
        return errors
    if parsed.username or parsed.password:
        errors.append("target_url must not include embedded credentials.")

    normalized_host = hostname.lower().rstrip(".")
    is_external = environment == "external_api"
    if environment not in {"mock_api", "external_api"}:
        errors.append("environment must be mock_api or external_api.")
    if is_external:
        if parsed.scheme != "https":
            errors.append("External API target_url must use HTTPS.")
        try:
            external_enabled = _external_targets_enabled()
        except ValueError as exc:
            return [str(exc)]
        if not external_enabled:
            errors.append(
                "REAL_EXECUTION_EXTERNAL_TARGETS_ENABLED is false; "
                "external targets are disabled."
            )
        try:
            ipaddress.ip_address(normalized_host)
            is_ip_literal = True
        except ValueError:
            is_ip_literal = False
        if is_ip_literal:
            errors.append("External API targets must use an allowlisted DNS hostname.")
    elif parsed.scheme != "http":
        errors.append("Mock API target_url must use http.")

    if normalized_host not in _allowed_hosts():
        errors.append(
            f"Target host '{hostname}' is not in REAL_EXECUTION_ALLOWED_HOSTS."
        )

    resolved_port = port if port is not None else (80 if parsed.scheme == "http" else 443)
    if resolved_port not in _allowed_ports():
        errors.append(
            f"Target port {resolved_port} is not in REAL_EXECUTION_ALLOWED_PORTS."
        )

    if parsed.query or parsed.fragment:
        errors.append("target_url must not contain a query or fragment.")
    if parsed.path not in {"", "/"}:
        errors.append(
            "target_url must be an origin only; put the request path in endpoint."
        )

    if normalized_host in _allowed_hosts():
        addresses, resolution_error = _resolve_target_addresses(
            normalized_host,
            resolved_port,
        )
        if resolution_error:
            errors.append(resolution_error)
        elif is_external:
            invalid_addresses = []
            for address in addresses:
                try:
                    parsed_address = ipaddress.ip_address(address)
                except ValueError:
                    invalid_addresses.append(address)
                    continue
                if not parsed_address.is_global:
                    invalid_addresses.append(address)
            if invalid_addresses:
                errors.append(
                    f"External target '{hostname}' resolves to a non-public address."
                )
        elif any(not ipaddress.ip_address(address).is_loopback for address in addresses):
            errors.append(
                f"Target host '{hostname}' resolves to a non-loopback address."
            )
    return errors


def validate_real_profile(
    profile: WorkloadProfile | None,
) -> dict[str, Any]:
    missing = missing_profile_inputs(profile)
    if missing:
        return {
            "status": "needs_input",
            "missing_inputs": missing,
            "blocked_reasons": [],
        }

    assert profile is not None
    errors: list[str] = []
    if profile.endpoint is not None:
        endpoint_parts = urlsplit(profile.endpoint)
        endpoint_path = unquote(endpoint_parts.path)
        if (
            not profile.endpoint.startswith("/")
            or profile.endpoint.startswith("//")
            or "://" in profile.endpoint
            or profile.endpoint.startswith("//")
            or "\\" in endpoint_path
            or "#" in profile.endpoint
            or any(ord(character) < 32 or ord(character) == 127 for character in endpoint_path)
            or endpoint_path.startswith("//")
            or any(part == ".." for part in endpoint_path.split("/"))
        ):
            errors.append(
                "endpoint must be an absolute path, not a URL or traversal path."
            )
    if profile.header_env is not None:
        forbidden_headers = {
            "connection",
            "content-length",
            "host",
            "transfer-encoding",
            "upgrade",
        }
        for header_name, env_name in profile.header_env.items():
            normalized_header = header_name.lower()
            if (
                not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", header_name)
                or normalized_header in forbidden_headers
                or normalized_header.startswith("proxy-")
            ):
                errors.append(f"header_env contains an unsupported header name: {header_name!r}.")
            if not re.fullmatch(r"[A-Z_][A-Z0-9_]*", env_name):
                errors.append(
                    f"header_env value for {header_name!r} must be an uppercase "
                    "environment variable name."
                )
    try:
        max_users = _configured_positive_int("REAL_EXECUTION_MAX_USERS", 500)
        max_duration = _configured_positive_int(
            "REAL_EXECUTION_MAX_DURATION_SECONDS",
            500,
        )
        max_ramp_up = _configured_positive_int(
            "REAL_EXECUTION_MAX_RAMP_UP_SECONDS",
            90,
        )
        assert profile.users is not None
        assert profile.max_rps is not None
        assert profile.duration_seconds is not None
        assert profile.ramp_up_seconds is not None
        if profile.users > max_users:
            errors.append(f"users exceeds the configured maximum of {max_users}.")
        if profile.tool == "jmeter":
            max_jmeter_rps = _configured_positive_int(
                "REAL_JMETER_MAX_RPS",
                1000,
            )
            if profile.max_rps > max_jmeter_rps:
                errors.append(
                    "max_rps exceeds the configured JMeter maximum of "
                    f"{max_jmeter_rps}."
                )
        if profile.duration_seconds > max_duration:
            errors.append(
                "duration_seconds exceeds the configured maximum of "
                f"{max_duration}."
            )
        if profile.ramp_up_seconds > max_ramp_up:
            errors.append(
                f"ramp_up_seconds exceeds the configured maximum of {max_ramp_up}."
            )
        if profile.ramp_up_seconds > profile.duration_seconds:
            errors.append("ramp_up_seconds cannot exceed duration_seconds.")
        if profile.ramp_up_seconds * 2 > profile.duration_seconds:
            errors.append(
                "duration_seconds must accommodate both ramp-up and ramp-down."
            )
        errors.extend(
            validate_target_url(
                profile.target_url or "",
                environment=profile.environment or "mock_api",
            )
        )
        real_execution_enabled = _enabled_by_configuration()
    except ValueError as exc:
        return {
            "status": "blocked",
            "missing_inputs": [],
            "blocked_reasons": [str(exc)],
        }

    if errors:
        return {
            "status": "rejected",
            "missing_inputs": [],
            "blocked_reasons": errors,
        }
    if not real_execution_enabled:
        return {
            "status": "blocked",
            "missing_inputs": [],
            "blocked_reasons": [
                "REAL_EXECUTION_ENABLED is false; real runs are disabled.",
            ],
        }
    return {
        "status": "ready",
        "missing_inputs": [],
        "blocked_reasons": [],
    }


def resolve_artifact_directory(
    job_id: str,
    tool: str | None = None,
) -> Path:
    if not _JOB_ID_PATTERN.fullmatch(job_id):
        raise ValueError("job_id must use the generated JOB-<uuid> format.")
    if tool is not None:
        root = artifact_root_directory(tool)
        candidate = root / job_id
        if candidate.is_symlink():
            raise ValueError("Artifact job directory must not be a symbolic link.")
        return candidate.resolve()

    existing: list[Path] = []
    roots = artifact_root_directories()
    for root in roots:
        candidate = root / job_id
        if candidate.is_symlink():
            raise ValueError("Artifact job directory must not be a symbolic link.")
        if candidate.exists():
            resolved = candidate.resolve()
            if resolved.parent != root:
                raise ValueError("Artifact job directory must be inside its tool root.")
            existing.append(resolved)
    if len(existing) > 1:
        raise ValueError("Job ID exists in multiple tool artifact roots.")
    if existing:
        return existing[0]
    return (artifact_root_directory() / job_id).resolve()


def _configured_artifact_root(environment_variable: str, default: Path) -> Path:
    artifact_root = Path(
        os.getenv(environment_variable, str(default))
    ).expanduser()
    if not artifact_root.is_absolute():
        artifact_root = _PROJECT_ROOT / artifact_root
    return artifact_root.resolve()


def artifact_root_directory(tool: str | None = None) -> Path:
    normalized_tool = tool.strip().lower() if isinstance(tool, str) else None
    if normalized_tool == "k6":
        if os.getenv("K6_EXECUTION_ARTIFACTS_ROOT"):
            return _configured_artifact_root(
                "K6_EXECUTION_ARTIFACTS_ROOT",
                _DEFAULT_K6_ARTIFACTS_ROOT,
            )
        if os.getenv("EXECUTION_ARTIFACTS_ROOT"):
            return _configured_artifact_root(
                "EXECUTION_ARTIFACTS_ROOT",
                _DEFAULT_K6_ARTIFACTS_ROOT,
            )
        return _configured_artifact_root(
            "K6_EXECUTION_ARTIFACTS_ROOT",
            _DEFAULT_K6_ARTIFACTS_ROOT,
        )
    if normalized_tool == "jmeter":
        if os.getenv("JMETER_EXECUTION_ARTIFACTS_ROOT"):
            return _configured_artifact_root(
                "JMETER_EXECUTION_ARTIFACTS_ROOT",
                _DEFAULT_JMETER_ARTIFACTS_ROOT,
            )
        if os.getenv("EXECUTION_ARTIFACTS_ROOT"):
            return _configured_artifact_root(
                "EXECUTION_ARTIFACTS_ROOT",
                _DEFAULT_JMETER_ARTIFACTS_ROOT,
            )
        return _configured_artifact_root(
            "JMETER_EXECUTION_ARTIFACTS_ROOT",
            _DEFAULT_JMETER_ARTIFACTS_ROOT,
        )
    return _configured_artifact_root(
        "EXECUTION_ARTIFACTS_ROOT",
        _DEFAULT_ARTIFACTS_ROOT,
    )


def artifact_root_directories() -> list[Path]:
    """Return unique known roots, including a configured legacy shared root."""
    roots = [
        artifact_root_directory("k6"),
        artifact_root_directory("jmeter"),
        artifact_root_directory(),
    ]
    return list(dict.fromkeys(roots))


def artifact_directory_reference(
    job_id: str,
    tool: str | None = None,
) -> str:
    """Return a stable project-relative artifact path when inside the repo."""
    artifact_directory = resolve_artifact_directory(job_id, tool=tool)
    try:
        return artifact_directory.relative_to(_PROJECT_ROOT).as_posix()
    except ValueError:
        return str(artifact_directory)


def create_execution_job_context(
    *,
    execution_mode: str = "SIMULATED",
    workload_profile: dict[str, Any] | WorkloadProfile | None = None,
    source_id: str | None = None,
    test_case_id: str | None = None,
    test_case_name: str | None = None,
    application: str | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    if not isinstance(execution_mode, str):
        raise ValueError("execution_mode must be REAL or SIMULATED.")
    mode = execution_mode.strip().upper()
    if mode not in {"REAL", "SIMULATED"}:
        raise ValueError("execution_mode must be REAL or SIMULATED.")

    if isinstance(workload_profile, dict):
        profile = workload_profile_from_test_case(
            {"workload_profile": workload_profile}
        )
    else:
        profile = workload_profile

    if mode == "REAL":
        preflight_data = validate_real_profile(profile)
    else:
        preflight_data = {
            "status": "not_required",
            "missing_inputs": [],
            "blocked_reasons": [],
        }
    preflight = ExecutionPreflight.model_validate(preflight_data)

    if job_id is None:
        job_id = f"JOB-{uuid.uuid4().hex}"
    artifact_directory = resolve_artifact_directory(
        job_id,
        tool=profile.tool if profile is not None else None,
    )

    status: ExecutionStatus = "not_started"
    if mode == "REAL" and preflight.status == "needs_input":
        status = "needs_input"
    elif mode == "REAL" and preflight.status in {"blocked", "rejected"}:
        status = "blocked"

    context = ExecutionJobContext(
        job_id=job_id,
        execution_mode="REAL" if mode == "REAL" else "SIMULATED",
        workload_profile=profile,
        execution_preflight=preflight,
        execution_status=status,
        execution_artifact_directory=str(artifact_directory),
        execution_artifacts=ExecutionArtifactManifest(
            job_id=job_id,
            execution_mode="REAL" if mode == "REAL" else "SIMULATED",
        ),
        execution_source_id=source_id,
        test_case_id=test_case_id,
        test_case_name=test_case_name,
        application=application,
    )
    return context.model_dump(mode="json")


def create_context_for_test_case(
    test_case: dict[str, Any],
    *,
    source_id: str | None = None,
    requested_tool: str | None = None,
) -> dict[str, Any]:
    profile = workload_profile_from_test_case(test_case)
    if requested_tool is not None:
        if requested_tool not in {"k6", "jmeter"}:
            raise ValueError("Catalog performance tests support k6 or JMeter.")
        profile = profile.model_copy(update={"tool": requested_tool})
        mode = "REAL"
    elif profile.tool == "k6":
        mode = "REAL"
    elif profile.tool in {"jmeter", "gatling"}:
        mode = "SIMULATED"
    else:
        mode = str(test_case.get("execution_mode", "SIMULATED")).strip().upper()
    return create_execution_job_context(
        execution_mode=mode,
        workload_profile=profile,
        source_id=source_id,
        test_case_id=(
            str(test_case["test_case_id"])
            if test_case.get("test_case_id") is not None
            else None
        ),
        test_case_name=(
            str(test_case["name"])
            if test_case.get("name") is not None
            else None
        ),
        application=(
            str(test_case["application"])
            if test_case.get("application") is not None
            else None
        ),
    )


__all__ = [
    "ExecutionArtifactManifest",
    "ExecutionJobResult",
    "ExecutionJobContext",
    "ExecutionMode",
    "ExecutionPreflight",
    "ExecutionStatus",
    "artifact_directory_reference",
    "artifact_root_directory",
    "artifact_root_directories",
    "ArtifactKey",
    "WorkloadProfile",
    "create_context_for_test_case",
    "create_execution_job_context",
    "extract_catalog_test_case_id",
    "is_k6_test_request",
    "is_jmeter_test_request",
    "requested_execution_tool",
    "is_explicit_execution_request",
    "is_simulated_tool_request",
    "missing_profile_inputs",
    "real_execution_gate",
    "resolve_artifact_directory",
    "validate_real_profile",
    "validate_target_url",
    "workload_profile_from_test_case",
]
import os
import re
import subprocess
from typing import Any


SUPPORTED_REAL_TOOLS = {"k6"}

DEFAULT_K6_API_PATH = "/api/v1/payment"
DEFAULT_EXPECTED_STATUS = 200


class K6OutputParser:
    @staticmethod
    def parse(stdout: str, stderr: str = "") -> dict[str, Any]:
        if not stdout or not stdout.strip():
            return {
                "status": "error",
                "message": "k6 returned empty stdout.",
                "stderr": stderr,
            }

        http_requests = K6OutputParser._extract_int_metric(
            stdout,
            "http_reqs",
        )

        error_rate = K6OutputParser._extract_percentage_metric(
            stdout,
            "http_req_failed",
        )

        failed_requests = K6OutputParser._extract_failed_request_count(
            stdout
        )

        if failed_requests is None:
            failed_requests = round(
                http_requests * error_rate / 100
            )

        successful_requests = (
            http_requests - failed_requests
        )

        avg_response_time = K6OutputParser._extract_duration_metric(
            stdout,
            "avg",
        )

        p95_response_time = K6OutputParser._extract_duration_metric(
            stdout,
            "p(95)",
        )

        max_response_time = K6OutputParser._extract_duration_metric(
            stdout,
            "max",
        )

        throughput = K6OutputParser._extract_throughput(
            stdout
        )

        checks_succeeded = K6OutputParser._extract_check_percentage(
            stdout,
            "checks_succeeded",
        )

        checks_failed = K6OutputParser._extract_check_percentage(
            stdout,
            "checks_failed",
        )

        test_passed = (
            checks_failed == 0
            and error_rate == 0
            and successful_requests == http_requests
        )

        return {
            "status": "success",
            "test_passed": test_passed,
            "total_requests": http_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "max_response_time": max_response_time,
            "throughput": throughput,
            "error_rate": error_rate,
            "checks_succeeded": checks_succeeded,
            "checks_failed": checks_failed,
            "stderr": stderr,
        }

    @staticmethod
    def _extract_int_metric(
        stdout: str,
        metric_name: str,
    ) -> int:
        pattern = rf"^\s*{re.escape(metric_name)}\.*:\s*(\d+)"
        match = re.search(
            pattern,
            stdout,
            re.MULTILINE,
        )

        if not match:
            return 0

        return int(match.group(1))

    @staticmethod
    def _extract_percentage_metric(
        stdout: str,
        metric_name: str,
    ) -> float:
        pattern = (
            rf"^\s*{re.escape(metric_name)}\.*:\s*"
            rf"([0-9]+(?:\.[0-9]+)?)%"
        )

        match = re.search(
            pattern,
            stdout,
            re.MULTILINE,
        )

        if not match:
            return 0.0

        return float(match.group(1))

    @staticmethod
    def _extract_check_percentage(
        stdout: str,
        metric_name: str,
    ) -> float:
        return K6OutputParser._extract_percentage_metric(
            stdout,
            metric_name,
        )

    @staticmethod
    def _extract_failed_request_count(
        stdout: str,
    ) -> int | None:
        pattern = (
            r"http_req_failed\.*:\s*"
            r"[0-9]+(?:\.[0-9]+)?%\s*"
            r"(\d+)\s+out of\s+(\d+)"
        )

        match = re.search(
            pattern,
            stdout,
            re.MULTILINE,
        )

        if not match:
            return None

        return int(match.group(1))

    @staticmethod
    def _extract_duration_metric(
        stdout: str,
        metric_name: str,
    ) -> float:
        pattern = (
            r"^\s*http_req_duration\.*:.*?"
            rf"{re.escape(metric_name)}="
            r"([0-9]+(?:\.[0-9]+)?)(ms|s)"
        )

        match = re.search(
            pattern,
            stdout,
            re.MULTILINE,
        )

        if not match:
            return 0.0

        value = float(match.group(1))
        unit = match.group(2)

        if unit == "s":
            value *= 1000

        return value

    @staticmethod
    def _extract_throughput(
        stdout: str,
    ) -> float:
        pattern = (
            r"^\s*http_reqs\.*:\s*"
            r"\d+\s+"
            r"([0-9]+(?:\.[0-9]+)?)/s"
        )

        match = re.search(
            pattern,
            stdout,
            re.MULTILINE,
        )

        if not match:
            return 0.0

        return float(match.group(1))


def resolve_k6_api_path(api_path: str) -> str:
    """
    Convert a planner/API description into a safe k6 API path.

    Known UPI payment API requests use the existing mock endpoint.

    If the planner already provides a valid absolute API path,
    preserve it.

    Unknown natural-language API descriptions return an empty path.
    The execution layer must not silently substitute an unrelated API.
    """

    if not api_path or not api_path.strip():
        return ""

    api_path = api_path.strip()

    if api_path.startswith("/"):
        return api_path

    normalized = api_path.lower()

    known_api_paths = {
    "upi payment api": "/api/v1/payment",
    "upi payment": "/api/v1/payment",
    "payment api": "/api/v1/payment",
    "payment": "/api/v1/payment",
    "neft payment api": "/api/v1/payment/neft",
    "neft payment": "/api/v1/payment/neft",
    "payment failure api": "/api/v1/payment/failure",
    "payment failure": "/api/v1/payment/failure",
    }

    if normalized in known_api_paths:
        return known_api_paths[normalized]

    return DEFAULT_K6_API_PATH


def execute_real_test(
    tool: str,
    script_path: str,
    base_url: str,
    users: int,
    duration: int,
    api_path: str = DEFAULT_K6_API_PATH,
    expected_status: int = DEFAULT_EXPECTED_STATUS,
) -> dict[str, Any]:

    if not tool:
        return {
            "status": "error",
            "message": "Performance-testing tool is required.",
        }

    tool_name = tool.lower().strip()

    if tool_name not in SUPPORTED_REAL_TOOLS:
        return {
            "status": "error",
            "message": (
                f"Real execution is currently supported only for: "
                f"{sorted(SUPPORTED_REAL_TOOLS)}."
            ),
        }

    if not script_path or not os.path.exists(script_path):
        return {
            "status": "error",
            "message": "Generated k6 script was not found.",
            "script_path": script_path,
        }

    if users < 1:
        return {
            "status": "error",
            "message": "Users must be greater than zero.",
        }

    if duration < 1:
        return {
            "status": "error",
            "message": "Duration must be greater than zero.",
        }

    if not base_url or not base_url.strip():
        return {
            "status": "error",
            "message": "Base URL is required for real k6 execution.",
        }

    resolved_api_path = resolve_k6_api_path(api_path)

    environment = os.environ.copy()

    environment["BASE_URL"] = base_url.rstrip("/")
    environment["VUS"] = str(users)
    environment["DURATION"] = f"{duration}s"
    environment["API_PATH"] = resolved_api_path
    environment["EXPECTED_STATUS"] = str(expected_status)

    try:
        completed_process = subprocess.run(
            [
                "k6",
                "run",
                script_path,
            ],
            env=environment,
            capture_output=True,
            text=True,
            timeout=duration + 60,
        )

    except FileNotFoundError:
        return {
            "status": "error",
            "message": (
                "k6 executable was not found. "
                "Make sure k6 is installed and available on PATH."
            ),
        }

    except subprocess.TimeoutExpired as exc:
        return {
            "status": "error",
            "message": "k6 execution timed out.",
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
        }

    stdout = completed_process.stdout or ""
    stderr = completed_process.stderr or ""

    stdout_preview = stdout[-4000:]
    stderr_preview = stderr[-4000:]

    parsed_result = K6OutputParser.parse(
        stdout=stdout,
        stderr=stderr,
    )

    if parsed_result.get("status") != "success":
        return {
            "status": "error",
            "message": "Unable to parse k6 execution output.",
            "return_code": completed_process.returncode,
            "stdout": stdout_preview,
            "stderr": stderr_preview,
            "metrics": parsed_result,
        }

    if completed_process.returncode != 0:
        return {
            "status": "error",
            "message": "k6 performance test execution failed.",
            "tool": tool_name,
            "script_path": script_path,
            "return_code": completed_process.returncode,
            "stdout": stdout_preview,
            "stderr": stderr_preview,
            "metrics": parsed_result,
        }

    if not parsed_result.get("test_passed"):
        return {
            "status": "error",
            "message": "k6 test completed but performance checks failed.",
            "tool": tool_name,
            "script_path": script_path,
            "return_code": completed_process.returncode,
            "stdout": stdout_preview,
            "stderr": stderr_preview,
            "metrics": parsed_result,
        }

    return {
        "status": "success",
        "message": "k6 performance test executed successfully.",
        "tool": tool_name,
        "script_path": script_path,
        "return_code": completed_process.returncode,
        "stdout": stdout_preview,
        "stderr": stderr_preview,
        "api_path": resolved_api_path,
        "metrics": parsed_result,
    }
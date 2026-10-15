from typing import Any


EXPECTED_KEYS = {
    "job_id",
    "application",
    "scenario",
    "api_name",
    "total_requests",
    "successful_requests",
    "failed_requests",
    "avg_response_time",
    "p95_response_time",
    "max_response_time",
    "throughput",
    "error_rate",
    "http_status",
}


def format_execution_result(
    execution_result: dict,
    monitoring_result: dict,
) -> dict:
    """
    Convert execution and monitoring information into the strict
    standardized result contract required by the Analysis Agent.

    The returned dictionary contains exactly the following fields:

    job_id
    application
    scenario
    api_name
    total_requests
    successful_requests
    failed_requests
    avg_response_time
    p95_response_time
    max_response_time
    throughput
    error_rate
    http_status
    """

    if execution_result.get("status") != "success":
        raise ValueError(
            "Cannot format an unsuccessful execution."
        )

    if monitoring_result.get("status") != "completed":
        raise ValueError(
            "Cannot format an execution that has not completed."
        )

    metrics = monitoring_result.get("metrics")

    if not isinstance(metrics, dict):
        raise ValueError(
            "Monitoring result does not contain valid metrics."
        )

    job_id = monitoring_result.get(
        "execution_id"
    )

    application = execution_result.get(
        "application",
        "Unknown",
    )

    scenario = execution_result.get(
        "scenario",
        "Unknown",
    )

    api_name = execution_result.get(
        "api_name",
        "Unknown",
    )

    result = {
        "job_id": str(job_id),
        "application": str(application),
        "scenario": str(scenario),
        "api_name": str(api_name),

        "total_requests": int(
            metrics["total_requests"]
        ),

        "successful_requests": int(
            metrics["successful_requests"]
        ),

        "failed_requests": int(
            metrics["failed_requests"]
        ),

        "avg_response_time": float(
            metrics["avg_response_time"]
        ),

        "p95_response_time": float(
            metrics["p95_response_time"]
        ),

        "max_response_time": float(
            metrics["max_response_time"]
        ),

        "throughput": float(
            metrics["throughput"]
        ),

        "error_rate": float(
            metrics["error_rate"]
        ),

        "http_status": int(
            metrics["http_status"]
        ),
    }

    _validate_result(result)

    return result


def _validate_result(result: dict) -> None:
    """
    Validate the standardized execution result.

    This ensures that the Analysis Agent receives exactly the
    agreed contract and that the basic metric relationships are valid.
    """

    actual_keys = set(result.keys())

    if actual_keys != EXPECTED_KEYS:
        missing_keys = EXPECTED_KEYS - actual_keys
        extra_keys = actual_keys - EXPECTED_KEYS

        raise ValueError(
            "Invalid execution result schema. "
            f"Missing keys: {missing_keys}. "
            f"Extra keys: {extra_keys}."
        )

    if (
        result["successful_requests"]
        + result["failed_requests"]
        != result["total_requests"]
    ):
        raise ValueError(
            "Successful requests + failed requests "
            "must equal total requests."
        )

    if not 0 <= result["error_rate"] <= 100:
        raise ValueError(
            "Error rate must be between 0 and 100."
        )

    if (
        result["max_response_time"]
        < result["p95_response_time"]
    ):
        raise ValueError(
            "Maximum response time cannot be lower than "
            "P95 response time."
        )
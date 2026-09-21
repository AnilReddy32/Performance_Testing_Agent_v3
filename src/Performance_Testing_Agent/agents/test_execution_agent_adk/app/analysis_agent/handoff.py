from typing import Any


EXPECTED_ANALYSIS_KEYS = {
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


def validate_analysis_payload(payload: dict[str, Any]) -> None:
    """
    Validate the exact payload contract expected by the Analysis Agent.
    """

    if not isinstance(payload, dict):
        raise ValueError(
            "Analysis handoff payload must be a dictionary."
        )

    actual_keys = set(payload.keys())

    if actual_keys != EXPECTED_ANALYSIS_KEYS:
        missing_keys = EXPECTED_ANALYSIS_KEYS - actual_keys
        extra_keys = actual_keys - EXPECTED_ANALYSIS_KEYS

        raise ValueError(
            "Invalid Analysis Agent handoff payload. "
            f"Missing keys: {missing_keys}. "
            f"Extra keys: {extra_keys}."
        )

    if (
        not isinstance(payload["job_id"], str)
        or not payload["job_id"].strip()
    ):
        raise ValueError("job_id must be a non-empty string.")

    if (
        not isinstance(payload["application"], str)
        or not payload["application"].strip()
    ):
        raise ValueError(
            "application must be a non-empty string."
        )

    if (
        not isinstance(payload["scenario"], str)
        or not payload["scenario"].strip()
    ):
        raise ValueError(
            "scenario must be a non-empty string."
        )

    if (
        not isinstance(payload["api_name"], str)
        or not payload["api_name"].strip()
    ):
        raise ValueError(
            "api_name must be a non-empty string."
        )

    integer_fields = {
        "total_requests",
        "successful_requests",
        "failed_requests",
        "http_status",
    }

    for field in integer_fields:
        if not isinstance(payload[field], int):
            raise ValueError(
                f"{field} must be an integer."
            )

    numeric_fields = {
        "avg_response_time",
        "p95_response_time",
        "max_response_time",
        "throughput",
        "error_rate",
    }

    for field in numeric_fields:
        if not isinstance(
            payload[field],
            (int, float),
        ):
            raise ValueError(
                f"{field} must be numeric."
            )

    if payload["total_requests"] < 0:
        raise ValueError(
            "total_requests cannot be negative."
        )

    if payload["successful_requests"] < 0:
        raise ValueError(
            "successful_requests cannot be negative."
        )

    if payload["failed_requests"] < 0:
        raise ValueError(
            "failed_requests cannot be negative."
        )

    if (
        payload["successful_requests"]
        + payload["failed_requests"]
        != payload["total_requests"]
    ):
        raise ValueError(
            "Successful and failed requests must equal total requests."
        )

    if not 0 <= payload["error_rate"] <= 100:
        raise ValueError(
            "error_rate must be between 0 and 100."
        )

    if payload["avg_response_time"] < 0:
        raise ValueError(
            "avg_response_time cannot be negative."
        )

    if payload["p95_response_time"] < 0:
        raise ValueError(
            "p95_response_time cannot be negative."
        )

    if payload["max_response_time"] < 0:
        raise ValueError(
            "max_response_time cannot be negative."
        )

    if (
        payload["p95_response_time"]
        < payload["avg_response_time"]
    ):
        raise ValueError(
            "p95_response_time cannot be lower "
            "than avg_response_time."
        )

    if (
        payload["max_response_time"]
        < payload["p95_response_time"]
    ):
        raise ValueError(
            "max_response_time cannot be lower "
            "than p95_response_time."
        )


def prepare_analysis_handoff(
    standardized_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate and return the exact payload that will be
    handed to the Analysis Agent.
    """

    validate_analysis_payload(
        standardized_result
    )

    return dict(standardized_result)
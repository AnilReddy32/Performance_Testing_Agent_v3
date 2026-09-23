import json
from pathlib import Path
from typing import Any


PROFILE_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "application_profile.json"
)


def get_api_information(
    endpoint: str | None = None,
    method: str | None = None,
) -> dict[str, Any]:
    """
    Retrieve API and endpoint information from the application profile.

    Use this tool when the security assessment requires information
    about API endpoints, HTTP methods, authentication requirements,
    authorization requirements, roles, or rate-limiting configuration.

    Args:
        endpoint: Optional API endpoint path, such as "/login" or "/users".
            If omitted, information for all endpoints is returned.

        method: Optional HTTP method such as "GET" or "POST".
            If provided, results are filtered by this method.

    Returns:
        A dictionary containing the requested API information.
    """

    if not PROFILE_PATH.exists():
        return {
            "success": False,
            "error": "Application profile not found."
        }

    try:
        with PROFILE_PATH.open("r", encoding="utf-8") as file:
            profile = json.load(file)

    except json.JSONDecodeError:
        return {
            "success": False,
            "error": "Application profile contains invalid JSON."
        }

    except OSError as exc:
        return {
            "success": False,
            "error": f"Unable to read application profile: {exc}"
        }

    api_data = profile.get("api")

    if not isinstance(api_data, dict):
        return {
            "success": False,
            "error": "API information is not available in the application profile."
        }

    endpoints = api_data.get("endpoints", [])

    if not isinstance(endpoints, list):
        return {
            "success": False,
            "error": "API endpoint information has an invalid format."
        }

    filtered_endpoints = endpoints

    if endpoint is not None:
        filtered_endpoints = [
            item
            for item in filtered_endpoints
            if item.get("path") == endpoint
        ]

    if method is not None:
        normalized_method = method.upper()

        filtered_endpoints = [
            item
            for item in filtered_endpoints
            if item.get("method", "").upper() == normalized_method
        ]

    if endpoint is not None and not filtered_endpoints:
        return {
            "success": False,
            "error": f"Endpoint '{endpoint}' was not found."
        }

    if method is not None and not filtered_endpoints:
        return {
            "success": False,
            "error": (
                f"No API endpoint matched the requested method "
                f"'{method.upper()}'."
            )
        }

    return {
        "success": True,
        "base_url": api_data.get("base_url"),
        "version": api_data.get("version"),
        "endpoints": filtered_endpoints,
    }
from typing import Any
from google.adk.tools import ToolContext
from security_agent.security.profiles import select_profile
from security_agent.tools.state_utils import snapshot_session_state


def get_api_information(
    endpoint: str | None = None,
    method: str | None = None,
    tool_context: ToolContext | None = None,
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

    try:
        selection = select_profile(
            snapshot_session_state(tool_context.state) if tool_context else {}
        )
    except (OSError, ValueError) as exc:
        return {
            "success": False,
            "error": f"Unable to load versioned application profiles: {exc}"
        }

    if selection["status"] != "matched":
        return {
            "success": False,
            "profile_match_status": selection["status"],
            "error": selection.get("reason", "A unique matching profile was not found."),
        }

    profile = selection["data"]

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
        "profile_id": selection["profile_id"],
        "profile_version": selection["profile_version"],
        "base_url": api_data.get("base_url"),
        "version": api_data.get("version"),
        "endpoints": filtered_endpoints,
    }

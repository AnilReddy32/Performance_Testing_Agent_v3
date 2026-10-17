from typing import Any
from google.adk.tools import ToolContext
from security_agent.security.profiles import select_profile
from security_agent.tools.state_utils import snapshot_session_state


def get_application_profile(
    section: str | None = None,
    tool_context: ToolContext | None = None,
) -> dict[str, Any]:
    """
    Retrieve application security profile information.

    Use this tool when you need structured information about the
    application being assessed.

    Args:
        section: Optional profile section to retrieve. Examples:
            "application", "authentication", "authorization",
            "api", "sql_security", "xss_security",
            "csrf_security", "oauth", "mfa".

            If omitted, the complete application profile is returned.

    Returns:
        A dictionary containing the requested application profile data.
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

    if section is None:
        return {
            "success": True,
            "profile_id": selection["profile_id"],
            "profile_version": selection["profile_version"],
            "data": profile
        }

    if section not in profile:
        return {
            "success": False,
            "error": f"Profile section '{section}' was not found."
        }

    return {
        "success": True,
        "profile_id": selection["profile_id"],
        "profile_version": selection["profile_version"],
        "section": section,
        "data": profile[section]
    }

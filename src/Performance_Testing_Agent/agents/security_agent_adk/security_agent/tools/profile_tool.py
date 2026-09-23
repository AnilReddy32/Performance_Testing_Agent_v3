import json
from pathlib import Path
from typing import Any


PROFILE_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "application_profile.json"
)


def get_application_profile(section: str | None = None) -> dict[str, Any]:
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

    if section is None:
        return {
            "success": True,
            "data": profile
        }

    if section not in profile:
        return {
            "success": False,
            "error": f"Profile section '{section}' was not found."
        }

    return {
        "success": True,
        "section": section,
        "data": profile[section]
    }
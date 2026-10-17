"""Versioned application profile registry and trusted-scope matching."""

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


REGISTRY_PATH = Path(__file__).resolve().parent.parent / "data" / "application_profile.json"


def _origin(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = urlsplit(value.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return None
        host = parsed.hostname.lower().rstrip(".")
        host = f"[{host}]" if ":" in host else host
        port = parsed.port
        default_port = 443 if parsed.scheme.lower() == "https" else 80
        return f"{parsed.scheme.lower()}://{host}" + (f":{port}" if port and port != default_port else "")
    except ValueError:
        return None


def _endpoint_matches(pattern: str, endpoint: str) -> bool:
    try:
        path = urlsplit(endpoint).path or "/"
    except ValueError:
        return False
    expression = re.sub(r"\{[^/{}]+\}", r"[^/]+", pattern.rstrip("/"))
    return re.fullmatch(expression + r"/?", path) is not None


def find_profile_endpoint(
    profile: dict[str, Any], endpoint: str | None, method: str | None
) -> dict[str, Any] | None:
    """Find the declared endpoint configuration corresponding to the job target."""
    api = profile.get("api")
    configured = api.get("endpoints") if isinstance(api, dict) else None
    if not isinstance(configured, list) or not isinstance(endpoint, str) or not isinstance(method, str):
        return None
    for item in configured:
        if (
            isinstance(item, dict)
            and isinstance(item.get("path"), str)
            and isinstance(item.get("method"), str)
            and item["method"].upper() == method.upper()
            and _endpoint_matches(item["path"], endpoint)
        ):
            return item
    return None


def load_registry() -> dict[str, Any]:
    with REGISTRY_PATH.open("r", encoding="utf-8") as source:
        registry = json.load(source)
    if registry.get("schema_version") != "1.0" or not isinstance(registry.get("profiles"), list):
        raise ValueError("Security profile registry must use schema_version 1.0 and a profiles list.")
    return registry


def select_profile(session_state: dict[str, Any]) -> dict[str, Any]:
    """Select exactly one profile whose app, environment and target scope match trusted job state."""
    workload = session_state.get("workload_profile")
    workload = workload if isinstance(workload, dict) else {}
    application = (
        workload.get("application")
        or workload.get("application_name")
        or session_state.get("application_name")
        or session_state.get("application")
    )
    environment = workload.get("environment")
    target_origin = _origin(workload.get("target_url"))
    if not application and target_origin:
        # A host can identify an external target for matching purposes; it
        # does not imply ownership or access to that provider's configuration.
        application = urlsplit(target_origin).hostname
    endpoint = workload.get("endpoint")
    method = workload.get("method")
    if isinstance(method, str):
        method = method.upper()

    registry = load_registry()
    candidates = []
    for profile in registry["profiles"]:
        scope = profile.get("scope", {})
        if not isinstance(scope, dict):
            continue
        if not application or str(scope.get("application", "")).casefold() != str(application).casefold():
            continue
        if scope.get("environment") != environment:
            continue
        if _origin(scope.get("target_origin")) != target_origin:
            continue
        endpoints = scope.get("endpoints", [])
        if not isinstance(endpoints, list):
            continue
        if any(
            isinstance(item, dict)
            and isinstance(item.get("method"), str)
            and item["method"].upper() == method
            and isinstance(item.get("path"), str)
            and isinstance(endpoint, str)
            and _endpoint_matches(item["path"], endpoint)
            for item in endpoints
        ):
            candidates.append(profile)

    if len(candidates) == 1:
        profile = candidates[0]
        return {
            "status": "matched",
            "profile_id": profile.get("profile_id"),
            "profile_version": profile.get("profile_version"),
            "application": profile.get("scope", {}).get("application"),
            "environment": profile.get("scope", {}).get("environment"),
            "data": profile,
        }
    if len(candidates) > 1:
        return {"status": "ambiguous", "reason": "More than one versioned profile matches the trusted application and target scope."}

    if not target_origin:
        reason = "Trusted job context does not provide a valid target origin; no application profile was selected."
    else:
        reason = "No versioned profile matches the trusted application, environment, target origin, endpoint, and method."
    return {"status": "no_match", "reason": reason}

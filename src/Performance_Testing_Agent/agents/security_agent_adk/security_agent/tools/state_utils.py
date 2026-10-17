"""Helpers for reading ADK session state in Security Agent tools."""

from collections.abc import Mapping
from typing import Any


def snapshot_session_state(state: Any) -> dict[str, Any]:
    """Return a plain snapshot from either ADK State or a mapping.

    ADK's State is iterable over keys but is not a Mapping, so ``dict(state)``
    incorrectly treats each key as a key/value pair. Its ``to_dict`` method is
    the supported way to obtain the complete state snapshot.
    """
    to_dict = getattr(state, "to_dict", None)
    if callable(to_dict):
        snapshot = to_dict()
        if isinstance(snapshot, dict):
            return snapshot
        raise TypeError("ADK session state to_dict() did not return a dictionary")

    if isinstance(state, Mapping):
        return dict(state)

    if state is None:
        return {}

    raise TypeError("Unsupported session state object; expected ADK State or a mapping")

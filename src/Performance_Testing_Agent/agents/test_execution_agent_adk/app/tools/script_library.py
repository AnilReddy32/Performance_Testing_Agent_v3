"""Reuse of reviewed REAL scripts across runs of the same catalog test case.

The REAL script builders are deterministic: one trusted workload profile always
renders the same script. This module keeps one stored copy per (runner, catalog
test case) and hands it back only when a fingerprint of everything that shapes
the script still matches and the stored bytes are intact. In every other case
the caller builds the script exactly as before, so reuse can only skip work; it
never changes what is run. It does not replace any safety gate: callers
re-validate a reused script, and the runners still rebuild and compare it
before executing.

Layout, beside (not inside) the per-job folders so retention cleanup, which
only removes JOB-<uuid> folders, never touches it:

    <artifact root>/_script_library/<tool>/<TEST_CASE_ID>/script.<ext>
    <artifact root>/_script_library/<tool>/<TEST_CASE_ID>/script.meta.json

Set SCRIPT_REUSE_ENABLED=false to turn reuse off and restore build-every-run.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import sys
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from Performance_Testing_Agent.execution_context import artifact_root_directory

logger = logging.getLogger(__name__)

LIBRARY_DIRECTORY_NAME = "_script_library"
REUSE_ENV_VARIABLE = "SCRIPT_REUSE_ENABLED"
SOURCE_REUSED = "reused"
SOURCE_GENERATED = "generated"

_FINGERPRINT_VERSION = 1
_CATALOG_TEST_CASE_ID = re.compile(r"(?:PTC|WTC)-\d{3}")
_TEMPLATE_FILES = {"jmeter": "jmeter_template.py", "k6": "k6_template.py"}
_SCRIPT_EXTENSIONS = {"jmeter": ".jmx", "k6": ".js"}
_META_FILENAME = "script.meta.json"
_FALSE_VALUES = {"false", "0", "no", "off"}


def reuse_enabled() -> bool:
    return os.getenv(REUSE_ENV_VARIABLE, "true").strip().lower() not in _FALSE_VALUES


def _eligible(tool: str, test_case_id: str | None) -> bool:
    """Only catalog test cases are reused; anything else builds as before."""
    return (
        reuse_enabled()
        and tool in _TEMPLATE_FILES
        and isinstance(test_case_id, str)
        and _CATALOG_TEST_CASE_ID.fullmatch(test_case_id) is not None
    )


def script_fingerprint(tool: str, test_case_id: str, profile: dict[str, Any]) -> str:
    """Hash everything the rendered script depends on.

    The whole validated profile is included, not just the fields the template
    reads today, so a future template change cannot make a stale script match.
    The template's own source and the Python version (XML serialisation) are
    included for the same reason.
    """
    template_bytes = Path(__file__).with_name(_TEMPLATE_FILES[tool]).read_bytes()
    material = json.dumps(
        {
            "version": _FINGERPRINT_VERSION,
            "tool": tool,
            "test_case_id": test_case_id,
            "profile": profile,
            "template_sha256": hashlib.sha256(template_bytes).hexdigest(),
            "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    return hashlib.sha256(material.encode("ascii")).hexdigest()


def _entry_directory(tool: str, test_case_id: str) -> Path:
    root = artifact_root_directory(tool)
    library = root / LIBRARY_DIRECTORY_NAME
    entry = library / tool / test_case_id
    for part in (library, library / tool, entry):
        if part.is_symlink():
            raise ValueError("The stored-script directory cannot be a symbolic link.")
    if not entry.resolve().is_relative_to(root.resolve()):
        raise ValueError("The stored-script directory is outside the artifact root.")
    return entry


def _load(tool: str, test_case_id: str, fingerprint: str) -> str | None:
    entry = _entry_directory(tool, test_case_id)
    script_path = entry / f"script{_SCRIPT_EXTENSIONS[tool]}"
    meta_path = entry / _META_FILENAME
    if (
        script_path.is_symlink()
        or meta_path.is_symlink()
        or not script_path.is_file()
        or not meta_path.is_file()
    ):
        return None
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if (
        not isinstance(meta, dict)
        or meta.get("tool") != tool
        or meta.get("test_case_id") != test_case_id
        or meta.get("fingerprint") != fingerprint
    ):
        return None
    data = script_path.read_bytes()
    if meta.get("sha256") != hashlib.sha256(data).hexdigest():
        return None
    return data.decode("utf-8")


def _atomic_write(path: Path, data: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        Path(temporary_name).unlink(missing_ok=True)


def _store(tool: str, test_case_id: str, fingerprint: str, content: str) -> None:
    entry = _entry_directory(tool, test_case_id)
    entry.mkdir(parents=True, exist_ok=True)
    data = content.encode("utf-8")
    script_name = f"script{_SCRIPT_EXTENSIONS[tool]}"
    # The script lands first and the metadata last: metadata that does not
    # match the script on disk (a half-finished write) is rejected on load.
    _atomic_write(entry / script_name, data)
    meta = {
        "schema_version": _FINGERPRINT_VERSION,
        "tool": tool,
        "test_case_id": test_case_id,
        "fingerprint": fingerprint,
        "sha256": hashlib.sha256(data).hexdigest(),
        "script_file": script_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _atomic_write(
        entry / _META_FILENAME,
        (json.dumps(meta, indent=2, allow_nan=False) + "\n").encode("utf-8"),
    )


def reuse_or_build(
    tool: str,
    profile: dict[str, Any],
    test_case_id: str | None,
    *,
    build: Callable[[], str],
    verify: Callable[[str], None],
) -> tuple[str, str]:
    """Return (script content, SOURCE_REUSED | SOURCE_GENERATED).

    ``build`` renders the script exactly as it always has. ``verify`` re-runs
    the safety checks the builder would have run and raises if the stored
    script is not acceptable now (e.g. the host allowlist or RPS ceiling
    changed). On any doubt this falls back to ``build`` so its own errors and
    messages are unchanged, then replaces the stored script with the result.
    """
    if not _eligible(tool, test_case_id):
        return build(), SOURCE_GENERATED

    fingerprint: str | None = None
    stored: str | None = None
    try:
        fingerprint = script_fingerprint(tool, test_case_id, profile)
        stored = _load(tool, test_case_id, fingerprint)
    except Exception:  # reuse is an optimisation; never let it break a run
        logger.warning(
            "Stored %s script for %s could not be checked; regenerating.",
            tool,
            test_case_id,
            exc_info=True,
        )

    if stored is not None:
        try:
            verify(stored)
        except Exception as exc:
            logger.info(
                "Stored %s script for %s was not reused: %s",
                tool,
                test_case_id,
                exc,
            )
        else:
            logger.info(
                "Reusing the stored %s script for %s (fingerprint %s): not regenerated.",
                tool, test_case_id, fingerprint[:12],
            )
            return stored, SOURCE_REUSED

    content = build()
    if fingerprint is not None:
        try:
            _store(tool, test_case_id, fingerprint, content)
            logger.info(
                "Generated the %s script for %s and stored it for reuse (fingerprint %s).",
                tool, test_case_id, fingerprint[:12],
            )
        except Exception:
            logger.warning(
                "Could not store the %s script for %s; it was still generated.",
                tool,
                test_case_id,
                exc_info=True,
            )
    return content, SOURCE_GENERATED

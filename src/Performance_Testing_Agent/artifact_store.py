from __future__ import annotations

import json
import os
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from .execution_context import artifact_root_directory

_JOB_ID_PATTERN = re.compile(r"JOB-[0-9a-f]{32}")
_ARTIFACT_KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]{0,63}$")
ARTIFACT_MANIFEST_FILENAME = "artifact_manifest.json"


def _job_directory(job_id: str) -> Path:
    if not isinstance(job_id, str) or not _JOB_ID_PATTERN.fullmatch(job_id):
        raise ValueError("Invalid job ID.")
    root = artifact_root_directory()
    candidate = root / job_id
    if candidate.is_symlink():
        raise ValueError("Artifact job directory must not be a symbolic link.")
    directory = candidate.resolve()
    if directory.parent != root:
        raise ValueError("Artifact job directory must be inside the artifact root.")
    return directory


def artifact_retention_days() -> int:
    raw_value = os.getenv("ARTIFACT_RETENTION_DAYS", "30")
    try:
        days = int(raw_value)
    except ValueError as exc:
        raise ValueError("ARTIFACT_RETENTION_DAYS must be a positive integer.") from exc
    if days < 1:
        raise ValueError("ARTIFACT_RETENTION_DAYS must be a positive integer.")
    return days


def write_artifact_manifest(
    job_id: str,
    execution_mode: str,
    artifacts: dict[str, str],
    *,
    created_at: datetime | None = None,
) -> dict[str, Any]:
    job_directory = _job_directory(job_id)
    job_directory.mkdir(parents=True, exist_ok=True)
    registered: dict[str, str] = {}
    for key, filename in artifacts.items():
        if (
            not isinstance(key, str)
            or not _ARTIFACT_KEY_PATTERN.fullmatch(key)
            or not isinstance(filename, str)
            or not filename
            or Path(filename).name != filename
        ):
            raise ValueError("Artifact manifest contains an invalid key or filename.")
        path = (job_directory / filename).resolve()
        if path.parent != job_directory or not path.is_file():
            raise ValueError(
                f"Artifact '{key}' does not resolve to a file inside its job directory."
            )
        registered[key] = filename

    timestamp = created_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None or timestamp.utcoffset() != timedelta(0):
        raise ValueError("Artifact manifest creation time must be timezone-aware UTC.")
    manifest = {
        "schema_version": "1.0",
        "job_id": job_id,
        "execution_mode": execution_mode,
        "created_at": timestamp.isoformat(),
        "expires_at": (
            timestamp + timedelta(days=artifact_retention_days())
        ).isoformat(),
        "artifacts": registered,
    }
    manifest_path = job_directory / ARTIFACT_MANIFEST_FILENAME
    temporary_path = manifest_path.with_suffix(".json.tmp")
    temporary_path.write_text(
        json.dumps(manifest, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary_path.replace(manifest_path)
    return manifest


def resolve_registered_artifact(
    job_id: str,
    artifact_key: str,
    *,
    now: datetime | None = None,
) -> tuple[Path, datetime]:
    if not _JOB_ID_PATTERN.fullmatch(job_id):
        raise ValueError("Invalid job ID.")
    if not _ARTIFACT_KEY_PATTERN.fullmatch(artifact_key):
        raise ValueError("Invalid artifact key.")
    job_directory = _job_directory(job_id)
    manifest_path = job_directory / ARTIFACT_MANIFEST_FILENAME
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FileNotFoundError("Artifact manifest is unavailable.") from exc
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") != "1.0"
        or manifest.get("job_id") != job_id
        or not isinstance(manifest.get("artifacts"), dict)
    ):
        raise ValueError("Artifact manifest is invalid.")
    expires_at_value = manifest.get("expires_at")
    if not isinstance(expires_at_value, str):
        raise ValueError("Artifact manifest has no valid expiration time.")
    try:
        expires_at = datetime.fromisoformat(expires_at_value)
    except ValueError as exc:
        raise ValueError("Artifact manifest has an invalid expiration time.") from exc
    if expires_at.tzinfo is None or expires_at.utcoffset() != timedelta(0):
        raise ValueError("Artifact manifest expiration must be UTC.")

    filename = manifest["artifacts"].get(artifact_key)
    if not isinstance(filename, str) or Path(filename).name != filename:
        raise FileNotFoundError("Artifact key is not registered for this job.")
    artifact_path = (job_directory / filename).resolve()
    if artifact_path.parent != job_directory or not artifact_path.is_file():
        raise FileNotFoundError("Registered artifact file is unavailable.")
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        raise ValueError("Artifact access time must be timezone-aware.")
    if current_time.astimezone(timezone.utc) >= expires_at:
        raise TimeoutError("Artifact retention period has expired.")
    return artifact_path, expires_at


def purge_expired_artifact_directories(
    *,
    now: datetime | None = None,
) -> list[str]:
    current_time = now or datetime.now(timezone.utc)
    if current_time.tzinfo is None:
        raise ValueError("Cleanup time must be timezone-aware.")
    current_time = current_time.astimezone(timezone.utc)
    artifact_root = artifact_root_directory()
    if not artifact_root.exists():
        return []
    expired_job_ids: list[str] = []
    for job_directory in artifact_root.iterdir():
        if (
            not _JOB_ID_PATTERN.fullmatch(job_directory.name)
            or job_directory.is_symlink()
            or not job_directory.is_dir()
            or job_directory.resolve().parent != artifact_root
        ):
            continue
        manifest_path = job_directory / ARTIFACT_MANIFEST_FILENAME
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            expires_at = datetime.fromisoformat(manifest["expires_at"])
        except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
            continue
        if (
            not isinstance(manifest, dict)
            or manifest.get("job_id") != job_directory.name
            or expires_at.tzinfo is None
            or expires_at.utcoffset() != timedelta(0)
            or current_time < expires_at
        ):
            continue
        shutil.rmtree(job_directory)
        expired_job_ids.append(job_directory.name)
    return expired_job_ids


__all__ = [
    "ARTIFACT_MANIFEST_FILENAME",
    "artifact_retention_days",
    "purge_expired_artifact_directories",
    "resolve_registered_artifact",
    "write_artifact_manifest",
]

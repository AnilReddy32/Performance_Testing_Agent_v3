"""Status-code evidence from the performance run's own requests.

The load test already sent real traffic to the target. If the target throttled
it (HTTP 429), that is evidence of rate limiting that costs no extra requests.
Only the raw result file recorded for this job is read, and only from inside
the job's artifact directory.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from security_agent.passive.config import MAX_TRAFFIC_RECORDS
from security_agent.passive.models import TrafficEvidence

_STATUS_CODE = re.compile(r"[1-5]\d\d")
_MAX_DISTINCT_CODES = 12
_RAW_SUFFIXES = {"k6": "_raw.json", "jmeter": "_results.jtl"}


def _job_directory(state: Mapping[str, Any]) -> Path | None:
    directory = state.get("execution_artifact_directory")
    if not isinstance(directory, str) or not directory.strip():
        return None
    try:
        resolved = Path(directory).expanduser().resolve()
    except (OSError, RuntimeError):
        return None
    return resolved if resolved.is_dir() else None


def _raw_results_path(state: Mapping[str, Any], tool: str, job_dir: Path) -> Path | None:
    candidates: list[Path] = []
    manifest = state.get("execution_artifacts")
    if isinstance(manifest, Mapping) and manifest.get("job_id") == state.get("job_id"):
        artifacts = manifest.get("artifacts")
        raw = artifacts.get("raw_results") if isinstance(artifacts, Mapping) else None
        if isinstance(raw, str) and raw.strip():
            path = Path(raw)
            candidates.append(path if path.is_absolute() else job_dir / path)
    suffix = _RAW_SUFFIXES.get(tool)
    if suffix:
        candidates.extend(sorted(job_dir.glob(f"*{suffix}")))
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            continue
        if resolved.is_file() and resolved.is_relative_to(job_dir):
            return resolved
    return None


def _top(counter: Counter) -> dict[str, int]:
    return dict(counter.most_common(_MAX_DISTINCT_CODES))


def _read_k6(path: Path) -> TrafficEvidence:
    statuses: Counter = Counter()
    tls_versions: set[str] = set()
    total = records = 0
    truncated = False
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            records += 1
            if records > MAX_TRAFFIC_RECORDS:
                truncated = True
                break
            if '"http_reqs"' not in line or '"Point"' not in line:
                continue
            try:
                tags = json.loads(line)["data"]["tags"]
            except (ValueError, KeyError, TypeError):
                continue
            total += 1
            status = str(tags.get("status", ""))
            if _STATUS_CODE.fullmatch(status):
                statuses[status] += 1
            version = tags.get("tls_version")
            if isinstance(version, str) and version:
                tls_versions.add(version[:20])
    return TrafficEvidence(
        source=path.name,
        total_requests=total,
        status_counts=_top(statuses),
        tls_versions=tuple(sorted(tls_versions)),
        truncated=truncated,
    )


def _read_jmeter(path: Path) -> TrafficEvidence:
    statuses: Counter = Counter()
    total = 0
    truncated = False
    with path.open("r", encoding="utf-8", errors="replace", newline="") as handle:
        for row in csv.DictReader(handle):
            total += 1
            if total > MAX_TRAFFIC_RECORDS:
                truncated = True
                total -= 1
                break
            code = str(row.get("responseCode", "")).strip()
            if _STATUS_CODE.fullmatch(code):
                statuses[code] += 1
    return TrafficEvidence(
        source=path.name,
        total_requests=total,
        status_counts=_top(statuses),
        truncated=truncated,
    )


def read_run_traffic(state: Mapping[str, Any]) -> TrafficEvidence | None:
    """Return the run's status-code distribution, or None when unavailable."""
    profile = state.get("workload_profile")
    tool = profile.get("tool") if isinstance(profile, Mapping) else None
    if tool not in _RAW_SUFFIXES:
        return None
    job_dir = _job_directory(state)
    if job_dir is None:
        return None
    path = _raw_results_path(state, tool, job_dir)
    if path is None:
        return None
    try:
        evidence = _read_k6(path) if tool == "k6" else _read_jmeter(path)
    except (OSError, csv.Error, UnicodeError):
        return None
    return evidence if evidence.total_requests > 0 else None

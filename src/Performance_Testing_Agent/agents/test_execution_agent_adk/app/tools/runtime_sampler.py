"""Timestamped host resource sampling for REAL load-test runs."""

from __future__ import annotations

import csv
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psutil


_SAMPLE_FIELDS = (
    "timestamp",
    "elapsed_seconds",
    "cpu_percent",
    "memory_percent",
    "measurement_scope",
    "data_source",
    "target_resource_metric",
)


class RuntimeMetricsSampler:
    """Collect host-wide CPU and memory while k6 is running.

    These are measurements of the host running the load generator, not
    target-application resource metrics.
    """

    def __init__(
        self,
        output_path: Path,
        *,
        sample_interval_seconds: float = 1.0,
    ) -> None:
        if sample_interval_seconds <= 0:
            raise ValueError("The sample interval must be positive.")
        self.output_path = output_path
        self.sample_interval_seconds = sample_interval_seconds
        self.sample_count = 0
        self.sampling_error: str | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._start_monotonic: float | None = None
        self.started_at: datetime | None = None
        self.stopped_at: datetime | None = None
        self._file: Any = None
        self._writer: csv.DictWriter | None = None
        self._write_lock = threading.Lock()

    def start(self) -> None:
        if self._thread is not None:
            raise RuntimeError("The runtime metrics sampler has already started.")
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.output_path.open(
            "w",
            newline="",
            encoding="utf-8",
        )
        self._writer = csv.DictWriter(self._file, fieldnames=_SAMPLE_FIELDS)
        self._writer.writeheader()
        self._file.flush()

        self._start_monotonic = time.monotonic()
        self.started_at = datetime.now(timezone.utc)
        psutil.cpu_percent(interval=None)
        self._thread = threading.Thread(
            target=self._sample_loop,
            name="runtime-metrics-sampler",
            daemon=True,
        )
        self._thread.start()

    def _sample_loop(self) -> None:
        assert self._start_monotonic is not None
        assert self._writer is not None
        assert self._file is not None
        try:
            while not self._stop_event.wait(self.sample_interval_seconds):
                cpu_percent = psutil.cpu_percent(interval=None)
                memory_percent = psutil.virtual_memory().percent
                if self._stop_event.is_set():
                    break
                sample_time = datetime.now(timezone.utc)
                elapsed_seconds = time.monotonic() - self._start_monotonic
                with self._write_lock:
                    self._writer.writerow(
                        {
                            "timestamp": sample_time.isoformat(),
                            "elapsed_seconds": round(elapsed_seconds, 3),
                            "cpu_percent": cpu_percent,
                            "memory_percent": memory_percent,
                            "measurement_scope": "load_generator_host",
                            "data_source": "psutil",
                            "target_resource_metric": "false",
                        }
                    )
                    self._file.flush()
                    self.sample_count += 1
        except (csv.Error, OSError, psutil.Error, RuntimeError, ValueError) as exc:
            self.sampling_error = f"{type(exc).__name__}: {exc}"

    def stop(self) -> dict[str, Any]:
        if self._thread is None:
            return {
                "sample_count": 0,
                "sampling_error": "The runtime metrics sampler was not started.",
                "sample_interval_seconds": self.sample_interval_seconds,
                "sampler_started_at": None,
                "sampler_stopped_at": None,
            }
        self.stopped_at = datetime.now(timezone.utc)
        self._stop_event.set()
        self._thread.join(timeout=self.sample_interval_seconds + 1.0)
        if self._thread.is_alive():
            self.sampling_error = "Runtime metrics sampler did not stop in time."
        if self._file is not None:
            self._file.close()
            self._file = None
        self._thread = None
        return {
            "sample_count": self.sample_count,
            "sampling_error": self.sampling_error,
            "sample_interval_seconds": self.sample_interval_seconds,
            "sampler_started_at": (
                self.started_at.isoformat() if self.started_at else None
            ),
            "sampler_stopped_at": self.stopped_at.isoformat(),
        }


__all__ = ["RuntimeMetricsSampler"]

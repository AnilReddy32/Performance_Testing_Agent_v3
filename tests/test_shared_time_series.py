import csv
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_EXECUTION_AGENT_ROOT = (
    PROJECT_ROOT
    / "src"
    / "Performance_Testing_Agent"
    / "agents"
    / "test_execution_agent_adk"
)
if str(TEST_EXECUTION_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_EXECUTION_AGENT_ROOT))

from app.tools.time_series import (
    TIME_SERIES_BUCKET_SECONDS,
    TIME_SERIES_FIELDS,
    TIME_SERIES_SCHEMA_VERSION,
    write_aligned_time_series,
)


class TestSharedTimeSeries(unittest.TestCase):
    def test_aligns_sources_to_run_relative_five_second_buckets(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            run_started_at = datetime(
                2026,
                10,
                15,
                3,
                0,
                3,
                tzinfo=timezone.utc,
            )
            run_finished_at = run_started_at + timedelta(seconds=12)
            execution_path = directory / "execution.csv"
            monitoring_path = directory / "monitoring.csv"
            aligned_path = directory / "aligned.csv"
            with execution_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(
                    output,
                    fieldnames=[
                        "timestamp",
                        "elapsed_seconds",
                        "requests",
                        "successful_requests",
                        "failed_requests",
                        "avg_response_time_ms",
                        "throughput_rps",
                    ],
                )
                writer.writeheader()
                writer.writerows(
                    [
                        {
                            "timestamp": (run_started_at + timedelta(seconds=0)).isoformat(),
                            "elapsed_seconds": 0,
                            "requests": 10,
                            "successful_requests": 9,
                            "failed_requests": 1,
                            "avg_response_time_ms": 100,
                            "throughput_rps": 2,
                        },
                        {
                            "timestamp": (run_started_at + timedelta(seconds=5)).isoformat(),
                            "elapsed_seconds": 5,
                            "requests": 20,
                            "successful_requests": 20,
                            "failed_requests": 0,
                            "avg_response_time_ms": 200,
                            "throughput_rps": 4,
                        },
                    ]
                )
            with monitoring_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(
                    output,
                    fieldnames=[
                        "timestamp",
                        "elapsed_seconds",
                        "cpu_percent",
                        "memory_percent",
                        "measurement_scope",
                        "data_source",
                        "target_resource_metric",
                    ],
                )
                writer.writeheader()
                for elapsed, cpu, memory in ((1, 20, 40), (4, 40, 60), (6, 80, 90)):
                    writer.writerow(
                        {
                            "timestamp": (
                                run_started_at + timedelta(seconds=elapsed)
                            ).isoformat(),
                            "elapsed_seconds": elapsed,
                            "cpu_percent": cpu,
                            "memory_percent": memory,
                            "measurement_scope": "load_generator_host",
                            "data_source": "psutil",
                            "target_resource_metric": "false",
                        }
                    )

            bucket_count = write_aligned_time_series(
                execution_time_series_path=execution_path,
                monitoring_samples_path=monitoring_path,
                output_path=aligned_path,
                run_started_at=run_started_at,
                run_finished_at=run_finished_at,
            )

            with aligned_path.open(encoding="utf-8", newline="") as aligned_file:
                reader = csv.DictReader(aligned_file)
                rows = list(reader)
                self.assertEqual(tuple(reader.fieldnames or ()), TIME_SERIES_FIELDS)

        self.assertEqual(TIME_SERIES_SCHEMA_VERSION, "1.0")
        self.assertEqual(TIME_SERIES_BUCKET_SECONDS, 5)
        self.assertEqual(bucket_count, 3)
        self.assertEqual(len(rows), 3)
        self.assertEqual([int(row["elapsed_seconds"]) for row in rows], [0, 5, 10])
        self.assertEqual([float(row["bucket_duration_seconds"]) for row in rows], [5, 5, 2])
        self.assertEqual([int(row["requests"]) for row in rows], [10, 20, 0])
        self.assertEqual(float(rows[0]["throughput_rps"]), 2)
        self.assertEqual(float(rows[1]["throughput_rps"]), 4)
        self.assertEqual(float(rows[2]["throughput_rps"]), 0)
        self.assertEqual(float(rows[0]["cpu_avg_percent"]), 30)
        self.assertEqual(float(rows[0]["cpu_peak_percent"]), 40)
        self.assertEqual(float(rows[0]["memory_avg_percent"]), 50)
        self.assertEqual(float(rows[1]["cpu_avg_percent"]), 80)
        self.assertEqual(rows[2]["monitoring_data_source"], "")
        self.assertEqual(rows[0]["execution_measurement_scope"], "load_generator_observed_http_traffic")
        self.assertEqual(rows[0]["monitoring_measurement_scope"], "load_generator_host")
        self.assertEqual(rows[0]["target_resource_metrics"], "false")

    def test_partial_bucket_throughput_matches_serialized_duration(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            run_started_at = datetime(2026, 10, 15, tzinfo=timezone.utc)
            execution_path = directory / "execution.csv"
            monitoring_path = directory / "monitoring.csv"
            aligned_path = directory / "aligned.csv"
            with execution_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(
                    output,
                    fieldnames=[
                        "timestamp",
                        "elapsed_seconds",
                        "requests",
                        "successful_requests",
                        "failed_requests",
                        "avg_response_time_ms",
                        "throughput_rps",
                    ],
                )
                writer.writeheader()
                writer.writerow(
                    {
                        "timestamp": (
                            run_started_at + timedelta(seconds=6)
                        ).isoformat(),
                        "elapsed_seconds": 6,
                        "requests": 1,
                        "successful_requests": 1,
                        "failed_requests": 0,
                        "avg_response_time_ms": 10,
                        "throughput_rps": 1,
                    }
                )
            with monitoring_path.open("w", encoding="utf-8", newline="") as output:
                writer = csv.DictWriter(
                    output,
                    fieldnames=[
                        "timestamp",
                        "elapsed_seconds",
                        "cpu_percent",
                        "memory_percent",
                        "measurement_scope",
                        "data_source",
                        "target_resource_metric",
                    ],
                )
                writer.writeheader()

            write_aligned_time_series(
                execution_time_series_path=execution_path,
                monitoring_samples_path=monitoring_path,
                output_path=aligned_path,
                run_started_at=run_started_at,
                run_finished_at=run_started_at + timedelta(seconds=6.123456),
            )

            with aligned_path.open(encoding="utf-8", newline="") as aligned_file:
                rows = list(csv.DictReader(aligned_file))

        final_duration = float(rows[-1]["bucket_duration_seconds"])
        final_throughput = float(rows[-1]["throughput_rps"])
        self.assertAlmostEqual(final_duration, 1.123456, places=6)
        self.assertAlmostEqual(final_throughput, 1 / final_duration, places=6)


if __name__ == "__main__":
    unittest.main()

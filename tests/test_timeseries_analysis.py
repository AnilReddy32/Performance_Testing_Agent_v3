import csv
import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_APP_PATH = (
    PROJECT_ROOT
    / "src"
    / "Performance_Testing_Agent"
    / "agents"
    / "Analysis_Report_agent_adk"
    / "app"
    / "agents"
    / "analysis"
)
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))


def _register_package(package_name: str, package_path: Path):
    module = types.ModuleType(package_name)
    module.__path__ = [str(package_path)]
    module.__package__ = package_name
    sys.modules[package_name] = module


def _load_submodule(package_name: str, module_name: str, path: Path):
    full_name = f"{package_name}.{module_name}"
    spec = importlib.util.spec_from_file_location(full_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module


_register_package("timeseries_analysis_under_test", ANALYSIS_APP_PATH)
analysis_schemas = _load_submodule(
    "timeseries_analysis_under_test",
    "schemas",
    ANALYSIS_APP_PATH / "schemas.py",
)
analysis_tools = _load_submodule(
    "timeseries_analysis_under_test",
    "tools",
    ANALYSIS_APP_PATH / "tools.py",
)


class ToolContextStub:
    def __init__(self, state):
        self.state = state


class TestTimeSeriesAnalysis(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.job_id = "JOB-1234567890abcdef1234567890abcdef"
        self.job_directory = Path(self.temporary_directory.name) / self.job_id
        self.job_directory.mkdir()
        self.environment = patch.dict(
            os.environ,
            {"EXECUTION_ARTIFACTS_ROOT": self.temporary_directory.name},
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.run_started_at = datetime(
            2026,
            10,
            15,
            0,
            0,
            tzinfo=timezone.utc,
        )

    def _state(
        self,
        *,
        cpu_values=(20, 35, 50, 65, 80),
        memory_values=(30, 35, 40, 45, 50),
    ):
        series_name = "aligned.csv"
        metadata_name = "measurement_metadata.json"
        fields = [
            "timestamp",
            "elapsed_seconds",
            "bucket_duration_seconds",
            "requests",
            "successful_requests",
            "failed_requests",
            "avg_response_time_ms",
            "throughput_rps",
            "cpu_avg_percent",
            "cpu_peak_percent",
            "memory_avg_percent",
            "memory_peak_percent",
            "execution_data_source",
            "execution_measurement_scope",
            "monitoring_data_source",
            "monitoring_measurement_scope",
            "target_resource_metrics",
        ]
        observations = [
            (10, 0, 100),
            (20, 0, 125),
            (30, 1, 150),
            (40, 2, 175),
            (50, 5, 200),
        ]
        with (self.job_directory / series_name).open(
            "w",
            encoding="utf-8",
            newline="",
        ) as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            for index, (requests, failed, latency) in enumerate(observations):
                writer.writerow(
                    {
                        "timestamp": (
                            self.run_started_at
                            + timedelta(seconds=index * 5)
                        ).isoformat(),
                        "elapsed_seconds": index * 5,
                        "bucket_duration_seconds": 5,
                        "requests": requests,
                        "successful_requests": requests - failed,
                        "failed_requests": failed,
                        "avg_response_time_ms": latency,
                        "throughput_rps": requests / 5,
                        "cpu_avg_percent": cpu_values[index],
                        "cpu_peak_percent": min(cpu_values[index] + 2, 100),
                        "memory_avg_percent": memory_values[index],
                        "memory_peak_percent": min(memory_values[index] + 2, 100),
                        "execution_data_source": "k6",
                        "execution_measurement_scope": (
                            "load_generator_observed_http_traffic"
                        ),
                        "monitoring_data_source": "psutil",
                        "monitoring_measurement_scope": "load_generator_host",
                        "target_resource_metrics": "false",
                    }
                )
        (self.job_directory / metadata_name).write_text(
            json.dumps(
                {
                    "job_id": self.job_id,
                    "k6_run_window": {
                        "started_at": self.run_started_at.isoformat(),
                        "finished_at": (
                            self.run_started_at + timedelta(seconds=25)
                        ).isoformat(),
                    },
                    "shared_time_series": {
                        "schema_version": "1.0",
                        "bucket_seconds": 5,
                        "alignment_origin": "k6_run_window.started_at",
                    },
                }
            ),
            encoding="utf-8",
        )
        return {
            "job_id": self.job_id,
            "execution_mode": "REAL",
            "workload_profile": {"ramp_up_seconds": 10},
            "execution_artifacts": {
                "job_id": self.job_id,
                "execution_mode": "REAL",
                "artifacts": {
                    "aligned_time_series": series_name,
                    "measurement_metadata": metadata_name,
                },
            },
        }

    def test_deterministic_trends_correlation_load_and_post_ramp_degradation(self):
        result = analysis_tools.analyze_timeseries(
            ToolContextStub(self._state())
        )

        self.assertEqual(result["status"], "analyzed")
        self.assertEqual(
            result["provenance"]["execution_mode"],
            "REAL",
        )
        self.assertEqual(
            result["provenance"]["time_series"]["data_source"],
            "k6",
        )
        self.assertEqual(
            result["provenance"]["time_series"]["measurement_scope"],
            "load_generator_observed_http_traffic",
        )
        self.assertEqual(
            result["provenance"]["monitoring"]["data_source"],
            "psutil",
        )
        self.assertFalse(
            result["provenance"]["monitoring"]["target_resource_metrics"]
        )
        self.assertTrue(result["findings"])
        self.assertTrue(
            all(finding["execution_mode"] == "REAL" for finding in result["findings"])
        )
        self.assertIn("k6", result["findings"][0]["data_sources"])
        self.assertIn(
            "workload_profile",
            next(
                finding["data_sources"]
                for finding in result["findings"]
                if finding["category"] == "post_ramp_degradation"
            ),
        )
        self.assertEqual(result["bucket_count"], 5)
        self.assertEqual(result["latency"]["change_percentage"], 100)
        self.assertEqual(
            result["errors"]["first_rising_error_elapsed_seconds"],
            10,
        )
        self.assertEqual(
            result["errors"]["rising_error_buckets"][0]["throughput_rps"],
            6,
        )
        self.assertEqual(
            result["load"]["throughput_change_percentage"],
            400,
        )
        self.assertGreater(
            result["resource_correlation"][
                "latency_vs_load_generator_cpu_pearson"
            ],
            0.99,
        )
        self.assertGreater(
            result["resource_correlation"][
                "latency_vs_load_generator_memory_pearson"
            ],
            0.99,
        )
        self.assertTrue(result["degradation_after_ramp_up"]["degraded"])
        self.assertEqual(
            result["degradation_after_ramp_up"]["comparison_status"],
            "compared",
        )
        self.assertEqual(
            result["resource_correlation"]["interpretation"].split(";")[0],
            "Correlations are descriptive associations with host-wide "
            "load-generator resources",
        )

        finalized = analysis_tools.finalize_analysis(
            job_id=self.job_id,
            application="Payments",
            scenario="Peak traffic",
            quality_report={"status": "valid", "issues": []},
            time_series_analysis=result,
        )
        self.assertEqual(finalized["overall_status"], "warning")
        self.assertEqual(finalized["time_series_analysis"], result)
        analysis_schemas.AnalysisOutput(**finalized)

    def test_constant_host_resource_values_omit_undefined_correlations(self):
        result = analysis_tools.analyze_timeseries(
            ToolContextStub(
                self._state(cpu_values=(50, 50, 50, 50, 50))
            )
        )

        self.assertEqual(result["status"], "analyzed")
        self.assertIsNone(
            result["resource_correlation"][
                "latency_vs_load_generator_cpu_pearson"
            ]
        )

    def test_simulated_mode_is_explicitly_unavailable(self):
        result = analysis_tools.analyze_timeseries(
            ToolContextStub({"execution_mode": "SIMULATED"})
        )

        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["execution_mode"], "SIMULATED")
        self.assertEqual(
            result["provenance"]["execution_mode"],
            "SIMULATED",
        )
        self.assertEqual(
            result["provenance"]["time_series"]["data_source"],
            "simulated_estimate",
        )
        self.assertEqual(
            result["provenance"]["time_series"]["measurement_scope"],
            "simulated_estimate",
        )
        self.assertFalse(result["findings"])
        self.assertIn("No time-series measurements", result["provenance"]["note"])
        self.assertIn("requires an aligned REAL", result["reason"])
        finalized = analysis_tools.finalize_analysis(
            job_id=self.job_id,
            application="Payments",
            scenario="Simulated test",
            quality_report={"status": "valid", "issues": []},
            time_series_analysis=result,
        )
        self.assertEqual(
            finalized["time_series_analysis"]["provenance"]["execution_mode"],
            "SIMULATED",
        )
        analysis_schemas.AnalysisOutput(**finalized)

    def test_misaligned_utc_timestamp_is_rejected(self):
        state = self._state()
        series_path = self.job_directory / "aligned.csv"
        with series_path.open("r", encoding="utf-8", newline="") as source:
            rows = list(csv.DictReader(source))
            fields = rows[0].keys()
        rows[1]["timestamp"] = (
            self.run_started_at + timedelta(seconds=6)
        ).isoformat()
        with series_path.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

        result = analysis_tools.analyze_timeseries(ToolContextStub(state))

        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["provenance"]["execution_mode"], "REAL")
        self.assertIsNone(result["provenance"]["time_series"]["data_source"])
        self.assertIn("timestamp is not UTC-aligned", result["reason"])

    def test_final_analysis_carries_only_safe_execution_profile_and_artifacts(self):
        state = self._state()
        state["workload_profile"] = {
            "tool": "k6",
            "target_url": "http://127.0.0.1:8000",
            "endpoint": "/payments",
            "method": "POST",
            "users": 5,
            "max_rps": 10,
            "duration_seconds": 30,
            "ramp_up_seconds": 5,
            "credentials_ref": "secret-reference",
            "payload_template": {"card_number": "must-not-be-copied"},
        }
        state["execution_artifacts"]["artifacts"].update(
            {
                "native_report": "native_report.html",
                "raw_results": "raw_results.json",
            }
        )
        time_series_analysis = analysis_tools.analyze_timeseries(
            ToolContextStub(state)
        )

        finalized = analysis_tools.finalize_analysis(
            job_id=self.job_id,
            application="Payments",
            scenario="Peak traffic",
            quality_report={"status": "valid", "issues": []},
            time_series_analysis=time_series_analysis,
        )

        self.assertEqual(finalized["execution_mode"], "REAL")
        self.assertEqual(finalized["execution_profile"]["tool"], "k6")
        self.assertEqual(finalized["execution_profile"]["users"], 5)
        self.assertNotIn("credentials_ref", finalized["execution_profile"])
        self.assertNotIn("payload_template", finalized["execution_profile"])
        self.assertTrue(
            finalized["execution_artifact_directory"].endswith(self.job_id)
        )
        self.assertEqual(
            finalized["execution_artifacts"]["native_report"],
            "native_report.html",
        )
        self.assertEqual(
            finalized["execution_artifacts"]["raw_results"],
            "raw_results.json",
        )
        analysis_schemas.AnalysisOutput(**finalized)


if __name__ == "__main__":
    unittest.main()

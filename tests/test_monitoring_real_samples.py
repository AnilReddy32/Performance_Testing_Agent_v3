import csv
import asyncio
import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MONITORING_APP_PATH = (
    PROJECT_ROOT
    / "src"
    / "Performance_Testing_Agent"
    / "agents"
    / "monitoring_agent_adk"
    / "app"
)
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
REPORT_APP_PATH = (
    PROJECT_ROOT
    / "src"
    / "Performance_Testing_Agent"
    / "agents"
    / "Analysis_Report_agent_adk"
    / "app"
    / "agents"
    / "report"
)
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))


def _register_package(package_name: str, package_path: Path):
    module = types.ModuleType(package_name)
    module.__path__ = [str(package_path)]
    module.__package__ = package_name
    sys.modules[package_name] = module
    return module


def _load_submodule(package_name: str, module_name: str, path: Path):
    full_name = f"{package_name}.{module_name}"
    spec = importlib.util.spec_from_file_location(full_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[full_name] = module
    spec.loader.exec_module(module)
    return module


_register_package("monitoring_agent_under_test", MONITORING_APP_PATH)
_load_submodule(
    "monitoring_agent_under_test",
    "metric_simulator",
    MONITORING_APP_PATH / "metric_simulator.py",
)
monitoring_agent = _load_submodule(
    "monitoring_agent_under_test",
    "agent",
    MONITORING_APP_PATH / "agent.py",
)
_register_package("analysis_tools_under_test", ANALYSIS_APP_PATH)
analysis_schemas = _load_submodule(
    "analysis_tools_under_test",
    "schemas",
    ANALYSIS_APP_PATH / "schemas.py",
)
analysis_tools = _load_submodule(
    "analysis_tools_under_test",
    "tools",
    ANALYSIS_APP_PATH / "tools.py",
)
_register_package("report_agent_under_test", REPORT_APP_PATH.parent.parent)
_register_package(
    "report_agent_under_test.agents",
    REPORT_APP_PATH.parent,
)
_register_package(
    "report_agent_under_test.agents.analysis",
    ANALYSIS_APP_PATH,
)
_register_package("report_agent_under_test.agents.report", REPORT_APP_PATH)
_load_submodule(
    "report_agent_under_test.agents.analysis",
    "schemas",
    ANALYSIS_APP_PATH / "schemas.py",
)
_load_submodule(
    "report_agent_under_test.agents.report",
    "schemas",
    REPORT_APP_PATH / "schemas.py",
)
report_tools = _load_submodule(
    "report_agent_under_test.agents.report",
    "tools",
    REPORT_APP_PATH / "tools.py",
)


class ToolContextStub:
    def __init__(self, state):
        self.state = state

    async def save_artifact(self, filename, artifact):
        return 0


class TestMonitoringRealSamples(unittest.TestCase):
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

    def _state(self, samples_name="runtime_samples.csv"):
        samples_path = self.job_directory / samples_name
        with samples_path.open("w", encoding="utf-8", newline="") as output:
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
            for timestamp, cpu, memory in (
                ("2026-10-15T00:00:01+00:00", 20, 40),
                ("2026-10-15T00:00:02+00:00", 60, 80),
            ):
                writer.writerow(
                    {
                        "timestamp": timestamp,
                        "elapsed_seconds": 1,
                        "cpu_percent": cpu,
                        "memory_percent": memory,
                        "measurement_scope": "load_generator_host",
                        "data_source": "psutil",
                        "target_resource_metric": "false",
                    }
                )
        (self.job_directory / "measurement_metadata.json").write_text(
            json.dumps(
                {
                    "job_id": self.job_id,
                    "sources": {
                        "runtime_samples": {
                            "status": "available",
                            "data_source": "psutil",
                            "measurement_scope": "load_generator_host",
                            "target_resource_metrics": False,
                            "sample_count": 2,
                            "sampling_error": None,
                        }
                    },
                }
            ),
            encoding="utf-8",
        )
        return {
            "job_id": self.job_id,
            "execution_mode": "REAL",
            "execution_status": "completed",
            "test_execution_result": {
                "job_id": self.job_id,
                "application": "Payments",
                "scenario": "Payment test",
                "avg_response_time": 125.5,
                "throughput": 4.5,
            },
            "execution_artifacts": {
                "job_id": self.job_id,
                "execution_mode": "REAL",
                "artifacts": {
                    "monitoring_samples": samples_name,
                    "measurement_metadata": "measurement_metadata.json",
                },
            },
        }

    def test_real_run_uses_samples_and_preserves_metric_provenance(self):
        state = self._state()

        with patch.object(
            monitoring_agent,
            "simulate_monitoring_metrics",
            side_effect=AssertionError("REAL monitoring must not simulate"),
        ):
            result = monitoring_agent.collect_monitoring_metrics(
                ToolContextStub(state)
            )

        self.assertIs(result, state["monitoring_result"])
        self.assertEqual(result["execution_mode"], "REAL")
        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["cpu_usage"], 40)
        self.assertEqual(result["cpu_peak_usage"], 60)
        self.assertEqual(result["memory_usage"], 60)
        self.assertEqual(result["memory_peak_usage"], 80)
        self.assertIsNone(result["db_connections"])
        self.assertEqual(result["response_time"], 125.5)
        self.assertEqual(result["tps"], 4.5)
        self.assertEqual(result["sample_count"], 2)
        self.assertEqual(
            result["measurement_provenance"]["cpu_usage"]["measurement_scope"],
            "load_generator_host",
        )
        self.assertFalse(
            result["measurement_provenance"]["cpu_usage"][
                "target_resource_metric"
            ]
        )
        self.assertEqual(
            result["measurement_provenance"]["db_connections"]["status"],
            "not_collected",
        )
        analyzed = analysis_tools.analyze_infra_health(
            result,
            test_execution_avg_response_time=125.5,
        )
        self.assertEqual(analyzed["cpu_peak_usage"], 60)
        self.assertEqual(analyzed["memory_peak_usage"], 80)
        self.assertEqual(analyzed["data_source"], result["data_source"])
        analysis_schemas.InfraHealthFinding(**analyzed)
        report = report_tools.build_report_sections(
            job_id=self.job_id,
            application="Payments",
            scenario="Payment test",
            data_quality_status="valid",
            unusable_reason=None,
            overall_status="pass",
            api_findings=[],
            infra_health=analyzed,
            security_summary=None,
            summary="Monitoring collected host samples.",
        )
        monitoring_row = next(
            row
            for row in next(
                section
                for section in report["sections"]
                if section["title"] == "Agent Activity Summary"
            )["table_rows"]
            if row[0] == "Monitoring"
        )
        self.assertIn("REAL: psutil", monitoring_row[1])
        self.assertIn("load_generator_host", monitoring_row[1])
        self.assertIn("not collected", monitoring_row[1])

    def test_report_sections_include_execution_mode_profile_and_artifact_paths(self):
        native_report = self.job_directory / "native_report.html"
        raw_results = self.job_directory / "raw_results.json"
        native_report.write_text("<html>Dashboard</html>", encoding="utf-8")
        raw_results.write_text('{"requests": 3}\n', encoding="utf-8")
        result = report_tools.build_report_sections(
            job_id=self.job_id,
            application="Payments",
            scenario="Payment test",
            data_quality_status="valid",
            unusable_reason=None,
            overall_status="pass",
            api_findings=[],
            infra_health=None,
            security_summary=None,
            summary="Completed.",
            execution_mode="REAL",
            execution_profile={
                "tool": "k6",
                "users": 5,
                "duration_seconds": 30,
            },
            execution_artifact_directory=(
                f"src/generated_scripts/k6 native reports/{self.job_id}"
            ),
            execution_artifacts={
                "native_report": native_report.name,
                "raw_results": raw_results.name,
            },
            time_series_analysis={
                "status": "analyzed",
                "execution_mode": "REAL",
                "series": [
                    {
                        "elapsed_seconds": 0,
                        "avg_response_time_ms": 100,
                        "throughput_rps": 2,
                        "cpu_avg_percent": 25,
                    },
                    {
                        "elapsed_seconds": 5,
                        "avg_response_time_ms": 150,
                        "throughput_rps": 4,
                        "cpu_avg_percent": 55,
                    },
                ],
            },
        )

        section = next(
            section
            for section in result["sections"]
            if section["title"] == "Execution Profile and Artifacts"
        )
        self.assertIn("Execution mode: REAL", section["content"])
        self.assertIn("tool: k6", section["content"])
        self.assertIn("users: 5", section["content"])
        self.assertIn(
            f'<link href="/artifacts/{self.job_id}/native_report">',
            section["content"],
        )
        self.assertIn(
            f'<link href="/artifacts/{self.job_id}/raw_results">',
            section["content"],
        )
        archive_path = self.job_directory / f"{self.job_id}_native_report.zip"
        self.assertIn(
            f'<link href="/artifacts/{self.job_id}/native_report_archive">',
            section["content"],
        )
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(
                set(archive.namelist()),
                {
                    "native_report/native_report.html",
                    "raw_results/raw_results.json",
                },
            )
            self.assertEqual(
                archive.read("native_report/native_report.html"),
                b"<html>Dashboard</html>",
            )
            self.assertEqual(
                archive.read("raw_results/raw_results.json"),
                b'{"requests": 3}\n',
            )
            chart_section = next(
                section
                for section in result["sections"]
                if section["title"] == "Time-Series Charts (REAL Measurements)"
            )
            self.assertEqual(len(chart_section["charts"]), 3)
            self.assertEqual(
                [chart["title"] for chart in chart_section["charts"]],
                [
                    "Response latency over time",
                    "Throughput over time",
                    "Load-generator host CPU over time",
                ],
            )
            reports_directory = Path(self.temporary_directory.name) / "reports"
            with patch.object(report_tools, "REPORTS_DIR", str(reports_directory)):
                pdf_path = asyncio.run(
                    report_tools.render_pdf_report(
                        self.job_id,
                        [section, chart_section],
                        ToolContextStub({}),
                    )
                )
        pdf_bytes = (
            reports_directory / f"{self.job_id}_report.pdf"
        ).read_bytes()
        self.assertIn(b"/URI", pdf_bytes)
        self.assertIn(
            f"/artifacts/{self.job_id}/native_report".encode(),
            pdf_bytes,
        )

    def test_report_packaging_rejects_artifact_path_traversal(self):
        with self.assertRaisesRegex(ValueError, "safe job-local path"):
            report_tools.build_report_sections(
                job_id=self.job_id,
                application="Payments",
                scenario="Payment test",
                data_quality_status="valid",
                unusable_reason=None,
                overall_status="pass",
                api_findings=[],
                infra_health=None,
                security_summary=None,
                summary="Completed.",
                execution_mode="REAL",
                execution_artifacts={
                    "native_report": "../outside.html",
                    "raw_results": "raw_results.json",
                },
            )

    def test_partial_real_samples_are_explicitly_labelled(self):
        state = self._state()
        metadata_path = self.job_directory / "measurement_metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata["sources"]["runtime_samples"].update(
            status="partial",
            sampling_error="RuntimeError: sampler stopped early",
        )
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

        result = monitoring_agent.collect_monitoring_metrics(
            ToolContextStub(state)
        )

        self.assertEqual(result["sampling_status"], "partial")
        self.assertIn("REAL (partial)", result["data_source"])
        self.assertEqual(
            result["sampling_error"],
            "RuntimeError: sampler stopped early",
        )

    def test_missing_real_samples_are_unavailable_not_simulated(self):
        state = self._state()
        (self.job_directory / "runtime_samples.csv").unlink()

        with patch.object(
            monitoring_agent,
            "simulate_monitoring_metrics",
            side_effect=AssertionError("REAL monitoring must not simulate"),
        ):
            result = monitoring_agent.collect_monitoring_metrics(
                ToolContextStub(state)
            )

        self.assertEqual(result["status"], "UNAVAILABLE")
        self.assertEqual(result["execution_mode"], "REAL")
        self.assertIsNone(result["cpu_usage"])
        self.assertIn("could not be read", result["message"])
        infra_result = analysis_tools.analyze_infra_health(
            result,
            test_execution_avg_response_time=125.5,
        )
        self.assertEqual(infra_result["status"], "warning")
        self.assertIsNone(infra_result["cpu_usage"])
        self.assertIn("Monitoring data was unavailable", infra_result["anomalies"][0])
        analysis_schemas.InfraHealthFinding(**infra_result)

    def test_simulated_run_keeps_simulator_and_identifies_estimates(self):
        state = {
            "execution_mode": "SIMULATED",
            "test_execution_result": {
                "job_id": self.job_id,
                "application": "Payments",
                "scenario": "Payment test",
                "error_rate": 0,
                "avg_response_time": 100,
                "throughput": 2,
            },
        }

        result = monitoring_agent.collect_monitoring_metrics(
            ToolContextStub(state)
        )

        self.assertEqual(result["execution_mode"], "SIMULATED")
        self.assertEqual(result["measurement_scope"], "simulated_estimate")
        self.assertIn("simulated", result["data_source"].lower())
        self.assertTrue(
            all(
                entry["measurement_scope"] == "simulated_estimate"
                for entry in result["measurement_provenance"].values()
            )
        )


if __name__ == "__main__":
    unittest.main()

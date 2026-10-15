import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from google.adk.sessions.state import State


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

from app.tools import k6_runner, script_generation
from app.agent import run_test_execution_adk
from app.analysis_agent.handoff import prepare_analysis_handoff


class TestRealK6Runner(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.job_id = "JOB-0123456789abcdef0123456789abcdef"
        self.job_directory = Path(self.temporary_directory.name) / self.job_id
        self.profile = {
            "tool": "k6",
            "target_url": "http://localhost:8000",
            "environment": "mock_api",
            "endpoint": "/api/payment",
            "method": "POST",
            "payload_template": {"transaction_id": "run-{{__VU}}-{{__ITER}}"},
            "expected_status_code": 200,
            "expected_response_time_ms": 750,
            "p95_threshold_ms": 750,
            "users": 1,
            "max_rps": 10,
            "duration_seconds": 4,
            "ramp_up_seconds": 1,
            "credentials_ref": "none",
        }
        self.environment = patch.dict(
            os.environ,
            {
                "EXECUTION_ARTIFACTS_ROOT": self.temporary_directory.name,
                "REAL_EXECUTION_ENABLED": "true",
                "REAL_EXECUTION_ALLOWED_HOSTS": "localhost,127.0.0.1",
                "REAL_EXECUTION_ALLOWED_PORTS": "8000",
                "REAL_EXECUTION_MAX_USERS": "500",
                "REAL_EXECUTION_MAX_DURATION_SECONDS": "500",
                "REAL_EXECUTION_MAX_RAMP_UP_SECONDS": "90",
            },
            clear=True,
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)
        dns_patch = patch(
            "Performance_Testing_Agent.execution_context.socket.getaddrinfo",
            return_value=[(None, None, None, None, ("127.0.0.1", 8000))],
        )
        dns_patch.start()
        self.addCleanup(dns_patch.stop)
        generated = script_generation.generate_script(
            tool="k6",
            application="Payments",
            scenario="Payment API Load Test",
            api_name="Payment API",
            execution_mode="REAL",
            workload_profile=self.profile,
            job_id=self.job_id,
            artifact_directory=str(self.job_directory),
            test_case_id="PTC-001",
            test_case_name="Payment API Load Test",
        )
        self.script_path = Path(generated["file_path"])

    def test_threshold_breach_is_completed_with_native_and_raw_artifacts(self):
        raw_samples = [
            {
                "type": "Point",
                "metric": "http_reqs",
                "data": {
                    "time": "2026-01-01T00:00:01Z",
                    "value": 1,
                    "tags": {"status": "500"},
                },
            },
            {
                "type": "Point",
                "metric": "http_req_failed",
                "data": {
                    "time": "2026-01-01T00:00:01Z",
                    "value": 1,
                    "tags": {"status": "500"},
                },
            },
            {
                "type": "Point",
                "metric": "http_req_duration",
                "data": {
                    "time": "2026-01-01T00:00:01Z",
                    "value": 500,
                    "tags": {"status": "500"},
                },
            },
        ]
        summary = {
            "metrics": {
                "http_reqs": {
                    "count": 1,
                    "rate": 0.25,
                    "thresholds": {"rate>10": False},
                },
                "http_req_duration": {
                    "avg": 500,
                    "p(95)": 400,
                    "max": 600,
                },
                "http_req_failed": {
                    "fails": 1,
                    "passes": 0,
                    "value": 1,
                    "thresholds": {"rate<0.01": False},
                },
            }
        }

        def fake_run(command, **kwargs):
            if command[1] == "inspect":
                return type(
                    "CompletedProcess",
                    (),
                    {"returncode": 0, "stdout": "script inspected", "stderr": ""},
                )()
            self.assertEqual(command[command.index("--rps") + 1], "10")
            raw_path = Path(command[command.index("--out") + 1].removeprefix("json="))
            summary_path = Path(
                command[command.index("--summary-export") + 1]
            )
            for sample in raw_samples:
                sample["data"]["time"] = datetime.now(
                    timezone.utc
                ).isoformat()
            raw_path.write_text(
                "".join(json.dumps(item) + "\n" for item in raw_samples),
                encoding="utf-8",
            )
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            Path(kwargs["env"]["K6_WEB_DASHBOARD_EXPORT"]).write_text(
                "<html>native dashboard</html>",
                encoding="utf-8",
            )
            return type(
                "CompletedProcess",
                (),
                {"returncode": 99, "stdout": "threshold breached", "stderr": ""},
            )()

        with (
            patch.object(k6_runner.shutil, "which", return_value="/usr/bin/k6"),
            patch.object(k6_runner.subprocess, "run", side_effect=fake_run),
        ):
            result = k6_runner.run_real_k6_test(
                job_id=self.job_id,
                profile_data=self.profile,
                artifact_directory=str(self.job_directory),
                script_path=str(self.script_path),
                test_case_id="PTC-001",
                application="Payments",
                scenario="Payment API Load Test",
                api_name="Payment API",
            )

        self.assertEqual(result["status"], "completed")
        self.assertFalse(result["thresholds_passed"])
        self.assertEqual(result["metrics"]["total_requests"], 1)
        self.assertEqual(result["metrics"]["failed_requests"], 1)
        self.assertEqual(result["metrics"]["http_status"], 500)
        self.assertEqual(result["metrics"]["avg_response_time"], 500)
        self.assertEqual(result["metrics"]["p95_response_time"], 400)
        self.assertFalse(
            result["measurement_sources"]["runtime_samples"][
                "target_resource_metrics"
            ]
        )
        self.assertEqual(
            result["measurement_sources"]["runtime_samples"]["measurement_scope"],
            "load_generator_host",
        )
        self.assertFalse(
            result["measurement_sources"]["k6_time_series"][
                "target_resource_metrics"
            ]
        )
        self.assertEqual(set(prepare_analysis_handoff(result["metrics"])), {
            "job_id",
            "application",
            "scenario",
            "api_name",
            "total_requests",
            "successful_requests",
            "failed_requests",
            "avg_response_time",
            "p95_response_time",
            "max_response_time",
            "throughput",
            "error_rate",
            "http_status",
        })
        for artifact_key in (
            "raw_results",
            "k6_summary",
            "normalized_metrics",
            "time_series",
            "aligned_time_series",
            "monitoring_samples",
            "measurement_metadata",
            "native_report",
            "runner_log",
        ):
            self.assertIn(artifact_key, result["artifacts"])
            self.assertTrue(
                (self.job_directory / result["artifacts"][artifact_key]).is_file()
            )
        measurement_metadata = json.loads(
            (
                self.job_directory
                / result["artifacts"]["measurement_metadata"]
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(
            measurement_metadata["sources"], result["measurement_sources"]
        )

    def test_modified_script_is_rejected_before_k6_runs(self):
        self.script_path.write_text("// modified script\n", encoding="utf-8")
        with (
            patch.object(k6_runner.shutil, "which", return_value="/usr/bin/k6"),
            patch.object(k6_runner.subprocess, "run") as run,
        ):
            result = k6_runner.run_real_k6_test(
                job_id=self.job_id,
                profile_data=self.profile,
                artifact_directory=str(self.job_directory),
                script_path=str(self.script_path),
                test_case_id="PTC-001",
                application="Payments",
                scenario="Payment API Load Test",
                api_name="Payment API",
            )

        self.assertEqual(result["status"], "failed")
        self.assertIn("no longer matches", result["message"])
        run.assert_not_called()

    def _real_agent_state(self):
        return {
            "job_id": self.job_id,
            "execution_mode": "REAL",
            "execution_preflight": {"status": "ready"},
            "workload_profile": self.profile,
            "execution_artifact_directory": str(self.job_directory),
            "execution_artifacts": {
                "job_id": self.job_id,
                "execution_mode": "REAL",
                "artifacts": {"native_report": "old-run/report.html"},
            },
            "test_case_id": "PTC-001",
            "test_case_name": "Payment API Load Test",
            "test_execution_result": {"job_id": "old-run"},
            "monitoring_result": {"job_id": "old-run"},
            "security_result": {"job_id": "old-run"},
            "analysis_result": {"job_id": "old-run"},
            "report_result": {"job_id": "old-run"},
        }

    def test_completed_threshold_breach_is_handed_to_analysis(self):
        state = self._real_agent_state()
        metrics = {
            "job_id": self.job_id,
            "application": "Payments",
            "scenario": "Payment API Load Test",
            "api_name": "Payment API",
            "total_requests": 100,
            "successful_requests": 90,
            "failed_requests": 10,
            "avg_response_time": 500,
            "p95_response_time": 1200,
            "max_response_time": 1500,
            "throughput": 10,
            "error_rate": 10.0,
            "http_status": 500,
        }
        execution_result = {
            "status": "completed",
            "execution_mode": "REAL",
            "job_id": self.job_id,
            "thresholds_passed": False,
            "metrics": metrics,
            "artifacts": {"raw_results": "run_raw.json"},
        }

        with (
            patch(
                "app.agent.generate_script",
                return_value={
                    "status": "success",
                    "message": "script prepared",
                    "file_path": str(self.script_path),
                    "artifact_path": self.script_path.name,
                },
            ),
            patch(
                "app.agent.run_real_k6_test",
                return_value=execution_result,
            ),
        ):
            result = run_test_execution_adk(
                "Run the test and analyze results",
                type(
                    "ToolContextStub",
                    (),
                    {"state": State(state, {})},
                )(),
            )

        self.assertEqual(result["status"], "completed")
        self.assertFalse(result["thresholds_passed"])
        self.assertEqual(state["execution_status"], "completed")
        self.assertEqual(state["test_execution_result"], metrics)
        self.assertEqual(state["execution_stage_result"]["metrics"], metrics)
        self.assertNotIn(
            "old-run/report.html",
            state["execution_artifacts"]["artifacts"].values(),
        )
        for stale_key in (
            "monitoring_result",
            "security_result",
            "analysis_result",
            "report_result",
        ):
            self.assertIsNone(state[stale_key])

    def test_k6_script_request_runs_real_by_default(self):
        state = self._real_agent_state()
        execution_result = {
            "status": "completed",
            "execution_mode": "REAL",
            "job_id": self.job_id,
            "thresholds_passed": True,
            "metrics": {"job_id": self.job_id, "total_requests": 10},
            "artifacts": {"native_report": "run_native.html"},
        }

        with (
            patch(
                "app.agent.generate_script",
                return_value={
                    "status": "success",
                    "message": "script prepared",
                    "file_path": str(self.script_path),
                    "artifact_path": self.script_path.name,
                },
            ),
            patch(
                "app.agent.run_real_k6_test",
                return_value=execution_result,
            ) as run_real,
        ):
            result = run_test_execution_adk(
                "Generate a k6 script for the payment API",
                type(
                    "ToolContextStub",
                    (),
                    {"state": State(state, {})},
                )(),
            )

        self.assertEqual(result["status"], "completed")
        run_real.assert_called_once()

    def test_k6_request_without_profile_does_not_use_simulated_runner(self):
        state = {}
        with patch("app.agent.handle_test_request") as simulate:
            result = run_test_execution_adk(
                "Generate and run a k6 script",
                type(
                    "ToolContextStub",
                    (),
                    {"state": State(state, {})},
                )(),
            )

        self.assertEqual(result["execution_mode"], "REAL")
        self.assertEqual(result["status"], "needs_input")
        self.assertIn("tool", result["missing_inputs"])
        simulate.assert_not_called()

    def test_jmeter_request_uses_simulated_path_even_in_real_session(self):
        state = self._real_agent_state()
        with patch(
            "app.agent.handle_test_request",
            return_value={"status": "success", "tool": "jmeter"},
        ) as simulate:
            result = run_test_execution_adk(
                "Generate a JMeter test plan",
                type(
                    "ToolContextStub",
                    (),
                    {"state": State(state, {})},
                )(),
            )

        self.assertEqual(result["tool"], "jmeter")
        self.assertEqual(state["execution_mode"], "SIMULATED")
        self.assertIsNone(state["monitoring_result"])
        self.assertIsNone(state["analysis_result"])
        simulate.assert_called_once()

    def test_runner_failure_is_execution_error_and_clears_stale_metrics(self):
        state = self._real_agent_state()
        execution_result = {
            "status": "failed",
            "execution_mode": "REAL",
            "job_id": self.job_id,
            "message": "k6 crashed",
            "artifacts": {"runner_log": "run_runner.log"},
        }

        with (
            patch(
                "app.agent.generate_script",
                return_value={
                    "status": "success",
                    "message": "script prepared",
                    "file_path": str(self.script_path),
                    "artifact_path": self.script_path.name,
                },
            ),
            patch(
                "app.agent.run_real_k6_test",
                return_value=execution_result,
            ),
        ):
            result = run_test_execution_adk(
                "Run the test and analyze results",
                type(
                    "ToolContextStub",
                    (),
                    {"state": State(state, {})},
                )(),
            )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["message"], "k6 crashed")
        self.assertEqual(state["execution_status"], "failed")
        self.assertIsNone(state["test_execution_result"])
        self.assertNotIn(
            "old-run/report.html",
            state["execution_artifacts"]["artifacts"].values(),
        )
        for stale_key in (
            "test_execution_result",
            "monitoring_result",
            "security_result",
            "analysis_result",
            "report_result",
        ):
            self.assertIsNone(state[stale_key])


if __name__ == "__main__":
    unittest.main()

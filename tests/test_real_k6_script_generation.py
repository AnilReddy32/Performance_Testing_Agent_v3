import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


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

from app.tools import script_generation


class TestRealK6ScriptGeneration(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.job_id = "JOB-0123456789abcdef0123456789abcdef"
        self.job_directory = Path(self.temp_directory.name) / self.job_id
        self.profile = {
            "tool": "k6",
            "target_url": "http://localhost:8000",
            "environment": "mock_api",
            "endpoint": "/api/payment",
            "method": "POST",
            "payload_template": {
                "transaction_id": "test-{{__VU}}-{{__ITER}}",
                "amount": 10.5,
            },
            "expected_status_code": 201,
            "expected_response_time_ms": 750,
            "p95_threshold_ms": 750,
            "users": 20,
            "max_rps": 10,
            "duration_seconds": 30,
            "ramp_up_seconds": 5,
            "credentials_ref": "none",
        }
        self.environment = patch.dict(
            os.environ,
            {
                "EXECUTION_ARTIFACTS_ROOT": self.temp_directory.name,
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

    def test_real_k6_uses_reviewed_template_and_job_directory(self):
        with patch.object(
            script_generation,
            "ArtifactGenerator",
            side_effect=AssertionError("REAL scripts must not use the LLM."),
        ):
            result = script_generation.generate_script(
                tool="k6",
                application="Payments",
                scenario="Payment load test",
                api_name="Payment API",
                execution_mode="REAL",
                workload_profile=self.profile,
                job_id=self.job_id,
                artifact_directory=str(self.job_directory),
                test_case_id="PTC-001",
                test_case_name="Payment API Load Test",
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["execution_status"], "prepared")
        self.assertEqual(
            result["artifact_path"],
            "k6_PTC_001_Payment_API_Load_Test.js",
        )
        self.assertEqual(
            Path(result["file_path"]),
            self.job_directory.resolve() / "k6_PTC_001_Payment_API_Load_Test.js",
        )

        script = Path(result["file_path"]).read_text(encoding="utf-8")
        self.assertIn("stages: [{\"duration\":\"5s\",\"target\":20}", script)
        self.assertIn("{\"duration\":\"20s\",\"target\":20}", script)
        self.assertIn("{\"duration\":\"5s\",\"target\":0}", script)
        self.assertIn("p(95)<750", script)
        self.assertIn("rps: 10", script)
        self.assertIn("rate<0.01", script)
        self.assertIn("EXPECTED_STATUS = 201", script)
        self.assertIn("METHOD = \"POST\"", script)
        self.assertIn('ENDPOINT = "/api/payment"', script)
        self.assertIn(
            "BODY_TEMPLATE = \"{\\\"transaction_id\\\":\\\"test-{{__VU}}-{{__ITER}}\\\",\\\"amount\\\":10.5}\"",
            script,
        )
        self.assertIn(".replace(/\\{\\{__VU\\}\\}/g, String(__VU))", script)
        self.assertIn(".replace(/\\{\\{__ITER\\}\\}/g, String(__ITER))", script)
        self.assertIn("__ENV.AUTHORIZATION_HEADER", script)
        self.assertNotIn("credentials_ref", script)
        self.assertIn("redirects: 0", script)
        self.assertNotIn("http://localhost", script)

    def test_real_k6_rejects_missing_profile_values_without_calling_llm(self):
        incomplete_profile = dict(self.profile)
        incomplete_profile.pop("payload_template")

        with patch.object(
            script_generation,
            "ArtifactGenerator",
            side_effect=AssertionError("REAL scripts must not use the LLM."),
        ):
            result = script_generation.generate_script(
                tool="k6",
                application="Payments",
                scenario="Payment load test",
                api_name="Payment API",
                execution_mode="REAL",
                workload_profile=incomplete_profile,
                job_id=self.job_id,
                artifact_directory=str(self.job_directory),
                test_case_id="PTC-001",
                test_case_name="Payment API Load Test",
            )

        self.assertEqual(result["status"], "error")
        self.assertIn("payload_template", result["message"])
        self.assertFalse(self.job_directory.exists())

    def test_simulated_k6_generation_still_uses_existing_generator(self):
        with patch.object(
            script_generation,
            "ArtifactGenerator",
        ) as generator:
            with patch.object(
                script_generation,
                "GENERATED_SCRIPTS_DIR",
                self.temp_directory.name,
            ):
                generator.return_value.generate_script.return_value = "simulated-script"
                result = script_generation.generate_script(
                    tool="k6",
                    application="Payments",
                    scenario="Payment load test",
                    api_name="Payment API",
                )

        self.assertEqual(result["status"], "success")
        generator.return_value.generate_script.assert_called_once()

    def test_real_k6_script_name_uses_catalog_title(self):
        result = script_generation.generate_script(
            tool="k6",
            application="Payments",
            scenario="Script Generation",
            api_name="Payment API",
            execution_mode="REAL",
            workload_profile=self.profile,
            job_id=self.job_id,
            artifact_directory=str(self.job_directory),
            test_case_id="PTC-011",
            test_case_name="Local Mock Payment API — k6 Script Generation",
        )

        self.assertEqual(
            result["file_name"],
            "k6_PTC_011_Local_Mock_Payment_API_k6_Script_Generation.js",
        )


if __name__ == "__main__":
    unittest.main()

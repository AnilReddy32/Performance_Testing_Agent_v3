import os
import unittest
from unittest.mock import patch

from Performance_Testing_Agent.execution_context import (
    WorkloadProfile,
    artifact_directory_reference,
    create_context_for_test_case,
    create_execution_job_context,
    is_k6_test_request,
    is_jmeter_test_request,
    is_simulated_tool_request,
    missing_profile_inputs,
    real_execution_gate,
    requested_execution_tool,
    validate_real_profile,
    validate_target_url,
    workload_profile_from_test_case,
)
from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case


class TestWorkloadProfile(unittest.TestCase):
    def test_k6_test_script_requests_select_real_execution(self):
        self.assertTrue(
            is_k6_test_request("Generate a k6 script for the payment API")
        )
        self.assertTrue(is_k6_test_request("Run the k6 workload"))
        self.assertTrue(is_jmeter_test_request("Generate a JMeter test plan"))
        self.assertFalse(is_simulated_tool_request("Generate a JMeter test plan"))
        self.assertTrue(is_simulated_tool_request("Run the Gatling workload"))
        self.assertFalse(is_k6_test_request("Generate a JMeter test plan"))
        self.assertFalse(is_k6_test_request("Generate a Gatling simulation"))
        self.assertFalse(is_simulated_tool_request("Generate a k6 script"))
        self.assertEqual(
            requested_execution_tool(
                "Run test case PTC-001 using JMeter; this case normally uses k6"
            ),
            "jmeter",
        )
        self.assertEqual(
            requested_execution_tool("Run test case PTC-001 using k6"),
            "k6",
        )
        with self.assertRaisesRegex(ValueError, "either k6 or JMeter"):
            requested_execution_tool(
                "Run the k6 test and the JMeter test for PTC-001"
            )

    def test_adapts_existing_catalog_fields_without_guessing_missing_values(self):
        profile = workload_profile_from_test_case(
            {
                "endpoint": "/api/payment",
                "method": "post",
                "virtual_users": 200,
                "duration_seconds": 50,
                "ramp_up_seconds": 20,
                "expected_status_code": 200,
            }
        )

        self.assertEqual(profile.method, "POST")
        self.assertEqual(profile.endpoint, "/api/payment")
        self.assertEqual(profile.users, 200)
        self.assertEqual(profile.tool, None)
        self.assertEqual(profile.target_url, None)
        self.assertIn("credentials_ref", missing_profile_inputs(profile))
        self.assertIn("payload_template", missing_profile_inputs(profile))

    def test_unknown_profile_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            workload_profile_from_test_case(
                {"workload_profile": {"target": "http://localhost:8000"}}
            )

    def test_simulated_context_keeps_existing_path_and_has_artifact_contract(self):
        context = create_execution_job_context()

        self.assertEqual(context["execution_mode"], "SIMULATED")
        self.assertEqual(context["execution_preflight"]["status"], "not_required")
        self.assertEqual(context["execution_status"], "not_started")
        self.assertEqual(context["execution_artifacts"]["artifacts"], {})
        self.assertEqual(
            context["execution_artifacts"]["execution_mode"],
            "SIMULATED",
        )
        self.assertTrue(context["execution_artifact_directory"].endswith(context["job_id"]))

    def test_default_job_artifacts_live_under_generated_scripts(self):
        with patch.dict(
            os.environ,
            {"REAL_EXECUTION_ENABLED": "false"},
            clear=True,
        ):
            context = create_execution_job_context()

        self.assertTrue(
            context["execution_artifact_directory"].endswith(
                f"/src/generated_scripts/k6 native reports/{context['job_id']}"
            )
        )
        self.assertTrue(
            artifact_directory_reference(context["job_id"]).startswith(
                "src/generated_scripts/k6 native reports/"
            )
        )

    def test_catalog_case_defaults_to_simulated(self):
        context = create_context_for_test_case(
            {
                "test_case_id": "PTC-002",
                "name": "Login API Load Test",
                "endpoint": "/api/login",
                "method": "GET",
            }
        )
        self.assertEqual(context["execution_mode"], "SIMULATED")
        self.assertEqual(context["test_case_name"], "Login API Load Test")

    def test_catalog_exposes_normalized_profile_and_explicit_mode(self):
        case = get_test_case("PTC-001")

        self.assertEqual(case["execution_mode"], "REAL")
        self.assertEqual(case["workload_profile"]["endpoint"], "/api/users/23")
        self.assertEqual(case["workload_profile"]["users"], 1)
        self.assertEqual(case["workload_profile"]["target_url"], "https://reqres.in")

    def test_real_report_case_has_complete_capped_profile(self):
        case = get_test_case("PTC-012")

        self.assertEqual(case["execution_mode"], "REAL")
        self.assertEqual(
            case["name"],
            "Local Mock Payment API — Capped k6 Report Run",
        )
        self.assertEqual(case["workload_profile"]["tool"], "k6")
        self.assertEqual(case["workload_profile"]["users"], 10)
        self.assertEqual(case["workload_profile"]["max_rps"], 5)
        self.assertEqual(case["workload_profile"]["duration_seconds"], 50)
        self.assertEqual(case["workload_profile"]["ramp_up_seconds"], 10)

    def test_real_profile_requests_missing_inputs(self):
        profile = WorkloadProfile(
            tool="k6",
            endpoint="/api/payment",
            method="POST",
            users=10,
            duration_seconds=30,
            ramp_up_seconds=5,
            expected_response_time_ms=500,
            p95_threshold_ms=500,
            expected_status_code=200,
            credentials_ref="none",
        )

        result = validate_real_profile(profile)

        self.assertEqual(result["status"], "needs_input")
        self.assertEqual(
            result["missing_inputs"],
            ["target_url", "environment", "max_rps", "payload_template"],
        )

    def test_real_execution_gate_requests_missing_values_without_running(self):
        result = real_execution_gate(
            {
                "job_id": "JOB-0123456789abcdef0123456789abcdef",
                "execution_preflight": {
                    "status": "needs_input",
                    "missing_inputs": ["target_url"],
                },
            }
        )

        self.assertEqual(result["status"], "needs_input")
        self.assertEqual(result["missing_inputs"], ["target_url"])
        self.assertEqual(result["artifacts"], {})

    def test_real_execution_gate_rejects_ready_preflight_without_profile(self):
        result = real_execution_gate(
            {
                "job_id": "JOB-0123456789abcdef0123456789abcdef",
                "execution_preflight": {
                    "status": "ready",
                    "missing_inputs": [],
                    "blocked_reasons": [],
                },
            }
        )

        self.assertEqual(result["status"], "blocked")
        self.assertIn("No simulated fallback", result["message"])
        self.assertIn("valid workload profile", result["blocked_reasons"][0])

    def test_real_profile_enforces_configured_caps(self):
        profile = WorkloadProfile(
            tool="k6",
            target_url="http://127.0.0.1:8000",
            environment="mock_api",
            endpoint="/api/payment",
            method="GET",
            users=501,
            max_rps=10,
            duration_seconds=501,
            ramp_up_seconds=91,
            p95_threshold_ms=500,
            expected_status_code=200,
            credentials_ref="none",
        )

        with (
            patch.dict(
                os.environ,
                {
                    "REAL_EXECUTION_ENABLED": "true",
                    "REAL_EXECUTION_MAX_USERS": "500",
                    "REAL_EXECUTION_MAX_DURATION_SECONDS": "500",
                    "REAL_EXECUTION_MAX_RAMP_UP_SECONDS": "90",
                    "REAL_EXECUTION_ALLOWED_HOSTS": "localhost,127.0.0.1",
                    "REAL_EXECUTION_ALLOWED_PORTS": "8000",
                },
                clear=True,
            ),
            patch(
                "Performance_Testing_Agent.execution_context.socket.getaddrinfo",
                return_value=[(None, None, None, None, ("127.0.0.1", 8000))],
            ),
        ):
            result = validate_real_profile(profile)

        self.assertEqual(result["status"], "rejected")
        self.assertEqual(len(result["blocked_reasons"]), 3)

    def test_real_mode_stays_blocked_until_explicitly_enabled(self):
        profile = WorkloadProfile(
            tool="k6",
            target_url="http://localhost:8000",
            environment="mock_api",
            endpoint="/api/payment",
            method="GET",
            users=10,
            max_rps=10,
            duration_seconds=30,
            ramp_up_seconds=5,
            p95_threshold_ms=500,
            expected_status_code=200,
            credentials_ref="none",
        )

        with (
            patch.dict(
                os.environ,
                {
                    "REAL_EXECUTION_ENABLED": "false",
                    "REAL_EXECUTION_ALLOWED_HOSTS": "localhost,127.0.0.1",
                    "REAL_EXECUTION_ALLOWED_PORTS": "8000",
                },
                clear=True,
            ),
            patch(
                "Performance_Testing_Agent.execution_context.socket.getaddrinfo",
                return_value=[(None, None, None, None, ("127.0.0.1", 8000))],
            ),
        ):
            result = validate_real_profile(profile)

        self.assertEqual(result["status"], "blocked")
        self.assertIn("REAL_EXECUTION_ENABLED is false", result["blocked_reasons"][0])

    def test_target_requires_allowlisted_local_host_and_port(self):
        with patch(
            "Performance_Testing_Agent.execution_context.socket.getaddrinfo",
            return_value=[(None, None, None, None, ("::1", 8000, 0, 0))],
        ):
            self.assertEqual(
                validate_target_url("http://localhost:8000"),
                [],
            )
            rejected = validate_target_url("http://example.com:8000")

        self.assertTrue(any("not in REAL_EXECUTION_ALLOWED_HOSTS" in x for x in rejected))

    def test_target_rejects_non_loopback_resolution(self):
        with patch(
            "Performance_Testing_Agent.execution_context.socket.getaddrinfo",
            return_value=[(None, None, None, None, ("192.0.2.10", 8000))],
        ):
            errors = validate_target_url("http://localhost:8000")

        self.assertTrue(any("non-loopback" in error for error in errors))

    def test_target_rejects_other_port_and_embedded_credentials(self):
        errors = validate_target_url("http://operator@localhost:9000")

        self.assertIn("target_url must not include embedded credentials.", errors)
        self.assertTrue(any("Target port 9000" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

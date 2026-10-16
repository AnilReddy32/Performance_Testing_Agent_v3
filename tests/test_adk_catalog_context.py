import os
import tempfile
import unittest
from unittest.mock import patch

from Performance_Testing_Agent.orchestrator.tools import (
    bind_explicit_catalog_case,
    load_catalog_test_case,
)


class TestAdkCatalogContext(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
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

    def test_loads_real_job_context_from_selected_catalog_case(self):
        state = {}
        result = load_catalog_test_case(
            " ptc-012 ",
            type("ToolContextStub", (), {"state": state})(),
        )

        self.assertEqual(result["status"], "loaded")
        self.assertEqual(result["execution_mode"], "REAL")
        self.assertEqual(result["preflight"]["status"], "ready")
        self.assertEqual(state["test_case_id"], "PTC-012")
        self.assertEqual(
            state["test_case_name"],
            "Local Mock Payment API — Capped k6 Report Run",
        )
        self.assertEqual(state["workload_profile"]["max_rps"], 5)
        self.assertEqual(state["execution_source_id"], "ADK_WEB")

    def test_rejects_case_conflicting_with_existing_session_context(self):
        state = {
            "job_id": "JOB-0123456789abcdef0123456789abcdef",
            "test_case_id": "PTC-011",
            "execution_mode": "REAL",
        }

        with self.assertRaisesRegex(ValueError, "different trusted test case"):
            load_catalog_test_case(
                "PTC-012",
                type("ToolContextStub", (), {"state": state})(),
            )

        self.assertEqual(state["test_case_id"], "PTC-011")

    def test_case_selection_replaces_an_unbound_needs_input_job(self):
        state = {
            "job_id": "JOB-0123456789abcdef0123456789abcdef",
            "execution_status": "needs_input",
            "test_execution_result": None,
        }

        result = load_catalog_test_case(
            "PTC-012",
            type("ToolContextStub", (), {"state": state})(),
        )

        self.assertEqual(result["status"], "loaded")
        self.assertEqual(state["test_case_id"], "PTC-012")
        self.assertNotEqual(state["job_id"], "JOB-0123456789abcdef0123456789abcdef")
        self.assertEqual(state["execution_preflight"]["status"], "ready")

    def test_case_selection_cannot_replace_an_active_job(self):
        state = {
            "job_id": "JOB-0123456789abcdef0123456789abcdef",
            "execution_status": "running",
        }

        with self.assertRaisesRegex(ValueError, "active or unrecognized"):
            load_catalog_test_case(
                "PTC-012",
                type("ToolContextStub", (), {"state": state})(),
            )

    def test_before_agent_callback_binds_case_id_from_adk_web_request(self):
        state = {
            "job_id": "JOB-0123456789abcdef0123456789abcdef",
            "execution_status": "needs_input",
        }
        callback_context = type(
            "CallbackContextStub",
            (),
            {
                "state": state,
                "user_content": type(
                    "ContentStub",
                    (),
                    {
                        "parts": [
                            type(
                                "PartStub",
                                (),
                                {"text": "Run test case PTC-012"},
                            )()
                        ]
                    },
                )(),
            },
        )()

        bind_explicit_catalog_case(callback_context)

        self.assertEqual(state["test_case_id"], "PTC-012")
        self.assertEqual(state["execution_mode"], "REAL")
        self.assertEqual(state["execution_preflight"]["status"], "ready")

    def test_same_catalog_id_can_select_both_real_runners(self):
        state = {}
        callback_context = type(
            "CallbackContextStub",
            (),
            {
                "state": state,
                "user_content": type(
                    "ContentStub",
                    (),
                    {
                        "parts": [
                            type(
                                "PartStub",
                                (),
                                {"text": "Run test case PTC-012 using JMeter"},
                            )()
                        ]
                    },
                )(),
            },
        )()

        bind_explicit_catalog_case(callback_context)
        self.assertEqual(state["test_case_id"], "PTC-012")
        self.assertEqual(state["workload_profile"]["tool"], "jmeter")
        self.assertEqual(state["execution_mode"], "REAL")
        self.assertEqual(state["execution_preflight"]["status"], "ready")

        callback_context.user_content.parts[0].text = (
            "Run test case PTC-012 using k6"
        )
        bind_explicit_catalog_case(callback_context)
        self.assertEqual(state["test_case_id"], "PTC-012")
        self.assertEqual(state["workload_profile"]["tool"], "k6")
        self.assertEqual(state["execution_mode"], "REAL")
        self.assertEqual(state["execution_preflight"]["status"], "ready")

    def test_unknown_catalog_id_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "Unknown test case ID"):
            load_catalog_test_case(
                "PTC-999",
                type("ToolContextStub", (), {"state": {}})(),
            )


if __name__ == "__main__":
    unittest.main()

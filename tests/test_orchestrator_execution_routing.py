import unittest
import os
from types import SimpleNamespace
from unittest.mock import patch

from Performance_Testing_Agent.orchestrator.orchestrator import Orchestrator


class _SessionService:
    async def create_session(self, *, state, **kwargs):
        self.state = state

    async def get_session(self, **kwargs):
        return SimpleNamespace(state=self.state)


class _Runner:
    async def run_async(self, **kwargs):
        if False:
            yield None


class TestOrchestratorExecutionRouting(unittest.IsolatedAsyncioTestCase):
    async def _execute(self, query):
        orchestrator = Orchestrator.__new__(Orchestrator)
        orchestrator.session_service = _SessionService()
        orchestrator.runner = _Runner()
        result = await orchestrator.execute(query)
        return result, orchestrator.session_service.state

    async def test_k6_script_request_starts_real_job_and_requests_profile(self):
        result, _ = await self._execute(
            "Generate a k6 script for the payment API"
        )

        self.assertEqual(result["execution_job"]["execution_mode"], "REAL")
        self.assertEqual(result["execution_job"]["status"], "needs_input")

    async def test_jmeter_and_gatling_requests_stay_simulated(self):
        for tool in ("JMeter", "Gatling"):
            with self.subTest(tool=tool):
                result, _ = await self._execute(
                    f"Generate a {tool} test script"
                )
                self.assertEqual(
                    result["execution_job"]["execution_mode"],
                    "SIMULATED",
                )

    async def test_explicit_catalog_id_binds_complete_real_profile(self):
        with (
            patch.dict(
                os.environ,
                {
                    "REAL_EXECUTION_ENABLED": "true",
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
            result, state = await self._execute(
                "Run test case PTC-012 and generate the final PDF report"
            )

        self.assertEqual(state["test_case_id"], "PTC-012")
        self.assertEqual(state["execution_mode"], "REAL")
        self.assertEqual(state["execution_preflight"]["status"], "ready")
        self.assertEqual(state["workload_profile"]["users"], 10)
        self.assertEqual(state["workload_profile"]["max_rps"], 5)
        self.assertEqual(state["workload_profile"]["duration_seconds"], 50)
        self.assertEqual(result["execution_job"]["execution_mode"], "REAL")

    async def test_unknown_catalog_id_fails_before_agent_run(self):
        orchestrator = Orchestrator.__new__(Orchestrator)
        orchestrator.session_service = _SessionService()
        orchestrator.runner = _Runner()

        with self.assertRaisesRegex(ValueError, "Unknown test case ID"):
            await orchestrator.execute("Run test case PTC-999")

    async def test_multiple_catalog_ids_are_rejected_as_ambiguous(self):
        orchestrator = Orchestrator.__new__(Orchestrator)
        orchestrator.session_service = _SessionService()
        orchestrator.runner = _Runner()

        with self.assertRaisesRegex(ValueError, "only one catalog"):
            await orchestrator.execute("Compare PTC-011 and PTC-012")

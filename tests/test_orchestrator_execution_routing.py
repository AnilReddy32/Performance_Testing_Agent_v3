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

    async def test_jmeter_uses_real_preflight_while_gatling_stays_simulated(self):
        jmeter_result, _ = await self._execute("Generate a JMeter test script")
        self.assertEqual(jmeter_result["execution_job"]["execution_mode"], "REAL")
        self.assertEqual(jmeter_result["execution_job"]["status"], "needs_input")

        gatling_result, _ = await self._execute("Generate a Gatling test script")
        self.assertEqual(gatling_result["execution_job"]["execution_mode"], "SIMULATED")

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

    async def test_same_catalog_case_can_select_jmeter_or_k6_explicitly(self):
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
            jmeter_result, jmeter_state = await self._execute(
                "Run test case PTC-012 using JMeter and generate the report"
            )
            k6_result, k6_state = await self._execute(
                "Run test case PTC-012 using k6 and generate the report"
            )

        self.assertEqual(jmeter_state["test_case_id"], "PTC-012")
        self.assertEqual(jmeter_state["workload_profile"]["tool"], "jmeter")
        self.assertEqual(jmeter_state["execution_preflight"]["status"], "ready")
        self.assertEqual(jmeter_state["workload_profile"]["target_url"], "http://localhost:8000")
        self.assertEqual(jmeter_result["execution_job"]["execution_mode"], "REAL")

        self.assertEqual(k6_state["test_case_id"], "PTC-012")
        self.assertEqual(k6_state["workload_profile"]["tool"], "k6")
        self.assertEqual(k6_state["execution_preflight"]["status"], "ready")
        self.assertEqual(k6_result["execution_job"]["execution_mode"], "REAL")

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

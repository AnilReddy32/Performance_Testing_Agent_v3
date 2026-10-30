"""The pipeline's results must reach the stored session, not just a local copy.

google-adk's InMemorySessionService.get_session returns a copy, so updating
session.state in place (the old persist_state) was silently lost. Later agents,
including the Report agent, read the stored session, so the per-check security
verdicts and the pipeline's execution_outcome never reached them on the
/chat and Jira paths.
"""

import asyncio
import json
import unittest

from google.adk.events import Event, EventActions
from google.adk.sessions import InMemorySessionService

from Performance_Testing_Agent.orchestrator import orchestrator as om

JOB = "JOB-" + "c" * 32


def security_result(status="WARNING"):
    return {
        "schema_version": "1.0", "job_id": JOB, "status": status, "security_score": "63%",
        "issues": ["x"], "recommendations": [], "assessment_outcome": "partially_assessed",
        "check_summary": {"total": 2, "assessed": 2, "passed": 1, "failed": 1, "inconclusive": 0},
        "check_results": [
            {"check_id": "tls_protocol", "verdict": "passed", "severity": "high"},
            {"check_id": "header_hsts", "verdict": "failed", "severity": "medium"},
        ],
        "live_testing_status": "completed", "limitations": [],
    }


def completed_state():
    return {
        "job_id": JOB, "execution_mode": "REAL", "execution_status": "completed",
        "workload_profile": {
            "tool": "k6", "application": "Posts API", "environment": "external_api",
            "target_url": "https://api.example.com", "endpoint": "/posts/1",
        },
        "test_execution_result": {"job_id": JOB, "total_requests": 5},
        "execution_stage_result": {"job_id": JOB, "status": "completed", "message": "done"},
    }


class TestPersistedPipelineState(unittest.IsolatedAsyncioTestCase):
    async def run_pipeline(self, assessor_result):
        orchestrator = om.Orchestrator()
        service = orchestrator.session_service
        user, session_id = "api_user", "s1"
        await service.create_session(
            app_name=om.ADK_APP_NAME, user_id=user, session_id=session_id, state=completed_state()
        )
        seen = {}

        async def fake_invoke(agent, *, user_id, session_id, message):
            session = await service.get_session(app_name=om.ADK_APP_NAME, user_id=user_id, session_id=session_id)
            delta = {}
            if agent.name == "monitoring_agent":
                delta = {"monitoring_result": {"job_id": JOB}}
            elif agent.name == "analysis_agent":
                # The Analysis model re-types what it is shown; it never sees the raw per-check list.
                shown = json.loads(message.split("Current-job inputs: ", 1)[1])["security_result"]
                seen["analysis_prompt_security"] = shown
                summary = {k: v for k, v in (shown or {}).items()
                           if k not in {"check_results", "check_summary", "assessment_outcome"}}
                delta = {"analysis_result": {
                    "job_id": JOB, "ready_for_report": True, "data_quality_status": "valid",
                    "overall_status": "pass", "security_summary": summary or None,
                }}
            elif agent.name == "report_agent":
                seen["report_sees"] = session.state.get("analysis_result")
                delta = {"report_result": {"job_id": JOB, "file_path": "r.pdf", "report_format": "pdf", "rejected": False}}
            await service.append_event(session, Event(author=agent.name, actions=EventActions(state_delta=delta)))

        async def assessor(state):
            return assessor_result

        orchestrator._invoke_agent = fake_invoke
        original = om.passive_security_assessor
        om.passive_security_assessor = assessor
        try:
            state = await orchestrator._get_state(user, session_id)
            result = await orchestrator._complete_real_k6_pipeline(
                user_id=user, session_id=session_id, user_query="Run PTC-004.", state=state, agents_called=[],
            )
        finally:
            om.passive_security_assessor = original
        return result, await orchestrator._get_state(user, session_id), seen

    async def test_per_check_verdicts_reach_the_report_agent_and_the_stored_session(self):
        (state, pipeline), stored, seen = await self.run_pipeline(security_result())

        self.assertEqual(pipeline["security"], "completed (automatic passive assessment)")
        # The model was not shown the raw per-check list...
        self.assertNotIn("check_results", seen["analysis_prompt_security"])
        # ...yet the Report agent, which reads the stored session, sees every verdict.
        summary = seen["report_sees"]["security_summary"]
        self.assertEqual([c["check_id"] for c in summary["check_results"]], ["tls_protocol", "header_hsts"])
        self.assertEqual(summary["assessment_outcome"], "partially_assessed")
        self.assertIn("security_result", stored)

    async def test_the_pipelines_other_additions_are_persisted_too(self):
        (state, pipeline), stored, seen = await self.run_pipeline(security_result())

        outcome = seen["report_sees"]["execution_outcome"]
        self.assertEqual(outcome["job_id"], JOB)
        self.assertEqual(outcome["security_result"]["check_summary"]["failed"], 1)
        self.assertEqual(stored["analysis_result"]["execution_mode"], "REAL")

    async def test_persist_state_survives_a_session_service_that_returns_copies(self):
        service = InMemorySessionService()
        await service.create_session(app_name="a", user_id="u", session_id="s", state={"k": 1})

        session = await service.get_session(app_name="a", user_id="u", session_id="s")
        session.state.update({"lost": True})                       # the old behaviour
        await service.append_event(
            session, Event(author="pipeline", actions=EventActions(state_delta={"kept": True}))
        )
        stored = (await service.get_session(app_name="a", user_id="u", session_id="s")).state

        self.assertNotIn("lost", stored)
        self.assertTrue(stored["kept"])


if __name__ == "__main__":
    unittest.main()

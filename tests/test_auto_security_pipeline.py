"""Automatic passive security assessment inside the REAL pipeline."""

import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from Performance_Testing_Agent.orchestrator import orchestrator as orchestrator_module
from Performance_Testing_Agent.orchestrator.pipeline import (
    complete_real_k6_pipeline,
    security_opted_out,
)

JOB_ID = "JOB-" + "c" * 32

CHECKS = [
    {"check_id": "tls_protocol", "title": "TLS protocol and cipher", "category": "transport",
     "verdict": "passed", "severity": "high", "summary": "TLSv1.3 negotiated.",
     "evidence": {"negotiated_version": "TLSv1.3"}, "recommendation": None},
    {"check_id": "header_hsts", "title": "Strict-Transport-Security", "category": "headers",
     "verdict": "failed", "severity": "medium", "summary": "HSTS is not set.",
     "evidence": {"http_status": 200}, "recommendation": "Send HSTS."},
    {"check_id": "https_redirect", "title": "HTTP to HTTPS redirect", "category": "transport",
     "verdict": "inconclusive", "severity": "medium", "summary": "HTTP 403.",
     "evidence": {}, "recommendation": None},
]


def security_result(status="WARNING", job_id=JOB_ID):
    return {
        "schema_version": "1.0", "job_id": job_id, "status": status, "security_score": "63%",
        "security_score_basis": "5 of 8 points", "issues": ["[medium] Strict-Transport-Security: HSTS is not set."],
        "recommendations": ["Send HSTS."], "assessment_mode": "configuration_and_live",
        "live_testing_requested": True, "live_testing_authorized": True, "live_testing_status": "completed",
        "assessment_outcome": "partially_assessed",
        "check_summary": {"total": 3, "assessed": 2, "passed": 1, "failed": 1, "inconclusive": 1},
        "check_results": copy.deepcopy(CHECKS), "requested_controls": ["external_surface"],
        "assessed_controls": ["external_surface"], "not_assessed_controls": [],
        "coverage": {"requested_count": 1, "assessed_count": 1, "not_assessed_count": 0},
        "control_results": [{"control": "external_surface", "assessment_status": "assessed",
                            "assessment_basis": "live_observation", "status": status}],
        "evidence_references": [f"passive-assessment:{job_id}"], "limitations": ["Passive only."],
    }


def completed_state(**profile):
    return {
        "job_id": JOB_ID, "execution_mode": "REAL", "execution_status": "completed",
        "workload_profile": {
            "tool": "k6", "application": "Posts API", "environment": "external_api",
            "target_url": "https://api.example.com", "endpoint": "/posts/1", **profile,
        },
        "test_execution_result": {"job_id": JOB_ID, "total_requests": 5},
        "execution_stage_result": {"job_id": JOB_ID, "status": "completed", "message": "done"},
    }


class Harness:
    def __init__(self, state=None, analysis_drops_checks=True, analysis_summary="drop"):
        self.state = state or completed_state()
        self.calls = []
        self.messages = {}
        self.persisted = []
        self.analysis_summary = analysis_summary
        self.agents = {n: SimpleNamespace(name=n) for n in ("monitoring", "security", "analysis", "report")}

    async def invoke(self, agent, message):
        self.calls.append(agent.name)
        self.messages[agent.name] = message
        state = self.state
        if agent.name == "monitoring":
            state["monitoring_result"] = {"job_id": JOB_ID}
        elif agent.name == "security":
            state["security_result"] = security_result("PASS")
        elif agent.name == "analysis":
            analysis = {"job_id": JOB_ID, "ready_for_report": True, "data_quality_status": "valid",
                        "overall_status": "pass"}
            sent = state.get("security_result")
            if sent and self.analysis_summary == "drop":
                # The agent re-types the result and loses the per-check detail.
                analysis["security_summary"] = {
                    k: v for k, v in sent.items() if k not in {"check_results", "check_summary", "assessment_outcome"}
                }
            elif sent and self.analysis_summary == "omit":
                pass
            state["analysis_result"] = analysis
        elif agent.name == "report":
            state["report_result"] = {"job_id": JOB_ID, "file_path": "r.pdf", "report_format": "pdf", "rejected": False}

    async def persist(self, values):
        self.persisted.append(values)

    async def run(self, query="Run PTC-004.", passive=None, **flags):
        return await complete_real_k6_pipeline(
            state=self.state, user_query=query, invoke_agent=self.invoke,
            monitoring_agent=self.agents["monitoring"], security_agent=self.agents["security"],
            analysis_agent=self.agents["analysis"], report_agent=self.agents["report"],
            persist_state=self.persist, passive_security=passive, **flags,
        )


def assessor(result=None, record=None, error=None):
    async def run(state):
        if record is not None:
            record.append(dict(state))
        if error:
            raise error
        return copy.deepcopy(result) if result is not None else None
    return run


class TestOptOut(unittest.TestCase):
    def test_refusals_are_recognised(self):
        for text in (
            "Run it. Do not run security scans.", "skip security", "Run without security checks",
            "Security assessment is not needed.", "Please don't do any security", "no security this time",
            "Execute the test, skipping security",
        ):
            self.assertTrue(security_opted_out(text), text)

    def test_ordinary_requests_are_not_refusals(self):
        for text in (
            "", "Run PTC-004.", "Run it and assess the security surface.",
            "Run and check the security headers", "Monitor CPU, then report. Include security.",
        ):
            self.assertFalse(security_opted_out(text), text)


class TestAutomaticAssessment(unittest.IsolatedAsyncioTestCase):
    async def test_a_plain_run_against_an_external_api_is_assessed_without_the_model(self):
        harness = Harness()
        record = []

        pipeline = await harness.run("Run PTC-004.", passive=assessor(security_result(), record))

        self.assertEqual(pipeline["security"], "completed (automatic passive assessment)")
        self.assertEqual(harness.calls, ["monitoring", "analysis", "report"])     # no LLM security agent
        self.assertEqual(harness.state["security_result"]["job_id"], JOB_ID)
        self.assertEqual(harness.persisted[0], {"security_result": harness.state["security_result"]})
        self.assertEqual(record[0]["job_id"], JOB_ID)

    async def test_a_target_the_assessor_does_not_cover_is_skipped_with_the_old_wording(self):
        harness = Harness(completed_state(environment="mock_api", target_url="http://localhost:8000"))

        pipeline = await harness.run(passive=assessor(None))

        self.assertEqual(pipeline["security"], "skipped: not requested")
        self.assertEqual(harness.calls, ["monitoring", "analysis", "report"])
        self.assertNotIn("security_result", harness.state)

    async def test_without_an_assessor_nothing_changes(self):
        harness = Harness()

        pipeline = await harness.run("Run PTC-004.", passive=None)

        self.assertEqual(pipeline["security"], "skipped: not requested")

    async def test_the_text_can_opt_out_and_nothing_is_sent(self):
        harness = Harness()
        record = []

        pipeline = await harness.run("Run it. Do not run security scans.", passive=assessor(security_result(), record))

        self.assertEqual(pipeline["security"], "skipped: not requested")
        self.assertEqual(record, [])

    async def test_a_run_that_did_not_start_is_not_assessed(self):
        for status in ("blocked", "needs_input"):
            state = completed_state()
            state["execution_status"] = status
            record = []
            pipeline = await Harness(state).run(passive=assessor(security_result(), record))
            self.assertEqual(pipeline["security"], "skipped: not requested", status)
            self.assertEqual(record, [], status)

    async def test_a_failed_run_is_still_assessed(self):
        state = completed_state()
        state["execution_status"] = "failed"

        pipeline = await Harness(state).run(passive=assessor(security_result()))

        self.assertEqual(pipeline["security"], "completed (automatic passive assessment)")

    async def test_an_assessor_failure_never_blocks_analysis_or_the_report(self):
        harness = Harness()

        pipeline = await harness.run(passive=assessor(error=RuntimeError("probe exploded")))

        self.assertTrue(pipeline["security"].startswith("failed: RuntimeError"))
        self.assertEqual(pipeline["analysis"], "completed")
        self.assertEqual(pipeline["report"], "completed")
        self.assertIn('"security_result":null', harness.messages["analysis"])

    async def test_a_result_for_another_job_is_rejected(self):
        harness = Harness()

        pipeline = await harness.run(passive=assessor(security_result(job_id="JOB-" + "d" * 32)))

        self.assertEqual(pipeline["security"], "missing_result")
        self.assertNotIn("security_result", harness.state)

    async def test_an_existing_result_for_this_job_is_reused_not_recomputed(self):
        harness = Harness()
        harness.state["security_result"] = security_result("PASS")
        record = []

        pipeline = await harness.run(passive=assessor(security_result(), record))

        self.assertEqual(pipeline["security"], "already_available")
        self.assertEqual(record, [])

    async def test_a_stale_result_for_another_job_is_replaced(self):
        harness = Harness()
        harness.state["security_result"] = security_result("FAIL", job_id="JOB-" + "e" * 32)

        pipeline = await harness.run(passive=assessor(security_result()))

        self.assertEqual(pipeline["security"], "completed (automatic passive assessment)")
        self.assertEqual(harness.state["security_result"]["job_id"], JOB_ID)

    async def test_an_explicit_request_uses_the_security_agent_and_not_a_second_assessment(self):
        harness = Harness()
        record = []

        pipeline = await harness.run(
            "Run PTC-004 and assess the security surface.", passive=assessor(security_result(), record)
        )

        self.assertEqual(pipeline["security"], "completed")
        self.assertEqual(harness.calls, ["monitoring", "security", "analysis", "report"])
        self.assertEqual(record, [])

    async def test_a_jira_plan_that_did_not_ask_for_security_still_gets_the_automatic_check(self):
        harness = Harness()

        pipeline = await harness.run("Run it.", passive=assessor(security_result()), security_requested=False)

        self.assertEqual(pipeline["security"], "completed (automatic passive assessment)")

    async def test_a_jira_text_that_refuses_security_is_respected(self):
        harness = Harness()
        record = []

        pipeline = await harness.run(
            "Execute the test. Do not run security scans.",
            passive=assessor(security_result(), record), security_requested=False,
        )

        self.assertEqual(pipeline["security"], "skipped: not requested")
        self.assertEqual(record, [])


class TestVerdictsReachTheReport(unittest.IsolatedAsyncioTestCase):
    async def test_analysis_receives_the_verdict_without_the_raw_per_check_evidence(self):
        harness = Harness()

        await harness.run(passive=assessor(security_result()))
        sent = json.loads(harness.messages["analysis"].split("Current-job inputs: ", 1)[1])

        self.assertEqual(sent["security_result"]["status"], "WARNING")
        self.assertEqual(sent["security_result"]["check_summary"]["failed"], 1)
        self.assertNotIn("check_results", sent["security_result"])

    async def test_the_full_verdict_list_is_restored_when_analysis_drops_it(self):
        harness = Harness(analysis_summary="drop")

        await harness.run(passive=assessor(security_result()))
        summary = harness.state["analysis_result"]["security_summary"]

        self.assertEqual(summary["check_results"], CHECKS)
        self.assertEqual(summary["assessment_outcome"], "partially_assessed")
        self.assertEqual(summary["check_summary"]["inconclusive"], 1)
        self.assertEqual(summary["status"], "WARNING")                 # the rest is left as analysis wrote it

    async def test_a_missing_security_summary_is_rebuilt_from_the_pipeline_copy(self):
        harness = Harness(analysis_summary="omit")

        await harness.run(passive=assessor(security_result("FAIL")))
        analysis = harness.state["analysis_result"]

        self.assertEqual(analysis["security_summary"]["job_id"], JOB_ID)
        self.assertEqual(analysis["security_summary"]["check_results"], CHECKS)
        self.assertEqual(analysis["overall_status"], "fail")           # a security FAIL is never hidden

    async def test_a_rebuilt_warning_does_not_downgrade_or_invent_a_failure(self):
        harness = Harness(analysis_summary="omit")

        await harness.run(passive=assessor(security_result("WARNING")))

        self.assertEqual(harness.state["analysis_result"]["overall_status"], "pass")

    async def test_results_without_per_check_verdicts_are_left_exactly_alone(self):
        harness = Harness(analysis_summary="omit")
        plain = security_result("PASS")
        for key in ("check_results", "check_summary", "assessment_outcome"):
            plain.pop(key)

        await harness.run(passive=assessor(plain))

        self.assertNotIn("security_summary", harness.state["analysis_result"])


class TestOrchestratorWiring(unittest.IsolatedAsyncioTestCase):
    async def test_the_orchestrator_hands_the_assessor_to_the_pipeline(self):
        captured = {}

        async def fake_pipeline(**kwargs):
            captured.update(kwargs)
            return {"report": "completed"}

        orchestrator = orchestrator_module.Orchestrator()
        with patch.object(orchestrator_module, "complete_real_k6_pipeline", fake_pipeline):
            result = await orchestrator._complete_real_k6_pipeline(
                user_id="u", session_id="s", user_query="Run PTC-004", state={}, agents_called=[],
            )

        self.assertIsNotNone(result)
        self.assertIs(captured["passive_security"], orchestrator_module.passive_security_assessor)
        self.assertTrue(callable(captured["passive_security"]))


if __name__ == "__main__":
    unittest.main()

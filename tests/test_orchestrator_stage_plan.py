import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from Performance_Testing_Agent.orchestrator import orchestrator as orchestrator_module
from Performance_Testing_Agent.orchestrator.orchestrator import Orchestrator
from Performance_Testing_Agent.orchestrator.pipeline import (
    complete_real_k6_pipeline,
)

JOB_ID = "JOB-" + "a" * 32


def completed_state():
    return {
        "job_id": JOB_ID,
        "execution_mode": "REAL",
        "execution_status": "completed",
        "workload_profile": {"tool": "jmeter", "application": "Banking"},
        "test_execution_result": {"job_id": JOB_ID, "total_requests": 5},
        "execution_stage_result": {
            "job_id": JOB_ID,
            "status": "completed",
            "message": "REAL JMeter execution completed.",
            "thresholds_passed": True,
        },
        "execution_artifacts": {
            "job_id": JOB_ID,
            "execution_mode": "REAL",
            "artifacts": {"native_report_archive": "report.zip"},
        },
    }


def fake_agents():
    return {
        name: SimpleNamespace(name=name)
        for name in ("monitoring", "security", "analysis", "report")
    }


class TestPipelineRequestedStages(unittest.IsolatedAsyncioTestCase):
    async def run_pipeline(self, user_query, **flags):
        state = completed_state()
        agents = fake_agents()
        calls = []

        async def invoke_agent(agent, message):
            calls.append(agent.name)
            if agent.name == "monitoring":
                state["monitoring_result"] = {"job_id": JOB_ID}
            elif agent.name == "security":
                state["security_result"] = {"job_id": JOB_ID, "status": "PASS"}
            elif agent.name == "analysis":
                state["analysis_result"] = {
                    "job_id": JOB_ID,
                    "ready_for_report": True,
                    "data_quality_status": "valid",
                }
            elif agent.name == "report":
                state["report_result"] = {
                    "job_id": JOB_ID,
                    "file_path": "r.pdf",
                    "report_format": "pdf",
                    "rejected": False,
                }

        pipeline = await complete_real_k6_pipeline(
            state=state,
            user_query=user_query,
            invoke_agent=invoke_agent,
            monitoring_agent=agents["monitoring"],
            security_agent=agents["security"],
            analysis_agent=agents["analysis"],
            report_agent=agents["report"],
            **flags,
        )
        return calls, pipeline

    async def test_defaults_are_unchanged(self):
        calls, pipeline = await self.run_pipeline("Run the load test.")

        self.assertEqual(calls, ["monitoring", "analysis", "report"])
        self.assertEqual(pipeline["security"], "skipped: not requested")

        calls, _ = await self.run_pipeline("Run it and assess the security surface.")
        self.assertEqual(calls, ["monitoring", "security", "analysis", "report"])

    async def test_security_flag_overrides_the_keyword_search(self):
        calls, _ = await self.run_pipeline("Run the load test.", security_requested=True)
        self.assertEqual(calls, ["monitoring", "security", "analysis", "report"])

        calls, pipeline = await self.run_pipeline(
            "Assess the security surface.", security_requested=False
        )
        self.assertEqual(calls, ["monitoring", "analysis", "report"])
        self.assertEqual(pipeline["security"], "skipped: not requested")

    async def test_monitoring_can_be_skipped(self):
        calls, pipeline = await self.run_pipeline("Run.", monitoring_requested=False)

        self.assertEqual(calls, ["analysis", "report"])
        self.assertEqual(pipeline["monitoring"], "skipped: not requested")


class TestExecuteStagePlan(unittest.IsolatedAsyncioTestCase):
    async def run_plan(self, *, security, monitoring=True, execution_status="completed"):
        order = []
        state = {
            "job_id": JOB_ID,
            "execution_mode": "REAL",
            "workload_profile": {"tool": "jmeter", "application": "Banking"},
            "execution_status": "not_started",
        }
        names = {
            orchestrator_module.test_execution_agent.name: "execution",
            orchestrator_module.monitoring_agent.name: "monitoring",
            orchestrator_module.security_agent.name: "security",
            orchestrator_module.analysis_agent.name: "analysis",
            orchestrator_module.report_agent.name: "report",
        }

        async def fake_invoke(agent, *, user_id, session_id, message):
            stage = names[agent.name]
            order.append((stage, message))
            if stage == "execution":
                state.update(completed_state())
                state["execution_status"] = execution_status
            elif stage == "monitoring":
                state["monitoring_result"] = {"job_id": JOB_ID}
            elif stage == "security":
                state["security_result"] = {"job_id": JOB_ID, "status": "PASS"}
            elif stage == "analysis":
                state["analysis_result"] = {
                    "job_id": JOB_ID,
                    "ready_for_report": True,
                    "data_quality_status": "valid",
                }
            elif stage == "report":
                state["report_result"] = {
                    "job_id": JOB_ID,
                    "file_path": "C:/reports/JOB_report.pdf",
                    "report_format": "pdf",
                    "rejected": False,
                }

        async def fake_state(user_id, session_id):
            return dict(state)

        with tempfile.TemporaryDirectory() as root:
            job_directory = Path(root) / JOB_ID
            job_directory.mkdir()
            (job_directory / "report.zip").write_bytes(b"zip")

            orchestrator = Orchestrator()
            with (
                patch.dict(os.environ, {"JMETER_EXECUTION_ARTIFACTS_ROOT": root}),
                patch.object(orchestrator, "_invoke_agent", side_effect=fake_invoke),
                patch.object(orchestrator, "_get_state", side_effect=fake_state),
            ):
                result = await orchestrator.execute_stage_plan(
                    execution_context=dict(state),
                    execution_message="RUN-IT",
                    request_text="the Jira description",
                    monitoring_requested=monitoring,
                    security_requested=security,
                )
            archive = str((job_directory / "report.zip").resolve())
        return order, result, archive

    async def test_stages_run_one_at_a_time_in_order(self):
        order, result, archive = await self.run_plan(security=True)

        self.assertEqual(
            [stage for stage, _ in order],
            ["execution", "monitoring", "security", "analysis", "report"],
        )
        self.assertEqual(order[0][1], "RUN-IT")
        self.assertEqual(result["execution_status"], "completed")
        self.assertTrue(result["thresholds_passed"])
        self.assertEqual(result["report_path"], "C:/reports/JOB_report.pdf")
        self.assertEqual(result["artifacts"], {"native_report_archive": archive})
        self.assertEqual(result["pipeline"]["security"], "completed")

    async def test_security_is_left_out_unless_planned(self):
        order, result, _ = await self.run_plan(security=False)

        self.assertEqual(
            [stage for stage, _ in order],
            ["execution", "monitoring", "analysis", "report"],
        )
        self.assertEqual(result["pipeline"]["security"], "skipped: not requested")

    async def test_a_failed_run_skips_monitoring_but_still_reports(self):
        order, result, _ = await self.run_plan(security=False, execution_status="failed")

        self.assertEqual(
            [stage for stage, _ in order],
            ["execution", "analysis", "report"],
        )
        self.assertEqual(result["execution_status"], "failed")
        self.assertEqual(
            result["pipeline"]["monitoring"], "skipped: execution was not completed"
        )


if __name__ == "__main__":
    unittest.main()

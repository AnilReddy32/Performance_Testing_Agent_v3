import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from Performance_Testing_Agent.execution_context import (
    workload_profile_from_test_case,
)
from Performance_Testing_Agent.jira_agent_integration import jira_service
from Performance_Testing_Agent.jira_agent_integration.test_case_resolver import (
    TEST_CASE_FIELD_ID,
)
from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case

# Target validation resolves DNS; keep these tests offline and deterministic.
PUBLIC_ADDRESS = [(2, 1, 6, "", ("93.184.216.34", 443))]


def with_tool(case, tool):
    """Copy a catalog case with its tool changed in both places it is stored."""
    return {
        **case,
        "tool": tool,
        "workload_profile": {**case["workload_profile"], "tool": tool},
    }


# Pin the catalog defaults so these tests do not depend on the live catalog.
CATALOG_CASE = with_tool(get_test_case("PTC-001"), "k6")

COMPLETED = {
    "job_id": "JOB-1",
    "execution_status": "completed",
    "execution_message": "REAL execution completed.",
    "thresholds_passed": True,
    "pipeline": {
        "monitoring": "completed",
        "security": "skipped: not requested",
        "analysis": "completed",
        "report": "completed",
    },
    "report_path": "C:/reports/JOB-1_report.pdf",
    "artifacts": {
        "native_report_entrypoint": "C:/jobs/JOB-1/native_report.html",
        "native_report_archive": "C:/jobs/JOB-1/native_report.zip",
        "raw_results": "C:/jobs/JOB-1/results.jtl",
    },
}


def issue(summary="Load check", description="", case_id="PTC-001"):
    return {
        "key": "PTA-FLOW",
        "fields": {
            "summary": summary,
            "description": description,
            TEST_CASE_FIELD_ID: {"id": "10194", "value": case_id},
            "attachment": [],
        },
    }


def adf(text):
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": text}]}
        ],
    }


class StageFlowTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.catalog_profile = workload_profile_from_test_case(
            CATALOG_CASE
        ).model_dump(mode="json")

    async def run_issue(
        self,
        jira_issue,
        *,
        catalog_case=CATALOG_CASE,
        stage_result=COMPLETED,
        stage_error=None,
    ):
        events = []

        async def fake_stage_plan(**kwargs):
            events.append("run")
            if stage_error is not None:
                raise stage_error
            return stage_result

        def fake_comment(key, text):
            events.append("comment")
            return {"id": f"c-{len(events)}"}

        def fake_transition(key, transition_id):
            events.append(f"transition:{transition_id}")
            return {"success": True}

        with (
            patch(
                "Performance_Testing_Agent.jira_agent_integration."
                "test_case_resolver.get_test_case",
                return_value=catalog_case,
            ),
            patch(
                "Performance_Testing_Agent.execution_context.socket.getaddrinfo",
                return_value=PUBLIC_ADDRESS,
            ),
            patch.object(
                jira_service, "run_stage_plan", side_effect=fake_stage_plan
            ) as stage_plan,
            patch.object(
                jira_service,
                "run_orchestrator",
                new_callable=AsyncMock,
                return_value="LEGACY_RESPONSE",
            ) as legacy,
            patch.object(
                jira_service, "transition_issue", side_effect=fake_transition
            ),
            patch.object(
                jira_service, "add_issue_comment", side_effect=fake_comment
            ) as comment,
        ):
            result = await jira_service.process_single_issue(jira_issue)

        return SimpleNamespace(
            result=result,
            events=events,
            stage_plan=stage_plan,
            legacy=legacy,
            comments=[c.args[1] for c in comment.call_args_list],
            stage_kwargs=(
                stage_plan.call_args.kwargs if stage_plan.call_args else None
            ),
        )


class TestRunnerSelection(StageFlowTestCase):
    """The Jira text may replace the catalog's tool, and nothing else."""

    def assert_only_tool_changed(self, run, tool):
        context = run.stage_kwargs["execution_context"]
        self.assertEqual(context["execution_mode"], "REAL")
        self.assertEqual(
            context["workload_profile"], {**self.catalog_profile, "tool": tool}
        )
        return context

    async def test_description_runner_replaces_catalog_tool(self):
        run = await self.run_issue(
            issue(description="Please run this test using JMeter.")
        )

        context = self.assert_only_tool_changed(run, "jmeter")
        self.assertIn("Jmeter native reports", context["execution_artifact_directory"])
        self.assertIn(
            "Runner: JMeter (selected in the Jira text; catalog default: k6)",
            run.comments[0],
        )
        self.assertIn("using JMeter", run.stage_kwargs["execution_message"])
        run.legacy.assert_not_awaited()

    async def test_summary_runner_also_counts(self):
        run = await self.run_issue(issue(summary="Run PTC-001 with JMeter"))
        self.assert_only_tool_changed(run, "jmeter")

    async def test_rich_text_description_is_read(self):
        run = await self.run_issue(
            issue(description=adf("Run the load check using JMeter."))
        )
        self.assert_only_tool_changed(run, "jmeter")

    async def test_no_runner_in_text_keeps_catalog_tool(self):
        run = await self.run_issue(issue(description="Baseline before release."))

        context = self.assert_only_tool_changed(run, "k6")
        self.assertIn("k6 native reports", context["execution_artifact_directory"])
        self.assertIn("Runner: k6 (catalog default)", run.comments[0])

    async def test_naming_the_catalog_tool_is_not_an_override(self):
        run = await self.run_issue(issue(description="Run this using k6."))

        self.assert_only_tool_changed(run, "k6")
        self.assertIn("Runner: k6 (catalog default)", run.comments[0])

    async def test_text_can_switch_a_jmeter_case_to_k6(self):
        run = await self.run_issue(
            issue(description="Run this using k6."),
            catalog_case=with_tool(CATALOG_CASE, "jmeter"),
        )

        self.assert_only_tool_changed(run, "k6")
        self.assertIn(
            "Runner: k6 (selected in the Jira text; catalog default: JMeter)",
            run.comments[0],
        )

    async def test_jmeter_catalog_case_runs_for_real_without_naming_a_runner(self):
        run = await self.run_issue(
            issue(description="Run the load check."),
            catalog_case=with_tool(CATALOG_CASE, "jmeter"),
        )

        self.assert_only_tool_changed(run, "jmeter")
        self.assertIn("Runner: JMeter (catalog default)", run.comments[0])

    async def test_conflicting_runners_fail_before_any_work(self):
        run = await self.run_issue(
            issue(summary="Run using k6", description="Actually use JMeter.")
        )

        self.assertEqual(run.result["status"], "Validation Failed")
        self.assertIn("either k6 or JMeter", run.result["error"])
        self.assertEqual(run.events, [])

    async def test_workflow_case_keeps_the_existing_path(self):
        workflow_case = get_test_case("WTC-001")
        run = await self.run_issue(
            issue(description="Run this using JMeter.", case_id="WTC-001"),
            catalog_case=workflow_case,
        )

        run.legacy.assert_awaited_once()
        run.stage_plan.assert_not_called()
        self.assertEqual(
            run.legacy.await_args.kwargs["initial_state"]["execution_mode"],
            "SIMULATED",
        )


class TestStagePlanFlow(StageFlowTestCase):
    async def test_plan_is_posted_before_anything_runs_and_done_follows(self):
        run = await self.run_issue(
            issue(description="Run it, collect monitoring, assess security.")
        )

        self.assertEqual(
            run.events,
            ["transition:21", "comment", "run", "comment", "transition:31"],
        )
        self.assertIn("Execution Plan", run.comments[0])
        self.assertIn("Assess the security surface", run.comments[0])
        self.assertIn("Processing Result", run.comments[1])
        self.assertIn("C:/reports/JOB-1_report.pdf", run.comments[1])
        self.assertIn("C:/jobs/JOB-1/native_report.zip", run.comments[1])
        self.assertIn("moved to Done", run.comments[1])
        self.assertEqual(run.result["status"], "Done")

    async def test_stages_come_from_the_description_keywords(self):
        run = await self.run_issue(
            issue(description="Run it and assess the security surface.")
        )
        self.assertTrue(run.stage_kwargs["security_requested"])
        self.assertTrue(run.stage_kwargs["monitoring_requested"])

        run = await self.run_issue(issue(description="Run it."))
        self.assertFalse(run.stage_kwargs["security_requested"])
        self.assertIn("Security assessment not requested", run.comments[0])

    async def test_refusing_another_stage_does_not_cancel_the_test(self):
        run = await self.run_issue(
            issue(description="Execute the test. Do not run security scans.")
        )

        self.assertFalse(run.stage_kwargs["security_requested"])
        self.assertEqual(run.result["status"], "Done")

    async def test_refusing_to_run_starts_nothing(self):
        run = await self.run_issue(issue(description="Do not run the test."))

        self.assertEqual(run.result["status"], "Not Executed")
        run.stage_plan.assert_not_called()
        self.assertEqual(run.events, ["transition:21", "comment"])
        self.assertIn("nothing will run", run.comments[0])

    async def test_description_is_the_prompt_and_summary_is_the_fallback(self):
        run = await self.run_issue(
            issue(summary="Summary text", description="Description text.")
        )
        self.assertEqual(run.stage_kwargs["request_text"], "Description text.")

        run = await self.run_issue(issue(summary="Summary text", description=""))
        self.assertEqual(run.stage_kwargs["request_text"], "Summary text")

    async def test_dropdown_wins_over_a_different_id_in_the_description(self):
        run = await self.run_issue(
            issue(description="Run PTC-001 please.", case_id="PTC-005"),
            catalog_case={**CATALOG_CASE, "test_case_id": "PTC-005"},
        )

        self.assertEqual(
            run.stage_kwargs["execution_context"]["test_case_id"], "PTC-005"
        )
        self.assertIn("PTC-005", run.stage_kwargs["execution_message"])
        self.assertIn("mentions PTC-001", run.comments[0])
        self.assertEqual(run.result["test_case_id"], "PTC-005")

    async def test_failed_execution_is_not_moved_to_done(self):
        failed = {
            **COMPLETED,
            "execution_status": "failed",
            "execution_message": "k6 executable was not found on PATH.",
            "thresholds_passed": None,
        }
        run = await self.run_issue(issue(), stage_result=failed)

        self.assertNotIn("transition:31", run.events)
        self.assertEqual(run.result["status"], "In Progress")
        self.assertIn("left In Progress", run.comments[1])
        self.assertIn("k6 executable was not found", run.comments[1])

    async def test_missing_report_is_not_moved_to_done(self):
        run = await self.run_issue(
            issue(), stage_result={**COMPLETED, "report_path": None}
        )

        self.assertNotIn("transition:31", run.events)
        self.assertIn("report was not created", run.comments[1])

    async def test_a_crash_posts_a_comment_and_leaves_the_issue_in_progress(self):
        run = await self.run_issue(issue(), stage_error=RuntimeError("boom"))

        self.assertEqual(run.result["status"], "Failed")
        self.assertEqual(run.events[-1], "comment")
        self.assertIn("RuntimeError: boom", run.comments[-1])
        self.assertNotIn("transition:31", run.events)


if __name__ == "__main__":
    unittest.main()

"""A Jira issue that names one catalog test case in its text, with no Test Case ID
selected, is planned and run like a selected one (plan comment first, REAL run).
Everything that does not name exactly one catalog case keeps its old path."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from Performance_Testing_Agent.execution_context import (
    workload_profile_from_test_case,
)
from Performance_Testing_Agent.jira_agent_integration import jira_service
from Performance_Testing_Agent.jira_agent_integration.test_case_resolver import (
    TEST_CASE_FIELD_ID,
    resolve_text_test_case,
)
from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case

# Target validation resolves DNS; keep these tests offline and deterministic.
PUBLIC_ADDRESS = [(2, 1, 6, "", ("93.184.216.34", 443))]

RESOLVER = "Performance_Testing_Agent.jira_agent_integration.test_case_resolver"

COMPLETED = {
    "job_id": "JOB-1",
    "execution_status": "completed",
    "execution_message": "REAL execution completed.",
    "thresholds_passed": True,
    "pipeline": {
        "monitoring": "completed",
        "security": "completed",
        "analysis": "completed",
        "report": "completed",
    },
    "report_path": "C:/reports/JOB-1_report.pdf",
    "artifacts": {},
}


def adf(text):
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": text}]}
        ],
    }


def issue(summary, description="", *, selected=None, attachments=()):
    fields = {
        "summary": summary,
        "description": adf(description) if description else None,
        "attachment": list(attachments),
    }
    if selected is not None:
        fields[TEST_CASE_FIELD_ID] = {"id": "10194", "value": selected}
    return {"key": "PTA-TEXT", "fields": fields}


def fake_catalog(known):
    """get_test_case that knows only the given cases, like the real one for other IDs."""

    def lookup(test_case_id):
        if test_case_id not in known:
            raise ValueError(f"Unknown test case ID: {test_case_id}")
        return known[test_case_id]

    return lookup


class ResolveTextTestCase(unittest.TestCase):
    def test_one_id_in_the_text_resolves_the_catalog_case(self):
        for summary, description in (
            ("Please run the test case for PTC-005", ""),
            ("Run it", "Run PTC-005 using Jmeter."),
            ("Please Run test case for PTC 005", "Run PTC-005 using Jmeter."),
            ("run ptc005 now", ""),
            ("Run PTC-005 (PTC-005 again)", "and PTC-005"),
        ):
            with self.subTest(summary=summary, description=description):
                case = resolve_text_test_case(summary, description)
                self.assertEqual(case["test_case_id"], "PTC-005")

    def test_nothing_resolves_unless_exactly_one_known_case_is_named(self):
        for summary, description in (
            ("Load test the user API", "50 users for 60 seconds"),
            ("Compare PTC-001 and PTC-002", ""),
            ("Run PTC-005", "Also PTC 006"),
            ("Run PTC-999", ""),
            ("Run PTC-0051", ""),
            ("Run XPTC-005", ""),
            ("", ""),
            (None, None),
        ):
            with self.subTest(summary=summary, description=description):
                self.assertIsNone(resolve_text_test_case(summary, description))

    def test_an_inactive_case_does_not_resolve(self):
        inactive = {**get_test_case("PTC-005"), "status": "retired"}
        with patch(
            f"{RESOLVER}.get_test_case", side_effect=fake_catalog({"PTC-005": inactive})
        ):
            self.assertIsNone(resolve_text_test_case("Run PTC-005", ""))

    def test_a_broken_catalog_is_an_error_not_a_silent_miss(self):
        with patch(
            f"{RESOLVER}.get_test_case", side_effect=ValueError("catalog is broken")
        ):
            with self.assertRaises(ValueError):
                resolve_text_test_case("Run PTC-005", "")


class TextNamedCaseFlow(unittest.IsolatedAsyncioTestCase):
    async def run_issue(self, jira_issue, *, catalog=None):
        events = []

        async def fake_stage_plan(**kwargs):
            events.append("run")
            return COMPLETED

        def fake_comment(key, text):
            events.append("comment")
            return {"id": f"c-{len(events)}"}

        def fake_transition(key, transition_id):
            events.append(f"transition:{transition_id}")
            return {"success": True}

        known = catalog if catalog is not None else {
            case_id: get_test_case(case_id)
            for case_id in ("PTC-001", "PTC-002", "PTC-005", "PTC-007")
        }
        with (
            patch(f"{RESOLVER}.get_test_case", side_effect=fake_catalog(known)),
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
            stage_kwargs=stage_plan.call_args.kwargs if stage_plan.call_args else None,
        )

    def assert_planned_real_run(self, run, test_case_id, tool):
        self.assertEqual(run.result["status"], "Done")
        self.assertEqual(run.result["input_source"], "TEST_CASE")
        self.assertEqual(run.result["test_case_id"], test_case_id)
        run.legacy.assert_not_called()
        run.stage_plan.assert_called_once()
        context = run.stage_kwargs["execution_context"]
        self.assertEqual(context["execution_mode"], "REAL")
        self.assertEqual(context["workload_profile"]["tool"], tool)
        self.assertEqual(context["test_case_id"], test_case_id)
        # The plan comment is posted before anything runs.
        self.assertIn("Execution Plan", run.comments[0])
        self.assertLess(run.events.index("comment"), run.events.index("run"))

    async def test_the_issue_texts_that_ran_simulated_now_plan_then_run_real(self):
        # The wording of the Jira issues that were handled as SUMMARY_DESCRIPTION.
        for summary, description, case_id in (
            (
                "Please run the test case for PTC-005",
                "Run PTC-005 using Jmeter. Execute the real performance test and "
                "collect monitoring results. Assess the security surface for the "
                "same job. Analyze the current job's results and generate the "
                "final PDF with security coverage and evidence.",
                "PTC-005",
            ),
            (
                "Generate and execute the Jmeter script for the PTC-007",
                "",
                "PTC-007",
            ),
            (
                "Please Run test case for PTC 005",
                "Run PTC-005 using Jmeter.",
                "PTC-005",
            ),
        ):
            with self.subTest(summary=summary):
                run = await self.run_issue(issue(summary, description))
                self.assert_planned_real_run(run, case_id, "jmeter")

    async def test_the_runner_in_the_text_is_the_runner_used(self):
        for description, tool in (
            ("Run PTC-001 using JMeter.", "jmeter"),
            ("Run PTC-001 using k6.", "k6"),
        ):
            with self.subTest(description=description):
                run = await self.run_issue(issue("Run it", description))
                self.assert_planned_real_run(run, "PTC-001", tool)
                self.assertIn(f"Runner: {'JMeter' if tool == 'jmeter' else 'k6'}", run.comments[0])

    async def test_the_plan_follows_what_the_text_asks_for(self):
        run = await self.run_issue(
            issue("Run PTC-005", "Run PTC-005 using JMeter and assess the security surface.")
        )
        self.assert_planned_real_run(run, "PTC-005", "jmeter")
        self.assertTrue(run.stage_kwargs["security_requested"])
        self.assertTrue(run.stage_kwargs["monitoring_requested"])
        self.assertIn("Assess the security surface", run.comments[0])

    async def test_a_selected_test_case_id_still_wins_over_the_text(self):
        run = await self.run_issue(
            issue("Run PTC-001", "Run PTC-001 using JMeter.", selected="PTC-002")
        )
        self.assertEqual(run.result["test_case_id"], "PTC-002")
        self.assertEqual(
            run.stage_kwargs["execution_context"]["test_case_id"], "PTC-002"
        )
        run.legacy.assert_not_called()

    async def test_other_issues_keep_the_old_path(self):
        for label, jira_issue in (
            ("no id in the text", issue("Load test the user API", "50 users, 60 s")),
            ("two ids", issue("Compare PTC-001 and PTC-002", "")),
            ("unknown id", issue("Run PTC-999", "")),
            (
                "an attachment keeps its precedence",
                issue(
                    "Run PTC-001",
                    "",
                    attachments=[{"id": "1", "filename": "notes.exe"}],
                ),
            ),
        ):
            with self.subTest(label):
                run = await self.run_issue(jira_issue)
                run.stage_plan.assert_not_called()
                run.legacy.assert_awaited_once()
                self.assertNotIn(
                    "Execution Plan", "\n".join(run.comments), "no plan on the old path"
                )
                self.assertEqual(run.result["input_source"], "SUMMARY_DESCRIPTION")

    async def test_text_only_issue_with_a_blank_field_value_is_resolved(self):
        jira_issue = issue("Run PTC-005", "Run PTC-005 using JMeter.")
        jira_issue["fields"][TEST_CASE_FIELD_ID] = {"id": "0", "value": "  "}
        run = await self.run_issue(jira_issue)
        self.assert_planned_real_run(run, "PTC-005", "jmeter")

    async def test_an_inactive_case_named_in_the_text_keeps_the_old_path(self):
        inactive = {**get_test_case("PTC-005"), "status": "retired"}
        run = await self.run_issue(
            issue("Run PTC-005", ""), catalog={"PTC-005": inactive}
        )
        run.stage_plan.assert_not_called()
        run.legacy.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()

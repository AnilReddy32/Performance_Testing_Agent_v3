import json
import unittest

from Performance_Testing_Agent.jira_agent_integration import jira_service
from Performance_Testing_Agent.jira_agent_integration.app.routes import jira
from Performance_Testing_Agent.jira_agent_integration.test_case_resolver import (
    TEST_CASE_FIELD_ID,
)
from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case

from unittest.mock import ANY, AsyncMock, Mock, call, patch

def sample_issue():
    return {
        "key": "PTA-MOCK",
        "fields": {
            "summary": "Verify test-case handoff",
            "description": "Local mocked test; do not execute a load test.",
            TEST_CASE_FIELD_ID: {
                "id": "10194",
                "value": "PTC-001",
            },
            "attachment": [],
        },
    }


class TestJiraHandoff(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        # Safety guard: fail if code attempts a real requests HTTP call.
        network_guard = patch(
            "requests.sessions.Session.request",
            side_effect=AssertionError(
                "Unexpected real HTTP request during mocked test."
            ),
        )
        network_guard.start()
        self.addCleanup(network_guard.stop)

    def assert_prompt_context(self, mocked_runner):
        mocked_runner.assert_awaited_once()

        prompt = mocked_runner.await_args.args[0]
        marker = "TASK_CONTEXT_JSON:\n"

        self.assertIn(marker, prompt)

        context = json.loads(prompt.split(marker, 1)[1])

        self.assertEqual(context["jira_issue_key"], "PTA-MOCK")
        self.assertEqual(context["summary"], "Verify test-case handoff")
        self.assertEqual(context["test_case_id"], "PTC-001")
        self.assertEqual(context["execution_mode"], "SIMULATED")

        # Verify the whole definition, not only the ID.
        self.assertEqual(
            context["test_case"],
            get_test_case("PTC-001"),
        )

        return context

    async def test_service_handoff(self):
        with (
            patch.object(
                jira_service,
                "run_orchestrator",
                new_callable=AsyncMock,
                return_value="MOCK_RESPONSE",
            ) as mocked_runner,
            patch.object(
                jira_service,
                "transition_issue",
                return_value={"success": True},
            ) as mocked_transition,
            patch.object(
                jira_service,
                "extract_issue_attachments",
                new_callable=AsyncMock,
                return_value="Mock attachment content",
            ) as mocked_attachments,
            patch.object(
                jira_service,
                "add_issue_comment",
                return_value={"id": "mock-comment-001"},
            ) as mocked_comment,
        ):

            # Record the relative order of Jira operations.
            jira_operations = Mock()
            jira_operations.attach_mock(
                mocked_transition, "transition"
            )
            jira_operations.attach_mock(
                mocked_comment, "comment"
            )

            result = await jira_service.process_single_issue(sample_issue())

            context = self.assert_prompt_context(mocked_runner)
            execution_state = mocked_runner.await_args.kwargs["initial_state"]
            self.assertEqual(execution_state["execution_mode"], "SIMULATED")
            self.assertEqual(execution_state["execution_source_id"], "PTA-MOCK")
            self.assertEqual(
                execution_state["workload_profile"]["endpoint"],
                "/api/payment",
            )

            self.assertEqual(
                context["attachment_content"],
                "Mock attachment content",
            )
            self.assertEqual(result["agent_response"], "MOCK_RESPONSE")
            mocked_attachments.assert_awaited_once_with([])

            # Confirms existing transitions used the mock, not Jira.
            self.assertEqual(
                mocked_transition.call_args_list,
                [
                    call("PTA-MOCK", "21"),
                    call("PTA-MOCK", "31"),
                ],
            )
            self.assertEqual(result["status"], "Done")

            mocked_comment.assert_called_once()

            comment_args = mocked_comment.call_args.args
            self.assertEqual(comment_args[0], "PTA-MOCK")
            self.assertIn("PTC-001", comment_args[1])
            self.assertIn("MOCK_RESPONSE", comment_args[1])

            self.assertEqual(
                result["comment_id"],
                "mock-comment-001",
            )

            self.assertEqual(
                jira_operations.mock_calls,
                [
                    call.transition("PTA-MOCK", "21"),
                    call.comment("PTA-MOCK", ANY),
                    call.transition("PTA-MOCK", "31"),
                ],
            )

    async def test_direct_route_handoff(self):
        with (
            patch.object(
                jira,
                "get_issue",
                return_value=sample_issue(),
            ) as mocked_get_issue,
            patch.object(
                jira,
                "run_orchestrator",
                new_callable=AsyncMock,
                return_value="MOCK_RESPONSE",
            ) as mocked_runner,
        ):
            result = await jira.execute_jira_issue("PTA-MOCK")

            self.assert_prompt_context(mocked_runner)

            mocked_get_issue.assert_called_once_with("PTA-MOCK")
            self.assertTrue(result["success"])
            self.assertEqual(result["agent_response"], "MOCK_RESPONSE")


    async def test_workflow_service_handoff(self):
        issue = {
            "key": "PTA-WORKFLOW-MOCK",
            "fields": {
                "summary": "Fund Transfer End-to-End Assessment",
                "description": "Mocked workflow handoff verification.",
                TEST_CASE_FIELD_ID: {
                    "value": "WTC-001",
                },
                "attachment": [],
            },
        }

        expected_case = get_test_case("WTC-001")

        with (
            patch.object(
                jira_service,
                "run_orchestrator",
                new_callable=AsyncMock,
                return_value="MOCK_WORKFLOW_RESPONSE",
            ) as mocked_runner,
            patch.object(
                jira_service,
                "transition_issue",
                return_value={"success": True},
            ) as mocked_transition,
            patch.object(
                jira_service,
                "extract_issue_attachments",
                new_callable=AsyncMock,
                return_value="",
            ) as mocked_attachments,
            patch.object(
                jira_service,
                "add_issue_comment",
                return_value={"id": "mock-workflow-comment"},
            ) as mocked_comment,
        ):
            jira_operations = Mock()
            jira_operations.attach_mock(
                mocked_transition, "transition"
            )
            jira_operations.attach_mock(
                mocked_comment, "comment"
            )

            result = await jira_service.process_single_issue(issue)

            # Verify the exact content passed to the orchestrator.
            mocked_runner.assert_awaited_once()
            agent_prompt = mocked_runner.await_args.args[0]

            marker = "TASK_CONTEXT_JSON:\n"
            self.assertIn(marker, agent_prompt)

            context = json.loads(
                agent_prompt.split(marker, 1)[1]
            )

            self.assertEqual(
                context["jira_issue_key"],
                "PTA-WORKFLOW-MOCK",
            )
            self.assertEqual(context["test_case_id"], "WTC-001")
            self.assertEqual(context["test_case"], expected_case)

            # Exact comparison ensures no prompt text was lost or changed.
            self.assertEqual(
                context["test_case"]["prompt"],
                expected_case["prompt"],
            )
            self.assertEqual(context["execution_mode"], "SIMULATED")
            execution_state = mocked_runner.await_args.kwargs["initial_state"]
            self.assertEqual(execution_state["execution_mode"], "SIMULATED")
            self.assertEqual(
                execution_state["workload_profile"],
                expected_case["workload_profile"],
            )

            mocked_attachments.assert_awaited_once_with([])

            # Verify the recorded result and Jira comment.
            self.assertEqual(result["status"], "Done")
            self.assertEqual(result["test_case_id"], "WTC-001")
            self.assertEqual(
                result["agent_response"],
                "MOCK_WORKFLOW_RESPONSE",
            )
            self.assertEqual(
                result["comment_id"],
                "mock-workflow-comment",
            )

            mocked_comment.assert_called_once()
            comment_args = mocked_comment.call_args.args

            self.assertEqual(
                comment_args[0],
                "PTA-WORKFLOW-MOCK",
            )
            self.assertIn("WTC-001", comment_args[1])
            self.assertIn(
                "MOCK_WORKFLOW_RESPONSE",
                comment_args[1],
            )

            # Verify comment posting occurs before the Done transition.
            self.assertEqual(
                jira_operations.mock_calls,
                [
                    call.transition("PTA-WORKFLOW-MOCK", "21"),
                    call.comment("PTA-WORKFLOW-MOCK", ANY),
                    call.transition("PTA-WORKFLOW-MOCK", "31"),
                ],
            )

if __name__ == "__main__":
    unittest.main()
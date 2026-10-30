"""Whatever runner the prompt names is the runner used, whatever the catalog case defaults to.

A request like "Run PTC-003 in JMeter" was recognised as a JMeter task (so the
mismatch guard fired) but did not select JMeter as the runner (so the case kept
its catalog tool, k6), and the run was blocked with "requested tool does not
match the trusted workload profile". Prompts that name a runner with no action
word at all ("PTC-003 JMeter") silently ran the catalog tool instead.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from google.adk.sessions.state import State

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXECUTION_AGENT_ROOT = (
    PROJECT_ROOT / "src" / "Performance_Testing_Agent" / "agents" / "test_execution_agent_adk"
)
if str(EXECUTION_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(EXECUTION_AGENT_ROOT))

import Performance_Testing_Agent  # noqa: F401  (resolves a circular import in app.agent)
from app.agent import run_test_execution_adk
from Performance_Testing_Agent.execution_context import (
    create_context_for_test_case,
    is_jmeter_test_request,
    requested_execution_tool,
)
from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case

JMETER_WITH_ACTION_WORD = [
    "Run PTC-003 in JMeter",
    "Run PTC-003 on JMeter",
    "Run PTC-003 via Apache JMeter",
    "Run PTC-003 using Apache JMeter",
    "Run PTC-003. Tool: JMeter",
    "Run PTC-003, JMeter please",
    "JMeter run for PTC-003",
    "Run test case PTC-003 by means of JMeter",
    "Run PTC-003 (JMeter)",
    # phrasings that already worked must keep working
    "Run PTC-003 using JMeter",
    "Run PTC-003 with JMeter",
    "Use JMeter to run PTC-003",
    "Run the JMeter test PTC-003",
    "Run PTC-003 as a JMeter test",
    "Please run catalog test case PTC-003 using JMeter as the runner",
    "Use JMeter to run PTC-003. Observe the run, assess the configured endpoint's "
    "security surface, analyze the results from this job, and create a linked PDF report.",
]
JMETER_WITHOUT_ACTION_WORD = [
    "PTC-003 JMeter",
    "JMeter for PTC-003",
    "PTC-003 - JMeter",
    "Please JMeter PTC-003",
    "jmeter ptc-003",
    "PTC-003 with JMeter",
    "Analyze the JMeter results for PTC-003",
]
K6_PHRASINGS = [
    "Run PTC-001 in k6", "Run PTC-001 on k6", "Run PTC-001, k6 please", "Run test case PTC-001 using k6",
    "k6 for PTC-001", "PTC-001 k6", "PTC-001 - k6",
]


class TestRunnerSelection(unittest.TestCase):
    def test_every_way_of_naming_jmeter_selects_it(self):
        for prompt in JMETER_WITH_ACTION_WORD + JMETER_WITHOUT_ACTION_WORD:
            with self.subTest(prompt=prompt):
                self.assertEqual(requested_execution_tool(prompt), "jmeter")

    def test_a_jmeter_task_is_never_left_without_a_selected_runner(self):
        # The invariant behind the original block: a request recognised as a JMeter
        # task must always have JMeter selected as its runner.
        for prompt in JMETER_WITH_ACTION_WORD:
            with self.subTest(prompt=prompt):
                self.assertTrue(is_jmeter_test_request(prompt))
                self.assertEqual(requested_execution_tool(prompt), "jmeter")

    def test_every_way_of_naming_k6_selects_it_for_a_jmeter_default_case(self):
        for prompt in K6_PHRASINGS:
            with self.subTest(prompt=prompt):
                self.assertEqual(requested_execution_tool(prompt), "k6")

    def test_naming_the_catalog_default_runner_selects_it_too(self):
        self.assertEqual(requested_execution_tool("Run PTC-003 using k6"), "k6")
        self.assertEqual(requested_execution_tool("PTC-003 k6"), "k6")
        self.assertEqual(requested_execution_tool("Run PTC-001 using JMeter"), "jmeter")

    def test_existing_selections_are_unchanged(self):
        self.assertEqual(
            requested_execution_tool("Run test case PTC-001 using JMeter; this case normally uses k6"),
            "jmeter",
        )
        self.assertEqual(requested_execution_tool("Run PTC-003 using k6, not JMeter"), "k6")
        self.assertEqual(requested_execution_tool("Run PTC-003 with JMeter instead of k6"), "jmeter")
        with self.assertRaisesRegex(ValueError, "either k6 or JMeter"):
            requested_execution_tool("Run the k6 test and the JMeter test for PTC-001")

    def test_nothing_is_selected_when_no_runner_is_named_or_it_is_negated_or_ambiguous(self):
        for prompt in (
            "Run PTC-003",
            "Report on PTC-003",
            "PTC-003",
            "Run PTC-003 (no JMeter)",
            "Run PTC-003 without JMeter",
            "Run PTC-003 and do not use Apache JMeter",
            "Run PTC-003 in JMeter and in k6",           # ambiguous: left for the guard
        ):
            with self.subTest(prompt=prompt):
                self.assertIsNone(requested_execution_tool(prompt))

    def test_the_selected_runner_reaches_the_job_context_as_a_real_run_of_that_runner(self):
        case = get_test_case("PTC-003")
        self.assertEqual(case["tool"], "k6")                       # the catalog default

        for prompt in JMETER_WITH_ACTION_WORD + JMETER_WITHOUT_ACTION_WORD:
            with self.subTest(prompt=prompt):
                context = create_context_for_test_case(
                    case, source_id="TEST", requested_tool=requested_execution_tool(prompt)
                )
                self.assertEqual(context["workload_profile"]["tool"], "jmeter")
                self.assertEqual(context["execution_mode"], "REAL")
                self.assertEqual(context["workload_profile"]["endpoint"], case["endpoint"])
                self.assertEqual(context["workload_profile"]["users"], case["virtual_users"])

        jmeter_case = get_test_case("PTC-001")
        self.assertEqual(jmeter_case["tool"], "jmeter")
        for prompt in K6_PHRASINGS:
            with self.subTest(prompt=prompt):
                context = create_context_for_test_case(
                    jmeter_case, source_id="TEST", requested_tool=requested_execution_tool(prompt)
                )
                self.assertEqual(context["workload_profile"]["tool"], "k6")
                self.assertEqual(context["execution_mode"], "REAL")

    def test_a_request_that_names_no_runner_keeps_the_catalog_tool(self):
        case = get_test_case("PTC-003")

        context = create_context_for_test_case(
            case, source_id="TEST", requested_tool=requested_execution_tool("Run PTC-003")
        )

        self.assertEqual(context["workload_profile"]["tool"], "k6")


class TestTheWholePathFollowsTheNamedRunner(unittest.TestCase):
    """After selection, the agent must use that runner's script and runner, never the other."""

    def execute(self, prompt, *, bound_prompt=None):
        tool = requested_execution_tool(bound_prompt or prompt)
        state = create_context_for_test_case(get_test_case("PTC-003"), source_id="TEST", requested_tool=tool)
        state["execution_preflight"] = {"status": "ready"}
        context = type("ToolContextStub", (), {"state": State(state, {})})()
        completed = {"status": "completed", "execution_mode": "REAL", "metrics": {"total_requests": 1},
                     "artifacts": {}, "job_id": state["job_id"], "thresholds_passed": True}
        generated = {"status": "success", "message": "prepared", "file_path": "script", "artifact_path": "script"}
        with (
            patch("app.agent.generate_script", return_value=generated) as generate,
            patch("app.agent.run_real_jmeter_test", return_value=dict(completed)) as jmeter,
            patch("app.agent.run_real_k6_test", return_value=dict(completed)) as k6,
        ):
            result = run_test_execution_adk(prompt, context)
        return result, generate, jmeter, k6

    def test_a_catalog_k6_case_run_with_jmeter_generates_and_runs_jmeter_only(self):
        for prompt in ("Run PTC-003 in JMeter", "Use JMeter to run PTC-003", "Run PTC-003 using Apache JMeter"):
            with self.subTest(prompt=prompt):
                result, generate, jmeter, k6 = self.execute(prompt)

                self.assertEqual(generate.call_args.kwargs["tool"], "jmeter")
                jmeter.assert_called_once()
                k6.assert_not_called()
                self.assertEqual(result["status"], "completed")

    def test_a_catalog_jmeter_case_run_with_k6_generates_and_runs_k6_only(self):
        state = create_context_for_test_case(
            get_test_case("PTC-001"), source_id="TEST", requested_tool=requested_execution_tool("Run PTC-001 in k6")
        )
        state["execution_preflight"] = {"status": "ready"}
        context = type("ToolContextStub", (), {"state": State(state, {})})()
        completed = {"status": "completed", "execution_mode": "REAL", "metrics": {"total_requests": 1},
                     "artifacts": {}, "job_id": state["job_id"], "thresholds_passed": True}
        generated = {"status": "success", "message": "prepared", "file_path": "s", "artifact_path": "s"}
        with (
            patch("app.agent.generate_script", return_value=generated) as generate,
            patch("app.agent.run_real_jmeter_test", return_value=dict(completed)) as jmeter,
            patch("app.agent.run_real_k6_test", return_value=dict(completed)) as k6,
        ):
            run_test_execution_adk("Run PTC-001 in k6", context)

        self.assertEqual(generate.call_args.kwargs["tool"], "k6")
        k6.assert_called_once()
        jmeter.assert_not_called()

    def test_naming_the_runner_without_a_run_word_still_uses_that_runner_but_does_not_start_a_run(self):
        # Selection follows the named tool. Starting a run still needs a run word, as before.
        result, generate, jmeter, k6 = self.execute("PTC-003 JMeter")

        self.assertEqual(generate.call_args.kwargs["tool"], "jmeter")
        jmeter.assert_not_called()
        k6.assert_not_called()
        self.assertEqual(result["status"], "prepared")


class TestMismatchGuardStillFailsClosed(unittest.TestCase):
    def blocked(self, prompt):
        state = create_context_for_test_case(get_test_case("PTC-003"), source_id="TEST")  # k6 bound
        context = type("ToolContextStub", (), {"state": State(state, {})})()
        with (
            patch("app.agent.generate_script", side_effect=AssertionError("must not generate")),
            patch("app.agent.run_real_k6_test", side_effect=AssertionError("must not run k6")),
        ):
            return run_test_execution_adk(prompt, context), state

    def test_a_jmeter_request_against_a_k6_bound_case_runs_nothing(self):
        result, state = self.blocked("Run PTC-003 in JMeter")      # bound to k6: no selection happened

        self.assertEqual(result["status"], "blocked")
        self.assertEqual(state["execution_status"], "blocked")
        reason = result["blocked_reasons"][0]
        self.assertIn("does not match the trusted workload profile", reason)
        self.assertIn("(profile tool: k6)", reason)
        self.assertIn("using JMeter", reason)                       # tells the user how to ask


if __name__ == "__main__":
    unittest.main()

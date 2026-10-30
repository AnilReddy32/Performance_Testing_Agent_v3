"""The orchestrator must follow the flow: one stage at a time, in the fixed order.

execution -> monitoring -> security -> analysis -> report. Each stage reads what
the one before it produced. A model that answers one turn with several tool calls
used to make ADK run them concurrently: security started while the load test was
still running, saw no finished execution and reported itself blocked.
"""

import asyncio
import copy
import time
import unittest

from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import ToolContext
from google.genai import types

from Performance_Testing_Agent.orchestrator import agent as orchestrator_agent
from Performance_Testing_Agent.orchestrator.flow import one_stage_at_a_time

from test_auto_security_pipeline import JOB_ID, Harness, assessor, security_result

ORDER = [
    "record_test_case_prompt", "load_catalog_test_case", "test_execution_agent",
    "monitoring_agent", "security_agent", "analysis_agent", "report_agent",
]


def call(name):
    return types.Part(function_call=types.FunctionCall(name=name, args={}))


def response(*parts, **fields):
    return LlmResponse(content=types.Content(role="model", parts=list(parts)), **fields)


def names(llm_response):
    return [p.function_call.name for p in llm_response.content.parts if p.function_call]


class TestOneStageAtATime(unittest.TestCase):
    def setUp(self):
        self.callback = one_stage_at_a_time(ORDER)

    def test_a_turn_asking_for_security_and_execution_together_keeps_only_execution(self):
        trimmed = self.callback(None, response(call("security_agent"), call("test_execution_agent")))

        self.assertEqual(names(trimmed), ["test_execution_agent"])

    def test_the_earliest_stage_in_the_fixed_order_is_kept_whatever_order_the_model_listed_them(self):
        cases = [
            (["report_agent", "analysis_agent", "security_agent"], "security_agent"),
            (["security_agent", "monitoring_agent"], "monitoring_agent"),
            (["analysis_agent", "report_agent"], "analysis_agent"),
            (["test_execution_agent", "monitoring_agent", "security_agent"], "test_execution_agent"),
            (["test_execution_agent", "load_catalog_test_case"], "load_catalog_test_case"),
            (["test_execution_agent", "record_test_case_prompt", "load_catalog_test_case"], "record_test_case_prompt"),
        ]
        for asked, expected in cases:
            with self.subTest(asked=asked):
                trimmed = self.callback(None, response(*[call(n) for n in asked]))
                self.assertEqual(names(trimmed), [expected])

    def test_a_single_call_text_only_and_empty_responses_are_left_alone(self):
        self.assertIsNone(self.callback(None, response(call("security_agent"))))
        self.assertIsNone(self.callback(None, response(types.Part(text="done"))))
        self.assertIsNone(self.callback(None, LlmResponse()))

    def test_unknown_tools_run_after_the_known_stages_and_ties_keep_the_models_order(self):
        self.assertEqual(
            names(self.callback(None, response(call("something_else"), call("report_agent")))), ["report_agent"]
        )
        self.assertEqual(
            names(self.callback(None, response(call("alpha"), call("beta")))), ["alpha"]
        )
        self.assertEqual(
            names(self.callback(None, response(call("security_agent"), call("security_agent")))),
            ["security_agent"],
        )

    def test_text_and_the_responses_other_fields_survive(self):
        original = response(
            types.Part(text="Running the test now."), call("security_agent"), call("test_execution_agent"),
            finish_reason=types.FinishReason.STOP, error_message="note",
        )

        trimmed = self.callback(None, original)

        self.assertEqual(trimmed.content.parts[0].text, "Running the test now.")
        self.assertEqual(names(trimmed), ["test_execution_agent"])
        self.assertEqual(trimmed.finish_reason, types.FinishReason.STOP)
        self.assertEqual(trimmed.error_message, "note")
        self.assertEqual(len(original.content.parts), 3)           # the original is not modified


class TestTheRealOrchestratorIsWired(unittest.TestCase):
    def test_the_fixed_order_uses_the_real_agent_names(self):
        self.assertEqual(orchestrator_agent.STAGE_ORDER, ORDER)

    def test_the_orchestrator_enforces_it(self):
        self.assertIsNotNone(orchestrator_agent.root_agent.after_model_callback)
        asked = response(call("security_agent"), call("analysis_agent"), call("test_execution_agent"))

        callback = orchestrator_agent.root_agent.canonical_after_model_callbacks[0]
        trimmed = callback(None, asked)

        self.assertEqual(names(trimmed), ["test_execution_agent"])

    def test_the_prompt_no_longer_tells_the_model_to_call_agents_together(self):
        prompt = orchestrator_agent.ORCHESTRATOR_SYSTEM_PROMPT

        self.assertIn("Never call two agents in the same step", prompt)
        self.assertNotIn("analysis_agent - together", prompt)


# ----------------------------------------------- inside real ADK agents ----

LOG: list = []


async def _execution_stage(tool_context: ToolContext) -> dict:
    """Runs the test."""
    LOG.append(("test_execution_agent", "start", time.perf_counter(), None))
    await asyncio.sleep(0.3)
    tool_context.state["execution_status"] = "completed"
    LOG.append(("test_execution_agent", "end", time.perf_counter(), None))
    return {"status": "completed"}


async def _monitoring_stage(tool_context: ToolContext) -> dict:
    """Monitors."""
    LOG.append(("monitoring_agent", "start", time.perf_counter(), tool_context.state.get("execution_status")))
    return {"ok": True}


async def _security_stage(tool_context: ToolContext) -> dict:
    """Assesses security."""
    LOG.append(("security_agent", "start", time.perf_counter(), tool_context.state.get("execution_status")))
    return {"ok": True}


# The tools carry the orchestrator's real stage names (the ordering is by name); the
# Python names above avoid pytest collecting a function called test_execution_agent.
for _function, _name in ((_execution_stage, "test_execution_agent"),
                         (_monitoring_stage, "monitoring_agent"), (_security_stage, "security_agent")):
    _function.__name__ = _name


class AsksForEverythingAtOnce(BaseLlm):
    """Worst case: each turn it asks for every stage that has not answered yet, all together."""

    model: str = "scripted"

    async def generate_content_async(self, llm_request, stream=False):
        answered = {p.function_response.name for c in llm_request.contents for p in (c.parts or [])
                    if p.function_response}
        remaining = [n for n in ("security_agent", "monitoring_agent", "test_execution_agent") if n not in answered]
        parts = [call(n) for n in remaining] or [types.Part(text="done")]
        yield LlmResponse(content=types.Content(role="model", parts=parts))


async def run_orchestrator(callback=None):
    LOG.clear()
    agent = LlmAgent(
        name="orchestrator", model=AsksForEverythingAtOnce(),
        tools=[_execution_stage, _monitoring_stage, _security_stage],
        **({"after_model_callback": callback} if callback else {}),
    )
    service = InMemorySessionService()
    await service.create_session(app_name="t", user_id="u", session_id="s", state={"execution_status": "not_started"})
    runner = Runner(agent=agent, app_name="t", session_service=service)
    async for _ in runner.run_async(
        user_id="u", session_id="s", new_message=types.Content(role="user", parts=[types.Part(text="go")])
    ):
        pass
    return {(name, phase): (at, seen) for name, phase, at, seen in LOG}


class TestRealAdkFlow(unittest.IsolatedAsyncioTestCase):
    async def test_without_enforcement_security_starts_while_the_test_is_still_running(self):
        timeline = await run_orchestrator()

        started, finished = timeline[("security_agent", "start")], timeline[("test_execution_agent", "end")]
        self.assertLess(started[0], finished[0])             # the reported bug
        self.assertEqual(started[1], "not_started")

    async def test_with_enforcement_every_stage_waits_for_the_one_before_it(self):
        timeline = await run_orchestrator(one_stage_at_a_time(ORDER))

        execution_end = timeline[("test_execution_agent", "end")][0]
        monitoring_at, monitoring_saw = timeline[("monitoring_agent", "start")]
        security_at, security_saw = timeline[("security_agent", "start")]
        self.assertLess(timeline[("test_execution_agent", "start")][0], execution_end)
        self.assertGreater(monitoring_at, execution_end)
        self.assertGreater(security_at, monitoring_at)       # monitoring before security
        self.assertEqual((monitoring_saw, security_saw), ("completed", "completed"))
        self.assertEqual(len(LOG), 4)                        # nothing ran twice or was lost


# ------------------------------- a result produced too early is not kept ----

def too_early_result():
    result = security_result("WARNING")
    result["assessment_outcome"] = "not_assessed"
    result["live_test_result"] = {
        "status": "blocked", "reason_code": "run_not_finished",
        "reason": "Passive checks run only after the performance execution has ended.",
    }
    return result


class TestResultFromBeforeTheRunEnded(unittest.IsolatedAsyncioTestCase):
    async def test_an_explicitly_requested_assessment_is_redone_after_the_run_ended(self):
        harness = Harness()
        harness.state["security_result"] = too_early_result()

        pipeline = await harness.run("Run PTC-004 and assess the security surface.")

        self.assertEqual(pipeline["security"], "completed")          # not "already_available"
        self.assertIn("security", harness.calls)
        self.assertEqual(harness.state["security_result"]["status"], "PASS")

    async def test_the_automatic_assessment_is_redone_too(self):
        harness = Harness()
        harness.state["security_result"] = too_early_result()
        record = []

        pipeline = await harness.run("Run PTC-004.", passive=assessor(security_result(), record))

        self.assertEqual(pipeline["security"], "completed (automatic passive assessment)")
        self.assertEqual(len(record), 1)
        self.assertIsNone(harness.state["security_result"].get("live_test_result", {}).get("reason_code"))

    async def test_the_older_wording_of_the_same_block_is_recognised(self):
        harness = Harness()
        early = too_early_result()
        early["live_test_result"] = {
            "status": "blocked",
            "reason": "Live checks run only after the performance execution has ended, so they "
                      "cannot overlap or warm up its measurements.",
        }
        harness.state["security_result"] = early

        pipeline = await harness.run("Run PTC-004 and assess security.")

        self.assertEqual(pipeline["security"], "completed")

    async def test_a_result_blocked_for_any_other_reason_is_kept_as_it_is(self):
        harness = Harness()
        blocked = too_early_result()
        blocked["live_test_result"] = {"status": "blocked", "reason_code": "non_public_host",
                                       "reason": "'localhost' is not a public DNS hostname."}
        harness.state["security_result"] = copy.deepcopy(blocked)
        record = []

        pipeline = await harness.run("Run PTC-004.", passive=assessor(security_result(), record))

        self.assertEqual(pipeline["security"], "already_available")
        self.assertEqual(record, [])
        self.assertEqual(harness.state["security_result"]["live_test_result"]["reason_code"], "non_public_host")


if __name__ == "__main__":
    unittest.main()

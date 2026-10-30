"""The agent answers with the tool's SecurityResponse, in ONE answer, however it is run.

The model's own re-typed copy used to drop fields. Substituting the stored result
must not add a second answer: when the agent runs as a workflow node, a second output
fails with "Output already set. A node can produce at most one output."
"""

import json
from types import SimpleNamespace

import pytest
from google.adk.agents import LlmAgent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import AgentTool, ToolContext
from google.genai import types

from security_agent.tools.trusted_response import (
    FRESH_KEY,
    reset_trusted_result,
    use_trusted_result,
)

JOB = "JOB-" + "f" * 32
RESULT = {
    "job_id": JOB, "status": "FAIL", "security_score_basis": "x",
    "check_summary": {"total": 1},
    "check_results": [{"check_id": "cors_foreign_origin", "verdict": "failed"}],
}
LOSSY = json.dumps({"job_id": JOB, "status": "FAIL"})   # what a model re-types


def context(**state):
    return SimpleNamespace(state=dict(state))


def text_response(text="anything", **fields):
    return LlmResponse(content=types.Content(role="model", parts=[types.Part(text=text)]), **fields)


def fresh(**overrides):
    state = {"job_id": JOB, "security_result": RESULT, FRESH_KEY: True}
    state.update(overrides)
    return context(**state)


def test_a_run_starts_with_no_result_counting_as_current():
    ctx = context(**{FRESH_KEY: True})

    assert reset_trusted_result(ctx) is None
    assert ctx.state[FRESH_KEY] is False


def test_the_final_text_answer_is_replaced_by_the_stored_result_verbatim():
    replaced = use_trusted_result(fresh(), text_response(LOSSY, finish_reason=types.FinishReason.STOP))

    assert json.loads(replaced.content.parts[0].text) == RESULT
    assert len(replaced.content.parts) == 1 and replaced.content.role == "model"
    assert replaced.finish_reason == types.FinishReason.STOP          # the rest of the response is kept


def test_a_turn_that_calls_a_tool_is_never_touched():
    calling = LlmResponse(content=types.Content(role="model", parts=[
        types.Part(function_call=types.FunctionCall(name="finalize_assessment_with_live_observation", args={}))]))

    assert use_trusted_result(fresh(), calling) is None


@pytest.mark.parametrize("state", [
    {FRESH_KEY: False},                                  # an earlier run's result
    {FRESH_KEY: None},                                   # never marked
    {"security_result": None},                           # nothing stored
    {"security_result": "text"},                         # not a result
    {"job_id": "JOB-other"},                             # another job's
])
def test_nothing_is_substituted_unless_a_current_result_exists(state):
    assert use_trusted_result(fresh(**state), text_response()) is None


def test_empty_and_partial_responses_are_left_alone():
    assert use_trusted_result(fresh(), LlmResponse()) is None
    assert use_trusted_result(fresh(), text_response(partial=True)) is None


def test_a_broken_context_falls_back_to_the_model_text():
    class Exploding:
        @property
        def state(self):
            raise RuntimeError("no state")

    assert use_trusted_result(Exploding(), text_response()) is None
    assert reset_trusted_result(Exploding()) is None


# ------------------------------------------------ inside real ADK agents ----

def finalize_tool(tool_context: ToolContext) -> dict:
    """Stand-in for finalize_assessment: stores the deterministic result."""
    tool_context.state["security_result"] = RESULT
    tool_context.state[FRESH_KEY] = True
    return RESULT


class Scripted(BaseLlm):
    """Calls one tool (if any), then answers with a lossy copy. No API call."""

    model: str = "scripted"
    tool_name: str | None = None
    answer: str = LOSSY

    async def generate_content_async(self, llm_request, stream=False):
        last = llm_request.contents[-1] if llm_request.contents else None
        got_result = bool(last and any(p.function_response for p in (last.parts or [])))
        if self.tool_name and not got_result:
            part = types.Part(function_call=types.FunctionCall(name=self.tool_name, args={}))
        else:
            part = types.Part(text=self.answer)
        yield LlmResponse(content=types.Content(role="model", parts=[part]))


def security_agent(*, hooks, finalizes=True):
    extra = dict(before_agent_callback=reset_trusted_result, after_model_callback=use_trusted_result) if hooks else {}
    inner = LlmAgent(
        name="security_operations_agent",
        model=Scripted(tool_name="finalize_tool" if finalizes else None),
        tools=[finalize_tool], **extra,
    )
    return LlmAgent(
        name="security_agent", model=Scripted(tool_name="security_operations_agent"),
        tools=[AgentTool(agent=inner)], **extra,
    )


async def run(host, state=None):
    service = InMemorySessionService()
    await service.create_session(app_name="t", user_id="u", session_id="s", state={"job_id": JOB, **(state or {})})
    runner = Runner(agent=host, app_name="t", session_service=service)
    answers, error = [], None
    try:
        async for event in runner.run_async(
            user_id="u", session_id="s",
            new_message=types.Content(role="user", parts=[types.Part(text="assess security")]),
        ):
            if event.content and event.content.parts and event.author == "security_agent":
                answers.extend(p.text for p in event.content.parts if p.text)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
    return answers, error


def as_workflow_node(agent):
    """How the orchestrator's ADK-web path runs a missing stage (orchestrator/agent.py)."""
    async def after(callback_context):
        await callback_context.run_node(agent.model_copy(update={"mode": "single_turn"}), node_input="assess")
        return None

    return LlmAgent(name="host", model=Scripted(answer="ok"), after_agent_callback=after)


@pytest.mark.asyncio
async def test_run_directly_there_is_exactly_one_answer_and_it_is_the_complete_result():
    answers, error = await run(security_agent(hooks=True))

    assert error is None
    assert len(answers) == 1                              # not the model copy followed by a second answer
    assert json.loads(answers[0]) == RESULT


@pytest.mark.asyncio
async def test_run_as_a_workflow_node_there_is_no_second_output_error():
    # The case that failed: "ValueError: Output already set. A node can produce at most one output."
    answers, error = await run(as_workflow_node(security_agent(hooks=True)))

    assert error is None
    assert len(answers) == 1
    assert json.loads(answers[0]) == RESULT


@pytest.mark.asyncio
async def test_without_the_hooks_the_model_copy_is_the_answer():
    answers, error = await run(security_agent(hooks=False))

    assert error is None and "check_results" not in answers[-1]       # the original symptom


@pytest.mark.asyncio
async def test_a_result_left_over_from_an_earlier_run_is_never_substituted():
    leftover = {"security_result": RESULT, FRESH_KEY: True}

    for host in (security_agent(hooks=True, finalizes=False),
                 as_workflow_node(security_agent(hooks=True, finalizes=False))):
        answers, error = await run(host, leftover)

        assert error is None
        assert answers and all("check_results" not in text for text in answers)

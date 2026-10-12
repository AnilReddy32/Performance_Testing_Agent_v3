"""
Orchestrator-level tools.

record_test_case_prompt is the one new piece needed so the final report
can include the user's original request verbatim: it's an ordinary tool
call (same pattern every other agent in this codebase already uses to
write results into shared session state via tool_context.state), not a
framework-level callback.
"""

from google.adk.tools import ToolContext


def record_test_case_prompt(prompt: str, tool_context: ToolContext) -> dict:
    """
    Records the user's exact original request text into shared session
    state under "test_case_prompt". Must be called ONCE, at the very start
    of handling any new user request, BEFORE any other agent runs.

    prompt: the user's message, copied verbatim - never paraphrased.
    """
    tool_context.state["test_case_prompt"] = prompt
    return {"recorded": True}
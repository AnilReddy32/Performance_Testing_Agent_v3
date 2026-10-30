"""Keep the LLM-driven orchestrator on the fixed stage order, one stage at a time.

The flow is execution -> monitoring -> security -> analysis -> report, and each
stage reads what the one before it produced. The orchestrator model is told to
call one agent at a time, but a model can still answer a single turn with several
tool calls, and ADK runs those calls concurrently. Security then started while the
load test was still running, saw no finished execution, and reported itself
blocked.

The ordering is enforced here in code instead of being left to the model: when a
turn asks for more than one tool, only the earliest in the fixed order is kept.
The model sees that call's result and asks for the next one on its next turn.
"""

from collections.abc import Callable, Sequence
from typing import Any

from google.adk.models.llm_response import LlmResponse
from google.genai import types

from .logger import logger


def one_stage_at_a_time(
    order: Sequence[str],
) -> Callable[[Any, LlmResponse], LlmResponse | None]:
    """Build an ADK after_model_callback that keeps one tool call per turn.

    ``order`` lists the tool names in the order they must run. Tools not listed
    sort last; if a turn repeats the same tool or lists equals, the model's own
    order breaks the tie.
    """
    rank = {name: position for position, name in enumerate(order)}

    def callback(callback_context: Any, llm_response: LlmResponse) -> LlmResponse | None:
        content = llm_response.content
        parts = list(content.parts) if content is not None and content.parts else []
        calls = [part for part in parts if part.function_call]
        if len(calls) <= 1:
            return None
        _, kept = min(
            enumerate(calls),
            key=lambda item: (rank.get(item[1].function_call.name, len(rank)), item[0]),
        )
        deferred = [part.function_call.name for part in calls if part is not kept]
        logger.info(
            "Orchestrator asked for %d tools in one turn; running %s now and deferring %s "
            "until it finishes.",
            len(calls),
            kept.function_call.name,
            deferred,
        )
        trimmed = [part for part in parts if not part.function_call or part is kept]
        return llm_response.model_copy(
            update={"content": types.Content(role=content.role, parts=trimmed)}
        )

    return callback

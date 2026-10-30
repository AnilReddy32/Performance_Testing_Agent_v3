"""Make the agent's final answer the tool-built SecurityResponse.

The security agent is an LLM agent whose last step is to "return the result".
A model re-typing a large JSON document can drop or alter fields (it dropped
the per-check verdicts and a dozen contract fields in practice). The result the
finalization tool stored in session state is deterministic, so once it exists
for the current run it replaces the text the model was about to give.

It is swapped in inside the model's own final response (an after-model hook), not
added as a second answer afterwards: when this agent runs as a workflow node a
node may produce only one output, and a second answer from an after-agent hook
fails with "Output already set. A node can produce at most one output."
"""

import json
import logging
from typing import Any

from google.genai import types as genai_types

logger = logging.getLogger(__name__)

FRESH_KEY = "security_result_fresh"


def reset_trusted_result(callback_context: Any) -> None:
    """Start of a run: nothing in state counts as this run's result yet."""
    try:
        callback_context.state[FRESH_KEY] = False
    except Exception:  # never let bookkeeping stop an assessment
        logger.exception("Could not reset the security result marker")
    return None


def use_trusted_result(callback_context: Any, llm_response: Any) -> Any | None:
    """After a model turn: if it is the final text answer, give the stored result instead."""
    try:
        content = llm_response.content
        if content is None or not content.parts or getattr(llm_response, "partial", None):
            return None
        if any(part.function_call or part.function_response for part in content.parts):
            return None  # still working: this turn calls a tool
        state = callback_context.state
        result = state.get("security_result")
        if state.get(FRESH_KEY) is not True or not isinstance(result, dict):
            return None
        if result.get("job_id") != state.get("job_id"):
            return None
        return llm_response.model_copy(
            update={
                "content": genai_types.Content(
                    role="model",
                    parts=[genai_types.Part(text=json.dumps(result, ensure_ascii=False))],
                )
            }
        )
    except Exception:  # fall back to the model's own text
        logger.exception("Could not return the stored security result")
        return None

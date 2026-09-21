from typing import Any


SUPPORTED_INTENTS = {
    "execute_test",
    "generate_script",
    "generate_test_data",
    "prepare_environment",
    "invalid",
}


TOOL_MAPPING = {
    "execute_test": "run_execution_workflow",
    "generate_script": "generate_script",
    "generate_test_data": "generate_test_data",
    "prepare_environment": "prepare_environment",
}


def dispatch_tool(plan: dict[str, Any]) -> str:
    """
    Determine which high-level ADK capability should handle a
    structured performance-testing plan.

    This function performs TOOL SELECTION only.

    It does not execute the selected tool.

    Args:
        plan: Structured plan produced by the Test Planner.

    Returns:
        Name of the high-level capability responsible for the request.

    Raises:
        ValueError: If the planner output is invalid.
    """

    if not isinstance(plan, dict):
        raise ValueError("Test plan must be a dictionary.")

    required_fields = {
        "intent",
        "test_type",
        "tool",
        "application",
        "scenario",
        "api_name",
        "users",
        "duration",
    }

    actual_fields = set(plan.keys())

    if actual_fields != required_fields:
        missing_fields = required_fields - actual_fields
        extra_fields = actual_fields - required_fields

        raise ValueError(
            "Invalid test plan schema. "
            f"Missing fields: {missing_fields}. "
            f"Extra fields: {extra_fields}."
        )

    intent = plan["intent"]

    if intent not in SUPPORTED_INTENTS:
        raise ValueError(
            f"Unsupported intent: {intent}"
        )

    if intent == "invalid":
        return "stop"

    return TOOL_MAPPING[intent]
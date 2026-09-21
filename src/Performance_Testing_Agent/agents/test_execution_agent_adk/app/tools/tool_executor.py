from typing import Any

from app.tools.test_planner import TestPlanner
from app.tools.script_generation import generate_script
from app.tools.data_generation import generate_test_data
from app.tools.environment import prepare_environment
from app.tools.execution_workflow import run_execution_workflow
from app.tools.tool_dispatcher import dispatch_tool


def execute_dispatched_tool(plan: dict[str, Any]) -> dict:
    selected_tool = dispatch_tool(plan)

    if selected_tool == "stop":
        return {
            "status": "rejected",
            "message": "I can only help with performance-testing requests.",
        }

    if selected_tool == "generate_script":
        return generate_script(
            tool=plan["tool"],
            application=plan["application"],
            scenario=plan["scenario"],
            api_name=plan["api_name"],
        )

    if selected_tool == "generate_test_data":
        data_type = plan["scenario"] or "transactions"

        return generate_test_data(
            data_type=data_type,
            count=plan["users"] if plan["users"] > 0 else 100,
            output_format="csv",
            requirements=plan["application"],
        )

    if selected_tool == "prepare_environment":
        return prepare_environment(
            application=plan["application"],
            scenario=plan["scenario"],
            environment="test",
            users=plan["users"] if plan["users"] > 0 else 1,
            requirements=plan["api_name"],
        )

    if selected_tool == "run_execution_workflow":
        # k6 execution uses the real k6 CLI.
        # JMeter and Gatling continue using the existing
        # Fake MCP execution path for now.
        use_real_execution = plan["tool"].lower() == "k6"

        execution_target = (
            "http://localhost:8000"
            if plan["tool"].lower() == "k6"
            else "http://localhost"
        )

        return run_execution_workflow(
            tool=plan["tool"],
            test_type=plan["test_type"],
            users=plan["users"],
            duration=plan["duration"],
            target=execution_target,
            application=plan["application"],
            scenario=plan["scenario"],
            api_name=plan["api_name"],
            real_execution=use_real_execution,
        )

    raise ValueError(
        f"No executor implemented for capability: {selected_tool}"
    )


def handle_test_request(user_request: str) -> dict:
    planner = TestPlanner()

    planning_result = planner.plan(user_request)

    if planning_result.get("status") != "success":
        return planning_result

    plan = planning_result["plan"]

    return execute_dispatched_tool(plan)
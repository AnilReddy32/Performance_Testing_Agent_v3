from app.tools.script_generation import generate_script
from app.tools.data_generation import generate_test_data
from app.tools.environment import prepare_environment
from app.tools.execution import execute_test
from app.tools.monitoring import monitor_execution
from app.tools.result_formatter import format_execution_result
from app.analysis_agent.handoff import prepare_analysis_handoff

def run_execution_workflow(
    tool: str = "jmeter",
    test_type: str = "load",
    users: int = 1,
    duration: int = 60,
    ramp_up: int = 60,
    target: str = "http://localhost",
    application: str = "Unknown",
    scenario: str = "Performance Test",
    api_name: str = "Unknown",
    generate_test_data_artifact: bool = True,
    data_type: str = "transactions",
    data_count: int = 100,
    data_format: str = "csv",
    prepare_environment_artifact: bool = True,
    requirements: str = "",
    real_execution: bool = False,
) -> dict:

    if users < 1:
        return {
            "status": "error",
            "message": "Users must be greater than zero.",
        }

    if duration < 1:
        return {
            "status": "error",
            "message": "Duration must be greater than zero.",
        }

    workflow_steps = []

    # ---------------------------------------------------------
    # STEP 1: Generate performance-testing script
    # ---------------------------------------------------------

    script_result = generate_script(
        tool=tool,
        application=application,
        scenario=scenario,
        api_name=api_name,
    )

    if script_result.get("status") != "success":
        return {
            "status": "error",
            "message": "Script generation failed.",
            "script_result": script_result,
        }

    workflow_steps.append("script_generated")

    # ---------------------------------------------------------
    # STEP 2: Generate test data
    # ---------------------------------------------------------

    data_result = {}

    if generate_test_data_artifact:
        data_result = generate_test_data(
            data_type=data_type,
            count=data_count,
            output_format=data_format,
            requirements=requirements,
        )

        if data_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Test-data generation failed.",
                "script_result": script_result,
                "data_result": data_result,
            }

        workflow_steps.append("test_data_generated")

    # ---------------------------------------------------------
    # STEP 3: Prepare environment
    # ---------------------------------------------------------

    environment_result = {}

    if prepare_environment_artifact:
        environment_result = prepare_environment(
            application=application,
            scenario=scenario,
            environment="test",
            users=users,
            requirements=requirements,
        )

        if environment_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Environment preparation failed.",
                "script_result": script_result,
                "data_result": data_result,
                "environment_result": environment_result,
            }

        workflow_steps.append("environment_prepared")



    # ---------------------------------------------------------
    # Existing Fake MCP execution path
    # ---------------------------------------------------------

    execution_result = execute_test(
        tool=tool,
        test_type=test_type,
        users=users,
        duration=duration,
        ramp_up=ramp_up,
        target=target,
        application=application,
        scenario=scenario,
        api_name=api_name,
        additional_parameters=requirements,
    )

    if execution_result.get("status") != "success":
        return {
            "status": "error",
            "message": "Performance test execution failed to start.",
            "workflow_steps": workflow_steps,
            "script_result": script_result,
            "data_result": data_result,
            "environment_result": environment_result,
            "execution_result": execution_result,
        }

    workflow_steps.append("execution_started")

    # ---------------------------------------------------------
    # Existing Fake MCP monitoring
    # ---------------------------------------------------------

    monitoring_result = monitor_execution(
        execution_id=execution_result["execution_id"]
    )

    if monitoring_result.get("status") != "completed":
        return {
            "status": "error",
            "message": "Performance test monitoring failed.",
            "workflow_steps": workflow_steps,
            "script_result": script_result,
            "data_result": data_result,
            "environment_result": environment_result,
            "execution_result": execution_result,
            "monitoring": monitoring_result,
        }

    workflow_steps.append("execution_completed")

    # ---------------------------------------------------------
    # Existing standardized 13-field result
    # ---------------------------------------------------------

    standardized_result = format_execution_result(
        execution_result=execution_result,
        monitoring_result=monitoring_result,
    )

    workflow_steps.append("result_standardized")

    # ---------------------------------------------------------
    # Existing Analysis Agent handoff
    # ---------------------------------------------------------

    analysis_handoff = prepare_analysis_handoff(
        standardized_result
    )

    workflow_steps.append("analysis_handoff_ready")

    return analysis_handoff
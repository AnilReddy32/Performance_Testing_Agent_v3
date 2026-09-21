from app.mcp.execution_service import MCPExecutionService


mcp_service = MCPExecutionService()


def execute_test(
    tool: str = "jmeter",
    test_type: str = "load",
    users: int = 1,
    duration: int = 60,
    ramp_up: int = 60,
    target: str = "http://localhost",
    application: str = "Unknown",
    scenario: str = "Performance Test",
    api_name: str = "Unknown",
    additional_parameters: str = "",
) -> dict:
    """
    Execute a performance test through MCP.

    The execution is delegated to MCPExecutionService.

    Default values are used when optional execution parameters
    are not provided.
    """

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

    response = mcp_service.start_execution(
        tool=tool,
        test_type=test_type,
        users=users,
        duration=duration,
        ramp_up=ramp_up,
        target=target,
        application=application,
        scenario=scenario,
        api_name=api_name,
        additional_parameters=additional_parameters,
    )

    if response.get("status") != "running":
        return {
            "status": "error",
            "message": "Performance test execution failed to start.",
            "mcp_response": response,
        }

    return {
        "status": "success",
        "message": "Performance test execution started successfully.",
        "execution_id": response["execution_id"],
        "execution_status": response["status"],
        "application": application,
        "scenario": scenario,
        "api_name": api_name,
        "tool": tool,
        "test_type": test_type,
    }
from app.mcp.mcp_client import MCPClient


class MCPExecutionService:
    """
    Service layer between the Test Execution Agent and MCP.

    This service owns a single MCPClient instance so that execution
    state is shared between:

        start execution
        ↓
        check status
        ↓
        get metrics

    The current MCP implementation uses FakeMCPServer.
    """

    def __init__(self):
        self.client = MCPClient()

    def start_execution(
        self,
        tool: str,
        test_type: str,
        users: int,
        duration: int,
        ramp_up: int,
        target: str,
        application: str,
        scenario: str,
        api_name: str,
        additional_parameters: str = "",
    ) -> dict:
        """
        Start a performance-test execution through MCP.
        """

        return self.client.run_test(
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

    def get_status(self, execution_id: str) -> dict:
        """
        Retrieve the current execution status from MCP.
        """

        if not execution_id:
            return {
                "status": "error",
                "message": "Execution ID is required.",
            }

        return self.client.get_execution_status(execution_id)

    def get_metrics(self, execution_id: str) -> dict:
        """
        Retrieve execution metrics from MCP.

        Metrics returned by the current Fake MCP are simulated.
        """

        if not execution_id:
            return {
                "status": "error",
                "message": "Execution ID is required.",
            }

        return self.client.get_live_metrics(execution_id)
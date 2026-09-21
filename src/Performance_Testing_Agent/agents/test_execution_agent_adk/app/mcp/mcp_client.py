from app.mcp.fake_mcp_server import FakeMCPServer


class MCPClient:
    """
    Client used by the Test Execution Agent to communicate
    with the MCP server.

    Currently connected to FakeMCPServer.
    """

    def __init__(self):
        self.server = FakeMCPServer()

    def run_test(
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

        return self.server.run_test(
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

    def get_execution_status(
        self,
        execution_id: str,
    ) -> dict:

        return self.server.get_execution_status(
            execution_id
        )

    def get_live_metrics(
        self,
        execution_id: str,
    ) -> dict:

        return self.server.get_live_metrics(
            execution_id
        )
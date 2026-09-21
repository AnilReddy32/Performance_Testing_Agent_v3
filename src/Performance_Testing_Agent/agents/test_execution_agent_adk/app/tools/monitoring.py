import time

from app.tools.execution import mcp_service


def monitor_execution(
    execution_id: str,
    poll_interval: int = 2,
) -> dict:
    """
    Monitor a running performance-test execution through MCP.

    The monitoring process:
        1. Checks execution status through MCP.
        2. Waits while execution is running.
        3. Retrieves metrics after completion.

    Metrics returned by the current MCP implementation are simulated.
    """

    if not execution_id:
        return {
            "status": "error",
            "message": "Execution ID is required.",
        }

    if poll_interval < 1:
        poll_interval = 1

    while True:

        status_response = mcp_service.get_status(
            execution_id
        )

        status = status_response.get("status")

        if status == "not_found":
            return {
                "status": "error",
                "message": (
                    f"Execution '{execution_id}' was not found."
                ),
            }

        if status == "completed":

            metrics = mcp_service.get_metrics(
                execution_id
            )

            if metrics.get("status") == "not_found":
                return {
                    "status": "error",
                    "message": (
                        f"Metrics for execution "
                        f"'{execution_id}' were not found."
                    ),
                }

            return {
                "status": "completed",
                "execution_id": execution_id,
                "metrics": metrics,
            }

        time.sleep(poll_interval)
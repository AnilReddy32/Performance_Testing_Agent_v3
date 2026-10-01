import time

from app.tools.execution import mcp_service


def monitor_execution(
    execution_id: str,
    poll_interval: int = 2,
    max_wait_seconds: int = 30,
) -> dict:
    """
    Monitor a running performance-test execution through MCP.

    The monitoring process:
        1. Checks execution status through MCP.
        2. Waits while execution is running.
        3. Retrieves metrics after completion.

    Metrics returned by the current MCP implementation are simulated.

    CHANGE: added max_wait_seconds (default 30) - the original loop had
    no upper bound and would poll forever if status never reached
    "completed" (e.g. if this call gets re-invoked/restarted before the
    fake server's own ~5s simulated completion delay elapses, each
    restart resets its internal clock via a brand-new execution_id, so
    the loop could genuinely never converge). This bound guarantees the
    tool always returns within max_wait_seconds, instead of hanging
    indefinitely - it does not change behavior for the normal case,
    where completion still happens well within this bound.
    """

    if not execution_id:
        return {
            "status": "error",
            "message": "Execution ID is required.",
        }

    if poll_interval < 1:
        poll_interval = 1

    elapsed = 0

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

        if elapsed >= max_wait_seconds:
            return {
                "status": "error",
                "message": (
                    f"Execution '{execution_id}' did not reach "
                    f"'completed' status within {max_wait_seconds} "
                    f"seconds (last status: '{status}'). This usually "
                    f"means the execution was restarted with a new "
                    f"execution_id before it could finish - check "
                    f"whether the caller is re-invoking this tool "
                    f"before it has a chance to complete."
                ),
            }

        time.sleep(poll_interval)
        elapsed += poll_interval
import random
import time
import uuid


class FakeMCPServer:
    """
    Simulates the MCP server used by the Test Execution Agent.

    The fake server allows us to validate the complete execution
    workflow before integrating real JMeter, k6, or Gatling execution.
    """

    def __init__(self):
        self.executions = {}

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
        """
        Start a simulated performance-test execution.
        """

        execution_id = f"JOB-{uuid.uuid4().hex[:8]}"

        self.executions[execution_id] = {
            "tool": tool,
            "test_type": test_type,
            "users": users,
            "duration": duration,
            "ramp_up": ramp_up,
            "target": target,
            "application": application,
            "scenario": scenario,
            "api_name": api_name,
            "additional_parameters": additional_parameters,
            "started_at": time.time(),
            "status": "running",
        }

        return {
            "status": "running",
            "execution_id": execution_id,
        }

    def get_execution_status(
        self,
        execution_id: str,
    ) -> dict:
        """
        Return the current simulated execution status.
        """

        execution = self.executions.get(execution_id)

        if execution is None:
            return {
                "status": "not_found",
            }

        elapsed_time = time.time() - execution["started_at"]

        # Simulate completion after a short period.
        if elapsed_time >= 5:
            execution["status"] = "completed"

        return {
            "status": execution["status"],
            "execution_id": execution_id,
        }

    def get_live_metrics(
        self,
        execution_id: str,
    ) -> dict:
        """
        Return simulated performance metrics for a completed execution.
        """

        execution = self.executions.get(execution_id)

        if execution is None:
            return {
                "status": "not_found",
            }

        total_requests = random.randint(
            100000,
            500000,
        )

        failed_requests = random.randint(
            0,
            int(total_requests * 0.02),
        )

        successful_requests = (
            total_requests - failed_requests
        )

        avg_response_time = round(
            random.uniform(150, 1000),
            2,
        )

        p95_response_time = round(
            avg_response_time * random.uniform(1.2, 1.8),
            2,
        )

        max_response_time = round(
            p95_response_time * random.uniform(1.1, 1.5),
            2,
        )

        throughput = round(
            random.uniform(100, 500),
            2,
        )

        error_rate = round(
            (failed_requests / total_requests) * 100,
            2,
        )

        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "max_response_time": max_response_time,
            "throughput": throughput,
            "error_rate": error_rate,
            "http_status": 200,
        }
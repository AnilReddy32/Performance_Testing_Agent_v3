# from google.adk.agents import LlmAgent
# from google.adk.models.lite_llm import LiteLlm
# from google.adk.tools import ToolContext

# from ..config import LITELLM_MODEL_NAME, TEMPERATURE


# def run_test_execution(tool_context: ToolContext) -> dict:
#     """Executes the banking application's performance/load test scenario.

#     Takes no arguments. Returns the raw performance metrics produced by the
#     test run (job id, request counts, response times, throughput, error
#     rate), and also stores them in shared session state under
#     "test_execution_result" so other agents (e.g. analysis, report) can use
#     the exact same numbers later in this conversation.
#     """

#     print("===== Test Execution Agent: run_test_execution =====")

#     result = {
#         "job_id": "JOB1001",
#         "application": "Banking",
#         "scenario": "Load Test",
#         "api_name": "Fund Transfer",

#         "total_requests": 10000,
#         "successful_requests": 9985,
#         "failed_requests": 15,

#         "avg_response_time": 1.45,
#         "p95_response_time": 2.20,
#         "max_response_time": 3.50,

#         "throughput": 950.4,
#         "error_rate": 0.15,

#         "http_status": 200,
#     }

#     tool_context.state["test_execution_result"] = result

#     return result


# test_execution_agent = LlmAgent(
#     name="test_execution_agent",
#     model=LiteLlm(
#         model=LITELLM_MODEL_NAME,
#         temperature=TEMPERATURE,
#     ),
#     mode="single_turn",  # call-and-return, like an ADK workflow node, not a sticky chat transfer
#     instruction=(
#         "You are the Test Execution Agent for a Banking AI Performance "
#         "Testing System. Whenever you are asked to do anything - run/execute "
#         "a performance test, a load test, a script, or to report throughput, "
#         "response time, or concurrent-user metrics - call run_test_execution "
#         "and report back its exact results. Never invent or alter numbers."
#     ),
#     description=(
#         "Executes JMeter/k6-style performance and load tests against the "
#         "banking application and reports throughput, response time, and "
#         "error-rate metrics."
#     ),
#     tools=[run_test_execution],
# )

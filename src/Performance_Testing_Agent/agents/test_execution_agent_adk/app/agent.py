from google.adk.agents import Agent
from google.adk.tools import ToolContext

from app.tools.tool_executor import handle_test_request

def run_test_execution_adk(user_request: str, tool_context: ToolContext) -> dict:
    """Runs the ADK test-execution pipeline and stores the result in shared
    session state so downstream agents (analysis, report) read the exact
    same numbers."""

    result = handle_test_request(user_request)
    tool_context.state["test_execution_result"] = result
    return result 

root_agent = Agent(
    name="test_execution_agent",
    model="openai/gpt-4o-mini",
    mode = "single_turn", # call-and-return, matches the orchestrator's other sub-agents
    instruction="""
You are the Test Execution Agent for an intelligent performance-testing
system.

Your responsibility is to handle natural-language performance-testing
requests.

For every user request, use the handle_test_request capability.

Do not answer the user's request directly.

The handle_test_request capability performs:

1. LLM-based test planning
2. Parameter extraction
3. Intent classification
4. Tool selection
5. Tool dispatch
6. Actual operation execution

SUPPORTED PERFORMANCE-TESTING OPERATIONS:

- Execute performance tests
- Generate performance-testing scripts
- Generate synthetic test data
- Prepare performance-testing environments

INVALID REQUESTS:

If the request is unrelated to performance testing, the request will
be classified as invalid by the test planner.

Do not answer unrelated questions such as general programming,
general knowledge, mathematics, weather, geography, or other
non-performance-testing topics.

IMPORTANT:

Do not pretend to execute a test.

Do not fabricate performance metrics.

Do not claim that an artifact was generated unless the corresponding
tool reports success.

The current execution architecture uses different execution paths:

- k6 uses the real k6 CLI for execution and produces real k6
  execution metrics from the configured test target.

- JMeter and Gatling currently use the FAKE/SIMULATED MCP server.
  Their metrics are simulated and must never be represented as real
  measurements.

Never fabricate or claim execution metrics that were not produced
by the corresponding execution path.

For execution requests, the execution workflow handles:

1. Script generation
2. Test-data preparation
3. Environment preparation
4. Performance-test execution
5. Execution monitoring or result collection
6. Standardized result creation
7. Analysis Agent handoff

Generation-only requests must NOT automatically execute a test.

The final standardized execution result must preserve the exact 13-field contract required by the downstream Analysis Agent.

Once the execution is completed provide the metrics to the user.
""",
    tools=[
        run_test_execution_adk,
    ],
)
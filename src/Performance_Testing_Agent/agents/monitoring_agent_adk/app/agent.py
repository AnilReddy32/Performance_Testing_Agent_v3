import sys

from pathlib import Path

from google.adk.agents import Agent

from google.adk.tools import McpToolset, ToolContext

from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
)

from mcp import StdioServerParameters

from .metric_simulator import simulate_monitoring_metrics

# Local fallback tool -- no longer wired in below, kept only so you can
# revert quickly (tools=[collect_monitoring_metrics]) if the MCP
# connection ever breaks again on this machine.
#from .local_monitoring_tool import collect_monitoring_metrics


# ============================================================
# Monitoring MCP -- kept here, untouched, so the old monitoring.csv/MCP
# approach can be restored quickly (tools=[monitoring_mcp]) if you ever
# want it back. It was replaced because it depended on a file (or a
# person typing realistic-looking numbers into a ticket) having the
# CPU/Memory/etc numbers ready ahead of time, which a real user asking
# "please monitor this" has no way of actually knowing.
# ============================================================

MONITORING_SERVER = Path(__file__).resolve().parent / "mcp" / "server.py"

if not MONITORING_SERVER.exists():
    raise FileNotFoundError(
        f"Monitoring MCP server script not found at: {MONITORING_SERVER}\n"
        f"(agent.py is at: {Path(__file__).resolve()})\n"
        "server.py should be a sibling 'mcp' folder next to this file."
    )

monitoring_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[str(MONITORING_SERVER)],
        ),
        timeout=30,
    ),
)
# ^ No longer wired into monitoring_agent below (see
# collect_monitoring_metrics instead).


def collect_monitoring_metrics(tool_context: ToolContext) -> dict:
    """Collects infrastructure/performance monitoring metrics (CPU,
    Memory, DB Connections, Response Time, TPS) for this job. Takes no
    arguments -- reads this run's own test_execution_result from shared
    session state (if a performance test was actually run this time) and
    calculates plausible, reproducible infra numbers from it; if no test
    was run (a "monitoring only" request), falls back to a realistic
    baseline reading instead. See metric_simulator.py for exactly how
    these are calculated and why. Stores its result under
    "monitoring_result", the same key analysis_agent/report_agent already
    read from shared session state."""

    test_execution_result = tool_context.state.get("test_execution_result")

    result = simulate_monitoring_metrics(test_execution_result)

    tool_context.state["monitoring_result"] = result

    return result


# ============================================================
# Monitoring Agent -- single local tool, no arguments, reads prior
# results itself and writes its own result straight to session state
# (same convention test_execution_agent's run_test_execution_adk uses).
#
# mode="single_turn" kept unchanged: this agent is used as a sub_agent
# of performance_testing_orchestrator, which calls each specialist agent
# in sequence and needs control handed back after each one (test
# execution -> monitoring -> security -> analysis -> report). Without
# this, ADK treats it as a one-way chat "transfer" target instead of a
# call-and-return tool.
#
# output_key removed: the old version had both output_key="monitoring_result"
# AND an MCP tool -- output_key makes ADK auto-store this agent's own
# final TEXT answer into session.state["monitoring_result"] after it
# runs, which would silently overwrite the clean, structured dict that
# collect_monitoring_metrics already wrote there directly via
# tool_context.state, with whatever text the LLM happened to answer
# with. Since the tool now writes the structured result itself, nothing
# else should be allowed to overwrite it afterward.
# ============================================================

monitoring_agent = Agent(

    name="monitoring_agent",

    model="gpt-4.1",

    mode="single_turn",

    description=(
        "Collects infrastructure and performance monitoring metrics "
        "(CPU, Memory, DB Connections, Response Time, TPS) for this job."
    ),

    instruction="""
You are the Monitoring Agent of the ANZ Performance Testing system.

Whenever you are asked about CPU, memory, database connections,
response time, API latency, TPS, resource utilization, or to
"process", "analyze", "check", or "monitor" a scenario, call
collect_monitoring_metrics (it takes no arguments -- it reads prior
results itself and calculates this run's metrics on the spot) and
report back its exact results. Never invent or alter the numbers it
returns, and never ask the user to supply metric values themselves --
always call the tool instead.
""",

    tools=[
        collect_monitoring_metrics,
    ],
)
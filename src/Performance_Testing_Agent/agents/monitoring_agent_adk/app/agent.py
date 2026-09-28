import sys
 
from pathlib import Path
 
from google.adk.agents import Agent
 
from google.adk.tools import McpToolset
 
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StdioConnectionParams,
)
 
from mcp import StdioServerParameters
 
# Local fallback tool -- no longer wired in below, kept only so you can
# revert quickly (tools=[collect_monitoring_metrics]) if the MCP
# connection ever breaks again on this machine.
#from .local_monitoring_tool import collect_monitoring_metrics
 
 
# ============================================================
# Monitoring MCP -- this is now the tool actually wired in below.
# The earlier "Connection closed" error was caused by server.py's
# `from mcp.server.fastmcp import FastMCP` failing under mcp 2.x
# (FastMCP was renamed/moved in that release). Pinning the
# environment to `mcp<2` (mcp==1.30.0) restored the module server.py
# imports, so the MCP subprocess can now actually start and complete
# its handshake with ADK.
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
 
 
# ============================================================
# Monitoring Agent -- single agent, MCP tool directly attached,
# JSON output enforced through instruction (not output_schema,
# since ADK doesn't allow tools + output_schema on one agent).
# ============================================================
 
monitoring_agent = Agent(
 
    name="monitoring_agent",
 
    model="gpt-4.1",
 
    description=(
        "Collects infrastructure and performance "
        "monitoring metrics through MCP."
    ),
 
    instruction="""
You are the Monitoring Agent of the ANZ Performance Testing system.
 
WHEN TO USE THE MONITORING MCP TOOL (always do this):
Treat any of the following as a request for monitoring data, and in
every one of these cases call the Monitoring MCP tool immediately,
before writing your final answer:
- Any mention of CPU, memory, database connections, response time,
  API latency, or TPS.
- Any request to "process", "analyze", "check", "monitor", or
  "identify" a scenario, bottleneck, correlation, or metric.
- Any request that references "the supplied performance-testing log"
  or "execution data" -- this means data the MCP server already has
  access to. Never ask the user to paste or supply a log or metrics
  yourself -- always call the tool instead.
- If the MCP tool call itself fails or returns nothing, that is the
  only time you report a metric as unavailable -- you must still
  have attempted the tool call first.
 
RULES:
- Return actual values received from the MCP server. Never invent
  monitoring values.
- Do not modify the MCP server's results.
 
INPUT YOU MAY RECEIVE:
If a Test Execution output is available in the conversation,
extract and preserve:

- job_id
- application
- scenario

and include them in the final JSON response.

Use monitoring MCP only for:
- cpu_usage
- memory_usage
- db_connections
- response_time
- tps
- alerts

Do not change the Test Execution metadata.
 
FINAL OUTPUT FORMAT -- NO EXCEPTIONS:

Call the Monitoring MCP tool and use the returned values.
Return the MCP tool result as a Python dictionary object.
Do not serialize the response.
Do not convert the response to a JSON string.
Do not wrap the response in markdown.
Do not rewrite field names.
Return the result in the following dictionary structure:
 
{
  "job_id": "<from the Test execution output block, or \\"unknown\\" if none was given>",
  "application": "<from the Test execution output block, or \\"unknown\\">",
  "scenario": "<from the Test execution output block, or \\"unknown\\">",
  "cpu_usage": <actual number from the MCP server, or 0 if unavailable>,
  "memory_usage": <actual number from the MCP server, or 0 if unavailable>,
  "db_connections": <actual number from the MCP server, or 0 if unavailable>,
  "response_time": <actual number from the MCP server, or 0 if unavailable>,
  "tps": <actual number from the MCP server, or 0 if unavailable>,
  "status": "<\\"OK\\" if no alerts, \\"WARNING\\" or \\"CRITICAL\\" mirroring the worst alert from the MCP server, or \\"UNAVAILABLE\\" if any metric could not be retrieved>",
  "alerts": [<exact alert strings from the MCP server, or an empty list>]
}
 
Never invent numbers to fill this shape -- if the MCP server didn't
return a metric, use 0 for that field and set status to
"UNAVAILABLE" instead.
""",
 
    tools=[
        monitoring_mcp,
    ],
    output_key="monitoring_result",
)
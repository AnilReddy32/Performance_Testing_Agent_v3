"""
Runs the REAL agents (LLM + tools, via ADK's Runner) end to end:
Analysis Agent -> (session state) -> Report Agent.
 
This is what "running the project for real" looks like, as opposed to
demo_pipeline.py which only exercises the plain-Python tool functions.
 
Requires:
  export OPENAI_API_KEY=sk-...
 
Usage:
  python run_agents.py
"""
import asyncio
import json
import os
 
from dotenv import load_dotenv
load_dotenv()  # reads .env from the project root automatically
 
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
 
from app.agents.analysis.agent import analysis_agent
from app.agents.report.agent import report_agent
 
APP_NAME = "anz_perf_testing"
USER_ID = "local-test-user"
 
# Sample data matching what test_execution_agent, monitoring_agent, and
# security_agent actually produce
TEST_JOB_INPUT = {
    "job_id": "JOB-3001",
    "application": "ANZ-Payments",
    "scenario": "peak_load",
    "test_execution_results": [
        {
            "job_id": "JOB-3001", "application": "ANZ-Payments", "scenario": "peak_load",
            "api_name": "POST /payments", "total_requests": 10000,
            "successful_requests": 9820, "failed_requests": 180,
            "avg_response_time": 210.0, "p95_response_time": 890.0,
            "max_response_time": 2100.0, "throughput": 45.2,
            "error_rate": 1.8, "http_status": 200,
        }
    ],
    "monitoring_result": {
        "job_id": "JOB-3001", "application": "ANZ-Payments", "scenario": "peak_load",
        "cpu_usage": 61.67, "memory_usage": 66.08, "db_connections": 151.92,
        "response_time": 466.25, "tps": 156.92, "status": "OK", "alerts": [],
    },
    "security_result": {
        "status": "WARNING", "security_score": "80%",
        "issues": ["JWT expiry not enforced on retry endpoint"],
        "recommendations": ["Reject retried requests with expired JWTs at the gateway"],
    },
}
 
 
async def run_agent(agent, session_service, session_id: str, user_message: str) -> str:
    """Sends one message to an agent and returns its final text response."""
    runner = Runner(agent=agent, app_name=APP_NAME, session_service=session_service)
    content = types.Content(role="user", parts=[types.Part(text=user_message)])
 
    final_text = ""
    async for event in runner.run_async(user_id=USER_ID, session_id=session_id, new_message=content):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text or final_text
    return final_text
 
 
async def main():
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Set OPENAI_API_KEY before running this script.")
 
    session_service = InMemorySessionService()
    session = await session_service.create_session(app_name=APP_NAME, user_id=USER_ID)
 
    # --- Step 1: Analysis Agent -------------------------------------------------
    analysis_message = (
        "Analyze this performance test job using the data provided from "
        "test_execution_agent, monitoring_agent, and security_agent, and "
        "return the structured result.\n\n"
        f"{json.dumps(TEST_JOB_INPUT, indent=2)}"
    )
    print("Running Analysis Agent...")
    analysis_response_text = await run_agent(analysis_agent, session_service, session.id, analysis_message)
    print("\n--- Analysis Agent final response ---")
    print(analysis_response_text)
 
    # ADK's output_key="analysis_result" (set in analysis_agent) already wrote this
    # into session.state automatically -- re-fetch the session to see it.
    updated_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=session.id
    )
    print("\nanalysis_result now in session.state:",
          "analysis_result" in updated_session.state)
 
    # --- Step 2: Report Agent (same session -> sees analysis_result in state) ---
    report_message = "Generate the report for this job's analysis result."
    print("\nRunning Report Agent...")
    report_response_text = await run_agent(report_agent, session_service, session.id, report_message)
    print("\n--- Report Agent final response ---")
    print(report_response_text)
 
 
if __name__ == "__main__":
    asyncio.run(main())
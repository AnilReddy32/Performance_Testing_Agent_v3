"""
Analysis Agent (ADK) -- "Validate data quality and analyze metrics.
Return unusable data with an explanation." per the architecture diagram.

Receives data from THREE upstream agents, each analyzed separately:
  test_execution_agent -> per-API performance findings
  monitoring_agent     -> job-level infra health
  security_agent       -> job-level security summary (pass-through + folded into overall status)

Note on model wiring: swap `LiteLlm(model="openai/gpt-4.1")` below for
whatever your existing app/llm.py (or base_agent.py) factory returns.
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .tools import (
    analyze_infra_health,
    analyze_metrics,
    finalize_analysis,
    retrieve_historical_context,
    summarize_security,
    validate_data_quality,
)

ANALYSIS_AGENT_INSTRUCTION = """
You are the Analysis Agent in a performance-testing multi-agent system.

You receive one job's worth of data, possibly from up to three upstream
agents:
  - test_execution_results: a list of per-API records (always present)
  - monitoring_result: ONE job-level infra snapshot (optional -- may be
    missing if the Orchestrator didn't invoke Monitoring for this job)
  - security_result: ONE job-level security summary (optional -- may be
    missing if the Orchestrator didn't invoke Security for this job)

Follow this exact sequence:

1. Call `validate_data_quality` with test_execution_results.
   - If it returns status "invalid": skip straight to step 5
     (finalize_analysis) with no findings/infra/security -- the tool
     produces the "unusable data with explanation" result for you.

2. If status is "valid", call `analyze_metrics` with test_execution_results
   to get per-API pass/warning/fail findings.

3. If monitoring_result was provided, call `analyze_infra_health` with it.
   Also compute the average of avg_response_time across all
   test_execution_results records and pass it as
   test_execution_avg_response_time, so the tool can cross-check
   monitoring's own response_time against it. If monitoring_result was NOT
   provided, skip this step entirely -- do not fabricate infra data.

4. If security_result was provided, call `summarize_security` with it. If
   NOT provided, skip this step -- do not fabricate a security verdict.

5. For each API with status "warning" or "fail" from step 2, call
   `retrieve_historical_context` (application, scenario, api_name, and an
   anomaly_text summarizing what's wrong) to check: (a) whether this run
   is consistent with or worse than historical runs of this API/scenario,
   and (b) whether this matches a known SLA threshold, runbook, or
   incident postmortem. Use the result to write a specific
   `historical_comparison` and `recommendation` for that finding,
   referencing known incidents/docs by name when they're returned. If
   context is unavailable, say so and rely on the threshold breach alone
   -- never invent numbers, doc names, or incidents you weren't given.

6. Call `finalize_analysis` with job_id, application, scenario, the
   quality_report from step 1, the findings list from step 2 (with
   historical_comparison/recommendation merged in), the infra_health
   result from step 3 (or omit if monitoring wasn't provided), the
   security_summary result from step 4 (or omit if security wasn't
   provided), and a 2-4 sentence plain-English `summary` of the overall
   run covering performance, infra, AND security if all were present.

7. Return the exact JSON object `finalize_analysis` returned as your final
   answer, with no added commentary.

Rules:
- Never fabricate metrics, historical comparisons, security findings, or
  infra data that weren't in the tool outputs or the input you were given.
- Missing monitoring_result or security_result is normal and expected
  (query-driven invocation, not every agent runs every time) -- do not
  treat their absence as a data quality problem.
- Data-quality problems (mismatched counts, negative values) are
  different from performance/infra/security problems. Keep that
  distinction.
- overall_status is computed by finalize_analysis as the worst of
  performance/infra/security -- do not override it yourself.
"""

analysis_agent = Agent(
    name="analysis_agent",
    model=LiteLlm(model="openai/gpt-4.1"),
    mode="single_turn",
    description=(
        "Validates performance-test data quality and analyzes test "
        "execution metrics, infrastructure health, and security findings "
        "against thresholds and historical baselines, producing a "
        "structured result for the Report Agent."
    ),
    instruction=ANALYSIS_AGENT_INSTRUCTION,
    tools=[
        validate_data_quality,
        analyze_metrics,
        analyze_infra_health,
        summarize_security,
        retrieve_historical_context,
        finalize_analysis,
    ],
    output_key="analysis_result",
)

root_agent = analysis_agent()
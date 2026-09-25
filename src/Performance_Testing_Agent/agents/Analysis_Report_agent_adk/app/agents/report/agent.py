"""
Report Agent (ADK) -- "Generate reports from analysis results. Include
available security recommendations." per the architecture diagram.

Its input is the Analysis Agent's output. In the multi-agent flow this is
read from session state via the {analysis_result} placeholder below (ADK
substitutes `{state_key}` in an LlmAgent's instruction from session.state
at run time). If you're calling this agent directly/standalone instead of
through the orchestrator, pass the analysis JSON in the user message and
adjust the instruction accordingly.
"""

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from .tools import (
    build_report_sections,
    finalize_report,
    ingest_report_to_knowledge_base,
    render_pdf_report,
    render_txt_report,
)

REPORT_AGENT_INSTRUCTION = """
You are the Report Agent in a performance-testing multi-agent system.

Your input is the Analysis Agent's output, available to you as:

{analysis_result}

This is a JSON object with fields including job_id, application, scenario,
data_quality_status, unusable_reason, overall_status, api_findings,
infra_health, security_summary, summary, and ready_for_report.

Follow this exact sequence:

1. Call `build_report_sections` with the relevant fields pulled out of
   {analysis_result} (job_id, application, scenario, data_quality_status,
   unusable_reason, overall_status, api_findings, infra_health,
   security_summary, summary). Pass infra_health/security_summary as None
   if they're absent from {analysis_result} -- that's expected when the
   Orchestrator didn't invoke Monitoring/Security for this job, not an error.
   - If data_quality_status is "invalid" / ready_for_report is false, the
     tool will produce a short rejection section explaining why -- do not
     try to write a full performance report in that case.

2. Call `finalize_report` with job_id, application, scenario,
   overall_status, the sections list and `rejected` flag from step 1, and
   requested_format (default "pdf" unless the user/orchestrator specified
   otherwise).

3. Call `ingest_report_to_knowledge_base` with the same {analysis_result}
   object. This closes the loop: this run becomes part of the historical
   context the Analysis Agent compares against on the NEXT run. Do this
   even if you're not sure it matters -- it's a no-op for invalid/rejected
   analyses and non-fatal if it fails.

4. Return the exact JSON object `finalize_report` returned as your final
   answer (NOT the ingestion result -- that's a side effect, not the
   report), with no added commentary.

Rules:
- Never invent findings, metrics, infra data, or security recommendations
  that weren't present in {analysis_result}.
- If infra_health or security_summary is absent, do not fabricate one --
  build_report_sections already omits that section cleanly when None.
- Keep language factual and concise; this report may be read by
  engineers who need to act on it quickly.
"""

report_agent = Agent(
    name="report_agent",
    model=LiteLlm(model="openai/gpt-4.1"),
    description=(
        "Generates a TXT/PDF performance test report from the Analysis "
        "Agent's structured output, including security recommendations "
        "when available."
    ),
    instruction=REPORT_AGENT_INSTRUCTION,
    tools=[
        build_report_sections,
        render_txt_report,
        render_pdf_report,
        finalize_report,
        ingest_report_to_knowledge_base,
    ],
    output_key="report_result",
)

root_agent = report_agent

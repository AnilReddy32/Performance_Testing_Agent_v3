import re

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import ToolContext

from Performance_Testing_Agent.config import LITELLM_MODEL_NAME
from Performance_Testing_Agent.execution_context import (
    ExecutionJobResult,
    create_execution_job_context,
    is_k6_test_request,
    is_simulated_tool_request,
    real_execution_gate,
)

from app.tools.k6_runner import run_real_k6_test
from app.tools.script_generation import generate_script
from app.tools.tool_executor import handle_test_request


_EXECUTION_REQUEST = re.compile(
    r"\b(?:please\s+)?(?:run|execute|perform|start|launch)\b"
    r"[^.!?,;\n]{0,80}\b(?:test|script|scenario|workload|it|this|against|"
    r"now|PTC-\d{3}|WTC-\d{3})\b",
    re.I,
)
_NEGATED_EXECUTION_ACTION = re.compile(
    r"\b(?:do not|don't|never|without|avoid|no need to|not)\b"
    r"[^.!?,;\n]{0,80}\b(?:run|execute|perform|start|launch)\b",
    re.I,
)
_SCRIPT_PREPARATION_ACTION = re.compile(
    r"\b(?:generate|create|prepare|write)\b",
    re.I,
)
_SEQUENTIAL_ACTION = re.compile(r"\b(?:and|then|also|next)\b|[,;]", re.I)


def _real_execution_requested(user_request: str) -> bool:
    if _NEGATED_EXECUTION_ACTION.search(user_request):
        return False
    preparation = _SCRIPT_PREPARATION_ACTION.search(user_request)
    for match in _EXECUTION_REQUEST.finditer(user_request):
        prefix = user_request[: match.start()]
        if preparation and preparation.start() < match.start():
            between = user_request[preparation.end() : match.start()]
            if not _SEQUENTIAL_ACTION.search(between):
                continue
        if re.search(
            r"\b(?:can|could|would|will|might|should)\s*$",
            prefix,
            re.I,
        ):
            continue
        return True
    return False


def run_test_execution_adk(user_request: str, tool_context: ToolContext) -> dict:
    """Runs the ADK test-execution pipeline and stores the result in shared
    session state so downstream agents (analysis, report) read the exact
    same numbers."""

    requested_mode = (
        "REAL"
        if is_k6_test_request(user_request)
        else "SIMULATED"
        if is_simulated_tool_request(user_request)
        else None
    )
    current_mode = str(
        tool_context.state.get("execution_mode", "SIMULATED")
    ).upper()
    if requested_mode is not None and requested_mode != current_mode:
        profile = tool_context.state.get("workload_profile")
        job_context = create_execution_job_context(
            execution_mode=requested_mode,
            workload_profile=profile if isinstance(profile, dict) else None,
            source_id=tool_context.state.get("execution_source_id"),
            test_case_id=tool_context.state.get("test_case_id"),
            test_case_name=tool_context.state.get("test_case_name"),
            job_id=tool_context.state.get("job_id"),
        )
        tool_context.state.update(job_context)
        tool_context.state.update(
            {
                state_key: None
                for state_key in (
                    "test_execution_result",
                    "monitoring_result",
                    "security_result",
                    "analysis_result",
                    "report_result",
                )
            }
        )

    execution_mode = str(
        tool_context.state.get("execution_mode", "SIMULATED")
    ).upper()
    profile = tool_context.state.get("workload_profile")
    real_k6_execution_requested = (
        (
            is_k6_test_request(user_request)
            or (
                isinstance(profile, dict)
                and profile.get("tool") == "k6"
                and _SCRIPT_PREPARATION_ACTION.search(user_request)
            )
        )
        and not _NEGATED_EXECUTION_ACTION.search(user_request)
    )

    if execution_mode == "REAL":
        if _real_execution_requested(user_request) or real_k6_execution_requested:
            tool_context.state.update(
                {
                    state_key: None
                    for state_key in (
                        "test_execution_result",
                        "monitoring_result",
                        "security_result",
                        "analysis_result",
                        "report_result",
                    )
                }
            )
            prior_manifest = tool_context.state.get("execution_artifacts") or {}
            tool_context.state["execution_artifacts"] = {
                **prior_manifest,
                "artifacts": {},
            }

        preflight = tool_context.state.get("execution_preflight") or {}
        profile = tool_context.state.get("workload_profile")
        if preflight.get("status") == "ready" and isinstance(profile, dict):
            if profile.get("tool") != "k6":
                result = ExecutionJobResult(
                    job_id=tool_context.state["job_id"],
                    execution_mode="REAL",
                    status="blocked",
                    message="Real script generation is currently supported only for k6.",
                    blocked_reasons=[
                        "The deterministic JMeter and Gatling templates are not "
                        "available yet."
                    ],
                ).model_dump(mode="json")
            else:
                generated = generate_script(
                    tool="k6",
                    application=str(profile.get("application") or "Unknown"),
                    scenario=str(profile.get("scenario") or "Performance Test"),
                    api_name=str(profile.get("api_name") or profile.get("endpoint")),
                    execution_mode="REAL",
                    workload_profile=profile,
                    job_id=tool_context.state.get("job_id"),
                    artifact_directory=tool_context.state.get(
                        "execution_artifact_directory"
                    ),
                    test_case_id=tool_context.state.get("test_case_id"),
                    test_case_name=tool_context.state.get("test_case_name"),
                )
                if generated.get("status") == "success":
                    manifest = tool_context.state.get("execution_artifacts") or {}
                    artifacts = dict(manifest.get("artifacts") or {})
                    artifacts["generated_script"] = generated["artifact_path"]
                    tool_context.state["execution_artifacts"] = {
                        **manifest,
                        "artifacts": artifacts,
                    }
                    if _real_execution_requested(
                        user_request
                    ) or real_k6_execution_requested:
                        execution = run_real_k6_test(
                            job_id=tool_context.state["job_id"],
                            profile_data=profile,
                            artifact_directory=tool_context.state[
                                "execution_artifact_directory"
                            ],
                            script_path=generated["file_path"],
                            test_case_id=tool_context.state.get("test_case_id"),
                            application=str(
                                profile.get("application") or "Unknown"
                            ),
                            scenario=str(
                                tool_context.state.get("test_case_name")
                                or profile.get("scenario")
                                or "Performance Test"
                            ),
                            api_name=str(
                                profile.get("api_name")
                                or profile.get("endpoint")
                                or "Unknown"
                            ),
                        )
                        artifacts.update(execution.get("artifacts") or {})
                        tool_context.state["execution_artifacts"] = {
                            **manifest,
                            "artifacts": artifacts,
                        }
                        if execution.get("status") == "completed":
                            normalized_metrics = execution["metrics"]
                            tool_context.state["test_execution_result"] = (
                                normalized_metrics
                            )
                            tool_context.state["execution_status"] = "completed"
                            result = {
                                **execution,
                                "artifacts": artifacts,
                            }
                        else:
                            tool_context.state["execution_status"] = "failed"
                            result = {
                                **execution,
                                "artifacts": artifacts,
                            }
                    else:
                        result = {
                            "job_id": tool_context.state["job_id"],
                            "execution_mode": "REAL",
                            "status": "prepared",
                            "message": generated["message"],
                            "artifacts": artifacts,
                        }
                else:
                    result = ExecutionJobResult(
                        job_id=tool_context.state["job_id"],
                        execution_mode="REAL",
                        status="failed",
                        message="Reviewed REAL k6 script generation failed.",
                        blocked_reasons=[str(generated.get("message", "Unknown error."))],
                    ).model_dump(mode="json")
        else:
            result = real_execution_gate(tool_context.state)
        tool_context.state["execution_status"] = result["status"]
        tool_context.state["execution_stage_result"] = result
        return result

    if execution_mode != "SIMULATED":
        raise ValueError(
            f"Unsupported execution mode in session state: {execution_mode}"
        )

    result = handle_test_request(user_request)
    tool_context.state["test_execution_result"] = result
    if "total_requests" in result and "job_id" in result:
        tool_context.state["execution_status"] = "completed"
    elif result.get("status") == "error":
        tool_context.state["execution_status"] = "failed"
    elif result.get("status") == "success":
        tool_context.state["execution_status"] = "prepared"
    return result


root_agent = Agent(
    name="test_execution_agent",
    model=LiteLlm(model=LITELLM_MODEL_NAME),
    instruction="""
You are the Test Execution Agent for an intelligent performance-testing
system.

Your responsibility is to handle performance-testing requests using
the trusted execution context supplied by the orchestrator.

For SIMULATED requests, use the existing planning and fake-execution
workflow. For REAL requests, do not use the planner to choose workload
values. When preflight passes for k6, prepare the deterministic
reviewed k6 script from workload_profile. A k6 test/script request runs
the test for real by default, even if the request says only "generate a
script"; only an explicit instruction not to execute it keeps the request
at script preparation. Capture real k6 raw results, normalized metrics,
and the native HTML report for completed runs.
Never substitute simulated execution for a REAL request.

Do not answer the user's request directly.

The simulated handle_test_request capability performs:

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

The orchestrator selects REAL mode for k6 test/script requests and
SIMULATED mode for JMeter/Gatling test/script requests. Never infer or
override workload_profile values from the user's prose. SIMULATED mode
uses only the fake runner. REAL mode must never fall back to simulation;
if its preflight is incomplete or blocked, report the missing
inputs/reasons and do not execute.

The current execution architecture uses different execution paths:

- k6 uses the real k6 CLI for execution and produces real k6
  execution metrics from the configured test target.

- JMeter and Gatling currently use the FAKE/SIMULATED MCP server.
  Their metrics are simulated and must never be represented as real
  measurements.

Never fabricate or claim execution metrics that were not produced
by the corresponding execution path.

For simulated execution requests, the execution workflow handles:

1. Script generation
2. Test-data preparation
3. Environment preparation
4. Performance-test execution
5. Execution monitoring or result collection
6. Standardized result creation
7. Analysis Agent handoff

For k6 requests, follow the REAL execution rule above. For other tools,
generation-only requests must NOT automatically execute a test.

The final standardized execution result must preserve the exact 13-field contract required by the downstream Analysis Agent.

Return the exact execution result and available artifact paths to the
orchestrator. Do not claim that a consolidated PDF was generated; only the
Report Agent can confirm that by returning its report path. If the REAL
execution result contains a native_report or native_report_archive artifact,
identify it as already generated and include its path in the result. Do not
offer to provide it later or ask whether the user wants it.
""",
    tools=[
        run_test_execution_adk,
    ],
)
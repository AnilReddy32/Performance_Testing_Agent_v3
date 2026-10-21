"""Keyword-driven stage plan for a Jira issue that selects a catalog test case.

The workload (target, users, duration, thresholds) always comes from the
catalog test case. The Jira text only decides which stages run around it, and
only through the fixed keyword rules below; it is never executed or trusted.

Stages, always in this order:
    execution -> monitoring -> security -> analysis -> report
Execution, analysis and report are the main stages. Monitoring runs by default
(as it does for every real run) unless the text says to skip it. Security runs
only when the text asks for it.
"""

import re
from dataclasses import dataclass, field

_CASE_ID = re.compile(r"\b(?:PTC|WTC)-\d{3}\b", re.IGNORECASE)

_MONITORING = re.compile(
    r"\b(?:monitor\w*|cpu|memory|infrastructure|resource\s+(?:usage|utili[sz]ation))\b",
    re.IGNORECASE,
)
# Mirrors the keywords orchestrator.pipeline uses to detect a security request.
_SECURITY = re.compile(
    r"\b(?:security|vulnerabilit\w*|penetration|sql injection|"
    r"authentication|authorization|oauth|owasp)\b",
    re.IGNORECASE,
)

_NEGATION_WORDS = {
    "not", "don't", "dont", "never", "skip", "skipping", "without",
    "exclude", "excluding", "avoid", "no",
}
_NOT_NEEDED_AFTER = re.compile(
    r"\b(?:is\s+not|isn't|not)\s+(?:required|needed|necessary|wanted)\b|\bunnecessary\b",
    re.IGNORECASE,
)

# "do not run <something>": only an execution refusal when <something> is the
# test itself, not another stage ("Do not run security scans").
_REFUSED_EXECUTION = re.compile(
    r"\b(?:do not|don't|dont|never|avoid|no need to)\s+(?:actually\s+)?"
    r"(?:run|execute|perform|start|launch)\b(?P<tail>[^.!?;\n]*)",
    re.IGNORECASE,
)
_OTHER_STAGE_TAIL = re.compile(
    r"\b(?:security|monitor\w*|vulnerabilit\w*|analy[sz]\w*|report|pdf)\b",
    re.IGNORECASE,
)
_PREPARE_ONLY = re.compile(
    r"\bwithout\s+(?:running|executing|performing|starting|launching)\b|"
    r"\b(?:script|plan)\s+only\b|"
    r"\b(?:only|just)\s+(?:generate|create|prepare|write)\b",
    re.IGNORECASE,
)

_CLAUSE_SPLIT = re.compile(r"[.!?;\n,]+")

_RUNNER_NAMES = {"jmeter": "JMeter", "k6": "k6"}


def runner_name(tool: str | None) -> str:
    return _RUNNER_NAMES.get(tool or "", tool or "the configured tool")


@dataclass(frozen=True)
class StagePlan:
    execute: bool
    monitoring: bool
    security: bool
    notes: tuple[str, ...] = field(default_factory=tuple)


def _mentions(pattern: re.Pattern, text: str) -> tuple[bool, bool]:
    """Return (asked_for, refused) for a keyword group across the text."""
    asked = refused = False
    for clause in _CLAUSE_SPLIT.split(text):
        for match in pattern.finditer(clause):
            nearby = re.findall(r"[\w']+", clause[: match.start()].lower())[-4:]
            if any(word in _NEGATION_WORDS for word in nearby) or _NOT_NEEDED_AFTER.search(
                clause[match.end():]
            ):
                refused = True
            else:
                asked = True
    return asked, refused


def _execution_skipped(text: str) -> bool:
    if _PREPARE_ONLY.search(text):
        return True
    for clause in _CLAUSE_SPLIT.split(text):
        match = _REFUSED_EXECUTION.search(clause)
        if match and not _OTHER_STAGE_TAIL.search(match.group("tail")):
            return True
    return False


def build_stage_plan(prompt_text: str, *, test_case_id: str) -> StagePlan:
    """Build the plan for one issue from its prompt text (description first)."""
    text = prompt_text or ""
    notes: list[str] = []

    execute = not _execution_skipped(text)
    if not execute:
        notes.append(
            "The text asks not to run the test, so no load test and no later "
            "stage will start."
        )

    monitoring_asked, monitoring_refused = _mentions(_MONITORING, text)
    monitoring = not (monitoring_refused and not monitoring_asked)
    if not monitoring:
        notes.append("Monitoring skipped: the text says it is not needed.")

    security_asked, _ = _mentions(_SECURITY, text)
    if not security_asked:
        notes.append("Security assessment not requested in the text; skipped.")

    other_ids = sorted(
        {m.group(0).upper() for m in _CASE_ID.finditer(text)} - {test_case_id.upper()}
    )
    if other_ids:
        notes.append(
            f"The text mentions {', '.join(other_ids)}; the Test Case ID selected "
            f"in Jira ({test_case_id}) is used."
        )

    return StagePlan(
        execute=execute,
        monitoring=monitoring and execute,
        security=security_asked and execute,
        notes=tuple(notes),
    )


def build_execution_message(test_case_id: str, tool: str | None) -> str:
    """Message for the execution agent, built from trusted values only."""
    return (
        f"Run test case {test_case_id} using {runner_name(tool)}. Execute the real "
        "performance test with the trusted workload profile and return the "
        "execution result."
    )


def format_plan_comment(
    plan: StagePlan,
    *,
    test_case_id: str,
    test_case_name: str,
    tool: str | None,
    tool_overridden: bool,
    catalog_tool: str | None,
) -> str:
    runner = runner_name(tool)
    runner_line = (
        f"Runner: {runner} (selected in the Jira text; catalog default: "
        f"{runner_name(catalog_tool)})"
        if tool_overridden
        else f"Runner: {runner} (catalog default)"
    )
    lines = [
        "Performance Testing Agent — Execution Plan",
        "",
        f"Test case: {test_case_id} — {test_case_name}",
        runner_line,
        "Workload: taken from the test case (target, users, duration, ramp-up, thresholds)",
        "",
    ]
    if plan.execute:
        steps = [
            f"Execute the REAL {runner} performance test using the workload from {test_case_id}.",
        ]
        if plan.monitoring:
            steps.append("Collect monitoring results for this job.")
        if plan.security:
            steps.append(
                "Assess the security surface for this job and the configured target."
            )
        steps.append("Analyze the current job's results.")
        steps.append(
            "Generate the final PDF report"
            + (" with security coverage and evidence." if plan.security else ".")
        )
        lines.append("Plan:")
        lines.extend(f"{number}. {step}" for number, step in enumerate(steps, 1))
    else:
        lines.append("Plan: nothing will run.")
    if plan.notes:
        lines.append("")
        lines.append("Notes:")
        lines.extend(f"- {note}" for note in plan.notes)
    return "\n".join(lines)


def evaluate_done(result: dict) -> tuple[bool, str]:
    """Done means the main stages finished: the test completed and the PDF exists."""
    status = result.get("execution_status")
    if status != "completed":
        message = result.get("execution_message")
        detail = f": {message}" if isinstance(message, str) and message.strip() else ""
        return False, f"test execution status is '{status}'{detail}"
    if not result.get("report_path"):
        return False, "the final PDF report was not created"
    return True, ""


def format_result_comment(
    result: dict,
    *,
    test_case_id: str,
    tool: str | None,
    tool_overridden: bool,
    catalog_tool: str | None,
    done: bool,
    not_done_reason: str,
) -> str:
    pipeline = result.get("pipeline") or {}
    runner = runner_name(tool)
    status = result.get("execution_status")
    execution_line = f"Execution: {status}"
    if status == "completed" and result.get("thresholds_passed") is not None:
        execution_line += f" (thresholds passed: {result['thresholds_passed']})"
    elif result.get("execution_message"):
        execution_line += f" — {result['execution_message']}"

    report_line = (
        f"Report: {pipeline.get('report', 'not run')}"
        if result.get("report_path")
        else f"Report: not created ({pipeline.get('report', 'not run')})"
    )
    lines = [
        "Performance Testing Agent — Processing Result",
        "",
        "Input source: TEST_CASE",
        f"Test Case ID: {test_case_id}",
        (
            f"Runner: {runner} (selected in the Jira text; catalog default: "
            f"{runner_name(catalog_tool)})"
            if tool_overridden
            else f"Runner: {runner} (catalog default)"
        ),
        f"Job ID: {result.get('job_id')}",
        "",
        "Stage results:",
        f"- {execution_line}",
        f"- Monitoring: {pipeline.get('monitoring', 'not run')}",
        f"- Security: {pipeline.get('security', 'not run')}",
        f"- Analysis: {pipeline.get('analysis', 'not run')}",
        f"- {report_line}",
        "",
        "Saved locally:",
    ]
    artifacts = result.get("artifacts") or {}
    labels = (
        ("native_report_entrypoint", f"Native {runner} report (HTML)"),
        ("native_report_archive", f"Native {runner} dashboard + raw results (ZIP)"),
        ("raw_results", f"Raw {runner} results"),
        ("runner_log", "Runner log"),
    )
    saved = [(label, artifacts[key]) for key, label in labels if key in artifacts]
    if result.get("report_path"):
        saved.insert(0, ("Final PDF report", result["report_path"]))
    lines.extend(f"- {label}: {path}" for label, path in saved)
    if not saved:
        lines.append("- (no artifacts were produced)")
    lines.append("")
    lines.append(
        "Jira status: moved to Done."
        if done
        else f"Jira status: left In Progress — {not_done_reason}."
    )
    return "\n".join(lines)

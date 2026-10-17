import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.agents.analysis.tools import (
    finalize_analysis,
    summarize_security,
)
from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.agents.report import tools as report_tools
from Performance_Testing_Agent.orchestrator.pipeline import complete_real_k6_pipeline
from security_agent.live_testing.models import HTTPExecutionResult, HTTPResponse
from security_agent.models.request import SecurityAssessmentRequest
from security_agent.security.evaluation import evaluate_configured_controls
from security_agent.security.profiles import select_profile
from security_agent.tools.live_test_tool import execute_authorized_live_test


def _known_job_state(endpoint="/users", method="GET"):
    return {
        "job_id": "JOB-CURRENT",
        "test_case_id": "PTC-001",
        "execution_mode": "REAL",
        "execution_status": "completed",
        "application": "Demo Banking API",
        "workload_profile": {
            "application": "Demo Banking API",
            "environment": "development",
            "target_url": "https://example.internal",
            "endpoint": endpoint,
            "method": method,
            "tool": "k6",
        },
    }


def test_matching_and_mismatched_target_profiles_are_distinguished():
    matching = select_profile(_known_job_state())
    mismatched = select_profile(_known_job_state(endpoint="/not-in-profile"))

    assert matching["status"] == "matched"
    assert matching["profile_id"]
    assert mismatched["status"] == "no_match"


def test_missing_required_profile_evidence_is_not_assessed(tmp_path, monkeypatch):
    from security_agent.security import profiles

    registry = {
        "schema_version": "1.0",
        "profiles": [{
            "profile_id": "minimal-profile",
            "profile_version": "1.0.0",
            "scope": {
                "application": "Demo Banking API",
                "environment": "development",
                "target_origin": "https://example.internal",
                "endpoints": [{"path": "/users", "method": "GET"}],
            },
        }],
    }
    registry_path = tmp_path / "application_profile.json"
    registry_path.write_text(json.dumps(registry), encoding="utf-8")
    monkeypatch.setattr(profiles, "REGISTRY_PATH", registry_path)

    selection = select_profile(_known_job_state())
    request = SecurityAssessmentRequest(
        objective="Check authentication",
        requested_controls=["authentication"],
        required_evidence_by_control={
            "authentication": ["authentication.enabled", "authentication.type"]
        },
    )
    result = evaluate_configured_controls(request, selection)

    control = result["control_results"][0]
    assert selection["status"] == "matched"
    assert control["assessment_status"] == "not_assessed"
    assert set(control["missing_evidence"]) == {
        "authentication.enabled",
        "authentication.type",
    }


@pytest.mark.asyncio
async def test_failed_security_invocation_does_not_block_analysis_or_report():
    state = {
        **_known_job_state(),
        "test_execution_result": {"job_id": "JOB-CURRENT", "metrics": {}},
    }
    called = []
    agents = {
        name: SimpleNamespace(name=f"{name}_agent")
        for name in ("monitoring", "security", "analysis", "report")
    }

    async def invoke(agent, message):
        called.append(agent.name)
        if agent is agents["security"]:
            raise RuntimeError("simulated Security Agent outage")
        if agent is agents["monitoring"]:
            state["monitoring_result"] = {"job_id": "JOB-CURRENT", "status": "UNAVAILABLE"}
        elif agent is agents["analysis"]:
            assert '"security_result":null' in message
            state["analysis_result"] = {
                "job_id": "JOB-CURRENT",
                "ready_for_report": True,
                "data_quality_status": "valid",
                "summary": "Performance analysis completed without security input.",
            }
        elif agent is agents["report"]:
            state["report_result"] = {
                "job_id": "JOB-CURRENT",
                "file_path": "/tmp/JOB-CURRENT_report.pdf",
                "report_format": "pdf",
                "rejected": False,
            }

    pipeline = await complete_real_k6_pipeline(
        state=state,
        user_query="Run this test and perform a security assessment.",
        invoke_agent=invoke,
        monitoring_agent=agents["monitoring"],
        security_agent=agents["security"],
        analysis_agent=agents["analysis"],
        report_agent=agents["report"],
    )

    assert pipeline["security"].startswith("failed: RuntimeError")
    assert pipeline["analysis"] == "completed"
    assert pipeline["report"] == "completed"
    assert agents["analysis"].name in called
    assert agents["report"].name in called


def test_security_finding_affects_overall_status_and_summary_requires_job_match():
    security_result = {
        "job_id": "JOB-CURRENT",
        "status": "FAIL",
        "security_score": "N/A",
        "issues": ["Authentication configuration is disabled."],
        "recommendations": ["Enable authentication."],
        "assessment_mode": "configuration_only",
        "live_testing_requested": False,
        "live_testing_status": "not_requested",
        "requested_controls": ["authentication"],
        "assessed_controls": ["authentication"],
        "not_assessed_controls": [],
        "coverage": {"requested": 1, "assessed": 1, "not_assessed": 0},
        "control_results": [{
            "control": "authentication",
            "assessment_status": "assessed",
            "assessment_basis": "configuration_declaration",
            "evidence_fields": ["authentication.enabled"],
            "evidence_references": ["profile:demo@1.0.0"],
        }],
        "evidence_references": ["profile:demo@1.0.0"],
        "limitations": ["Configuration declarations do not establish runtime behavior."],
    }

    summary = summarize_security(security_result, "JOB-CURRENT")
    stale_summary = summarize_security(security_result, "JOB-OTHER")
    analysis = finalize_analysis(
        job_id="JOB-CURRENT",
        application="Demo Banking API",
        scenario="Smoke test",
        quality_report={"status": "valid", "issues": []},
        findings=[{
            "api_name": "/users",
            "status": "pass",
            "severity": "low",
            "metrics": {},
        }],
        security_summary=summary,
        summary="Performance is within thresholds.",
    )

    assert stale_summary is None
    assert analysis["overall_status"] == "fail"
    assert analysis["security_summary"]["job_id"] == "JOB-CURRENT"
    assert analysis["security_summary"]["coverage"]["assessed"] == 1
    assert analysis["security_summary"]["control_results"][0]["assessment_basis"] == "configuration_declaration"


@pytest.mark.asyncio
async def test_authorized_live_check_is_separate_and_unrequested_check_sends_nothing(monkeypatch):
    from security_agent import config
    from security_agent.tools import live_test_tool

    monkeypatch.setattr(config.settings, "SECURITY_LIVE_TESTS_ENABLED", True)
    monkeypatch.setattr(config.settings, "SECURITY_LIVE_ALLOWED_HOSTS", ("api.example.test",))
    monkeypatch.setattr(config.settings, "SECURITY_LIVE_ALLOWED_PATHS", ("/health",))
    monkeypatch.setattr(config.settings, "SECURITY_LIVE_ALLOWED_PORTS", (443,))
    monkeypatch.setattr(config.settings, "SECURITY_LIVE_ENVIRONMENT", "staging")
    requests = []

    class FakeExecutor:
        def __init__(self, policy):
            self.policy = policy

        async def execute(self, request):
            requests.append(request)
            return HTTPExecutionResult(
                success=True,
                response=HTTPResponse(
                    status_code=200,
                    headers={"strict-transport-security": "max-age=1000"},
                    elapsed_ms=12.0,
                ),
            )

    monkeypatch.setattr(live_test_tool, "HTTPExecutor", FakeExecutor)
    authorized_context = SimpleNamespace(state={
        **_known_job_state(endpoint="/health"),
        "test_case_prompt": "Run an active security check after the test.",
        "workload_profile": {
            "target_url": "https://api.example.test",
            "endpoint": "/health",
            "environment": "staging",
            "tool": "k6",
        },
    })
    live_result = await execute_authorized_live_test("active security check", authorized_context)

    unrequested_context = SimpleNamespace(state={
        **authorized_context.state,
        "test_case_prompt": "Run a configuration security assessment only.",
    })
    unrequested = await execute_authorized_live_test("security assessment", unrequested_context)

    assert live_result["status"] == "completed"
    assert live_result["requests_sent"] == 1
    assert requests[0].method == "HEAD"
    assert requests[0].url == "https://api.example.test/health"
    assert unrequested["status"] == "not_requested"
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_report_pdf_uses_current_job_security_and_labels_configuration_only(tmp_path, monkeypatch):
    import reportlab.rl_config

    job_id = "JOB-0123456789abcdef0123456789abcdef"
    security_summary = {
        "job_id": job_id,
        "status": "WARNING",
        "security_score": "N/A",
        "issues": ["Evidence is limited to profile configuration."],
        "recommendations": [],
        "assessment_mode": "configuration_only",
        "live_testing_requested": False,
        "live_testing_status": "not_requested",
        "coverage": {"requested": 1, "assessed": 0, "not_assessed": 1},
        "requested_controls": ["authentication"],
        "not_assessed_controls": ["authentication"],
        "control_results": [{
            "control": "authentication",
            "assessment_status": "not_assessed",
            "assessment_basis": "configuration_declaration",
            "evidence_fields": [],
            "evidence_references": [],
        }],
        "evidence_references": [],
        "limitations": ["Configuration-only result; runtime security behavior was not tested."],
    }
    sections_result = report_tools.build_report_sections(
        job_id=job_id,
        application="Demo Banking API",
        scenario="Smoke test",
        data_quality_status="valid",
        unusable_reason=None,
        overall_status="warning",
        api_findings=[],
        infra_health=None,
        security_summary=security_summary,
        summary="Performance completed.",
        execution_mode="REAL",
        execution_status="completed",
        execution_outcome={"job_id": job_id, "security_result": security_summary},
    )
    security_section = next(
        section for section in sections_result["sections"]
        if section["title"] == "Security Findings (Security Agent)"
    )
    assert f"Security result job ID: {job_id}" in security_section["content"]
    assert "Live security check: not requested." in security_section["content"]
    assert "configuration_declaration" in security_section["content"]
    assert "Configuration-only result; runtime security behavior was not tested." in security_section["content"]
    assert "completed" not in security_section["content"].lower()  # no runtime test is implied

    class NoArtifactContext:
        state = {}

        async def save_artifact(self, **kwargs):
            raise RuntimeError("artifact backend not configured in this test")

    monkeypatch.setattr(report_tools, "REPORTS_DIR", str(tmp_path))
    job_artifact_directory = tmp_path / "job-artifacts"
    monkeypatch.setattr(
        report_tools,
        "resolve_artifact_directory",
        lambda requested_job, tool=None: job_artifact_directory,
    )
    old_compression = reportlab.rl_config.pageCompression
    reportlab.rl_config.pageCompression = 0
    try:
        report_result = await report_tools.finalize_report(
            job_id=job_id,
            application="Demo Banking API",
            scenario="Smoke test",
            overall_status="warning",
            sections=sections_result["sections"],
            rejected=False,
            tool_context=NoArtifactContext(),
        )
    finally:
        reportlab.rl_config.pageCompression = old_compression

    pdf_file = tmp_path / f"{job_id}_report.pdf"
    assert report_result["job_id"] == job_id
    assert report_result["report_format"] == "pdf"
    assert report_result["rejected"] is False
    assert report_result["file_path"] == str(pdf_file)
    assert pdf_file.is_file()
    contents = pdf_file.read_bytes()
    assert contents.startswith(b"%PDF-")
    assert job_id.encode() in contents
    assert b"profile configuration" in contents
    assert b"runtime security behavior was not tested" in contents
    assert report_result["artifacts"]["consolidated_report"] == f"{job_id}_report.pdf"
    assert (job_artifact_directory / f"{job_id}_report.pdf").is_file()

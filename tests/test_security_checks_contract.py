"""The per-check security verdicts survive Analysis and appear in the report."""

import time
import unittest

from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.agents.analysis.schemas import (
    SecuritySummary,
)
from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.agents.analysis.tools import (
    finalize_analysis,
    summarize_security,
)
from Performance_Testing_Agent.agents.Analysis_Report_agent_adk.app.agents.report import tools as report_tools
from security_agent.passive import assess_external_surface
from security_agent.passive.models import HttpObservation, TlsObservation

JOB_ID = "JOB-0123456789abcdef0123456789abcdef"
HEADERS = {
    "strict-transport-security": "max-age=31536000", "x-content-type-options": "nosniff",
    "x-frame-options": "DENY", "content-security-policy": "default-src 'none'",
    "referrer-policy": "no-referrer", "permissions-policy": "geolocation=()", "cache-control": "no-store",
}


def reply(label, status, headers=None, method="HEAD", body=""):
    return HttpObservation(
        label=label, method=method, target="/posts/1", scheme="https", status=status,
        headers=tuple((headers or {}).items()), body=body, elapsed_ms=3.0,
    )


class FakeNetwork:
    def __init__(self, budget, options_headers):
        self.budget, self.options_headers = budget, options_headers

    def tls_probe(self):
        return TlsObservation(
            ok=True, version="TLSv1.3", cipher_name="TLS_AES_256_GCM_SHA384", cipher_bits=256,
            subject="api.example.com", issuer="Example CA", san_count=1, not_after=time.time() + 90 * 86400,
        )

    def request(self, *, label, method, target, headers=None, tls=True, read_body=False):
        self.budget.consume()
        return {
            "primary": reply("primary", 200, HEADERS),
            "options": reply("options", 204, self.options_headers, method="OPTIONS"),
            "not_found": reply("not_found", 404, {}, method="GET", body="{}"),
            "http_redirect": reply("http_redirect", 301, {"location": "https://api.example.com/posts/1"}),
        }[label]


def state():
    return {
        "job_id": JOB_ID, "test_case_id": "PTC-004", "execution_mode": "REAL", "execution_status": "completed",
        "workload_profile": {
            "tool": "k6", "application": "Posts API", "environment": "external_api",
            "target_url": "https://api.example.com", "endpoint": "/posts/1", "method": "GET",
        },
    }


class TestSecurityChecksContract(unittest.IsolatedAsyncioTestCase):
    async def result(self, options_headers):
        return await assess_external_surface(
            state(),
            network_factory=lambda target, budget: FakeNetwork(budget, options_headers),
            resolver=lambda host, port: ["93.184.216.34"],
        )

    async def test_the_verdicts_pass_through_analysis_unchanged(self):
        result = await self.result({"allow": "GET, TRACE", "access-control-allow-origin": "*"})

        summary = summarize_security(result, JOB_ID)
        analysis = finalize_analysis(
            job_id=JOB_ID, application="Posts API", scenario="Posts check",
            quality_report={"status": "valid", "issues": []},
            findings=[{"api_name": "/posts/1", "status": "pass", "severity": "low", "metrics": {}}],
            security_summary=summary, summary="Within thresholds.",
        )

        kept = analysis["security_summary"]
        self.assertEqual(kept["check_results"], result["check_results"])
        self.assertEqual(kept["check_summary"], result["check_summary"])
        self.assertEqual(kept["assessment_outcome"], "partially_assessed")
        self.assertEqual(SecuritySummary(**summary).check_results[0]["check_id"], "tls_protocol")
        self.assertEqual(analysis["overall_status"], "warning")        # a failed medium check, no blocking one

    async def test_the_report_lists_each_verdict_with_its_severity_and_reason(self):
        result = await self.result({"allow": "GET, TRACE"})
        summary = summarize_security(result, JOB_ID)

        sections = report_tools.build_report_sections(
            job_id=JOB_ID, application="Posts API", scenario="Posts check", data_quality_status="valid",
            unusable_reason=None, overall_status="warning", api_findings=[], infra_health=None,
            security_summary=summary, summary="Done.", execution_mode="REAL", execution_status="completed",
            execution_outcome={"job_id": JOB_ID},
        )
        content = next(s for s in sections["sections"] if s["title"] == "Security Findings (Security Agent)")["content"]

        self.assertIn("Passive external-surface checks (14 of 15 assessed; 13 passed, 1 failed, 1 inconclusive;", content)
        self.assertIn("outcome: partially_assessed", content)
        self.assertIn("[PASSED] TLS protocol and cipher (high):", content)
        self.assertIn("[FAILED] HTTP methods advertised by OPTIONS (medium):", content)
        self.assertIn("TRACE", content)
        self.assertIn("[INCONCLUSIVE] Rate-limiting evidence (low):", content)
        self.assertIn("Live security check: completed.", content)

    async def test_the_summary_table_shows_the_totals_but_not_every_check(self):
        result = await self.result({"allow": "GET, OPTIONS"})
        summary = summarize_security(result, JOB_ID)

        rows = report_tools._build_agent_activity_rows(
            "Posts API", "Posts check", [], None, summary, "Done.", "pdf"
        )
        security_text = dict(rows)["Security Validation"]

        self.assertIn("Passive external-surface checks (14 of 15 assessed", security_text)
        self.assertNotIn("[PASSED]", security_text)
        self.assertNotIn(":\n", security_text.split("Passive external-surface checks")[1].split("\n")[0])

    async def test_a_result_without_verdicts_renders_exactly_as_before(self):
        legacy = {
            "job_id": JOB_ID, "status": "WARNING", "security_score": "N/A", "issues": ["x"],
            "recommendations": [], "assessment_mode": "configuration_only",
            "live_testing_requested": False, "live_testing_status": "not_requested",
            "control_results": [], "limitations": ["Configuration-only result."],
        }

        summary = summarize_security(legacy, JOB_ID)
        sections = report_tools.build_report_sections(
            job_id=JOB_ID, application="A", scenario="S", data_quality_status="valid", unusable_reason=None,
            overall_status="warning", api_findings=[], infra_health=None, security_summary=summary,
            summary="Done.", execution_mode="REAL", execution_status="completed",
            execution_outcome={"job_id": JOB_ID},
        )
        content = next(s for s in sections["sections"] if s["title"] == "Security Findings (Security Agent)")["content"]

        self.assertNotIn("Passive external-surface checks", content)
        self.assertEqual(SecuritySummary(**summary).check_results, [])
        self.assertIsNone(SecuritySummary(**summary).assessment_outcome)


if __name__ == "__main__":
    unittest.main()

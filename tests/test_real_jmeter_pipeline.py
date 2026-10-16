import unittest
from types import SimpleNamespace

from Performance_Testing_Agent.orchestrator.pipeline import (
    complete_real_k6_pipeline,
)


class TestRealJMeterPipeline(unittest.IsolatedAsyncioTestCase):
    async def test_handoffs_reach_report_and_retry_is_idempotent(self):
        job_id = "JOB-jmeter-current"
        metrics = {
            "job_id": job_id,
            "api_name": "Account API",
            "total_requests": 12,
            "successful_requests": 12,
            "failed_requests": 0,
            "avg_response_time": 14.0,
            "p95_response_time": 21.0,
            "latency_percentiles_ms": {
                "p50": 12.0,
                "p90": 19.0,
                "p95": 21.0,
                "p99": 26.0,
            },
        }
        state = {
            "job_id": job_id,
            "execution_mode": "REAL",
            "execution_status": "completed",
            "workload_profile": {"tool": "jmeter", "application": "Banking"},
            "test_execution_result": metrics,
            "execution_stage_result": {"job_id": job_id, "status": "completed"},
            "execution_artifacts": {
                "job_id": job_id,
                "execution_mode": "REAL",
                "artifacts": {"native_report_archive": "report.zip"},
            },
        }
        agents = {
            name: SimpleNamespace(name=name)
            for name in ("monitoring", "security", "analysis", "report")
        }
        calls = []

        async def invoke_agent(agent, message):
            calls.append(agent.name)
            if agent.name == "monitoring":
                state["monitoring_result"] = {
                    "job_id": job_id,
                    "execution_mode": "REAL",
                    "data_source": "jmeter JTL and runtime sampler",
                }
            elif agent.name == "analysis":
                self.assertIn('"latency_percentiles_ms"', message)
                self.assertIn("native_report_archive", message)
                self.assertEqual(state["monitoring_result"]["job_id"], job_id)
                state["analysis_result"] = {
                    "job_id": job_id,
                    "ready_for_report": True,
                    "data_quality_status": "valid",
                    "summary": "JMeter results analyzed.",
                }
            elif agent.name == "report":
                self.assertEqual(state["analysis_result"]["job_id"], job_id)
                state["report_result"] = {
                    "job_id": job_id,
                    "file_path": "/tmp/JOB-jmeter-current.pdf",
                    "report_format": "pdf",
                    "rejected": False,
                }

        kwargs = {
            "state": state,
            "user_query": "Run JMeter, monitor, analyze, and generate PDF report",
            "invoke_agent": invoke_agent,
            "monitoring_agent": agents["monitoring"],
            "security_agent": agents["security"],
            "analysis_agent": agents["analysis"],
            "report_agent": agents["report"],
        }
        pipeline = await complete_real_k6_pipeline(**kwargs)

        self.assertEqual(calls, ["monitoring", "analysis", "report"])
        self.assertEqual(pipeline["monitoring"], "completed")
        self.assertEqual(pipeline["analysis"], "completed")
        self.assertEqual(pipeline["report"], "completed")
        self.assertEqual(state["real_jmeter_pipeline"], pipeline)

        retry_pipeline = await complete_real_k6_pipeline(**kwargs)
        self.assertEqual(calls, ["monitoring", "analysis", "report"])
        self.assertEqual(retry_pipeline["monitoring"], "already_available")
        self.assertEqual(retry_pipeline["analysis"], "already_available")
        self.assertEqual(retry_pipeline["report"], "already_available")


if __name__ == "__main__":
    unittest.main()

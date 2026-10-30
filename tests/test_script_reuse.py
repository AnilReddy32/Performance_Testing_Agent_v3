import json
import os
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_EXECUTION_AGENT_ROOT = (
    PROJECT_ROOT
    / "src"
    / "Performance_Testing_Agent"
    / "agents"
    / "test_execution_agent_adk"
)
if str(TEST_EXECUTION_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(TEST_EXECUTION_AGENT_ROOT))

# Import the package first, as the application does: its __init__ wires the
# agents in the order the tool modules expect (importing them first cycles).
import Performance_Testing_Agent  # noqa: F401
from google.adk.sessions.state import State

from app import agent as execution_agent
from app.tools import script_generation, script_library
from Performance_Testing_Agent.execution_context import create_execution_job_context

TOOLS = ("k6", "jmeter")
SCRIPT_NAMES = {"k6": "script.js", "jmeter": "script.jmx"}


class TestScriptReuse(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

        self.environment = patch.dict(
            os.environ,
            {
                "EXECUTION_ARTIFACTS_ROOT": self.temp.name,
                "REAL_EXECUTION_ENABLED": "true",
                "REAL_EXECUTION_ALLOWED_HOSTS": "localhost,127.0.0.1",
                "REAL_EXECUTION_ALLOWED_PORTS": "8000",
                "REAL_EXECUTION_MAX_USERS": "500",
                "REAL_EXECUTION_MAX_DURATION_SECONDS": "500",
                "REAL_EXECUTION_MAX_RAMP_UP_SECONDS": "90",
            },
            clear=True,
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

        dns_patch = patch(
            "Performance_Testing_Agent.execution_context.socket.getaddrinfo",
            return_value=[(None, None, None, None, ("127.0.0.1", 8000))],
        )
        dns_patch.start()
        self.addCleanup(dns_patch.stop)

        # Spies that still call the real builders, to prove when a build ran.
        self.builds = {}
        for tool, name in (("k6", "build_real_k6_script"), ("jmeter", "build_real_jmeter_plan")):
            spy = patch.object(
                script_generation, name, wraps=getattr(script_generation, name)
            )
            self.builds[tool] = spy.start()
            self.addCleanup(spy.stop)

    def profile(self, tool, **overrides):
        values = {
            "tool": tool,
            "target_url": "http://localhost:8000",
            "environment": "mock_api",
            "endpoint": "/api/payment",
            "method": "POST",
            "payload_template": {"transaction_id": "test-{{__VU}}", "amount": 10.5},
            "expected_status_code": 201,
            "expected_response_time_ms": 750,
            "p95_threshold_ms": 750,
            "users": 20,
            "max_rps": 10,
            "duration_seconds": 30,
            "ramp_up_seconds": 5,
            "credentials_ref": "none",
        }
        values.update(overrides)
        return values

    def generate(self, tool, profile=None, test_case_id="PTC-001"):
        job_id = f"JOB-{uuid.uuid4().hex}"
        return script_generation.generate_script(
            tool=tool,
            application="Payments",
            scenario="Payment load test",
            api_name="Payment API",
            execution_mode="REAL",
            workload_profile=profile or self.profile(tool),
            job_id=job_id,
            artifact_directory=str(Path(self.temp.name) / job_id),
            test_case_id=test_case_id,
            test_case_name="Payment API Load Test",
        )

    def run_agent(self, tool, prompt):
        """One run through the execution agent, as a separate session, with the runners stubbed."""
        profile = self.profile(tool)
        state = create_execution_job_context(
            execution_mode="REAL", workload_profile=profile,
            test_case_id="PTC-001", test_case_name="Payment API Load Test",
        )
        context = type("ToolContextStub", (), {"state": State(state, {})})()
        completed = {"status": "completed", "execution_mode": "REAL", "job_id": state["job_id"],
                     "thresholds_passed": True, "metrics": {"total_requests": 1}, "artifacts": {}}
        with (
            patch("app.agent.run_real_jmeter_test", return_value=dict(completed)),
            patch("app.agent.run_real_k6_test", return_value=dict(completed)),
        ):
            result = execution_agent.run_test_execution_adk(prompt, context)
        return result, state

    def test_the_execution_agent_reports_whether_the_script_was_generated_or_reused(self):
        prompts = {
            "jmeter": ("Prepare the JMeter script for PTC-001", "Run PTC-001 using JMeter"),
            "k6": ("Prepare the k6 script for PTC-001", "Run PTC-001 using k6"),
        }
        for tool, (prepare, run) in prompts.items():
            with self.subTest(tool=tool):
                first, first_state = self.run_agent(tool, prepare)        # session 1
                second, second_state = self.run_agent(tool, prepare)      # session 2
                third, third_state = self.run_agent(tool, run)            # session 3, and it executes

                self.assertEqual(
                    (first["script_source"], second["script_source"], third["script_source"]),
                    ("generated", "reused", "reused"),
                )
                self.assertEqual(first_state["execution_script_source"], "generated")
                self.assertEqual(second_state["execution_script_source"], "reused")
                self.assertEqual(third_state["execution_script_source"], "reused")
                if tool == "jmeter":    # a k6 request always executes, so it has no "prepared" message
                    self.assertIn("generated", first["message"])
                    self.assertIn("reused from the stored script", second["message"])
                self.assertEqual(self.builds[tool].call_count, 1)         # built once, across all three
                self.assertEqual(third["status"], "completed")            # reuse does not change the run

    def test_a_run_that_never_reaches_script_generation_reports_no_script_source(self):
        state = create_execution_job_context(execution_mode="REAL", workload_profile=None)
        context = type("ToolContextStub", (), {"state": State(state, {})})()

        result = execution_agent.run_test_execution_adk("Run PTC-001 using JMeter", context)

        self.assertNotIn("script_source", result)
        self.assertIsNone(state["execution_script_source"])

    def entry(self, tool, test_case_id="PTC-001"):
        return self.root / script_library.LIBRARY_DIRECTORY_NAME / tool / test_case_id

    def test_first_run_generates_and_stores_then_rerun_reuses(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                first = self.generate(tool)
                self.assertEqual(first["status"], "success")
                self.assertEqual(first["script_source"], "generated")
                self.assertEqual(self.builds[tool].call_count, 1)
                self.assertTrue((self.entry(tool) / SCRIPT_NAMES[tool]).is_file())
                self.assertTrue((self.entry(tool) / "script.meta.json").is_file())

                second = self.generate(tool)
                self.assertEqual(second["status"], "success")
                self.assertEqual(second["script_source"], "reused")
                self.assertEqual(self.builds[tool].call_count, 1, "builder must not run on reuse")

                # Same visible result, same bytes, a separate copy in each job folder.
                for key in ("file_name", "artifact_path", "execution_status"):
                    self.assertEqual(first[key], second[key])
                # The message says which it was, so a reused script is never reported as
                # "generated" (the first run still reads exactly as it always did).
                self.assertIn("generated", first["message"])
                self.assertNotIn("reused", first["message"])
                self.assertIn("reused from the stored script", second["message"])
                self.assertIn("not regenerated", second["message"])
                self.assertIn("PTC-001", second["message"])
                self.assertNotEqual(first["file_path"], second["file_path"])
                self.assertEqual(
                    Path(first["file_path"]).read_bytes(),
                    Path(second["file_path"]).read_bytes(),
                )

    def test_reused_script_equals_what_the_runner_would_rebuild(self):
        for tool, build in (
            ("k6", script_generation.build_real_k6_script),
            ("jmeter", script_generation.build_real_jmeter_plan),
        ):
            with self.subTest(tool=tool):
                self.generate(tool)
                reused = self.generate(tool)
                self.assertEqual(reused["script_source"], "reused")
                expected = build(self.profile(tool), test_case_id="PTC-001")
                self.assertEqual(
                    Path(reused["file_path"]).read_text(encoding="utf-8"), expected
                )

    def test_changed_profile_value_regenerates_and_replaces_stored_script(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self.generate(tool)
                changed = self.profile(tool, users=25)
                regenerated = self.generate(tool, changed)
                self.assertEqual(regenerated["script_source"], "generated")
                self.assertEqual(self.builds[tool].call_count, 2)
                new_text = Path(regenerated["file_path"]).read_text(encoding="utf-8")
                self.assertIn("25", new_text)

                # The stored script was replaced: the new value now reuses ...
                again = self.generate(tool, changed)
                self.assertEqual(again["script_source"], "reused")
                self.assertEqual(
                    Path(again["file_path"]).read_text(encoding="utf-8"), new_text
                )
                # ... and the old value no longer matches the stored script.
                back = self.generate(tool)
                self.assertEqual(back["script_source"], "generated")

    def test_every_workload_field_that_shapes_the_script_forces_regeneration(self):
        for tool in TOOLS:
            for field, value in (
                ("duration_seconds", 40),
                ("ramp_up_seconds", 4),
                ("max_rps", 11),
                ("p95_threshold_ms", 800),
                ("expected_status_code", 200),
                ("endpoint", "/api/other"),
                ("method", "PUT"),
            ):
                with self.subTest(tool=tool, field=field):
                    self.generate(tool)  # stored script for the default profile
                    result = self.generate(tool, self.profile(tool, **{field: value}))
                    self.assertEqual(result["status"], "success")
                    self.assertEqual(result["script_source"], "generated")

    def test_template_source_change_invalidates_stored_script(self):
        for tool, other_template in (("k6", "jmeter_template.py"), ("jmeter", "k6_template.py")):
            with self.subTest(tool=tool):
                self.generate(tool)
                with patch.dict(script_library._TEMPLATE_FILES, {tool: other_template}):
                    result = self.generate(tool)
                self.assertEqual(result["script_source"], "generated")

    def test_tampered_or_partial_stored_script_is_rejected_and_repaired(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self.generate(tool)
                stored = self.entry(tool) / SCRIPT_NAMES[tool]
                original = stored.read_bytes()
                stored.write_bytes(original + b"\n// injected\n")

                result = self.generate(tool)
                self.assertEqual(result["script_source"], "generated")
                self.assertNotIn("injected", Path(result["file_path"]).read_text(encoding="utf-8"))
                self.assertEqual(stored.read_bytes(), original)

                (self.entry(tool) / "script.meta.json").write_text("{not json", encoding="utf-8")
                result = self.generate(tool)
                self.assertEqual(result["script_source"], "generated")
                self.assertEqual(self.generate(tool)["script_source"], "reused")

    def test_each_runner_has_its_own_stored_script_for_the_same_test_case(self):
        for tool in TOOLS:
            self.generate(tool)
        self.assertTrue((self.entry("k6") / "script.js").is_file())
        self.assertTrue((self.entry("jmeter") / "script.jmx").is_file())
        for tool in TOOLS:
            self.assertEqual(self.generate(tool)["script_source"], "reused")

    def test_only_catalog_test_cases_are_reused(self):
        for tool in TOOLS:
            for test_case_id in (None, "CUSTOM-1", "ptc-001", "PTC-1"):
                with self.subTest(tool=tool, test_case_id=test_case_id):
                    before = self.builds[tool].call_count
                    first = self.generate(tool, test_case_id=test_case_id)
                    second = self.generate(tool, test_case_id=test_case_id)
                    self.assertEqual(first["status"], "success")
                    self.assertEqual(second["script_source"], "generated")
                    self.assertEqual(self.builds[tool].call_count, before + 2)
        self.assertFalse((self.root / script_library.LIBRARY_DIRECTORY_NAME).exists())

    def test_reuse_can_be_switched_off(self):
        with patch.dict(os.environ, {script_library.REUSE_ENV_VARIABLE: "false"}):
            for tool in TOOLS:
                with self.subTest(tool=tool):
                    self.generate(tool)
                    second = self.generate(tool)
                    self.assertEqual(second["script_source"], "generated")
                    self.assertEqual(self.builds[tool].call_count, 2)
        self.assertFalse((self.root / script_library.LIBRARY_DIRECTORY_NAME).exists())

    def test_safety_preflight_still_applies_to_a_stored_script(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                self.assertEqual(self.generate(tool)["status"], "success")
                with patch.dict(os.environ, {"REAL_EXECUTION_ALLOWED_HOSTS": "example.invalid"}):
                    blocked = self.generate(tool)
                self.assertEqual(blocked["status"], "error")
                self.assertIn("safety preflight", blocked["message"])
                self.assertNotIn("script_source", blocked)

    def test_jmeter_rps_ceiling_still_applies_to_a_stored_script(self):
        self.assertEqual(self.generate("jmeter")["status"], "success")
        with patch.dict(os.environ, {"REAL_JMETER_MAX_RPS": "5"}):
            blocked = self.generate("jmeter")
        self.assertEqual(blocked["status"], "error")
        self.assertIn("maximum of 5", blocked["message"])
        self.assertNotIn("script_source", blocked)

    def test_a_failure_to_store_never_breaks_generation(self):
        for tool in TOOLS:
            with self.subTest(tool=tool):
                with patch.object(script_library, "_atomic_write", side_effect=OSError("disk full")):
                    result = self.generate(tool)
                self.assertEqual(result["status"], "success")
                self.assertEqual(result["script_source"], "generated")
                self.assertTrue(Path(result["file_path"]).is_file())

    def test_symlinked_library_directory_is_never_used(self):
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        link = self.root / script_library.LIBRARY_DIRECTORY_NAME
        try:
            os.symlink(outside.name, link, target_is_directory=True)
        except (OSError, NotImplementedError):
            # Windows without symlink rights: a junction needs no privilege and
            # is caught by the "resolves outside the artifact root" check.
            junction = (
                subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(link), outside.name],
                    capture_output=True,
                ).returncode
                if os.name == "nt"
                else 1
            )
            if junction != 0:
                self.skipTest("links are not available in this environment")
        result = self.generate("k6")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["script_source"], "generated")
        self.assertEqual(list(Path(outside.name).iterdir()), [])

    def test_stored_metadata_records_fingerprint_and_hash(self):
        self.generate("k6")
        meta = json.loads((self.entry("k6") / "script.meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["tool"], "k6")
        self.assertEqual(meta["test_case_id"], "PTC-001")
        self.assertEqual(len(meta["fingerprint"]), 64)
        self.assertEqual(len(meta["sha256"]), 64)


if __name__ == "__main__":
    unittest.main()

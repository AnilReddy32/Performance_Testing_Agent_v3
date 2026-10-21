import unittest

from Performance_Testing_Agent.jira_agent_integration.stage_plan import (
    build_execution_message,
    build_stage_plan,
    evaluate_done,
)

FULL_REQUEST = (
    "Run PTC-012 using Jmeter. Execute the real performance test and collect "
    "monitoring results. Assess the security surface for the same job and exact "
    "configured target. Analyze the current job’s results and generate the final "
    "PDF with security coverage and evidence, plus links to the native JMeter "
    "report, raw results, and final PDF."
)


def plan(text, case_id="PTC-012"):
    return build_stage_plan(text, test_case_id=case_id)


class TestKeywordPlan(unittest.TestCase):
    def test_full_request_plans_every_stage(self):
        result = plan(FULL_REQUEST)

        self.assertTrue(result.execute)
        self.assertTrue(result.monitoring)
        self.assertTrue(result.security)
        self.assertEqual(result.notes, ())

    def test_plain_run_monitors_but_skips_security(self):
        result = plan("Run PTC-012 using JMeter.")

        self.assertTrue(result.execute)
        self.assertTrue(result.monitoring)
        self.assertFalse(result.security)

    def test_empty_text_gives_the_default_plan(self):
        result = plan("")

        self.assertEqual(
            (result.execute, result.monitoring, result.security),
            (True, True, False),
        )

    def test_monitoring_can_be_skipped(self):
        for text in (
            "Skip monitoring.",
            "Run it without monitoring.",
            "No monitoring needed.",
            "Monitoring is not required.",
        ):
            with self.subTest(text=text):
                self.assertFalse(plan(text).monitoring)

    def test_refused_security_is_not_requested(self):
        for text in (
            "Do not run security scans.",
            "Skip the security assessment.",
            "No security checks please.",
        ):
            with self.subTest(text=text):
                self.assertFalse(plan(text).security)

    def test_refusing_other_stages_does_not_cancel_the_test(self):
        for text in (
            "Execute the test. Do not run security scans.",
            "Don't run monitoring, but do execute the load test.",
            "Do not execute anything for security.",
        ):
            with self.subTest(text=text):
                self.assertTrue(plan(text).execute)

    def test_mixed_request_keeps_the_wanted_stage(self):
        result = plan("Without monitoring, assess the security surface.")

        self.assertFalse(result.monitoring)
        self.assertTrue(result.security)

    def test_refusing_to_run_the_test_cancels_everything(self):
        for text in (
            "Do not run the test.",
            "Don't execute it.",
            "Only generate the script.",
            "Generate the script without running it.",
            "JMeter script only.",
        ):
            with self.subTest(text=text):
                result = plan(f"{text} Assess the security surface.")
                self.assertFalse(result.execute)
                self.assertFalse(result.monitoring)
                self.assertFalse(result.security)
                self.assertTrue(result.notes)

    def test_a_different_case_id_in_the_text_is_noted_and_ignored(self):
        result = plan("Run PTC-001 please.", case_id="PTC-005")

        self.assertTrue(result.execute)
        self.assertTrue(any("PTC-001" in note and "PTC-005" in note for note in result.notes))

    def test_the_selected_case_id_alone_adds_no_id_note(self):
        notes = plan("Run PTC-005.", case_id="PTC-005").notes

        self.assertFalse(any("PTC-" in note for note in notes))


class TestHelpers(unittest.TestCase):
    def test_execution_message_uses_only_trusted_values(self):
        message = build_execution_message("PTC-005", "jmeter")

        self.assertEqual(
            message,
            "Run test case PTC-005 using JMeter. Execute the real performance test "
            "with the trusted workload profile and return the execution result.",
        )

    def test_done_needs_a_completed_run_and_a_report(self):
        done, _ = evaluate_done(
            {"execution_status": "completed", "report_path": "r.pdf"}
        )
        self.assertTrue(done)

    def test_not_done_reasons_are_specific(self):
        _, reason = evaluate_done(
            {
                "execution_status": "failed",
                "execution_message": "k6 missing",
                "report_path": "r.pdf",
            }
        )
        self.assertIn("'failed'", reason)
        self.assertIn("k6 missing", reason)

        _, reason = evaluate_done(
            {"execution_status": "completed", "report_path": None}
        )
        self.assertIn("report was not created", reason)


if __name__ == "__main__":
    unittest.main()

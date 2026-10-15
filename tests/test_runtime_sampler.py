import csv
import sys
import tempfile
import time
import unittest
from pathlib import Path


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

from app.tools.runtime_sampler import RuntimeMetricsSampler


class TestRuntimeMetricsSampler(unittest.TestCase):
    def test_writes_timestamped_host_samples_with_provenance(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_path = Path(temporary_directory) / "runtime_samples.csv"
            sampler = RuntimeMetricsSampler(
                output_path,
                sample_interval_seconds=0.01,
            )
            sampler.start()
            time.sleep(0.05)
            result = sampler.stop()

            self.assertIsNone(result["sampling_error"])
            self.assertGreater(result["sample_count"], 0)
            with output_path.open(encoding="utf-8", newline="") as samples_file:
                rows = list(csv.DictReader(samples_file))

        sample = rows[0]
        self.assertTrue(sample["timestamp"].endswith("+00:00"))
        self.assertGreaterEqual(float(sample["elapsed_seconds"]), 0)
        self.assertGreaterEqual(float(sample["cpu_percent"]), 0)
        self.assertGreaterEqual(float(sample["memory_percent"]), 0)
        self.assertEqual(sample["measurement_scope"], "load_generator_host")
        self.assertEqual(sample["data_source"], "psutil")
        self.assertEqual(sample["target_resource_metric"], "false")


if __name__ == "__main__":
    unittest.main()

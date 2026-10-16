import os
import sys
import unittest
import xml.etree.ElementTree as ET
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

from app.tools.jmeter_template import build_real_jmeter_plan
from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case


class TestJMeterTemplate(unittest.TestCase):
    def test_https_catalog_case_uses_effective_default_port_443(self):
        profile = {
            **get_test_case("PTC-001")["workload_profile"],
            "tool": "jmeter",
        }
        with (
            patch.dict(
                os.environ,
                {
                    "REAL_EXECUTION_ENABLED": "true",
                    "REAL_EXECUTION_EXTERNAL_TARGETS_ENABLED": "true",
                    "REAL_EXECUTION_ALLOWED_HOSTS": "reqres.in",
                    "REAL_EXECUTION_ALLOWED_PORTS": "443",
                    "REAL_EXECUTION_MAX_USERS": "500",
                    "REAL_EXECUTION_MAX_DURATION_SECONDS": "500",
                    "REAL_EXECUTION_MAX_RAMP_UP_SECONDS": "90",
                },
                clear=True,
            ),
            patch(
                "Performance_Testing_Agent.execution_context.socket.getaddrinfo",
                return_value=[(None, None, None, None, ("8.8.8.8", 443))],
            ),
        ):
            plan = build_real_jmeter_plan(profile, test_case_id="PTC-001")

        root = ET.fromstring(plan)
        sampler_port = root.find(
            ".//HTTPSamplerProxy/stringProp[@name='HTTPSampler.port']"
        )
        self.assertIsNotNone(sampler_port)
        self.assertEqual(sampler_port.text, "443")


if __name__ == "__main__":
    unittest.main()

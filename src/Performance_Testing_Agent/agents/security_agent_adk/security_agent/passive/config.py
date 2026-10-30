"""Limits and switches for the passive external-surface assessment.

The assessment is deliberately small and fixed: a handful of ordinary,
non-state-changing requests against the job's own target, with no payloads.
None of these limits can be widened by a request, a prompt, or the model.
"""

import os

FALSE_VALUES = {"false", "0", "no", "off"}

# Hard ceiling on HTTP requests sent to the target in one assessment. The
# TLS handshake probe is a separate connection and sends no HTTP request.
MAX_HTTP_REQUESTS = 5
REQUEST_TIMEOUT_SECONDS = 5.0
# Overall deadline for all probing, so a slow target cannot stall the pipeline.
TOTAL_TIMEOUT_SECONDS = 40.0
MAX_RESPONSE_BYTES = 8192

HTTPS_PORT = 443
HTTP_PORT = 80
MAX_RESOLVED_ADDRESSES = 4
MAX_ENDPOINT_LENGTH = 1024

# A reserved, non-resolvable origin used only as the foreign Origin header of
# the CORS preflight. It can never be a real site.
FOREIGN_ORIGIN = "https://security-assessment.invalid"
USER_AGENT = "PerformanceTestingAgent-PassiveSecurityAssessment/1.0"

# Cap on how much of the performance run's own traffic log is read.
MAX_TRAFFIC_RECORDS = 2_000_000

AUTO_OBJECTIVE = (
    "Automatic passive external-surface security assessment of the "
    "performance-test target."
)


def _enabled(name: str) -> bool:
    return os.getenv(name, "true").strip().lower() not in FALSE_VALUES


def passive_assessment_enabled() -> bool:
    """Kill switch for every passive request (default on)."""
    return _enabled("SECURITY_PASSIVE_ASSESSMENT_ENABLED")


def auto_assessment_enabled() -> bool:
    """Whether REAL runs against external targets are assessed without being asked."""
    return _enabled("SECURITY_AUTO_ASSESSMENT_ENABLED")

import os
import warnings

# Corporate networks (e.g. HCL's) intercept outbound TLS with a proxy whose
# root CA is trusted by Windows but not by Python's bundled certifi CA list,
# which makes every outbound HTTPS call (including to api.openai.com) fail
# with CERTIFICATE_VERIFY_FAILED / "Connection error". Injecting truststore
# makes Python validate certificates against the OS trust store instead, so
# calls succeed the same way curl/the browser already do on this machine.
import truststore

truststore.inject_into_ssl()

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# ==========================================================
# FastAPI Configuration
# ==========================================================

APP_NAME = "Banking AI Performance Testing Agent"

APP_VERSION = "1.0.0"

HOST = "0.0.0.0"

PORT = 8000

# ==========================================================
# LLM Configuration
# (names match the variables defined in the .env file)
# ==========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-4.1"
)

OPENAI_EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small"
)

TEMPERATURE = float(
    os.getenv("TEMPERATURE", 0)
)

# ADK's LiteLlm wrapper (and the underlying openai / litellm SDKs) read the
# API key straight out of the OPENAI_API_KEY environment variable, so make
# sure it is exported even if it was only present in the .env file.
if OPENAI_API_KEY:
    os.environ.setdefault("OPENAI_API_KEY", OPENAI_API_KEY)
else:
    warnings.warn(
        "OPENAI_API_KEY is not set. Add it to your .env file before "
        "running the agent, otherwise every LLM call will fail."
    )

# LiteLLM model string ADK/LiteLlm expects, e.g. "openai/gpt-4.1"
LITELLM_MODEL_NAME = f"openai/{OPENAI_MODEL}"

# ==========================================================
# DATA
# (names match the variables defined in the .env file)
# ==========================================================

TEST_EXECUTION_DATASET = os.getenv(
    "TEST_EXECUTION_DATASET",
    "data/test_execution.csv"
)

MONITORING_DATASET = os.getenv(
    "MONITORING_DATASET",
    "data/monitoring.csv"
)

HISTORICAL_DATASET = os.getenv(
    "HISTORICAL_DATASET",
    "data/historical_execution.csv"
)

CHROMA_PATH = os.getenv(
    "CHROMA_PATH",
    "vector_db/chroma_db"
)

KNOWLEDGE_BASE_PATH = os.getenv(
    "KNOWLEDGE_BASE_PATH",
    "knowledge_base"
)

# ==========================================================
# Reports
# ==========================================================

REPORT_PATH = "generated_reports"

# ==========================================================
# Logging
# ==========================================================

LOG_LEVEL = "INFO"

# ==========================================================
# MCP TOOL CONNECTION
# (names match the variables defined in the .env file - both are
# optional and currently commented out there)
# ==========================================================

K6_TARGET_URL = os.getenv("K6_TARGET_URL")

JMETER_TARGET_URL = os.getenv("JMETER_TARGET_URL")

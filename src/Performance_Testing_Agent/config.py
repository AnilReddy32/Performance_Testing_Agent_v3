import os
from dotenv import load_dotenv
 
# Load environment variables

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
# ==========================================================
 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
 
MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "gemini-2.5-flash"
)
 
TEMPERATURE = float(
    os.getenv("TEMPERATURE", 0)
)
 
MAX_OUTPUT_TOKENS = int(
    os.getenv("MAX_OUTPUT_TOKENS", 2048)
)
 

 
# ==========================================================
# Vector Database
# ==========================================================
 
VECTOR_DB_PATH = "vector_db"
 
KNOWLEDGE_BASE_PATH = "knowledge_base"
 
# ==========================================================
# Reports
# ==========================================================
 
REPORT_PATH = "generated_reports"
 
# ==========================================================
# Logging
# ==========================================================
 
LOG_LEVEL = "INFO"
 
# ==========================================================
# MCP Server Configuration
# ==========================================================
 
MCP_SERVERS = {
 
    "test_execution": {
        "host": "localhost",
        "port": 8001
    },
 
    "monitoring": {
        "host": "localhost",
        "port": 8002
    },
 
    "security": {
        "host": "localhost",
        "port": 8003
    },
 
    "analysis": {
        "host": "localhost",
        "port": 8004
    },
 
    "report": {
        "host": "localhost",
        "port": 8005
    }
}
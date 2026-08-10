from ..agents.test_execution import TestExecutionAgent
from ..agents.monitoring import MonitoringAgent
from ..agents.security import SecurityAgent
from ..agents.analysis import AnalysisAgent
from ..agents.report import ReportAgent
 
AGENT_REGISTRY = {
 
    "Test Execution": TestExecutionAgent(),
 
    "Monitoring": MonitoringAgent(),
 
    "Security": SecurityAgent(),
 
    "Analysis": AnalysisAgent(),
 
    "Report": ReportAgent()
}

# Required by the ADK CLI (`adk web src` / `adk run`) so it can discover the
# orchestrator `root_agent` when this package is treated as an agent package.
from .orchestrator.agent import root_agent  # noqa: F401

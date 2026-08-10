from abc import ABC, abstractmethod
 
class BaseAgent(ABC):
    """
    Base class for all agents.
    Every agent must implement execute().
    """
 
    @abstractmethod
    async def execute(self, state):
        """
        Execute the agent.
 
        Args:
            state (dict): Shared AgentState
 
        Returns:
            Updated AgentState
        """
        pass
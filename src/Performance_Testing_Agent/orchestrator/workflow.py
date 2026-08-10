from langgraph.graph import StateGraph, END
 
from .state import AgentState
from .router import RouterNode
from .registry import (
    test_execution_node,
    monitoring_node,
    security_node,
    analysis_node,
    report_node,
)
 
 
class Workflow:
 
    def __init__(self):
 
        self.builder = StateGraph(AgentState)
 
        self._build_workflow()
 
        self.graph = self.builder.compile()
 
    def _build_workflow(self):
 
        # -------------------------
        # Add Nodes
        # -------------------------
 
        self.builder.add_node(
            "Router",
            RouterNode()
        )
 
        self.builder.add_node(
            "Test Execution",
            test_execution_node
        )
 
        self.builder.add_node(
            "Monitoring",
            monitoring_node
        )
 
        self.builder.add_node(
            "Security",
            security_node
        )
 
        self.builder.add_node(
            "Analysis",
            analysis_node
        )
 
        self.builder.add_node(
            "Report",
            report_node
        )
 
        # -------------------------
        # Entry Point
        # -------------------------
 
        self.builder.set_entry_point(
            "Router"
        )
 
        # -------------------------
        # Conditional Routing
        # -------------------------
 
        self.builder.add_conditional_edges(
            "Router",
            self.route_agents,
            {
                "Test Execution": "Test Execution",
                "Monitoring": "Monitoring",
                "Security": "Security",
                "Analysis": "Analysis",
                "Report": "Report",
            }
        )
 
        # -------------------------
        # End Nodes
        # -------------------------
 
        self.builder.add_edge(
            "Test Execution",
            END
        )
 
        self.builder.add_edge(
            "Monitoring",
            END
        )
 
        self.builder.add_edge(
            "Security",
            END
        )
 
        self.builder.add_edge(
            "Analysis",
            END
        )
 
        self.builder.add_edge(
            "Report",
            END
        )
 
    # -------------------------------------
 
    def route_agents(self, state):
 
        """
        Returns selected agents
        from AgentState.
        """
 
        return state["selected_agents"]
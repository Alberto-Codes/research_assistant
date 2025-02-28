"""
Research Agent Pydantic Graph implementation.
"""

from research_agent.core.dependencies import (
    CustomLLMClient,
    HelloWorldDependencies,
    LLMClient,
    MockLLMClient,
)
from research_agent.core.graph import display_results, get_hello_world_graph, run_graph

# Re-export key components for backward compatibility
from research_agent.core.nodes import CombineNode, HelloNode, PrintNode, WorldNode
from research_agent.core.state import MyState

__all__ = [
    # Nodes
    "HelloNode",
    "WorldNode",
    "CombineNode",
    "PrintNode",
    # State
    "MyState",
    # Graph
    "get_hello_world_graph",
    "run_graph",
    "display_results",
    # Dependencies
    "HelloWorldDependencies",
    "LLMClient",
    "MockLLMClient",
    "CustomLLMClient",
]

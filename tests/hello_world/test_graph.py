"""
Tests for the graph implementation.

This module tests the Hello World graph functionality, including initialization,
execution with various state and dependency configurations, and result processing.
"""

import pytest
import asyncio

from hello_world.core.graph import get_hello_world_graph as hello_world_graph, run_graph, display_results
from hello_world.core.state import MyState
from hello_world.core.nodes import HelloNode
from hello_world.core.dependencies import HelloWorldDependencies as GraphDependencies


@pytest.mark.asyncio
async def test_run_graph_default():
    """Test that the graph runs with default settings."""
    # Act
    output, state, history = await run_graph()
    
    # Assert
    assert output == "Hello World!"
    assert state.hello_text == "Hello"
    assert state.world_text == "World"
    assert state.combined_text == "Hello World!"
    assert len(history) == 5  # Four node steps + end step


@pytest.mark.asyncio
async def test_run_graph_with_initial_state():
    """Test that the graph respects initial state values."""
    # Arrange
    initial_state = MyState(hello_text="Custom Hello")
    
    # Act
    output, state, history = await run_graph(initial_state=initial_state)
    
    # Assert
    assert output == "Custom Hello World!"
    assert state.hello_text == "Custom Hello"  # Should not be changed
    assert state.world_text == "World"
    assert state.combined_text == "Custom Hello World!"


@pytest.mark.asyncio
async def test_run_graph_with_custom_dependencies(test_dependencies, test_llm_client):
    """Test that the graph works with custom dependencies."""
    # Act
    output, state, history = await run_graph(dependencies=test_dependencies)
    
    # Assert
    assert output == "Test Hello Test World!"
    assert state.hello_text == "Test Hello"
    assert state.world_text == "Test World"
    assert state.combined_text == "Test Hello Test World!"
    assert len(test_llm_client.calls) == 2  # Called for hello and world


@pytest.mark.asyncio
async def test_graph_with_complete_initial_state():
    """Test that the graph respects a complete initial state."""
    # Arrange
    initial_state = MyState(
        hello_text="Pre Hello", 
        world_text="Pre World", 
        combined_text="Pre Hello Pre World!"
    )
    
    # Act
    output, state, history = await run_graph(initial_state=initial_state)
    
    # Assert - State values should remain unchanged
    assert output == "Pre Hello Pre World!"
    assert state.hello_text == "Pre Hello"
    assert state.world_text == "Pre World"
    assert state.combined_text == "Pre Hello Pre World!"
    assert len(history) == 5  # All nodes + end step


class MockGraphRunResult:
    """Mock class for testing display_results."""
    def __init__(self, output, state, history):
        self.output = output
        self.state = state
        self.history = history


def test_display_results(capsys):
    """Test that display_results formats output correctly."""
    # Arrange
    state = MyState(hello_text="Test Hello", world_text="Test World", combined_text="Test Hello Test World!")
    history = [object(), object(), object(), object()]  # Dummy objects for history
    result = MockGraphRunResult("Test Hello Test World!", state, history)
    
    # Act
    display_results(result)
    
    # Assert
    captured = capsys.readouterr()
    assert "=== Graph Execution Results ===" in captured.out
    assert "Result: Test Hello Test World!" in captured.out
    assert "Final state: MyState" in captured.out
    assert "Node execution history:" in captured.out 
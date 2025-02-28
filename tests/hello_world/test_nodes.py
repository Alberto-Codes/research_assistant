"""
Tests for the Hello World nodes.
"""

import pytest
import asyncio

from hello_world.nodes import HelloNode, WorldNode, CombineNode, PrintNode
from hello_world.state import MyState
from hello_world.dependencies import GraphDependencies


@pytest.mark.asyncio
async def test_hello_node(initial_state, test_dependencies, test_llm_client):
    """Test that the HelloNode correctly updates the state."""
    # Arrange
    node = HelloNode()
    ctx = type("GraphRunContext", (), {"state": initial_state, "deps": test_dependencies})()
    
    # Act
    next_node = await node.run(ctx)
    
    # Assert
    assert initial_state.hello_text == "Test Hello"
    assert isinstance(next_node, WorldNode)
    assert "hello" in test_llm_client.calls[0].lower()


@pytest.mark.asyncio
async def test_world_node(initial_state, test_dependencies, test_llm_client):
    """Test that the WorldNode correctly updates the state."""
    # Arrange
    initial_state.hello_text = "Test Hello"  # Set by previous node
    node = WorldNode()
    ctx = type("GraphRunContext", (), {"state": initial_state, "deps": test_dependencies})()
    
    # Act
    next_node = await node.run(ctx)
    
    # Assert
    assert initial_state.world_text == "Test World"
    assert isinstance(next_node, CombineNode)
    assert "world" in test_llm_client.calls[0].lower()


@pytest.mark.asyncio
async def test_combine_node(initial_state, test_dependencies):
    """Test that the CombineNode correctly combines the texts."""
    # Arrange
    initial_state.hello_text = "Test Hello"
    initial_state.world_text = "Test World"
    node = CombineNode()
    ctx = type("GraphRunContext", (), {"state": initial_state, "deps": test_dependencies})()
    
    # Act
    next_node = await node.run(ctx)
    
    # Assert
    assert initial_state.combined_text == "Test Hello Test World!"
    assert isinstance(next_node, PrintNode)


@pytest.mark.asyncio
async def test_print_node(initial_state, test_dependencies):
    """Test that the PrintNode correctly ends the graph."""
    # Arrange
    initial_state.hello_text = "Test Hello"
    initial_state.world_text = "Test World"
    initial_state.combined_text = "Test Hello Test World!"
    node = PrintNode()
    ctx = type("GraphRunContext", (), {"state": initial_state, "deps": test_dependencies})()
    
    # Act
    result = await node.run(ctx)
    
    # Assert
    assert result.data == "Test Hello Test World!"
    # Check that the result is an End instance by checking its type/structure
    assert hasattr(result, 'data'), "Result should have a 'data' attribute"
    assert type(result).__name__ == "End", "Result should be an End object" 
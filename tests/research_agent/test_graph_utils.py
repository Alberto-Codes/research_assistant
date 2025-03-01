"""
Tests for the graph_utils module.

This module tests that the graph_utils module imports properly.
"""

import pytest

# Import the module to ensure it can be imported without errors
import research_agent.core.common.graph_utils as graph_utils


def test_graph_utils_imports():
    """Test that graph_utils module can be imported properly."""
    # Simply importing the module is enough to verify it loads correctly
    assert graph_utils is not None
    assert hasattr(graph_utils, "GraphRunResult")


if __name__ == "__main__":
    """Run the tests directly."""
    pytest.main(["-xvs", __file__])

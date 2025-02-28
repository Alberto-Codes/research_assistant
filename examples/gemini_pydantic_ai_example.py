"""
Example of using Pydantic-AI with Gemini via VertexAI.

This script demonstrates how to use Pydantic-AI directly to create
a simple graph with Gemini for AI response generation.
Based on the examples from https://ai.pydantic.dev/graph/#genai-example
"""

import asyncio
import time
from typing import Optional, List, Any, Dict
from dataclasses import dataclass, field

from pydantic_ai import Agent
from pydantic_ai.models.vertexai import VertexAIModel
from pydantic_graph import Graph, End
# Handle GraphDeps import - it might not be directly importable
try:
    from pydantic_graph import GraphDeps
except ImportError:
    # Define a simple GraphDeps class if not available
    @dataclass
    class GraphDeps:
        """Base class for graph dependencies."""
        pass

from pydantic_graph.nodes import BaseNode, GraphRunContext


# Define our state class to store data
@dataclass
class SimpleState:
    """Simple state for the Gemini example."""
    user_prompt: str = ""
    ai_response: str = ""
    generation_time: float = 0.0
    execution_history: List[str] = field(default_factory=list)


# Define dependencies to inject into nodes
@dataclass
class SimpleDeps(GraphDeps):
    """Simple dependencies for the Gemini example."""
    agent: Agent
    project_id: Optional[str] = None


# Define a node for generating AI responses
class GeminiResponseNode(BaseNode[SimpleState, SimpleDeps, str]):
    """Node that generates an AI response using Gemini."""
    
    async def run(self, ctx: GraphRunContext) -> End[str]:
        """Process the user prompt and generate a response."""
        # Record start time
        start_time = time.time()
        
        # Only generate response if we have a user prompt
        if ctx.state.user_prompt:
            try:
                # Use the Agent from dependencies to get a response
                ctx.state.ai_response = await ctx.deps.agent.run(ctx.state.user_prompt)
            except Exception as e:
                ctx.state.ai_response = f"Error generating response: {str(e)}"
            
            # Record generation time
            ctx.state.generation_time = time.time() - start_time
            
            # Add to execution history
            ctx.state.execution_history.append(
                f"GeminiResponseNode: Generated response to '{ctx.state.user_prompt[:30]}...'"
            )
        else:
            ctx.state.ai_response = "No prompt provided. Please enter a question or prompt."
        
        return End(ctx.state.ai_response)


def create_gemini_graph() -> Graph:
    """Create a graph with a GeminiResponseNode."""
    # Construct the graph with a list of node classes
    return Graph(
        nodes=[GeminiResponseNode],
    )


async def main(prompt: str, project_id: Optional[str] = None):
    """Run the Gemini example graph with the provided prompt."""
    print(f"Running Gemini example with prompt: {prompt}")
    
    try:
        # Create the Vertex AI model and agent
        if project_id:
            print(f"Using project ID: {project_id}")
            model = VertexAIModel('gemini-1.5-flash-001', project_id=project_id)
        else:
            print("Using default application credentials")
            model = VertexAIModel('gemini-1.5-flash-001')
        
        agent = Agent(model)
        
        # Initialize the state and dependencies
        state = SimpleState(user_prompt=prompt)
        deps = SimpleDeps(agent=agent, project_id=project_id)
        
        # Get the graph and run it
        graph = create_gemini_graph()
        print("Graph created, running...")
        result = await graph.run(GeminiResponseNode(), state=state, deps=deps)
        
        # Print the results
        print(f"\nUser Prompt: {result.state.user_prompt}")
        print(f"\nAI Response: {result.state.ai_response}")
        print(f"\nGeneration Time: {result.state.generation_time:.3f} seconds")
        print(f"\nExecution History: {result.state.execution_history}")
        
        return result
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise


if __name__ == "__main__":
    import sys
    
    # Get the prompt from command line arguments or use a default
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "What are the three laws of robotics?"
    
    # Run the example
    asyncio.run(main(prompt)) 
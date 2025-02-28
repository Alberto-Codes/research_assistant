"""
State definitions for the Hello World graph.
"""

from dataclasses import dataclass


@dataclass
class MyState:
    """State class for storing text values between nodes."""
    hello_text: str = ""
    world_text: str = ""
    combined_text: str = ""
    
    def __repr__(self) -> str:
        """Provide a nice string representation of the state."""
        return (
            f"MyState("
            f"hello_text='{self.hello_text}', "
            f"world_text='{self.world_text}', "
            f"combined_text='{self.combined_text}')"
        ) 
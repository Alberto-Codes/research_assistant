"""
State definition for the RAG graph in the Research Agent.

This module defines the state class used to store data as it flows
through the nodes in the RAG graph.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class RAGState:
    """
    State class for storing RAG workflow data including query, documents, and answer.

    Attributes:
        query: User's original query
        retrieved_documents: Documents retrieved from the collection
        answer: Generated answer based on the retrieved documents
        sources: Source information for the retrieved documents
        generation_time: Time taken to generate the answer
        retrieval_time: Time taken to retrieve documents
        total_time: Total time taken for the RAG process
    """

    query: str
    retrieved_documents: List[Dict[str, Any]] = field(default_factory=list)
    answer: Optional[str] = None
    sources: List[str] = field(default_factory=list)
    generation_time: float = 0.0
    retrieval_time: float = 0.0
    total_time: float = 0.0

    def __repr__(self) -> str:
        """Provide a nice string representation of the state."""
        return (
            f"RAGState("
            f"query='{self.query}', "
            f"num_docs={len(self.retrieved_documents)}, "
            f"answer_length={len(self.answer) if self.answer else 0}, "
            f"retrieval_time={self.retrieval_time:.3f}s, "
            f"generation_time={self.generation_time:.3f}s, "
            f"total_time={self.total_time:.3f}s)"
        )

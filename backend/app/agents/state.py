"""Shared LangGraph state for the multi-agent graph.

This is the typed channel every agent node reads from / writes to. It will grow as agents
are implemented in M2, but the shape is fixed here so nodes stay decoupled.
"""

from operator import add
from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage


class Citation(TypedDict):
    document_title: str
    page: int | None
    cloudinary_url: str | None
    snippet: str


class Evidence(TypedDict):
    content: str
    citation: Citation
    score: float


class AgentState(TypedDict, total=False):
    # Conversation messages (reducer appends).
    messages: Annotated[list[BaseMessage], add]
    # Planner output: ordered sub-questions.
    sub_questions: list[str]
    # Retrieval / research evidence gathered so far (reducer appends).
    evidence: Annotated[list[Evidence], add]
    # Supervisor routing decision.
    next_agent: str
    # Final composed answer + citations.
    answer: str
    citations: list[Citation]
    # Free-form scratchpad for inter-agent notes.
    scratchpad: dict[str, Any]

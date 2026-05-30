"""Multi-agent graph assembly (placeholder for M2).

The supervisor graph is built here and compiled with a Postgres checkpointer so every
conversation thread is durably persisted and resumable. Agent nodes are added in M2.
"""

from app.agents.state import AgentState

__all__ = ["AgentState", "build_graph"]


def build_graph():  # noqa: ANN201 - return type added when langgraph nodes land in M2
    """Build and compile the LangGraph supervisor graph.

    Implemented in milestone M2. Will:
      * register agent nodes (Planner, Retrieval, Market Research, Analyst, Writer, Critic)
      * wire the supervisor routing edges
      * compile with PostgresSaver (checkpointer) + PostgresStore (long-term memory)
    """
    raise NotImplementedError("Graph assembly arrives in milestone M2")

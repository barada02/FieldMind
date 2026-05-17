from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """State definition for the orchestrator agent."""
    messages: Annotated[list, add_messages]
    next_agent: str  # Track which agent should handle the request

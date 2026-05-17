"""
Orchestrator Agent using LangGraph.
This is the main conversational agent that will later coordinate with tools.
Phase 1: Basic conversation without tools.
"""

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from backend.app.config import get_settings

# Get application settings
settings = get_settings()

class AgentState(TypedDict):
    """State definition for the orchestrator agent."""
    messages: Annotated[list, add_messages]


class OrchestratorAgent:
    """
    Main orchestrator agent for Field Mind.
    Currently handles basic conversation, will be extended with tools later.
    """

    def __init__(self):
        """Initialize the orchestrator agent."""
        # Initialize LLM using the project's central settings
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            model=settings.openai_model,
            temperature=0.7
        )

        # System prompt
        self.system_prompt = """You are Field Mind, an intelligent assistant for field service technicians.

Your capabilities include:
- Machine diagnostics and troubleshooting
- Standard Operating Procedures (SOPs) guidance
- Inventory management support
- Ticket management assistance
- General technical support

Be helpful, concise, and professional. Provide clear, actionable advice."""

        # Create the graph
        self.graph = self._create_graph()

        # Memory for conversation history
        self.memory = MemorySaver()

        # Compile the graph with checkpointer
        self.app = self.graph.compile(checkpointer=self.memory)

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        workflow.add_node("llm", self._call_llm)
        workflow.add_edge(START, "llm")
        workflow.add_edge("llm", END)
        return workflow

    def _call_llm(self, state: AgentState) -> dict:
        """
        Call the LLM using LangChain wrapper.
        """
        messages = state["messages"]

        # Add system prompt to the beginning of the conversation
        full_messages = [{"role": "system", "content": self.system_prompt}] + messages

        try:
            response = self.llm.invoke(full_messages)
            return {
                "messages": [response]
            }
        except Exception as e:
            error_msg = f"Error calling LLM: {str(e)}"
            return {
                "messages": [{"role": "assistant", "content": error_msg}]
            }

    def chat(self, message: str, thread_id: str = "default") -> str:
        """
        Send a message and get a response.
        """
        input_state = {
            "messages": [{"role": "user", "content": message}]
        }
        config = {"configurable": {"thread_id": thread_id}}
        result = self.app.invoke(input_state, config)

        last_message = result["messages"][-1]
        return last_message.content if hasattr(last_message, "content") else last_message.get("content", "")

    async def achat(self, message: str, thread_id: str = "default") -> str:
        """
        Async version of chat.
        """
        input_state = {
            "messages": [{"role": "user", "content": message}]
        }
        config = {"configurable": {"thread_id": thread_id}}
        result = await self.app.ainvoke(input_state, config)

        last_message = result["messages"][-1]
        return last_message.content if hasattr(last_message, "content") else last_message.get("content", "")

    def get_history(self, thread_id: str = "default") -> list:
        """
        Get conversation history for a thread.
        """
        config = {"configurable": {"thread_id": thread_id}}
        try:
            state = self.app.get_state(config)
            if state and hasattr(state, "values") and "messages" in state.values:
                return [
                    {"role": "assistant" if hasattr(msg, "type") and msg.type == "ai" else "user",
                     "content": msg.content}
                    for msg in state.values["messages"]
                    if not (hasattr(msg, "type") and msg.type == "system")
                ]
        except Exception:
            pass
        return []


# Singleton instance
_agent_instance = None


def get_agent() -> OrchestratorAgent:
    """Get or create the orchestrator agent instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = OrchestratorAgent()
    return _agent_instance

# Made with Bob

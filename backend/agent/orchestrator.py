"""
Orchestrator Agent using LangGraph.
This is the main conversational agent that will later coordinate with tools.
Phase 1: Basic conversation without tools.
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
import os
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()


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
        # Get LLM configuration from environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
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
        # Initialize graph with state schema
        workflow = StateGraph(AgentState)
        
        # Add the LLM node
        workflow.add_node("llm", self._call_llm)
        
        # Set entry point
        workflow.add_edge(START, "llm")
        
        # Add edge from llm to END
        workflow.add_edge("llm", END)
        
        return workflow
    
    def _call_llm(self, state: AgentState) -> dict:
        """
        Call the LLM API with current conversation state.
        Uses OpenAI-compatible API.
        """
        messages = state["messages"]
        
        # Prepare messages for API call
        api_messages = [{"role": "system", "content": self.system_prompt}]
        
        for msg in messages:
            if hasattr(msg, "type"):
                # LangGraph message object
                role = "assistant" if msg.type == "ai" else "user"
                api_messages.append({"role": role, "content": msg.content})
            elif isinstance(msg, dict):
                # Already in dict format
                api_messages.append(msg)
        
        # Call OpenAI-compatible API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                
                # Extract assistant message
                assistant_message = result["choices"][0]["message"]["content"]
                
                # Return as LangGraph message
                return {
                    "messages": [{"role": "assistant", "content": assistant_message}]
                }
        
        except Exception as e:
            error_msg = f"Error calling LLM: {str(e)}"
            return {
                "messages": [{"role": "assistant", "content": error_msg}]
            }
    
    def chat(self, message: str, thread_id: str = "default") -> str:
        """
        Send a message and get a response.
        
        Args:
            message: User's message
            thread_id: Conversation thread ID for memory
            
        Returns:
            Agent's response
        """
        # Create input state
        input_state = {
            "messages": [{"role": "user", "content": message}]
        }
        
        # Configure with thread ID
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke the graph
        result = self.app.invoke(input_state, config)
        
        # Extract last message
        last_message = result["messages"][-1]
        if isinstance(last_message, dict):
            return last_message["content"]
        return last_message.content
    
    async def achat(self, message: str, thread_id: str = "default") -> str:
        """
        Async version of chat.
        
        Args:
            message: User's message
            thread_id: Conversation thread ID for memory
            
        Returns:
            Agent's response
        """
        # Create input state
        input_state = {
            "messages": [{"role": "user", "content": message}]
        }
        
        # Configure with thread ID
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke the graph asynchronously
        result = await self.app.ainvoke(input_state, config)
        
        # Extract last message
        last_message = result["messages"][-1]
        if isinstance(last_message, dict):
            return last_message["content"]
        return last_message.content
    
    def get_history(self, thread_id: str = "default") -> list:
        """
        Get conversation history for a thread.
        
        Args:
            thread_id: Conversation thread ID
            
        Returns:
            List of messages
        """
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            state = self.app.get_state(config)
            if state and hasattr(state, "values") and "messages" in state.values:
                messages = []
                for msg in state.values["messages"]:
                    if isinstance(msg, dict):
                        if msg.get("role") != "system":
                            messages.append(msg)
                    elif hasattr(msg, "type") and msg.type != "system":
                        role = "assistant" if msg.type == "ai" else "user"
                        messages.append({"role": role, "content": msg.content})
                return messages
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

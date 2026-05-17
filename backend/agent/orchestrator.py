"""
Orchestrator Agent using LangGraph.
Multi-Agent Network with RAG and Cloudant capabilities.
Phase 2: Agent routing and coordination.
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from backend.app.config import get_settings
import re

# Get application settings
settings = get_settings()

class AgentState(TypedDict):
    """State definition for the orchestrator agent."""
    messages: Annotated[list, add_messages]
    next_agent: str  # Track which agent should handle the request


class RagAgent:
    """
    RAG Agent for handling queries about SOPs, manuals, and how-to guides.
    Currently a shell implementation - will be connected to vector store later.
    """
    
    def __init__(self):
        """Initialize the RAG agent."""
        self.name = "RAG Agent"
    
    def process(self, state: AgentState) -> dict:
        """
        Process a query using RAG capabilities.
        Shell implementation - returns placeholder response.
        """
        messages = state["messages"]
        last_message = messages[-1]
        user_query = last_message.content if hasattr(last_message, "content") else last_message.get("content", "")
        
        response_content = f"""RAG Agent: I am ready to help with SOPs, manuals, and how-to guides.

Query received: "{user_query}"

[Shell Response] My vector store and document retrieval tools are not yet connected, but I'm designed to:
- Search through Standard Operating Procedures
- Retrieve relevant manual sections
- Provide step-by-step how-to guides
- Answer questions based on documentation

This capability will be fully implemented in the next phase."""
        
        return {
            "messages": [{"role": "assistant", "content": response_content}]
        }


class CloudantAgent:
    """
    Cloudant Agent for handling queries about machine status, tickets, and inventory.
    Currently a shell implementation - will be connected to Cloudant DB later.
    """
    
    def __init__(self):
        """Initialize the Cloudant agent."""
        self.name = "Cloudant Agent"
    
    def process(self, state: AgentState) -> dict:
        """
        Process a query using Cloudant database.
        Shell implementation - returns placeholder response.
        """
        messages = state["messages"]
        last_message = messages[-1]
        user_query = last_message.content if hasattr(last_message, "content") else last_message.get("content", "")
        
        response_content = f"""Cloudant Agent: I am ready to help with machine status, tickets, and inventory.

Query received: "{user_query}"

[Shell Response] My database tools are not yet connected, but I'm designed to:
- Check machine status and diagnostics
- Query and update service tickets
- Track inventory levels
- Retrieve equipment information

This capability will be fully implemented in the next phase."""
        
        return {
            "messages": [{"role": "assistant", "content": response_content}]
        }


class OrchestratorAgent:
    """
    Main orchestrator agent for Field Mind.
    Multi-agent coordinator with RAG and Cloudant capabilities.
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

        # Initialize specialized agents
        self.rag_agent = RagAgent()
        self.cloudant_agent = CloudantAgent()

        # Create the graph
        self.graph = self._create_graph()

        # Memory for conversation history
        self.memory = MemorySaver()

        # Compile the graph with checkpointer
        self.app = self.graph.compile(checkpointer=self.memory)

    def _create_graph(self) -> StateGraph:
        """
        Create the LangGraph workflow with multi-agent routing.
        
        Flow:
        START -> orchestrator -> route_request -> (rag_agent OR cloudant_agent OR llm) -> END
        """
        workflow = StateGraph(AgentState)
        
        # Add nodes for each agent
        workflow.add_node("orchestrator", self._orchestrator_node)
        workflow.add_node("rag", self._rag_node)
        workflow.add_node("cloudant", self._cloudant_node)
        workflow.add_node("llm", self._call_llm)
        
        # Start with orchestrator
        workflow.add_edge(START, "orchestrator")
        
        # Add conditional routing from orchestrator
        workflow.add_conditional_edges(
            "orchestrator",
            self._route_request,
            {
                "rag": "rag",
                "cloudant": "cloudant",
                "llm": "llm"
            }
        )
        
        # All agents return to END
        workflow.add_edge("rag", END)
        workflow.add_edge("cloudant", END)
        workflow.add_edge("llm", END)
        
        return workflow

    def _orchestrator_node(self, state: AgentState) -> dict:
        """
        Orchestrator node that prepares the state for routing.
        This node analyzes the query and sets up routing information.
        """
        # Simply pass through - routing logic is in _route_request
        return {"messages": state["messages"]}

    def _route_request(self, state: AgentState) -> Literal["rag", "cloudant", "llm"]:
        """
        Route the request to the appropriate agent based on query content.
        
        Routing logic:
        - RAG Agent: SOPs, manuals, how-to, procedures, documentation
        - Cloudant Agent: machine status, tickets, inventory, equipment
        - LLM: General queries, greetings, other topics
        """
        messages = state["messages"]
        last_message = messages[-1]
        query = last_message.content if hasattr(last_message, "content") else last_message.get("content", "")
        query_lower = query.lower()
        
        # RAG patterns: SOPs, manuals, how-to guides, procedures
        rag_patterns = [
            r'\b(sop|standard operating procedure)s?\b',
            r'\b(manual|documentation|guide)s?\b',
            r'\bhow\s+(to|do|can)\b',
            r'\b(procedure|process|step)s?\b',
            r'\b(instruction|tutorial)s?\b',
            r'\bwhat\s+is\s+the\s+(process|procedure)\b'
        ]
        
        # Cloudant patterns: machine status, tickets, inventory
        cloudant_patterns = [
            r'\b(machine|equipment|device)s?\s+(status|state|condition)\b',
            r'\b(ticket|service\s+request)s?\b',
            r'\b(inventory|stock|parts?)\b',
            r'\b(check|query|find|search)\s+(machine|equipment|ticket|inventory)\b',
            r'\b(machine|equipment)\s+(id|number|serial)\b',
            r'\b(open|closed|pending)\s+tickets?\b'
        ]
        
        # Check RAG patterns
        for pattern in rag_patterns:
            if re.search(pattern, query_lower):
                return "rag"
        
        # Check Cloudant patterns
        for pattern in cloudant_patterns:
            if re.search(pattern, query_lower):
                return "cloudant"
        
        # Default to general LLM for greetings and other queries
        return "llm"

    def _rag_node(self, state: AgentState) -> dict:
        """RAG agent node."""
        return self.rag_agent.process(state)

    def _cloudant_node(self, state: AgentState) -> dict:
        """Cloudant agent node."""
        return self.cloudant_agent.process(state)

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

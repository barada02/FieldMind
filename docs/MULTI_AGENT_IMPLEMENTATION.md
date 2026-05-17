# Multi-Agent Network Implementation

## Overview
This document describes the implementation of the multi-agent network architecture for Field Mind, transitioning from a single LLM node to a coordinated multi-agent system.

## Architecture

### Agent Structure

```
START → Orchestrator → Route Request → [RAG Agent | Cloudant Agent | General LLM] → END
```

### Components

#### 1. **RagAgent** (Shell Implementation)
- **Purpose**: Handles queries about SOPs, manuals, and how-to guides
- **Current Status**: Shell implementation with placeholder responses
- **Future**: Will be connected to vector store for document retrieval
- **Triggers**: Queries containing keywords like "SOP", "manual", "how to", "procedure", "guide"

#### 2. **CloudantAgent** (Shell Implementation)
- **Purpose**: Handles queries about machine status, tickets, and inventory
- **Current Status**: Shell implementation with placeholder responses
- **Future**: Will be connected to Cloudant database
- **Triggers**: Queries containing keywords like "machine status", "ticket", "inventory", "equipment"

#### 3. **General LLM**
- **Purpose**: Handles general queries, greetings, and other topics
- **Current Status**: Fully functional
- **Triggers**: Default fallback for queries not matching RAG or Cloudant patterns

### Routing Logic

The `_route_request()` method implements intelligent routing using regex pattern matching:

**RAG Patterns:**
- `\b(sop|standard operating procedure)s?\b`
- `\b(manual|documentation|guide)s?\b`
- `\bhow\s+(to|do|can)\b`
- `\b(procedure|process|step)s?\b`
- `\b(instruction|tutorial)s?\b`

**Cloudant Patterns:**
- `\b(machine|equipment|device)s?\s+(status|state|condition)\b`
- `\b(ticket|service\s+request)s?\b`
- `\b(inventory|stock|parts?)\b`
- `\b(check|query|find|search)\s+(machine|equipment|ticket|inventory)\b`

## Implementation Details

### State Management

```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str  # Track which agent should handle the request
```

### Graph Structure

```python
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("orchestrator", self._orchestrator_node)
workflow.add_node("rag", self._rag_node)
workflow.add_node("cloudant", self._cloudant_node)
workflow.add_node("llm", self._call_llm)

# Define edges
workflow.add_edge(START, "orchestrator")
workflow.add_conditional_edges(
    "orchestrator",
    self._route_request,
    {"rag": "rag", "cloudant": "cloudant", "llm": "llm"}
)
workflow.add_edge("rag", END)
workflow.add_edge("cloudant", END)
workflow.add_edge("llm", END)
```

## Testing

A test script (`test_agents.py`) has been created to verify routing functionality:

```bash
python test_agents.py
```

This will test:
1. RAG agent routing with SOP queries
2. RAG agent routing with manual queries
3. Cloudant agent routing with machine status queries
4. Cloudant agent routing with ticket queries
5. General LLM routing with greetings

## Example Queries

### RAG Agent
- "How do I perform maintenance on machine X?"
- "Show me the manual for equipment installation"
- "What is the procedure for system startup?"

### Cloudant Agent
- "What is the status of machine 123?"
- "Show me open tickets for site A"
- "Check inventory levels for part XYZ"

### General LLM
- "Hello, how are you?"
- "What can you help me with?"
- "Tell me about Field Mind"

## Next Steps

### Phase 2: Tool Integration
1. **RAG Agent**: Connect to vector store (Pinecone/Chroma)
   - Implement document embedding
   - Add similarity search
   - Integrate retrieval pipeline

2. **Cloudant Agent**: Connect to Cloudant database
   - Implement database queries
   - Add CRUD operations
   - Integrate with MCP tools

3. **Enhanced Routing**: Add context-aware routing
   - Consider conversation history
   - Implement multi-agent collaboration
   - Add fallback mechanisms

## Files Modified

- [`backend/agent/orchestrator.py`](../backend/agent/orchestrator.py) - Main implementation
- [`test_agents.py`](../test_agents.py) - Test script

## Benefits

1. **Modularity**: Each agent handles specific domain expertise
2. **Scalability**: Easy to add new specialized agents
3. **Maintainability**: Clear separation of concerns
4. **Flexibility**: Routing logic can be enhanced without affecting agents
5. **Performance**: Specialized agents can be optimized independently

## Notes

- Both RAG and Cloudant agents are currently shell implementations
- Routing is based on keyword matching (will be enhanced with semantic understanding)
- All agents maintain conversation context through LangGraph state management
- Memory is preserved across interactions using MemorySaver checkpointer
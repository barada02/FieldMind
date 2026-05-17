# Field Mind Orchestrator Agent

## Overview

The Orchestrator Agent is a LangGraph-based conversational agent that serves as the main interface for Field Mind. It's designed to be extended with tools and capabilities in future phases.

## Current Implementation (Phase 1)

### Features

- **Pure LangGraph Implementation**: Uses LangGraph for state management and workflow
- **Conversation Memory**: Maintains context across multiple messages using thread IDs
- **OpenAI-Compatible API**: Works with any OpenAI-compatible LLM provider
- **Async Support**: Provides both sync and async chat methods
- **Thread Management**: Supports multiple independent conversation threads

### Architecture

```
┌─────────────────────────────────────────┐
│         Orchestrator Agent              │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │      LangGraph Workflow          │  │
│  │                                  │  │
│  │  START → LLM Node → END          │  │
│  │                                  │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │      Memory Saver                │  │
│  │  (Conversation History)          │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

### Components

#### 1. AgentState
```python
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
```
Defines the state structure for the agent, containing the conversation messages.

#### 2. OrchestratorAgent
Main agent class that:
- Initializes the LLM connection
- Creates the LangGraph workflow
- Manages conversation memory
- Provides chat interfaces

#### 3. Graph Workflow
Simple linear workflow:
- **START**: Entry point
- **LLM Node**: Processes messages and generates responses
- **END**: Exit point

## Usage

### Basic Usage

```python
from agent import get_agent

# Get the agent instance
agent = get_agent()

# Send a message
response = agent.chat("Hello! Who are you?", thread_id="user_123")
print(response)

# Continue conversation (maintains context)
response = agent.chat("What can you help me with?", thread_id="user_123")
print(response)
```

### Async Usage

```python
import asyncio
from agent import get_agent

async def chat_async():
    agent = get_agent()
    response = await agent.achat("Hello!", thread_id="user_123")
    print(response)

asyncio.run(chat_async())
```

### Get Conversation History

```python
from agent import get_agent

agent = get_agent()
history = agent.get_history(thread_id="user_123")

for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

## Configuration

The agent uses environment variables for configuration:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview
```

## API Reference

### OrchestratorAgent

#### `__init__()`
Initializes the agent with LLM configuration and creates the graph.

#### `chat(message: str, thread_id: str = "default") -> str`
Send a message and get a response synchronously.

**Parameters:**
- `message`: User's message
- `thread_id`: Conversation thread ID for memory (default: "default")

**Returns:**
- Agent's response as a string

#### `achat(message: str, thread_id: str = "default") -> str`
Async version of chat.

**Parameters:**
- `message`: User's message
- `thread_id`: Conversation thread ID for memory (default: "default")

**Returns:**
- Agent's response as a string

#### `get_history(thread_id: str = "default") -> list`
Get conversation history for a thread.

**Parameters:**
- `thread_id`: Conversation thread ID

**Returns:**
- List of message dictionaries with 'role' and 'content' keys

### Helper Functions

#### `get_agent() -> OrchestratorAgent`
Get or create the singleton agent instance.

**Returns:**
- OrchestratorAgent instance

## Integration with FastAPI

The agent is integrated with the FastAPI chat endpoint:

```python
from agent import get_agent

@router.post("/chat")
async def chat(request: ChatRequest):
    agent = get_agent()
    response = await agent.achat(
        message=request.message,
        thread_id=request.conversation_id
    )
    return ChatResponse(
        conversation_id=request.conversation_id,
        message=response
    )
```

## Future Enhancements

### Phase 2: Tool Integration
- Add RAG tool for SOP retrieval
- Add database tools for machine/inventory queries
- Add ticket management tools

### Phase 3: Multi-Agent System
- Specialized agents for different tasks
- Agent coordination and routing
- Parallel agent execution

### Phase 4: Advanced Features
- Streaming responses
- Function calling
- Custom tool creation
- Agent memory persistence

## Testing

See [`tests/README.md`](../../tests/README.md) for testing instructions.

Quick test:
```bash
cd tests
python quick_test.py
```

Full test suite:
```bash
# Start server
cd backend
python -m uvicorn app.main:app --reload

# In another terminal
cd tests
python test_chat_api.py --mode test
```

## Troubleshooting

### Import Errors
The basedpyright errors about langgraph imports are expected if you haven't installed the dependencies yet. Install them with:
```bash
cd backend
pip install -r requirements.txt
```

### API Connection Issues
- Verify your `.env` file has correct credentials
- Check that OPENAI_BASE_URL is accessible
- Ensure the model name is correct for your provider

### Memory Issues
- Each thread_id maintains separate conversation history
- Use different thread_ids for different users/conversations
- Memory is stored in-memory and will be lost on restart

## Dependencies

- `langgraph`: Graph-based workflow framework
- `httpx`: HTTP client for API calls
- `python-dotenv`: Environment variable management

## License

Part of the Field Mind project.
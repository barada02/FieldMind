# Field Mind Testing Guide

## Testing the Orchestrator Agent

The orchestrator agent is a LangGraph-based conversational agent that serves as the main interface for Field Mind.

### Prerequisites

1. Ensure you have set up your `.env` file in the `backend` directory with:
   ```
   OPENAI_API_KEY=your_api_key
   OPENAI_BASE_URL=your_base_url
   OPENAI_MODEL=your_model_name
   ```

2. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

### Running Tests

#### 1. Start the Server

First, start the FastAPI server:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

The server will start at `http://localhost:8000`

#### 2. Run Automated Tests

In a new terminal, run the test suite:

```bash
cd tests
python test_chat_api.py --mode test
```

This will run automated tests including:
- Health check
- Simple greeting
- Follow-up questions (memory test)
- Technical questions
- Conversation history retrieval
- Multiple conversation threads

#### 3. Interactive Mode

For manual testing, use interactive mode:

```bash
cd tests
python test_chat_api.py --mode interactive
```

Commands in interactive mode:
- Type your message to chat with the agent
- `history` - View conversation history
- `new` - Start a new conversation
- `quit` or `exit` - Exit interactive mode

### Testing with Custom URL

If your server is running on a different port or host:

```bash
python test_chat_api.py --url http://localhost:8080 --mode test
```

### Expected Results

The orchestrator agent should:
- ✓ Respond to greetings and introductions
- ✓ Maintain conversation context across messages
- ✓ Answer technical questions about field service
- ✓ Store and retrieve conversation history
- ✓ Handle multiple conversation threads independently

### Troubleshooting

**Server not responding:**
- Check if the server is running: `http://localhost:8000/health`
- Verify your `.env` file has correct API credentials
- Check server logs for errors

**Agent not responding:**
- Verify OPENAI_API_KEY is set correctly
- Check OPENAI_BASE_URL is accessible
- Ensure the model name is correct

**Import errors:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify you're running from the correct directory

### Next Steps

After successful testing:
1. The agent can be extended with tools (RAG, database access, etc.)
2. Additional specialized agents can be added
3. The orchestrator can coordinate between multiple agents
4. Streaming responses can be implemented

## API Endpoints

### POST /api/chat
Send a message to the agent.

**Request:**
```json
{
  "message": "Hello, who are you?",
  "conversation_id": "optional-conversation-id"
}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "message": "Agent response",
  "sources": [],
  "metadata": {
    "agent": "orchestrator",
    "processing_time": 0.5
  },
  "timestamp": "2024-01-01T00:00:00"
}
```

### GET /api/chat/history/{conversation_id}
Retrieve conversation history.

**Response:**
```json
[
  {
    "role": "user",
    "content": "Hello",
    "timestamp": "2024-01-01T00:00:00"
  },
  {
    "role": "assistant",
    "content": "Hi there!",
    "timestamp": "2024-01-01T00:00:01"
  }
]
```

### GET /health
Check server health.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00"
}
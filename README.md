# Field Mind - Multi-Agent System for Field Technicians

Field Mind is an intelligent multi-agent system designed to assist technicians and field workers with:
- 🔍 Finding SOPs (Standard Operating Procedures) for any problem
- 🔧 Querying tool and parts inventory
- 🏭 Getting machine information and maintenance history
- 🎫 Creating purchase tickets for tools and parts

## Features

### 🤖 Intelligent Agent System
- Natural language understanding
- Context-aware responses
- Multi-tool orchestration with LangGraph
- Streaming responses for better UX

### 📚 RAG-Powered SOP Retrieval
- Semantic search across all SOPs
- Relevant section extraction
- Source citation and references
- Support for PDF, DOCX, TXT, and Markdown

### 🔌 Custom MCP Server
- Direct integration with IBM Cloudant
- Machine data queries
- Inventory management
- Ticket creation and tracking

### 💻 Simple Web Interface
- Clean, responsive chat UI
- Real-time streaming responses
- Quick action buttons
- Message history

## Architecture

```
┌─────────────┐
│   Frontend  │ (HTML/CSS/JS)
└──────┬──────┘
       │ HTTP/WebSocket
┌──────▼──────┐
│   FastAPI   │
│   Backend   │
└──────┬──────┘
       │
   ┌───▼────┐
   │LangGraph│
   │  Agent  │
   └───┬────┘
       │
   ┌───▼────────────┬──────────┐
   │                │          │
┌──▼───┐    ┌──────▼─┐   ┌───▼────┐
│ RAG  │    │  MCP   │   │  LLM   │
│Pipeline│  │ Server │   │Provider│
└──┬───┘    └───┬────┘   └────────┘
   │            │
┌──▼────┐  ┌───▼────────┐
│ChromaDB│  │  Cloudant  │
└────────┘  └────────────┘
```

## Technology Stack

- **Backend**: FastAPI, Python 3.10+
- **Agent Framework**: LangGraph
- **Vector Database**: ChromaDB
- **Database**: IBM Cloudant (NoSQL)
- **LLM**: OpenAI-compatible API (configurable)
- **Frontend**: HTML, CSS, JavaScript (Vanilla)
- **MCP**: Custom Model Context Protocol server

## Quick Start

### Prerequisites

- Python 3.10 or higher
- IBM Cloudant account with credentials
- OpenAI API key (or compatible provider)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd FieldMind
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

4. **Configure environment variables**
```bash
cp backend/.env.example backend/.env
# Edit .env with your credentials
```

5. **Initialize databases**
```bash
# Create Cloudant databases
python scripts/init_cloudant.py

# Initialize ChromaDB (automatic on first run)
```

6. **Start the MCP server**
```bash
python -m backend.mcp_server.server
```

7. **Start the FastAPI backend**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

8. **Access the application**
Open your browser and navigate to: `http://localhost:8000/static/index.html`

## Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# LLM Configuration
OPENAI_API_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4-turbo

# IBM Cloudant
CLOUDANT_URL=https://your-account.cloudant.com
CLOUDANT_API_KEY=your_cloudant_api_key
CLOUDANT_USERNAME=your_username
CLOUDANT_PASSWORD=your_password

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./data/chromadb

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# MCP Server
MCP_SERVER_PORT=3000
```

## Usage

### Chat Interface

1. Open the web interface
2. Type your question in the input field
3. Press Enter or click Send
4. View the agent's response with sources

### Example Queries

**Finding SOPs:**
```
"How do I calibrate the CNC machine?"
"What's the procedure for replacing the hydraulic pump?"
```

**Checking Inventory:**
```
"Do we have torque wrenches in stock?"
"Show me all tools below minimum quantity"
```

**Machine Information:**
```
"What's the status of machine Alpha-001?"
"Show me maintenance history for CNC machines"
```

**Creating Tickets:**
```
"Create a purchase ticket for 3 torque wrenches"
"I need to order replacement parts for machine Beta-002"
```

### Ingesting SOPs

Use the API endpoint to upload SOP documents:

```bash
curl -X POST "http://localhost:8000/api/sop/ingest" \
  -F "file=@path/to/sop.pdf" \
  -F "metadata={\"title\":\"CNC Calibration\",\"machine_types\":[\"CNC\"]}"
```

Or use the Python client:

```python
from backend.rag.ingestion import SOPIngestionPipeline

pipeline = SOPIngestionPipeline(
    persist_directory="./data/chromadb",
    openai_api_key="your_key"
)

pipeline.ingest_document(
    file_path="path/to/sop.pdf",
    metadata={
        "title": "CNC Calibration Procedure",
        "machine_types": ["CNC"],
        "version": "2.1"
    }
)
```

## Project Structure

```
FieldMind/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── models.py            # Pydantic models
│   │   └── api/
│   │       ├── chat.py          # Chat endpoints
│   │       └── sop.py           # SOP management
│   ├── agent/
│   │   ├── supervisor.py        # Main agent
│   │   ├── state.py             # Agent state
│   │   └── graph.py             # LangGraph definition
│   ├── rag/
│   │   ├── ingestion.py         # Document processing
│   │   ├── retriever.py         # RAG retrieval
│   │   └── embeddings.py        # Embedding generation
│   ├── mcp_server/
│   │   ├── server.py            # MCP server
│   │   ├── cloudant_client.py   # Cloudant wrapper
│   │   └── tools/
│   │       ├── machine.py       # Machine tools
│   │       ├── inventory.py     # Inventory tools
│   │       └── ticket.py        # Ticket tools
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── app.js
│       └── chat.js
├── data/
│   ├── sops/                    # SOP documents
│   └── chromadb/                # ChromaDB storage
├── docs/
│   ├── API.md
│   ├── SETUP.md
│   └── USER_GUIDE.md
├── tests/
│   ├── test_agent.py
│   ├── test_rag.py
│   └── test_mcp.py
├── scripts/
│   ├── init_cloudant.py         # Initialize Cloudant DBs
│   └── seed_data.py             # Seed sample data
├── .gitignore
├── README.md
├── ARCHITECTURE.md
└── IMPLEMENTATION_GUIDE.md
```

## API Documentation

### REST Endpoints

#### Chat
- `POST /api/chat` - Send message to agent
- `GET /api/chat/stream` - WebSocket for streaming responses

#### SOP Management
- `POST /api/sop/ingest` - Upload and process SOP document
- `GET /api/sop/list` - List all indexed SOPs
- `DELETE /api/sop/{sop_id}` - Remove SOP from index

#### Health
- `GET /api/health` - Health check endpoint

### WebSocket Protocol

Connect to `/api/chat/stream` and send:
```json
{
  "text": "Your question here",
  "context": {}
}
```

Receive:
```json
{
  "type": "chunk",
  "content": "Response chunk..."
}
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agent.py

# Run with coverage
pytest --cov=backend tests/
```

### Code Style

```bash
# Format code
black backend/

# Lint code
flake8 backend/

# Type checking
mypy backend/
```

### Adding New MCP Tools

1. Create tool file in `backend/mcp_server/tools/`
2. Implement tool class with `handle()` method
3. Register tool in `backend/mcp_server/server.py`
4. Update documentation

## Troubleshooting

### Common Issues

**MCP Server Connection Failed**
- Ensure MCP server is running on correct port
- Check firewall settings
- Verify environment variables

**ChromaDB Initialization Error**
- Check write permissions for data directory
- Ensure sufficient disk space
- Verify ChromaDB version compatibility

**Cloudant Connection Error**
- Verify credentials in .env file
- Check network connectivity
- Ensure databases exist

**LLM API Errors**
- Verify API key is valid
- Check API base URL
- Monitor rate limits

## Performance Optimization

- **Caching**: Implement Redis for frequent queries
- **Batch Processing**: Process multiple documents in parallel
- **Connection Pooling**: Reuse Cloudant connections
- **Async Operations**: Use async/await throughout
- **Streaming**: Stream responses for better UX

## Security

- Store credentials in environment variables
- Use HTTPS in production
- Implement rate limiting
- Validate all inputs
- Sanitize user queries
- Regular security audits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Your License Here]

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: See `docs/` directory
- Email: [support-email]

## Roadmap

### Phase 1 (Current)
- ✅ Core architecture design
- ⏳ Basic agent implementation
- ⏳ MCP server development
- ⏳ RAG pipeline setup

### Phase 2
- Multi-language support
- Voice input/output
- Mobile app
- Advanced analytics

### Phase 3
- Predictive maintenance
- Automated ticket routing
- Integration with ERP systems
- Offline mode

## Acknowledgments

- LangChain team for the agent framework
- Anthropic for MCP specification
- IBM for Cloudant database
- OpenAI for LLM capabilities
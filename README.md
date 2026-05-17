# Field Mind - AI-Powered Field Technician Assistant

Field Mind is a multi-agent system designed to assist field technicians with finding SOPs, querying inventory, checking machine information, and creating purchase tickets.

## 🌟 Features

- **SOP Search**: Semantic search across Standard Operating Procedures using RAG
- **Machine Information**: Query machine details from IBM Cloudant database
- **Inventory Management**: Check tool and parts availability
- **Ticket Creation**: Create purchase tickets for required tools/parts
- **Real-time Chat**: WebSocket-based streaming responses
- **Multi-Agent System**: Powered by LangGraph for intelligent task routing

## 🏗️ Architecture

Field Mind uses a multi-agent architecture with:
- **Supervisor Agent**: Routes queries to specialized agents
- **RAG Agent**: Searches SOPs using ChromaDB vector database
- **Database Agent**: Queries IBM Cloudant via custom MCP server
- **Synthesis Node**: Aggregates results and generates responses

## 📋 Prerequisites

- Python 3.10 or higher
- IBM Cloudant account and credentials
- OpenAI API key (or compatible LLM provider)
- Git

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd FieldMind
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment

```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit backend/.env with your credentials
# Required:
# - OPENAI_API_KEY
# - CLOUDANT_URL
# - CLOUDANT_USERNAME or CLOUDANT_API_KEY
```

### 5. Initialize Directories

```bash
# Create necessary directories
mkdir -p data/sops data/chromadb logs
```

### 6. Start the Application

```bash
# Start FastAPI backend
cd backend
uvicorn app.main:app --reload --port 8000

# Or use Python directly
python -m app.main
```

### 7. Access the Interface

Open your browser and navigate to:
```
http://localhost:8000
```

## 📁 Project Structure

```
FieldMind/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── health.py        # Health check endpoints
│   │       └── chat.py          # Chat endpoints
│   ├── agent/                   # Multi-agent system (Phase 4)
│   │   ├── __init__.py
│   │   ├── supervisor.py
│   │   ├── rag_agent.py
│   │   ├── database_agent.py
│   │   └── graph.py
│   ├── rag/                     # RAG pipeline (Phase 3)
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   └── retrieval.py
│   ├── mcp_server/              # MCP server (Phase 2)
│   │   ├── __init__.py
│   │   ├── server.py
│   │   └── tools/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── index.html               # Main HTML interface
│   ├── css/
│   │   └── styles.css           # Styles
│   └── js/
│       └── app.js               # Frontend logic
├── data/
│   ├── sops/                    # SOP documents
│   └── chromadb/                # Vector database
├── docs/                        # Documentation
├── Plandocs/                    # Planning documents
│   ├── PROJECT_PLAN.md
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_GUIDE.md
│   └── CONSIDERATIONS.md
├── scripts/                     # Utility scripts
├── tests/                       # Test files
└── README.md
```

## 🔧 Configuration

### Environment Variables

Edit `backend/.env` with your configuration:

```env
# OpenAI-compatible LLM
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# IBM Cloudant
CLOUDANT_URL=https://your-account.cloudant.com
CLOUDANT_USERNAME=your_username
CLOUDANT_PASSWORD=your_password
# OR
CLOUDANT_API_KEY=your_api_key

# Database Names
CLOUDANT_MACHINES_DB=machines
CLOUDANT_INVENTORY_DB=inventory
CLOUDANT_TICKETS_DB=tickets

# ChromaDB
CHROMA_PERSIST_DIRECTORY=../data/chromadb
CHROMA_COLLECTION_NAME=sops

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
APP_DEBUG=true
```

## 📊 API Endpoints

### Health Check
```
GET /api/health
```

### Chat
```
POST /api/chat
Body: {
  "message": "How do I calibrate the CNC machine?",
  "conversation_id": "optional-uuid"
}
```

### WebSocket
```
WS /ws/chat
```

## 🧪 Testing

```bash
# Run tests (Phase 6)
pytest tests/

# Run with coverage
pytest --cov=backend tests/
```

## 📈 Development Phases

- ✅ **Phase 1**: Foundation (Current)
  - Project structure
  - FastAPI application
  - Configuration management
  - Frontend interface

- ⏳ **Phase 2**: MCP Server
  - Custom MCP server for Cloudant
  - Database tools implementation

- ⏳ **Phase 3**: RAG Pipeline
  - ChromaDB setup
  - Document ingestion
  - Semantic search

- ⏳ **Phase 4**: Multi-Agent System
  - Supervisor agent
  - RAG agent
  - Database agent
  - LangGraph orchestration

- ⏳ **Phase 5**: Integration
  - Agent system integration
  - Streaming responses
  - Error handling

- ⏳ **Phase 6**: Testing & Documentation
  - Unit tests
  - Integration tests
  - Documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 📞 Support

For questions or issues, please open an issue on GitHub.

## 🙏 Acknowledgments

- Built with FastAPI, LangGraph, and ChromaDB
- Powered by OpenAI-compatible LLMs
- Integrated with IBM Cloudant

---

**Status**: Phase 1 Complete ✅  
**Version**: 1.0.0  
**Last Updated**: 2024
# Field Mind - Implementation Guide

## Technical Specifications

### 1. LangGraph Agent Implementation

#### Agent State Definition
```python
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_tool: str
    tool_results: dict
    context: dict
    next_action: str
```

#### Supervisor Agent Graph
```python
from langgraph.graph import StateGraph, END

def create_agent_graph():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("rag_tool", rag_tool_node)
    workflow.add_node("machine_tool", machine_tool_node)
    workflow.add_node("inventory_tool", inventory_tool_node)
    workflow.add_node("ticket_tool", ticket_tool_node)
    workflow.add_node("generate_response", response_node)
    
    # Add edges
    workflow.add_edge("supervisor", route_to_tool)
    workflow.add_edge("rag_tool", "generate_response")
    workflow.add_edge("machine_tool", "generate_response")
    workflow.add_edge("inventory_tool", "generate_response")
    workflow.add_edge("ticket_tool", "generate_response")
    workflow.add_edge("generate_response", END)
    
    workflow.set_entry_point("supervisor")
    
    return workflow.compile()
```

#### Tool Routing Logic
```python
def route_to_tool(state: AgentState) -> str:
    """Route to appropriate tool based on user query"""
    last_message = state["messages"][-1].content
    
    # Use LLM to classify intent
    classification = classify_intent(last_message)
    
    if "sop" in classification or "procedure" in classification:
        return "rag_tool"
    elif "machine" in classification or "equipment" in classification:
        return "machine_tool"
    elif "inventory" in classification or "stock" in classification:
        return "inventory_tool"
    elif "ticket" in classification or "purchase" in classification:
        return "ticket_tool"
    else:
        # Default to RAG for general queries
        return "rag_tool"
```

### 2. RAG Pipeline Implementation

#### Document Ingestion
```python
from langchain.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

class SOPIngestionPipeline:
    def __init__(self, persist_directory: str, openai_api_key: str):
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.vectorstore = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embeddings
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def ingest_document(self, file_path: str, metadata: dict):
        # Load document based on file type
        if file_path.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif file_path.endswith('.docx'):
            loader = UnstructuredWordDocumentLoader(file_path)
        else:
            loader = TextLoader(file_path)
        
        documents = loader.load()
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(documents)
        
        # Add metadata
        for chunk in chunks:
            chunk.metadata.update(metadata)
        
        # Add to vectorstore
        self.vectorstore.add_documents(chunks)
        self.vectorstore.persist()
        
        return len(chunks)
```

#### RAG Retrieval
```python
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI

class RAGRetriever:
    def __init__(self, vectorstore, llm):
        self.vectorstore = vectorstore
        self.llm = llm
        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
    
    def retrieve_sop(self, query: str) -> dict:
        # Retrieve relevant documents
        docs = self.retriever.get_relevant_documents(query)
        
        # Format context
        context = "\n\n".join([
            f"Source: {doc.metadata.get('title', 'Unknown')}\n{doc.page_content}"
            for doc in docs
        ])
        
        # Generate response using LLM
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            return_source_documents=True
        )
        
        result = qa_chain({"query": query})
        
        return {
            "answer": result["result"],
            "sources": [
                {
                    "title": doc.metadata.get("title"),
                    "page": doc.metadata.get("page"),
                    "content": doc.page_content[:200]
                }
                for doc in result["source_documents"]
            ]
        }
```

### 3. Custom MCP Server Implementation

#### MCP Server Structure
```python
# mcp_server/server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from .tools.machine import MachineTools
from .tools.inventory import InventoryTools
from .tools.ticket import TicketTools
from .cloudant_client import CloudantClient

class FieldMindMCPServer:
    def __init__(self):
        self.server = Server("fieldmind-mcp")
        self.cloudant = CloudantClient()
        self.machine_tools = MachineTools(self.cloudant)
        self.inventory_tools = InventoryTools(self.cloudant)
        self.ticket_tools = TicketTools(self.cloudant)
        
        self._register_tools()
    
    def _register_tools(self):
        # Register all tools
        tools = [
            # Machine tools
            Tool(
                name="get_machine_info",
                description="Get detailed information about a specific machine",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "machine_id": {"type": "string"}
                    },
                    "required": ["machine_id"]
                }
            ),
            Tool(
                name="search_machines",
                description="Search for machines by criteria",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "location": {"type": "string"},
                        "status": {"type": "string"}
                    }
                }
            ),
            # Inventory tools
            Tool(
                name="check_inventory",
                description="Check availability of a tool or part",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "tool_name": {"type": "string"}
                    },
                    "required": ["tool_name"]
                }
            ),
            Tool(
                name="get_low_stock_items",
                description="Get list of items below minimum quantity",
                inputSchema={"type": "object", "properties": {}}
            ),
            # Ticket tools
            Tool(
                name="create_ticket",
                description="Create a new purchase or maintenance ticket",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["purchase", "maintenance"]},
                        "items": {"type": "array"},
                        "priority": {"type": "string"},
                        "notes": {"type": "string"}
                    },
                    "required": ["type", "items"]
                }
            )
        ]
        
        for tool in tools:
            self.server.add_tool(tool)
    
    async def handle_call_tool(self, name: str, arguments: dict):
        # Route to appropriate tool handler
        if name.startswith("get_machine") or name.startswith("search_machine"):
            return await self.machine_tools.handle(name, arguments)
        elif name.startswith("check_inventory") or name.startswith("get_low_stock"):
            return await self.inventory_tools.handle(name, arguments)
        elif name.startswith("create_ticket") or name.startswith("get_ticket"):
            return await self.ticket_tools.handle(name, arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def run(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )
```

#### Cloudant Client Wrapper
```python
# mcp_server/cloudant_client.py
from cloudant.client import Cloudant
from cloudant.error import CloudantException
import os

class CloudantClient:
    def __init__(self):
        self.client = Cloudant.iam(
            account_name=os.getenv("CLOUDANT_USERNAME"),
            api_key=os.getenv("CLOUDANT_API_KEY"),
            url=os.getenv("CLOUDANT_URL"),
            connect=True
        )
        
        # Initialize databases
        self.machines_db = self.client["machines_db"]
        self.inventory_db = self.client["inventory_db"]
        self.tickets_db = self.client["tickets_db"]
        self.sop_metadata_db = self.client["sop_metadata_db"]
    
    def get_document(self, db_name: str, doc_id: str):
        db = getattr(self, f"{db_name}_db")
        try:
            return db[doc_id]
        except KeyError:
            return None
    
    def query_documents(self, db_name: str, selector: dict):
        db = getattr(self, f"{db_name}_db")
        return list(db.get_query_result(selector))
    
    def create_document(self, db_name: str, document: dict):
        db = getattr(self, f"{db_name}_db")
        doc = db.create_document(document)
        return doc["_id"]
    
    def update_document(self, db_name: str, doc_id: str, updates: dict):
        db = getattr(self, f"{db_name}_db")
        doc = db[doc_id]
        doc.update(updates)
        doc.save()
        return doc
```

#### Machine Tools Implementation
```python
# mcp_server/tools/machine.py
class MachineTools:
    def __init__(self, cloudant_client):
        self.cloudant = cloudant_client
    
    async def handle(self, tool_name: str, arguments: dict):
        if tool_name == "get_machine_info":
            return await self.get_machine_info(arguments["machine_id"])
        elif tool_name == "search_machines":
            return await self.search_machines(arguments)
        elif tool_name == "get_machine_history":
            return await self.get_machine_history(arguments["machine_id"])
    
    async def get_machine_info(self, machine_id: str):
        machine = self.cloudant.get_document("machines", machine_id)
        if not machine:
            return {"error": f"Machine {machine_id} not found"}
        
        return {
            "machine_id": machine["_id"],
            "name": machine["name"],
            "model": machine["model"],
            "location": machine["location"],
            "status": machine["status"],
            "last_maintenance": machine.get("last_maintenance"),
            "common_issues": machine.get("common_issues", []),
            "required_tools": machine.get("required_tools", [])
        }
    
    async def search_machines(self, criteria: dict):
        selector = {}
        if "query" in criteria:
            selector["name"] = {"$regex": f"(?i){criteria['query']}"}
        if "location" in criteria:
            selector["location"] = criteria["location"]
        if "status" in criteria:
            selector["status"] = criteria["status"]
        
        machines = self.cloudant.query_documents("machines", selector)
        return {
            "count": len(machines),
            "machines": [
                {
                    "id": m["_id"],
                    "name": m["name"],
                    "location": m["location"],
                    "status": m["status"]
                }
                for m in machines
            ]
        }
```

### 4. FastAPI Backend Implementation

#### Main Application
```python
# backend/app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api import chat, sop
from .config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Field Mind API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Include routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(sop.router, prefix="/api/sop", tags=["sop"])

@app.get("/")
async def root():
    return {"message": "Field Mind API is running"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
```

#### Chat Endpoint with Streaming
```python
# backend/app/api/chat.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from ..agent.supervisor import create_agent_graph
from ..models import ChatRequest, ChatResponse
import json
import asyncio

router = APIRouter()
agent_graph = create_agent_graph()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message to the agent"""
    result = await agent_graph.ainvoke({
        "messages": [{"role": "user", "content": request.message}],
        "context": request.context or {}
    })
    
    return ChatResponse(
        message=result["messages"][-1].content,
        tool_used=result.get("current_tool"),
        sources=result.get("tool_results", {}).get("sources", [])
    )

@router.websocket("/stream")
async def chat_stream(websocket: WebSocket):
    """Stream agent responses via WebSocket"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Stream agent response
            async for chunk in agent_graph.astream({
                "messages": [{"role": "user", "content": message["text"]}],
                "context": message.get("context", {})
            }):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk
                })
            
            await websocket.send_json({"type": "done"})
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
```

### 5. Frontend Implementation

#### Chat Interface
```javascript
// frontend/js/chat.js
class ChatInterface {
    constructor() {
        this.ws = null;
        this.messageContainer = document.getElementById('messages');
        this.inputField = document.getElementById('message-input');
        this.sendButton = document.getElementById('send-button');
        
        this.initializeWebSocket();
        this.attachEventListeners();
    }
    
    initializeWebSocket() {
        this.ws = new WebSocket('ws://localhost:8000/api/chat/stream');
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'chunk') {
                this.appendChunk(data.content);
            } else if (data.type === 'done') {
                this.finishMessage();
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.showError('Connection error. Please refresh the page.');
        };
    }
    
    attachEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.inputField.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
    }
    
    sendMessage() {
        const message = this.inputField.value.trim();
        if (!message) return;
        
        // Display user message
        this.addMessage('user', message);
        
        // Send to backend
        this.ws.send(JSON.stringify({
            text: message,
            context: {}
        }));
        
        // Clear input
        this.inputField.value = '';
        
        // Show typing indicator
        this.showTypingIndicator();
    }
    
    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-header">${role === 'user' ? 'You' : 'Field Mind'}</div>
                <div class="message-text">${this.formatMessage(content)}</div>
            </div>
        `;
        this.messageContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Convert markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }
    
    showTypingIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'typing-indicator';
        indicator.className = 'message agent-message';
        indicator.innerHTML = `
            <div class="message-content">
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        this.messageContainer.appendChild(indicator);
        this.scrollToBottom();
    }
    
    removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) indicator.remove();
    }
    
    scrollToBottom() {
        this.messageContainer.scrollTop = this.messageContainer.scrollHeight;
    }
}

// Initialize chat interface
document.addEventListener('DOMContentLoaded', () => {
    new ChatInterface();
});
```

### 6. Configuration Management

#### Environment Configuration
```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # LLM Configuration
    openai_api_base_url: str
    openai_api_key: str
    openai_model: str = "gpt-4-turbo"
    
    # IBM Cloudant
    cloudant_url: str
    cloudant_api_key: str
    cloudant_username: str
    cloudant_password: str
    
    # ChromaDB
    chroma_persist_directory: str = "./data/chromadb"
    
    # MCP Server
    mcp_server_port: int = 3000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

## Dependencies

### Backend Requirements
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
langchain==0.1.0
langchain-openai==0.0.5
langchain-community==0.0.13
langgraph==0.0.20
chromadb==0.4.22
cloudant==2.15.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
websockets==12.0
pypdf==3.17.4
python-docx==1.1.0
unstructured==0.11.8
python-dotenv==1.0.0
```

### Frontend Dependencies
```html
<!-- No external dependencies needed for basic implementation -->
<!-- Optional: Add these for enhanced features -->
<script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify/dist/purify.min.js"></script>
```

## Testing Strategy

### Unit Tests
- Test individual MCP tools
- Test RAG retrieval accuracy
- Test agent routing logic
- Test Cloudant operations

### Integration Tests
- Test end-to-end agent flow
- Test MCP server communication
- Test FastAPI endpoints
- Test WebSocket streaming

### Performance Tests
- RAG retrieval speed
- Agent response time
- Concurrent user handling
- Database query optimization

## Deployment Considerations

### Local Development
```bash
# Start MCP server
python -m mcp_server.server

# Start FastAPI backend
uvicorn backend.app.main:app --reload --port 8000

# Serve frontend (or use FastAPI static files)
python -m http.server 3000 --directory frontend
```

### Production Deployment
- Use Gunicorn/Uvicorn workers
- Set up reverse proxy (Nginx)
- Configure SSL certificates
- Set up monitoring and logging
- Use environment-specific configs
- Implement rate limiting
- Set up backup strategies

## Next Steps

1. Review this implementation guide
2. Confirm technical approach
3. Begin with Phase 1 implementation
4. Iterate based on feedback
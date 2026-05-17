"""
Field Mind - Main FastAPI Application
Multi-agent system for field technician assistance
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path

from backend.app.config import get_settings
from backend.app.api import chat, health

# Configure logging
settings = get_settings()
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Field Mind application...")
    logger.info(f"OpenAI Base URL: {settings.openai_base_url}")
    logger.info(f"ChromaDB Directory: {settings.chroma_persist_directory}")
    logger.info(f"MCP Server URL: {settings.mcp_server_url}")
    
    # Initialize databases and connections here
    # TODO: Initialize ChromaDB
    # TODO: Initialize Cloudant connection
    # TODO: Initialize MCP client
    
    yield
    
    # Shutdown
    logger.info("Shutting down Field Mind application...")
    # Cleanup resources here


# Create FastAPI application
app = FastAPI(
    title="Field Mind",
    description="Multi-agent system for field technician assistance",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    logger.info(f"Mounted static files from: {frontend_path}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - redirect to frontend."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Field Mind</title>
        <meta http-equiv="refresh" content="0; url=/static/index.html">
    </head>
    <body>
        <p>Redirecting to <a href="/static/index.html">Field Mind</a>...</p>
    </body>
    </html>
    """


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with streaming responses."""
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")
            
            logger.info(f"Received message: {message}")
            
            # TODO: Process message through agent system
            # For now, send a simple echo response
            response = {
                "type": "message",
                "content": f"Echo: {message}",
                "status": "complete"
            }
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
        log_level=settings.log_level.lower()
    )

# Made with Bob

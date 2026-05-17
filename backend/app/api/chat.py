"""
Chat API endpoints for Field Mind application.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging
import uuid
import time

from agent import get_agent

logger = logging.getLogger(__name__)
router = APIRouter()


class Message(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role: user, assistant, or system")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")
    history: Optional[List[Message]] = Field(default=[], description="Conversation history")


class ChatResponse(BaseModel):
    """Chat response model."""
    conversation_id: str = Field(..., description="Conversation ID")
    message: str = Field(..., description="Assistant response")
    sources: Optional[List[dict]] = Field(default=[], description="Source citations")
    metadata: Optional[dict] = Field(default={}, description="Additional metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StreamChunk(BaseModel):
    """Streaming response chunk model."""
    type: str = Field(..., description="Chunk type: token, source, or complete")
    content: str = Field(default="", description="Chunk content")
    metadata: Optional[dict] = Field(default={}, description="Additional metadata")


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def chat(request: ChatRequest):
    """
    Process a chat message and return a response.
    
    Args:
        request: ChatRequest containing user message and optional context
        
    Returns:
        ChatResponse: Assistant response with sources and metadata
    """
    try:
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        # Generate or use existing conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())
        
        # Get the orchestrator agent
        agent = get_agent()
        
        # Track processing time
        start_time = time.time()
        
        # Process message through agent
        response_message = await agent.achat(
            message=request.message,
            thread_id=conversation_id
        )
        
        processing_time = time.time() - start_time
        
        return ChatResponse(
            conversation_id=conversation_id,
            message=response_message,
            sources=[],
            metadata={
                "agent": "orchestrator",
                "processing_time": round(processing_time, 3)
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )


@router.get("/chat/history/{conversation_id}", response_model=List[Message])
async def get_conversation_history(conversation_id: str):
    """
    Retrieve conversation history by ID.
    
    Args:
        conversation_id: Unique conversation identifier
        
    Returns:
        List[Message]: Conversation history
    """
    try:
        logger.info(f"Retrieving conversation history: {conversation_id}")
        
        # Get agent and retrieve history
        agent = get_agent()
        history = agent.get_history(thread_id=conversation_id)
        
        # Convert to Message objects
        messages = []
        for msg in history:
            messages.append(Message(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.utcnow()
            ))
        
        return messages
        
    except Exception as e:
        logger.error(f"Error retrieving conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation history: {str(e)}"
        )


@router.delete("/chat/history/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_history(conversation_id: str):
    """
    Delete conversation history by ID.
    
    Args:
        conversation_id: Unique conversation identifier
    """
    try:
        logger.info(f"Deleting conversation history: {conversation_id}")
        
        # TODO: Delete from database/cache
        return None
        
    except Exception as e:
        logger.error(f"Error deleting conversation history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting conversation history: {str(e)}"
        )

# Made with Bob

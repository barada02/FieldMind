"""
Voice API endpoints for Field Mind application.
Provides Speech-to-Text and Text-to-Speech capabilities.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, status, Query
from fastapi.responses import Response
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import logging
from io import BytesIO

from backend.app.config import get_settings
from backend.voice.service import VoiceService
from backend.voice.utils import get_audio_content_type, validate_audio_file
from pathlib import Path

logger = logging.getLogger(__name__)
router = APIRouter()

# Global voice service instance
_voice_service: Optional[VoiceService] = None


def get_voice_service() -> VoiceService:
    """Get or create voice service instance."""
    global _voice_service
    
    if _voice_service is None:
        settings = get_settings()
        
        if not settings.voice_configured:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Voice services are not configured. Please set Watson credentials."
            )
        
        _voice_service = VoiceService(
            stt_apikey=settings.stt_apikey,
            stt_url=settings.stt_url,
            tts_apikey=settings.tts_apikey,
            tts_url=settings.tts_url,
            stt_model=settings.stt_model,
            tts_voice=settings.tts_voice
        )
    
    return _voice_service


class TranscriptionResponse(BaseModel):
    """Response model for transcription."""
    text: str = Field(..., description="Transcribed text")
    confidence: Optional[float] = Field(None, description="Confidence score")
    raw_result: Optional[Dict[str, Any]] = Field(None, description="Raw Watson result")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SynthesisRequest(BaseModel):
    """Request model for speech synthesis."""
    text: str = Field(..., description="Text to convert to speech", max_length=5000)
    voice: Optional[str] = Field(None, description="Voice to use (e.g., en-US_AllisonV3Voice)")
    format: str = Field(default="wav", description="Audio format: wav, mp3, ogg")


class VoiceInfoResponse(BaseModel):
    """Response model for voice service information."""
    enabled: bool = Field(..., description="Whether voice services are enabled")
    available_voices: Optional[list] = Field(None, description="Available TTS voices")
    available_models: Optional[list] = Field(None, description="Available STT models")


@router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio: UploadFile = File(..., description="Audio file to transcribe"),
    model: Optional[str] = Query(None, description="STT model to use"),
    include_raw: bool = Query(False, description="Include raw Watson result")
):
    """
    Transcribe audio file to text using Watson Speech-to-Text.
    
    Supported formats: WAV, FLAC, MP3, OGG, OPUS, WEBM
    Maximum file size: 10MB (configurable)
    """
    try:
        settings = get_settings()
        
        # Check file size
        content = await audio.read()
        if len(content) > settings.max_audio_size_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file too large. Maximum size: {settings.max_audio_size_mb}MB"
            )
        
        # Determine content type
        content_type = audio.content_type or "audio/wav"
        if audio.filename:
            file_path = Path(audio.filename)
            content_type = get_audio_content_type(file_path)
        
        logger.info(f"Transcribing audio file: {audio.filename}, type: {content_type}")
        
        # Get voice service and transcribe
        voice_service = get_voice_service()
        audio_stream = BytesIO(content)
        result = voice_service.transcribe_audio(audio_stream, content_type, model)
        
        # Extract transcript text
        transcript_text = voice_service.extract_transcript_text(result)
        
        # Calculate average confidence
        confidence = None
        if "results" in result and len(result["results"]) > 0:
            confidences = []
            for res in result["results"]:
                if "alternatives" in res and len(res["alternatives"]) > 0:
                    if "confidence" in res["alternatives"][0]:
                        confidences.append(res["alternatives"][0]["confidence"])
            if confidences:
                confidence = sum(confidences) / len(confidences)
        
        return TranscriptionResponse(
            text=transcript_text,
            confidence=confidence,
            raw_result=result if include_raw else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transcribing audio: {str(e)}"
        )


@router.post("/synthesize")
async def synthesize_speech(request: SynthesisRequest):
    """
    Convert text to speech using Watson Text-to-Speech.
    
    Returns audio file in the specified format.
    """
    try:
        logger.info(f"Synthesizing speech: {request.text[:50]}...")
        
        # Map format to MIME type
        format_mapping = {
            "wav": "audio/wav",
            "mp3": "audio/mp3",
            "ogg": "audio/ogg",
            "flac": "audio/flac",
            "opus": "audio/opus",
            "webm": "audio/webm"
        }
        
        accept = format_mapping.get(request.format.lower(), "audio/wav")
        
        # Get voice service and synthesize
        voice_service = get_voice_service()
        audio_data = voice_service.synthesize_speech(
            text=request.text,
            voice=request.voice,
            accept=accept
        )
        
        return Response(
            content=audio_data,
            media_type=accept,
            headers={
                "Content-Disposition": f"attachment; filename=speech.{request.format}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error synthesizing speech: {str(e)}"
        )


@router.get("/info", response_model=VoiceInfoResponse)
async def get_voice_info():
    """
    Get information about available voice services, models, and voices.
    """
    try:
        settings = get_settings()
        
        if not settings.voice_configured:
            return VoiceInfoResponse(
                enabled=False,
                available_voices=None,
                available_models=None
            )
        
        voice_service = get_voice_service()
        
        # Get available voices and models
        voices_result = voice_service.get_available_voices()
        models_result = voice_service.get_available_models()
        
        # Extract voice names
        voices = []
        if "voices" in voices_result:
            voices = [
                {
                    "name": v["name"],
                    "language": v.get("language", ""),
                    "gender": v.get("gender", ""),
                    "description": v.get("description", "")
                }
                for v in voices_result["voices"]
            ]
        
        # Extract model names
        models = []
        if "models" in models_result:
            models = [
                {
                    "name": m["name"],
                    "language": m.get("language", ""),
                    "description": m.get("description", "")
                }
                for m in models_result["models"]
            ]
        
        return VoiceInfoResponse(
            enabled=True,
            available_voices=voices,
            available_models=models
        )
        
    except Exception as e:
        logger.error(f"Error getting voice info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting voice info: {str(e)}"
        )


@router.get("/health")
async def voice_health_check():
    """
    Check if voice services are available and configured.
    """
    settings = get_settings()
    
    return {
        "status": "healthy" if settings.voice_configured else "unavailable",
        "voice_enabled": settings.voice_enabled,
        "stt_configured": bool(settings.stt_apikey and settings.stt_url),
        "tts_configured": bool(settings.tts_apikey and settings.tts_url),
        "timestamp": datetime.utcnow()
    }

# Made with Bob

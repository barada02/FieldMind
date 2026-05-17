"""
Utility functions for voice processing.
"""

from pathlib import Path
from typing import Optional
import os


def get_audio_content_type(audio_path: Path) -> str:
    """
    Determine the content type based on audio file extension.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        str: MIME type for the audio file
    """
    ext = audio_path.suffix.lower()
    mapping = {
        ".wav": "audio/wav",
        ".flac": "audio/flac",
        ".mp3": "audio/mp3",
        ".ogg": "audio/ogg",
        ".opus": "audio/opus",
        ".webm": "audio/webm",
    }
    return mapping.get(ext, "audio/wav")


def validate_audio_file(audio_path: Path) -> bool:
    """
    Validate that the audio file exists and has a supported format.
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not audio_path.exists():
        return False
    
    supported_extensions = {".wav", ".flac", ".mp3", ".ogg", ".opus", ".webm"}
    return audio_path.suffix.lower() in supported_extensions


def load_env_file(env_path: Path) -> None:
    """
    Load environment variables from a .env file.
    
    Args:
        env_path: Path to the .env file
    """
    if not env_path.exists():
        return
    
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key and key not in os.environ:
            os.environ[key] = value


def get_audio_format_from_accept(accept: str) -> str:
    """
    Convert HTTP Accept header to audio format.
    
    Args:
        accept: HTTP Accept header value
        
    Returns:
        str: Audio format (e.g., 'wav', 'mp3')
    """
    format_mapping = {
        "audio/wav": "wav",
        "audio/mp3": "mp3",
        "audio/ogg": "ogg",
        "audio/flac": "flac",
        "audio/opus": "opus",
        "audio/webm": "webm",
    }
    return format_mapping.get(accept.lower(), "wav")

# Made with Bob

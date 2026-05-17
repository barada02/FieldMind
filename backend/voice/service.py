"""
Voice service for Speech-to-Text and Text-to-Speech using IBM Watson.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, BinaryIO
from io import BytesIO

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1, TextToSpeechV1

from .utils import get_audio_content_type

logger = logging.getLogger(__name__)


class VoiceService:
    """
    Service for handling voice operations using IBM Watson.
    Provides Speech-to-Text and Text-to-Speech capabilities.
    """
    
    def __init__(
        self,
        stt_apikey: str,
        stt_url: str,
        tts_apikey: str,
        tts_url: str,
        stt_model: str = "en-US_BroadbandModel",
        tts_voice: str = "en-US_AllisonV3Voice"
    ):
        """
        Initialize the voice service with Watson credentials.
        
        Args:
            stt_apikey: IBM Watson Speech-to-Text API key
            stt_url: IBM Watson Speech-to-Text service URL
            tts_apikey: IBM Watson Text-to-Speech API key
            tts_url: IBM Watson Text-to-Speech service URL
            stt_model: Speech-to-Text model to use
            tts_voice: Text-to-Speech voice to use
        """
        self.stt_model = stt_model
        self.tts_voice = tts_voice
        
        # Initialize Speech-to-Text
        try:
            stt_authenticator = IAMAuthenticator(stt_apikey)
            self.stt = SpeechToTextV1(authenticator=stt_authenticator)
            self.stt.set_service_url(stt_url)
            logger.info("Speech-to-Text service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Speech-to-Text: {e}")
            raise
        
        # Initialize Text-to-Speech
        try:
            tts_authenticator = IAMAuthenticator(tts_apikey)
            self.tts = TextToSpeechV1(authenticator=tts_authenticator)
            self.tts.set_service_url(tts_url)
            logger.info("Text-to-Speech service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Text-to-Speech: {e}")
            raise
    
    def transcribe_audio(
        self,
        audio_file: BinaryIO,
        content_type: str = "audio/wav",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using Watson Speech-to-Text.
        
        Args:
            audio_file: Audio file as binary stream
            content_type: MIME type of the audio file
            model: Optional model override
            
        Returns:
            Dict containing transcription results with confidence scores
        """
        try:
            model_to_use = model or self.stt_model
            
            logger.info(f"Transcribing audio with model: {model_to_use}")
            
            result = self.stt.recognize(
                audio=audio_file,
                content_type=content_type,
                model=model_to_use,
            ).get_result()
            
            logger.info("Audio transcription completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            raise
    
    def transcribe_audio_file(
        self,
        audio_path: Path,
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_path: Path to the audio file
            model: Optional model override
            
        Returns:
            Dict containing transcription results
        """
        try:
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            content_type = get_audio_content_type(audio_path)
            
            with audio_path.open("rb") as audio_file:
                return self.transcribe_audio(audio_file, content_type, model)
                
        except Exception as e:
            logger.error(f"Error transcribing audio file: {e}")
            raise
    
    def extract_transcript_text(self, result: Dict[str, Any]) -> str:
        """
        Extract the transcript text from Watson STT result.
        
        Args:
            result: Watson STT result dictionary
            
        Returns:
            str: Extracted transcript text
        """
        try:
            if "results" in result and len(result["results"]) > 0:
                transcripts = []
                for res in result["results"]:
                    if "alternatives" in res and len(res["alternatives"]) > 0:
                        transcripts.append(res["alternatives"][0]["transcript"])
                return " ".join(transcripts).strip()
            return ""
        except Exception as e:
            logger.error(f"Error extracting transcript: {e}")
            return ""
    
    def synthesize_speech(
        self,
        text: str,
        voice: Optional[str] = None,
        accept: str = "audio/wav"
    ) -> bytes:
        """
        Convert text to speech using Watson Text-to-Speech.
        
        Args:
            text: Text to convert to speech
            voice: Optional voice override
            accept: Audio format (MIME type)
            
        Returns:
            bytes: Audio data
        """
        try:
            voice_to_use = voice or self.tts_voice
            
            logger.info(f"Synthesizing speech with voice: {voice_to_use}")
            
            audio = self.tts.synthesize(
                text,
                voice=voice_to_use,
                accept=accept,
            ).get_result().content
            
            logger.info("Speech synthesis completed successfully")
            return audio
            
        except Exception as e:
            logger.error(f"Error synthesizing speech: {e}")
            raise
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: Path,
        voice: Optional[str] = None,
        accept: str = "audio/wav"
    ) -> Path:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            voice: Optional voice override
            accept: Audio format (MIME type)
            
        Returns:
            Path: Path to the saved audio file
        """
        try:
            audio = self.synthesize_speech(text, voice, accept)
            output_path.write_bytes(audio)
            logger.info(f"Audio saved to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving synthesized speech: {e}")
            raise
    
    def get_available_voices(self) -> Dict[str, Any]:
        """
        Get list of available voices from Watson TTS.
        
        Returns:
            Dict containing available voices
        """
        try:
            voices = self.tts.list_voices().get_result()
            return voices
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            raise
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        Get list of available models from Watson STT.
        
        Returns:
            Dict containing available models
        """
        try:
            models = self.stt.list_models().get_result()
            return models
        except Exception as e:
            logger.error(f"Error getting available models: {e}")
            raise

# Made with Bob

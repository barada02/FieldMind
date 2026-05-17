# Voice Mode Integration Guide

## Overview

Field Mind now supports voice interaction through IBM Watson Speech-to-Text (STT) and Text-to-Speech (TTS) services. This enables hands-free operation for field technicians working in environments where typing is impractical.

## Architecture

### Components

1. **Voice Service** (`backend/voice/service.py`)
   - Manages Watson STT and TTS clients
   - Handles audio transcription and synthesis
   - Provides unified interface for voice operations

2. **Voice API** (`backend/app/api/voice.py`)
   - REST endpoints for voice operations
   - File upload handling for audio
   - Audio format conversion and validation

3. **Voice Utilities** (`backend/voice/utils.py`)
   - Audio format detection
   - File validation
   - Content type mapping

## Setup

### 1. Install Dependencies

```bash
pip install ibm-watson ibm-cloud-sdk-core
```

### 2. Configure Watson Services

Create IBM Watson Speech-to-Text and Text-to-Speech service instances:

1. Go to [IBM Cloud Console](https://cloud.ibm.com/)
2. Create Speech-to-Text service
3. Create Text-to-Speech service
4. Copy API keys and service URLs

### 3. Environment Configuration

Add to your `.env` file:

```env
# IBM Watson Speech-to-Text
STT_APIKEY=your_stt_api_key_here
STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/your-instance
STT_MODEL=en-US_BroadbandModel

# IBM Watson Text-to-Speech
TTS_APIKEY=your_tts_api_key_here
TTS_URL=https://api.us-south.text-to-speech.watson.cloud.ibm.com/instances/your-instance
TTS_VOICE=en-US_AllisonV3Voice

# Voice Mode Settings
VOICE_ENABLED=true
MAX_AUDIO_SIZE_MB=10
```

## API Endpoints

### 1. Transcribe Audio

**Endpoint:** `POST /api/voice/transcribe`

**Description:** Convert audio to text using Watson STT

**Request:**
```bash
curl -X POST "http://localhost:8000/api/voice/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "audio=@recording.wav" \
  -F "model=en-US_BroadbandModel" \
  -F "include_raw=false"
```

**Response:**
```json
{
  "text": "How do I calibrate the CNC machine?",
  "confidence": 0.95,
  "raw_result": null,
  "timestamp": "2026-05-17T15:00:00Z"
}
```

**Supported Formats:**
- WAV (audio/wav)
- FLAC (audio/flac)
- MP3 (audio/mp3)
- OGG (audio/ogg)
- OPUS (audio/opus)
- WEBM (audio/webm)

### 2. Synthesize Speech

**Endpoint:** `POST /api/voice/synthesize`

**Description:** Convert text to speech using Watson TTS

**Request:**
```bash
curl -X POST "http://localhost:8000/api/voice/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Here is the calibration procedure for the CNC machine",
    "voice": "en-US_AllisonV3Voice",
    "format": "wav"
  }' \
  --output response.wav
```

**Request Body:**
```json
{
  "text": "Your text here (max 5000 characters)",
  "voice": "en-US_AllisonV3Voice",
  "format": "wav"
}
```

**Available Formats:**
- `wav` - WAV format (default)
- `mp3` - MP3 format
- `ogg` - OGG format
- `flac` - FLAC format
- `opus` - OPUS format
- `webm` - WEBM format

### 3. Get Voice Information

**Endpoint:** `GET /api/voice/info`

**Description:** List available voices and models

**Response:**
```json
{
  "enabled": true,
  "available_voices": [
    {
      "name": "en-US_AllisonV3Voice",
      "language": "en-US",
      "gender": "female",
      "description": "Allison: American English female voice"
    },
    {
      "name": "en-US_MichaelV3Voice",
      "language": "en-US",
      "gender": "male",
      "description": "Michael: American English male voice"
    }
  ],
  "available_models": [
    {
      "name": "en-US_BroadbandModel",
      "language": "en-US",
      "description": "US English broadband model"
    }
  ]
}
```

### 4. Health Check

**Endpoint:** `GET /api/voice/health`

**Description:** Check voice service status

**Response:**
```json
{
  "status": "healthy",
  "voice_enabled": true,
  "stt_configured": true,
  "tts_configured": true,
  "timestamp": "2026-05-17T15:00:00Z"
}
```

## Usage Examples

### Python Client

```python
import requests
from pathlib import Path

# Transcribe audio
def transcribe_audio(audio_path: Path):
    with open(audio_path, 'rb') as f:
        files = {'audio': f}
        response = requests.post(
            'http://localhost:8000/api/voice/transcribe',
            files=files
        )
    return response.json()

# Synthesize speech
def synthesize_speech(text: str, output_path: Path):
    response = requests.post(
        'http://localhost:8000/api/voice/synthesize',
        json={
            'text': text,
            'voice': 'en-US_AllisonV3Voice',
            'format': 'wav'
        }
    )
    output_path.write_bytes(response.content)

# Example usage
result = transcribe_audio(Path('question.wav'))
print(f"Transcribed: {result['text']}")

synthesize_speech(
    "Here is the answer to your question",
    Path('answer.wav')
)
```

### JavaScript Client

```javascript
// Transcribe audio
async function transcribeAudio(audioFile) {
  const formData = new FormData();
  formData.append('audio', audioFile);
  
  const response = await fetch('/api/voice/transcribe', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Synthesize speech
async function synthesizeSpeech(text) {
  const response = await fetch('/api/voice/synthesize', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      text: text,
      voice: 'en-US_AllisonV3Voice',
      format: 'wav'
    })
  });
  
  return await response.blob();
}

// Example: Record and transcribe
async function recordAndTranscribe() {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const mediaRecorder = new MediaRecorder(stream);
  const chunks = [];
  
  mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.onstop = async () => {
    const blob = new Blob(chunks, { type: 'audio/wav' });
    const result = await transcribeAudio(blob);
    console.log('Transcribed:', result.text);
  };
  
  mediaRecorder.start();
  setTimeout(() => mediaRecorder.stop(), 5000); // Record for 5 seconds
}

// Example: Speak response
async function speakResponse(text) {
  const audioBlob = await synthesizeSpeech(text);
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  audio.play();
}
```

## Integration with Chat System

### Voice-Enabled Chat Flow

```python
from backend.voice.service import VoiceService
from backend.agent.orchestrator import get_agent

async def voice_chat(audio_file):
    # 1. Transcribe user's audio question
    voice_service = get_voice_service()
    result = voice_service.transcribe_audio(audio_file, "audio/wav")
    user_text = voice_service.extract_transcript_text(result)
    
    # 2. Process through agent system
    agent = get_agent()
    response_text = await agent.achat(
        message=user_text,
        thread_id="voice-session-123"
    )
    
    # 3. Convert response to speech
    audio_data = voice_service.synthesize_speech(
        text=response_text,
        accept="audio/wav"
    )
    
    return {
        "transcript": user_text,
        "response_text": response_text,
        "audio": audio_data
    }
```

## Available Watson Voices

### English (US)
- `en-US_AllisonV3Voice` - Female, expressive
- `en-US_MichaelV3Voice` - Male, expressive
- `en-US_LisaV3Voice` - Female, expressive
- `en-US_EmilyV3Voice` - Female, expressive

### English (UK)
- `en-GB_KateV3Voice` - Female, expressive
- `en-GB_CharlotteV3Voice` - Female, expressive

### Other Languages
- Spanish: `es-ES_EnriqueV3Voice`, `es-ES_LauraV3Voice`
- French: `fr-FR_NicolasV3Voice`, `fr-FR_ReneeV3Voice`
- German: `de-DE_BirgitV3Voice`, `de-DE_DieterV3Voice`
- Japanese: `ja-JP_EmiV3Voice`

## Available Watson STT Models

### English
- `en-US_BroadbandModel` - General purpose (16kHz+)
- `en-US_NarrowbandModel` - Telephony (8kHz)
- `en-US_Multimedia` - Multimedia content
- `en-US_Telephony` - Phone conversations

### Other Languages
- Spanish: `es-ES_BroadbandModel`
- French: `fr-FR_BroadbandModel`
- German: `de-DE_BroadbandModel`
- Japanese: `ja-JP_BroadbandModel`

## Best Practices

### Audio Quality
- Use 16kHz or higher sample rate for broadband models
- Use 8kHz for narrowband/telephony models
- Minimize background noise
- Use lossless formats (WAV, FLAC) when possible

### Performance Optimization
- Cache voice service instance
- Use appropriate audio format for use case
- Implement audio compression for network transfer
- Stream audio when possible for real-time feel

### Error Handling
```python
try:
    result = voice_service.transcribe_audio(audio_file, content_type)
except Exception as e:
    logger.error(f"Transcription failed: {e}")
    # Fallback to text input
    return {"error": "Voice recognition unavailable"}
```

### Security
- Validate audio file size (default: 10MB max)
- Validate audio format
- Sanitize transcribed text before processing
- Rate limit voice API calls
- Monitor Watson API usage and costs

## Troubleshooting

### Common Issues

1. **"Voice services not configured"**
   - Check STT_APIKEY and STT_URL in .env
   - Check TTS_APIKEY and TTS_URL in .env
   - Ensure VOICE_ENABLED=true

2. **"Audio file too large"**
   - Reduce audio quality/bitrate
   - Increase MAX_AUDIO_SIZE_MB in config
   - Split long recordings

3. **"Unsupported audio format"**
   - Convert to supported format (WAV, FLAC, MP3, OGG)
   - Check file extension matches content

4. **Low transcription confidence**
   - Improve audio quality
   - Reduce background noise
   - Use appropriate STT model
   - Speak clearly and at moderate pace

5. **Watson API errors**
   - Verify API credentials
   - Check service URLs
   - Ensure Watson services are active
   - Check API usage limits

## Cost Considerations

### Watson Pricing (as of 2026)
- **Speech-to-Text**: ~$0.02 per minute
- **Text-to-Speech**: ~$0.02 per 1000 characters

### Optimization Tips
- Cache common responses as audio files
- Use shorter, more concise responses
- Implement usage quotas per user
- Monitor and alert on high usage

## Testing

### Unit Tests
```python
import pytest
from backend.voice.service import VoiceService

def test_transcribe_audio():
    service = VoiceService(stt_apikey, stt_url, tts_apikey, tts_url)
    with open('test_audio.wav', 'rb') as f:
        result = service.transcribe_audio(f, 'audio/wav')
    assert 'results' in result

def test_synthesize_speech():
    service = VoiceService(stt_apikey, stt_url, tts_apikey, tts_url)
    audio = service.synthesize_speech("Hello world")
    assert len(audio) > 0
```

### Integration Tests
```bash
# Test transcription endpoint
curl -X POST http://localhost:8000/api/voice/transcribe \
  -F "audio=@test.wav"

# Test synthesis endpoint
curl -X POST http://localhost:8000/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Test message","format":"wav"}' \
  --output test_output.wav

# Test health endpoint
curl http://localhost:8000/api/voice/health
```

## Future Enhancements

- [ ] Real-time streaming transcription
- [ ] Voice activity detection
- [ ] Speaker diarization (multi-speaker support)
- [ ] Custom vocabulary for technical terms
- [ ] Noise cancellation preprocessing
- [ ] Voice biometrics for authentication
- [ ] Offline voice processing
- [ ] Multi-language auto-detection
- [ ] Voice command shortcuts
- [ ] Emotion detection in speech

## References

- [IBM Watson Speech-to-Text Documentation](https://cloud.ibm.com/docs/speech-to-text)
- [IBM Watson Text-to-Speech Documentation](https://cloud.ibm.com/docs/text-to-speech)
- [Watson Python SDK](https://github.com/watson-developer-cloud/python-sdk)
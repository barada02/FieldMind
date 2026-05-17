# FieldMind - AI-Powered Field Service Assistant

FieldMind is a multi-agent AI system designed to assist field technicians with SOPs, machine information, inventory management, and ticket creation. Now with **Voice Mode** support for hands-free operation!

## Features

### Core Capabilities
- 🔍 **SOP Search**: Semantic search across Standard Operating Procedures
- 🤖 **Multi-Agent System**: Specialized agents for different tasks
- 📊 **Machine Registry**: Query machine information and history
- 📦 **Inventory Management**: Check tool/part availability
- 🎫 **Ticket Creation**: Create purchase and maintenance tickets
- 🗣️ **Voice Mode**: Speech-to-Text and Text-to-Speech for hands-free operation

### Voice Mode Features (NEW!)
- 🎤 **Speech Input**: Convert spoken queries to text using IBM Watson STT
- 🔊 **Audio Output**: Convert responses to speech using IBM Watson TTS
- 🌐 **Multiple Languages**: Support for various languages and accents
- 🎭 **Voice Selection**: Choose from multiple voice options
- 📱 **Mobile-Friendly**: Works on mobile devices with microphone access

## Architecture

### Multi-Agent System
- **Supervisor Agent**: Routes queries to specialized agents
- **RAG Agent**: Searches and retrieves SOP documents
- **Database Agent**: Queries Cloudant for machines, inventory, tickets
- **Voice Service**: Handles audio transcription and synthesis

### Technology Stack
- **Backend**: FastAPI, LangGraph, ChromaDB
- **Voice**: IBM Watson Speech-to-Text & Text-to-Speech
- **Database**: IBM Cloudant (NoSQL)
- **LLM**: OpenAI-compatible API
- **Frontend**: HTML/CSS/JavaScript

## Quick Start

### Prerequisites
- Python 3.9+
- IBM Cloud account (for Cloudant and Watson services)
- OpenAI API key or compatible LLM provider

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd FieldMind
```

2. **Install dependencies**
```bash
pip install -r backend/requirements.txt
```

3. **Configure environment**
```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials
```

4. **Set up Watson Voice Services** (Optional)
   - Create IBM Watson Speech-to-Text service
   - Create IBM Watson Text-to-Speech service
   - Add credentials to `.env`:
```env
STT_APIKEY=your_stt_api_key
STT_URL=your_stt_service_url
TTS_APIKEY=your_tts_api_key
TTS_URL=your_tts_service_url
VOICE_ENABLED=true
```

5. **Ingest SOP documents**
```bash
python scripts/ingest_pdf.py
```

6. **Load Cloudant data**
```bash
python scripts/ingest_cloudant.py
```

7. **Run the application**
```bash
python scripts/run.py
```

8. **Access the application**
   - Web Interface: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Voice API: http://localhost:8000/api/voice/

## Voice Mode Usage

### API Endpoints

#### Transcribe Audio
```bash
curl -X POST "http://localhost:8000/api/voice/transcribe" \
  -F "audio=@recording.wav"
```

#### Synthesize Speech
```bash
curl -X POST "http://localhost:8000/api/voice/synthesize" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello, how can I help you?","format":"wav"}' \
  --output response.wav
```

#### Get Voice Info
```bash
curl "http://localhost:8000/api/voice/info"
```

### Supported Audio Formats
- **Input**: WAV, FLAC, MP3, OGG, OPUS, WEBM
- **Output**: WAV, MP3, OGG, FLAC, OPUS, WEBM

## Configuration

### Environment Variables

```env
# LLM Configuration
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4-turbo-preview

# Jina AI (Embeddings)
JINA_API_KEY=your_jina_api_key

# IBM Cloudant
CLOUDANT_URL=https://your-account.cloudant.com
CLOUDANT_USERNAME=your_username
CLOUDANT_PASSWORD=your_password

# IBM Watson Voice Services
STT_APIKEY=your_watson_stt_api_key
STT_URL=https://api.us-south.speech-to-text.watson.cloud.ibm.com
TTS_APIKEY=your_watson_tts_api_key
TTS_URL=https://api.us-south.text-to-speech.watson.cloud.ibm.com
VOICE_ENABLED=true

# Application
APP_HOST=0.0.0.0
APP_PORT=8000
```

## Project Structure

```
FieldMind/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── chat.py          # Chat endpoints
│   │   │   ├── voice.py         # Voice endpoints (NEW)
│   │   │   └── health.py        # Health checks
│   │   ├── config.py            # Configuration
│   │   └── main.py              # FastAPI app
│   ├── agent/
│   │   ├── orchestrator.py      # Multi-agent orchestrator
│   │   ├── rag_agent.py         # RAG specialist
│   │   └── state.py             # Agent state
│   ├── voice/                   # Voice services (NEW)
│   │   ├── service.py           # Watson STT/TTS
│   │   └── utils.py             # Voice utilities
│   ├── rag/
│   │   ├── embeddings.py        # Jina embeddings
│   │   └── vector_store.py      # ChromaDB
│   └── mcp_server/
│       ├── server.py            # MCP server
│       └── cloudant_client.py   # Cloudant client
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
├── data/
│   ├── sops/                    # SOP PDFs
│   └── cloudant/                # Cloudant JSON data
├── docs/
│   ├── VOICE_MODE_GUIDE.md      # Voice integration guide (NEW)
│   └── MULTI_AGENT_IMPLEMENTATION.md
├── Plandocs/
│   └── ARCHITECTURE.md          # System architecture
└── scripts/
    ├── ingest_pdf.py            # Ingest SOPs
    ├── ingest_cloudant.py       # Load Cloudant data
    └── run.py                   # Run application
```

## Usage Examples

### Text Chat
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"How do I calibrate the CNC machine?"}'
```

### Voice Chat (Full Workflow)
```python
import requests
from pathlib import Path

# 1. Record audio (user speaks question)
audio_file = Path("question.wav")

# 2. Transcribe to text
with open(audio_file, 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/voice/transcribe',
        files={'audio': f}
    )
transcript = response.json()['text']

# 3. Get answer from chat API
response = requests.post(
    'http://localhost:8000/api/chat',
    json={'message': transcript}
)
answer = response.json()['message']

# 4. Convert answer to speech
response = requests.post(
    'http://localhost:8000/api/voice/synthesize',
    json={'text': answer, 'format': 'wav'}
)
Path('answer.wav').write_bytes(response.content)

# 5. Play audio to user
```

## Documentation

- [Architecture Overview](Plandocs/ARCHITECTURE.md)
- [Multi-Agent Implementation](docs/MULTI_AGENT_IMPLEMENTATION.md)
- [Voice Mode Guide](docs/VOICE_MODE_GUIDE.md) ⭐ NEW
- [API Documentation](http://localhost:8000/docs) (when running)

## API Endpoints

### Chat
- `POST /api/chat` - Send chat message
- `GET /api/chat/history/{conversation_id}` - Get conversation history

### Voice (NEW)
- `POST /api/voice/transcribe` - Convert audio to text
- `POST /api/voice/synthesize` - Convert text to audio
- `GET /api/voice/info` - Get available voices and models
- `GET /api/voice/health` - Check voice service status

### Health
- `GET /api/health` - Application health check

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black backend/
flake8 backend/
```

### Adding New SOPs
1. Place PDF files in `data/sops/`
2. Run ingestion script:
```bash
python scripts/ingest_pdf.py
```

### Adding Voice Languages
Update configuration in `.env`:
```env
STT_MODEL=es-ES_BroadbandModel  # Spanish
TTS_VOICE=es-ES_LauraV3Voice    # Spanish female voice
```

## Troubleshooting

### Voice Services Not Working
1. Check Watson credentials in `.env`
2. Verify `VOICE_ENABLED=true`
3. Test health endpoint: `curl http://localhost:8000/api/voice/health`
4. Check Watson service status in IBM Cloud console

### Low Transcription Accuracy
- Use higher quality audio (16kHz+)
- Reduce background noise
- Speak clearly and at moderate pace
- Try different STT models

### Audio Format Issues
- Convert to WAV format: `ffmpeg -i input.mp3 output.wav`
- Ensure proper sample rate (8kHz for narrowband, 16kHz+ for broadband)

## Performance

- Simple queries: < 2 seconds
- RAG queries: < 5 seconds
- Voice transcription: < 3 seconds
- Voice synthesis: < 2 seconds
- Complex multi-agent queries: < 10 seconds

## Security

- API keys stored in environment variables
- Input validation on all endpoints
- File size limits for audio uploads (10MB default)
- Rate limiting on API calls
- Secure HTTPS connections to Watson services

## Cost Considerations

### Watson Pricing (Approximate)
- Speech-to-Text: ~$0.02 per minute
- Text-to-Speech: ~$0.02 per 1000 characters

### Optimization Tips
- Cache common audio responses
- Use shorter, concise responses
- Implement usage quotas
- Monitor API usage in IBM Cloud

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
- Documentation: [docs/](docs/)
- Voice Mode Guide: [docs/VOICE_MODE_GUIDE.md](docs/VOICE_MODE_GUIDE.md)

## Acknowledgments

- IBM Watson for Speech services
- LangChain/LangGraph for agent orchestration
- ChromaDB for vector storage
- FastAPI for the web framework

---

**Made with ❤️ for field technicians everywhere**
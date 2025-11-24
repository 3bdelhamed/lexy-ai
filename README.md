# Lexy-AI v2

**Serverless-First Dyslexia Accessibility Platform**

A modern REST API built for Vercel that makes digital content accessible for people with dyslexia through evidence-based text simplification and text-to-speech with synchronized highlighting.

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

### 🔤 Evidence-Based Text Simplification
- **5 Specialized Modes**: General, Academic, Technical, Narrative, Interactive
- **British Dyslexia Association Guidelines**: Research-backed simplification rules
- **Customizable Intensity**: Light, Medium, Heavy, or Custom
- **Advanced Options**: Control sentence length, vocabulary, formatting

### 🎙️ Text-to-Speech with Timestamps
- **In-Memory Audio Generation**: No file storage, fully serverless
- **Base64-Encoded Output**: Direct JSON response with WAV audio
- **Word-Level Timestamps**: Precise synchronization for highlighting
- **5 Premium Voices**: Puck, Chorus, Cora, Dan, Wave

### 🚀 Serverless Architecture
- **Vercel-Optimized**: 10-second timeout compliance
- **Minimal Dependencies**: Single AI provider (Google GenAI)
- **No Persistent Storage**: Stateless, scalable design
- **Fast Cold Starts**: Lazy-loaded services

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Deployment](#deployment)
- [Development](#development)
- [Testing](#testing)
- [Architecture](#architecture)
- [License](#license)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API Key ([Get one here](https://ai.google.dev/))

### Local Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lexy-ai.git
   cd lexy-ai
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Run the application**
   ```bash
   python src/main.py
   ```

6. **Access the API**
   - API: http://localhost:8000
   - Swagger Docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## 📚 API Documentation

### Base URL
```
https://your-app.vercel.app
```

### Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/simplify/text` | POST | Simplify text input |
| `/simplify/file` | POST | Simplify uploaded file |
| `/simplify/modes` | GET | Get available modes |
| `/tts/generate` | POST | Generate TTS audio |
| `/tts/simplify` | POST | Simplify + TTS combined |
| `/tts/voices` | GET | List available voices |

### Example: Simplify Text

**Request:**
```bash
curl -X POST "http://localhost:8000/simplify/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The quick brown fox jumps over the lazy dog.",
    "mode": "general",
    "intensity": "medium"
  }'
```

**Response:**
```json
{
  "original_text": "The quick brown fox jumps over the lazy dog.",
  "simplified_text": "The fast brown fox jumps over the lazy dog.",
  "processing_time_ms": 1234.56,
  "timestamp": "2025-11-23T15:30:00Z",
  "mode_used": "general",
  "intensity_used": "medium",
  "statistics": {
    "original_word_count": 9,
    "simplified_word_count": 9,
    "original_avg_sentence_length": 9.0,
    "simplified_avg_sentence_length": 9.0
  }
}
```

### Example: Generate TTS with Timestamps

**Request:**
```bash
curl -X POST "http://localhost:8000/tts/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, world!",
    "voice": "Puck",
    "sample_rate": 24000
  }'
```

**Response:**
```json
{
  "audio_base64": "UklGRiQAAABXQVZF...",
  "audio_format": "wav",
  "audio_duration": 1.234,
  "timestamps": [
    {"word": "Hello,", "start": 0.0, "end": 0.5},
    {"word": "world!", "start": 0.58, "end": 1.234}
  ],
  "processing_time_ms": 2345.67
}
```

### Simplification Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| **General** | Everyday content | News, emails, web pages |
| **Academic** | Educational materials | Textbooks, research papers |
| **Technical** | Documentation | Manuals, how-to guides |
| **Narrative** | Stories and fiction | Creative writing |
| **Interactive** | Multiple options | User chooses simplification level |

### Available Voices

- **Puck**: Neutral, clear (default)
- **Chorus**: Warm, friendly
- **Cora**: Professional, calm
- **Dan**: Authoritative, deep
- **Wave**: Energetic, dynamic

---

## 🌐 Deployment

### Deploy to Vercel

1. **Install Vercel CLI**
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Set environment variables**
   ```bash
   vercel env add GEMINI_API_KEY production
   vercel env add GEMINI_API_KEY preview
   vercel env add GEMINI_API_KEY development
   ```

4. **Deploy**
   ```bash
   vercel --prod
   ```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | ✅ Yes | - | Google Gemini API key |
| `MAX_FILE_SIZE_MB` | ❌ No | 10 | Max file upload size |
| `CORS_ORIGINS` | ❌ No | localhost | Allowed CORS origins |
| `LOG_LEVEL` | ❌ No | INFO | Logging level |

---

## 💻 Development

### Project Structure

```
lexy-ai/
├── src/
│   ├── main.py                    # FastAPI app entry point
│   ├── api/
│   │   ├── dependencies.py        # Dependency injection
│   │   ├── routes/
│   │   │   ├── simplify.py        # Simplification endpoints
│   │   │   └── tts.py             # TTS endpoints
│   │   └── schemas/
│   │       ├── common.py          # Shared schemas
│   │       ├── requests.py        # Request models
│   │       └── responses.py       # Response models
│   ├── core/
│   │   ├── config.py              # Settings
│   │   ├── exceptions.py          # Custom exceptions
│   │   └── middleware.py          # Middleware
│   ├── services/
│   │   ├── simplification/
│   │   │   ├── service.py         # Simplification service
│   │   │   └── prompts.py         # LLM prompts
│   │   └── tts/
│   │       ├── service.py         # TTS service
│   │       └── timestamp.py       # Timestamp algorithm
│   └── utils/
│       ├── file_parser.py         # File text extraction
│       └── validators.py          # Input validators
├── tests/
│   ├── unit/                      # Unit tests
│   └── integration/               # Integration tests
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── vercel.json                    # Vercel configuration
└── README.md
```

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Code Quality

```bash
# Format code
black src tests

# Lint code
ruff check src tests
```

---

## 🧪 Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Tests

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Specific test file
pytest tests/unit/test_simplification.py
```

### Test Coverage Goals

- **Minimum**: 75% overall coverage
- **Critical paths**: 100% coverage (services, validators)

---

## 🏗️ Architecture

### Serverless Design Principles

1. **No Persistent Storage**: All processing in-memory
2. **Lazy Loading**: Services initialized only when needed
3. **Timeout Management**: 8-second LLM timeout (2s buffer for Vercel)
4. **Memory Optimization**: Monitor usage, stay under 1024 MB
5. **Base64 Audio**: No file storage, direct JSON response

### Timestamp Algorithm

The word-level timestamp algorithm uses a heuristic approach:

1. **Tokenization**: Split text into words with punctuation
2. **Character Counting**: Count alphanumeric characters per word
3. **Pause Calculation**: Add pauses for punctuation (e.g., 0.20s for periods)
4. **Time Distribution**: Distribute speaking time proportionally by character count
5. **Monotonicity**: Ensure no timestamp overlaps

**Accuracy**: ±50-150ms per word

### Exception Handling

Custom exceptions with detailed error responses:

- `ValidationException`: Input validation errors (400)
- `FileSizeException`: File size limit exceeded (413)
- `UnsupportedFileException`: Unsupported file type (415)
- `LLMTimeoutException`: Request timeout (504)
- `TTSGenerationException`: TTS generation failed (500)

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **British Dyslexia Association**: For evidence-based guidelines
- **Google Gemini**: For AI capabilities
- **FastAPI**: For the excellent web framework
- **Vercel**: For serverless hosting

---

## 📞 Support

For issues, questions, or contributions:

- **Issues**: [GitHub Issues](https://github.com/yourusername/lexy-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/lexy-ai/discussions)
- **Email**: support@lexy-ai.com

---

**Made with ❤️ for accessibility**

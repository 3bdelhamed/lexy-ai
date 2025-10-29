# DyslexiaReader API

A FastAPI-based service that simplifies text for dyslexic readers using LangChain and Google's Gemini AI model.

## Features

- Text simplification with customizable options
- Multiple simplification modes and intensities
- Support for various document formats
- RESTful API with comprehensive documentation
- CORS support for cross-origin requests
- Health monitoring endpoints

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **LangChain**: Framework for developing LLM applications
- **Google Gemini**: Advanced language model for text processing
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: Lightning-fast ASGI server

## Prerequisites

- Python 3.8+
- Google Gemini API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd lexy-ai
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Required environment variables
GEMINI_API_KEY=your_api_key_here
```

## Running the Application

Start the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

- `GET /`: Root endpoint with API information
- `GET /health`: Health check endpoint
- `POST /api/v1/simplify`: Text simplification endpoint

### Simplification Options

The API supports various customization options:

- **Mode**: Different simplification approaches
- **Intensity**: Light, medium, or heavy simplification
- **Custom Controls**:
  - Sentence structure
  - Formatting
  - Vocabulary adjustments

## Testing

Run the test suite:
```bash
pytest
```

## Project Structure

```
app/
├── api/
│   └── v1/
│       └── endpoints/
│           └── simplify.py    # Simplification endpoints
├── config/
│   └── settings.py           # Application configuration
├── models/
│   └── schemas.py            # Data models and schemas
├── services/
│   ├── prompts.py           # LLM prompt templates
│   └── simplification_service.py  # Text simplification logic
└── utils/
    └── file_parser.py       # File handling utilities
```

## Contributing

Please read our contributing guidelines before submitting pull requests.

## License

[Add your license information here]

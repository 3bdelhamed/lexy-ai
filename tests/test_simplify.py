import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.config.settings import Settings
from app.models.schemas import SimplificationOptions, SimplificationMode, SimplificationIntensity

client = TestClient(app)


# Mock settings for testing
@pytest.fixture
def mock_settings():
    return Settings(
        app_name="Test DyslexiaReader API",
        version="1.0.0",
        debug=True,
        gemini_api_key="test_api_key",
        max_file_size_mb=5,
        allowed_file_types=["txt", "pdf", "docx"],
        cors_origins=["*"]
    )


# Test text simplification endpoint with default options
@pytest.mark.asyncio
@patch('app.services.simplification_service.SimplificationService.simplify_text')
def test_simplify_text_default(mock_simplify):
    # Setup mock
    mock_simplify.return_value = ("Simplified text.", 100, SimplificationOptions())
    
    # Make request
    response = client.post(
        "/api/v1/simplify/text",
        json={"text": "This is a complex text that needs simplification."}
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "original_text" in data
    assert "simplified_text" in data
    assert "processing_time_ms" in data
    assert "options_used" in data
    assert data["original_text"] == "This is a complex text that needs simplification."
    assert data["simplified_text"] == "Simplified text."
    assert data["processing_time_ms"] == 100


# Test text simplification endpoint with custom options
@pytest.mark.asyncio
@patch('app.services.simplification_service.SimplificationService.simplify_text')
def test_simplify_text_custom_options(mock_simplify):
    # Setup mock
    options = SimplificationOptions(
        mode=SimplificationMode.academic,
        intensity=SimplificationIntensity.heavy,
        custom_max_sentence_length=8
    )
    mock_simplify.return_value = ("Simplified academic text.", 150, options)
    
    # Make request
    response = client.post(
        "/api/v1/simplify/text",
        json={
            "text": "This is a complex academic text that needs simplification.",
            "options": {
                "mode": "academic",
                "intensity": "heavy",
                "custom_max_sentence_length": 8
            }
        }
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["original_text"] == "This is a complex academic text that needs simplification."
    assert data["simplified_text"] == "Simplified academic text."
    assert data["processing_time_ms"] == 150
    assert data["options_used"]["mode"] == "academic"
    assert data["options_used"]["intensity"] == "heavy"
    assert data["options_used"]["custom_max_sentence_length"] == 8


# Test file upload endpoint with form data
@pytest.mark.asyncio
@patch('app.services.simplification_service.SimplificationService.simplify_text')
@patch('app.utils.file_parser.FileParser.extract_text_from_file')
def test_simplify_file_with_options(mock_extract, mock_simplify):
    # Setup mocks
    mock_extract.return_value = ("txt", "This is a complex text that needs simplification.")
    options = SimplificationOptions(
        mode=SimplificationMode.technical,
        intensity=SimplificationIntensity.medium
    )
    mock_simplify.return_value = ("Simplified technical text.", 120, options)
    
    # Make request
    response = client.post(
        "/api/v1/simplify/file",
        files={"file": ("test.txt", "This is a complex text that needs simplification.", "text/plain")},
        data={
            "mode": "technical",
            "intensity": "medium",
            "paragraph_length": 2,
            "use_bullets": True
        }
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "original_text" in data
    assert "simplified_text" in data
    assert "processing_time_ms" in data
    assert "options_used" in data
    assert data["original_text"] == "This is a complex text that needs simplification."
    assert data["simplified_text"] == "Simplified technical text."
    assert data["options_used"]["mode"] == "technical"
    assert data["options_used"]["intensity"] == "medium"


# Test get simplification options endpoint
def test_get_simplification_options():
    response = client.get("/api/v1/simplify/options")
    
    assert response.status_code == 200
    data = response.json()
    assert "modes" in data
    assert "intensities" in data
    assert "sentence_structure" in data
    assert "vocabulary" in data
    assert "formatting" in data
    
    # Check specific modes
    assert "general" in data["modes"]
    assert "academic" in data["modes"]
    assert "technical" in data["modes"]
    assert "narrative" in data["modes"]
    assert "interactive" in data["modes"]
    
    # Check specific intensities
    assert "light" in data["intensities"]
    assert "medium" in data["intensities"]
    assert "heavy" in data["intensities"]
    assert "custom" in data["intensities"]


# Test error handling for empty text
def test_simplify_empty_text():
    response = client.post(
        "/api/v1/simplify/text",
        json={"text": ""}
    )
    
    assert response.status_code == 422  # Validation error


# Test error handling for unsupported file type
def test_simplify_unsupported_file():
    response = client.post(
        "/api/v1/simplify/file",
        files={"file": ("test.jpg", b"fake image data", "image/jpeg")}
    )
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


# Test root endpoint
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "DyslexiaReader API"


# Test health check endpoint
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
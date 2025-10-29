import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.config.settings import Settings

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


# Test text simplification endpoint
@pytest.mark.asyncio
@patch('app.services.simplification_service.SimplificationService.simplify_text')
def test_simplify_text(mock_simplify):
    # Setup mock
    mock_simplify.return_value = ("Simplified text.", 100)
    
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
    assert data["original_text"] == "This is a complex text that needs simplification."
    assert data["simplified_text"] == "Simplified text."
    assert data["processing_time_ms"] == 100


# Test file upload endpoint
@pytest.mark.asyncio
@patch('app.services.simplification_service.SimplificationService.simplify_text')
@patch('app.utils.file_parser.FileParser.extract_text_from_file')
def test_simplify_file(mock_extract, mock_simplify):
    # Setup mocks
    mock_extract.return_value = ("txt", "This is a complex text that needs simplification.")
    mock_simplify.return_value = ("Simplified text.", 100)
    
    # Make request
    response = client.post(
        "/api/v1/simplify/file",
        files={"file": ("test.txt", "This is a complex text that needs simplification.", "text/plain")}
    )
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "original_text" in data
    assert "simplified_text" in data
    assert "processing_time_ms" in data
    assert data["original_text"] == "This is a complex text that needs simplification."
    assert data["simplified_text"] == "Simplified text."
    assert data["processing_time_ms"] == 100


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
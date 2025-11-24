"""Integration tests for API endpoints"""
import pytest
from httpx import AsyncClient
from src.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Lexy-AI v2"
    assert "endpoints" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_simplify_text_endpoint(sample_text):
    """Test text simplification endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/simplify/text",
            json={
                "text": sample_text,
                "mode": "general",
                "intensity": "medium"
            }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "simplified_text" in data
    assert "statistics" in data
    assert data["mode_used"] == "general"


@pytest.mark.asyncio
async def test_simplify_text_validation():
    """Test text validation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Empty text
        response = await client.post(
            "/simplify/text",
            json={
                "text": "",
                "mode": "general",
                "intensity": "medium"
            }
        )
        assert response.status_code == 400
        
        # Text too long
        response = await client.post(
            "/simplify/text",
            json={
                "text": "a" * 10001,
                "mode": "general",
                "intensity": "medium"
            }
        )
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_modes_endpoint():
    """Test get modes endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/simplify/modes")
    
    assert response.status_code == 200
    data = response.json()
    assert "modes" in data
    assert "intensities" in data
    assert "general" in data["modes"]


@pytest.mark.asyncio
async def test_get_voices_endpoint():
    """Test get voices endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/tts/voices")
    
    assert response.status_code == 200
    data = response.json()
    assert "voices" in data
    assert "default_voice" in data
    assert "Puck" in data["voices"]


@pytest.mark.asyncio
async def test_cors_headers():
    """Test CORS headers"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options(
            "/simplify/text",
            headers={"Origin": "http://localhost:3000"}
        )
    
    assert "access-control-allow-origin" in response.headers

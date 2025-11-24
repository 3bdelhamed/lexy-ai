"""Test configuration and fixtures"""
import pytest
from fastapi.testclient import TestClient
from src.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_text():
    """Sample text for testing"""
    return "The quick brown fox jumps over the lazy dog. This is a test sentence."


@pytest.fixture
def long_text():
    """Long text for testing"""
    return """
    Artificial intelligence has revolutionized numerous industries and transformed 
    the way we interact with technology. Machine learning algorithms can now 
    process vast amounts of data and identify patterns that would be impossible 
    for humans to detect manually. Deep learning, a subset of machine learning, 
    has enabled breakthroughs in computer vision, natural language processing, 
    and speech recognition.
    """

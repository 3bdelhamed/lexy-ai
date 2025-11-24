"""Unit tests for SimplificationService"""
import pytest
from src.services.simplification import SimplificationService
from src.api.schemas import SimplificationMode, SimplificationIntensity
from src.core.exceptions import ValidationException


@pytest.mark.asyncio
async def test_simplify_general_mode(sample_text):
    """Test simplification in general mode"""
    service = SimplificationService()
    
    simplified, stats, time_ms = await service.simplify_text(
        text=sample_text,
        mode=SimplificationMode.GENERAL,
        intensity=SimplificationIntensity.MEDIUM
    )
    
    assert simplified
    assert len(simplified) > 0
    assert time_ms > 0
    assert stats.original_word_count > 0
    assert stats.simplified_word_count > 0


@pytest.mark.asyncio
async def test_simplify_academic_mode(long_text):
    """Test simplification in academic mode"""
    service = SimplificationService()
    
    simplified, stats, time_ms = await service.simplify_text(
        text=long_text,
        mode=SimplificationMode.ACADEMIC,
        intensity=SimplificationIntensity.MEDIUM
    )
    
    assert simplified
    assert stats.original_word_count > stats.simplified_word_count or \
           stats.original_avg_sentence_length > stats.simplified_avg_sentence_length


@pytest.mark.asyncio
async def test_calculate_max_sentence_length():
    """Test sentence length calculation"""
    service = SimplificationService()
    
    # Test general mode with medium intensity
    length = service._calculate_max_sentence_length(
        SimplificationMode.GENERAL,
        SimplificationIntensity.MEDIUM
    )
    assert length == 15
    
    # Test custom intensity
    length = service._calculate_max_sentence_length(
        SimplificationMode.GENERAL,
        SimplificationIntensity.CUSTOM,
        custom_length=20
    )
    assert length == 20


def test_calculate_statistics(sample_text):
    """Test statistics calculation"""
    service = SimplificationService()
    
    simplified = "The fox jumps. This is a test."
    stats = service._calculate_statistics(sample_text, simplified)
    
    assert stats.original_word_count > 0
    assert stats.simplified_word_count > 0
    assert stats.original_avg_sentence_length > 0
    assert stats.simplified_avg_sentence_length > 0

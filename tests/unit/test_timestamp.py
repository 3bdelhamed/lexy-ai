"""Unit tests for timestamp calculation"""
import pytest
from src.services.tts.timestamp import (
    tokenize_text,
    count_alphanumeric_chars,
    calculate_total_pause_time,
    calculate_timestamps
)


def test_tokenize_text():
    """Test text tokenization"""
    text = "Hello, world! How are you?"
    tokens = tokenize_text(text)
    
    assert len(tokens) == 5
    assert tokens[0] == ("Hello,", ",")
    assert tokens[1] == ("world!", "!")
    assert tokens[2] == ("How", "")


def test_count_alphanumeric_chars():
    """Test character counting"""
    assert count_alphanumeric_chars("Hello,") == 5
    assert count_alphanumeric_chars("world!") == 5
    assert count_alphanumeric_chars("...") == 0


def test_calculate_total_pause_time():
    """Test pause time calculation"""
    tokens = [("Hello,", ","), ("world!", "!"), ("How", "")]
    pause_time = calculate_total_pause_time(tokens)
    
    # Should be 0.08 (comma) + 0.20 (exclamation) = 0.28
    assert pause_time == pytest.approx(0.28, abs=0.01)


def test_calculate_timestamps():
    """Test timestamp calculation"""
    text = "Hello, world!"
    duration = 1.5
    
    timestamps = calculate_timestamps(text, duration)
    
    assert len(timestamps) == 2
    assert timestamps[0].word == "Hello,"
    assert timestamps[1].word == "world!"
    assert timestamps[0].start == 0.0
    assert timestamps[-1].end == duration
    
    # Ensure monotonicity
    for i in range(len(timestamps) - 1):
        assert timestamps[i].end <= timestamps[i + 1].start


def test_calculate_timestamps_empty():
    """Test timestamp calculation with empty text"""
    timestamps = calculate_timestamps("", 1.0)
    assert len(timestamps) == 0

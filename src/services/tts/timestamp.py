"""Word-level timestamp calculation algorithm"""
import re
from typing import List, Tuple
from api.schemas.common import WordTimestamp


# Pause durations for different punctuation marks (in seconds)
PAUSE_MAP = {
    ',': 0.08,   # Short pause
    ';': 0.10,   # Medium pause
    ':': 0.10,   # Medium pause
    '.': 0.20,   # Long pause (sentence end)
    '!': 0.20,   # Long pause (exclamation)
    '?': 0.20,   # Long pause (question)
    '...': 0.25, # Extra long pause
    '-': 0.02,   # Minimal pause
    '—': 0.02,   # Em dash
}


def tokenize_text(text: str) -> List[Tuple[str, str]]:
    """
    Tokenize text into words with their trailing punctuation.
    
    Args:
        text: Input text
    
    Returns:
        List of (word, punctuation) tuples
    """
    # Split on whitespace but keep punctuation
    tokens = text.split()
    result = []
    
    for token in tokens:
        # Extract trailing punctuation
        match = re.match(r'^(.*?)([.,;:!?—-]*)$', token)
        if match:
            word = match.group(1)
            punct = match.group(2)
            if word:  # Only add if there's actual text
                result.append((word + punct, punct))
    
    return result


def count_alphanumeric_chars(word: str) -> int:
    """Count only alphanumeric characters in a word"""
    return sum(1 for c in word if c.isalnum())


def calculate_total_pause_time(tokens: List[Tuple[str, str]]) -> float:
    """Calculate total pause time from punctuation"""
    total_pause = 0.0
    
    for _, punct in tokens:
        if not punct:
            continue
        
        # Check for ellipsis first
        if '...' in punct:
            total_pause += PAUSE_MAP['...']
        else:
            # Add pauses for each punctuation mark
            for char in punct:
                if char in PAUSE_MAP:
                    total_pause += PAUSE_MAP[char]
    
    return total_pause


def calculate_timestamps(text: str, audio_duration: float) -> List[WordTimestamp]:
    """
    Calculate word-level timestamps using heuristic algorithm.
    
    Algorithm:
    1. Tokenize text into words with punctuation
    2. Count alphanumeric characters per word
    3. Calculate total pause time from punctuation
    4. Distribute remaining time proportionally by character count
    5. Assign start/end times with pauses
    
    Args:
        text: Original text
        audio_duration: Total audio duration in seconds
    
    Returns:
        List of WordTimestamp objects
    """
    # Tokenize text
    tokens = tokenize_text(text)
    
    if not tokens:
        return []
    
    # Calculate total characters (excluding punctuation)
    total_chars = sum(count_alphanumeric_chars(word) for word, _ in tokens)
    
    if total_chars == 0:
        return []
    
    # Calculate total pause time
    total_pause_time = calculate_total_pause_time(tokens)
    
    # Calculate speaking time (total - pauses)
    speaking_time = max(0, audio_duration - total_pause_time)
    
    # Time per character
    time_per_char = speaking_time / total_chars if total_chars > 0 else 0
    
    # Generate timestamps
    timestamps = []
    current_time = 0.0
    
    for word, punct in tokens:
        # Start time
        start_time = current_time
        
        # Calculate speech duration for this word
        char_count = count_alphanumeric_chars(word)
        speech_duration = char_count * time_per_char
        
        # End time (before pause)
        end_time = start_time + speech_duration
        
        # Add timestamp
        timestamps.append(WordTimestamp(
            word=word,
            start=round(start_time, 3),
            end=round(end_time, 3)
        ))
        
        # Move current time forward (speech + pause)
        current_time = end_time
        
        # Add pause for punctuation
        if punct:
            if '...' in punct:
                current_time += PAUSE_MAP['...']
            else:
                for char in punct:
                    if char in PAUSE_MAP:
                        current_time += PAUSE_MAP[char]
    
    # Ensure last timestamp ends at audio duration
    if timestamps:
        timestamps[-1].end = round(audio_duration, 3)
    
    # Ensure monotonicity (no overlaps)
    for i in range(len(timestamps) - 1):
        if timestamps[i].end > timestamps[i + 1].start:
            timestamps[i].end = timestamps[i + 1].start
    
    return timestamps

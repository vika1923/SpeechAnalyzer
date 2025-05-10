from typing import Dict, Tuple
import re
def timestamp_punctuation_to_index( timestamped_transcript: Dict[Tuple[float, float], str], 
        punctuated_text: str
) -> Dict[Tuple[float, float], Tuple[int, int]]:
    """
    Match each word from a timestamped transcript to its character indices in a punctuated text.

    Args:
        timestamped_transcript (dict): Maps (start_time, end_time) to a word (str).
        punctuated_text (str): The full text with punctuation.

    Returns:
        dict: Maps each (start_time, end_time) to a (start_idx, end_idx) character range 
              in the punctuated text (end_idx is inclusive).

    Raises:
        ValueError: If the number of words doesn't match or words can't be aligned.
    """
    word_spans = [match.span() for match in re.finditer(r'\b\w+\b', punctuated_text)]
    timestamped_items = list(timestamped_transcript.items())
    result = {}
    if len(word_spans) != len(timestamped_items):
        raise ValueError(f"Word count mismatch: {len(word_spans)} spans vs {len(timestamped_items)} timestamps")
    for (timestamp, word), (start, end) in zip(timestamped_items, word_spans):
        if punctuated_text[start:end].lower().strip() != word.lower().strip():
            raise ValueError(f"Mismatch between '{word}' and '{punctuated_text[start:end]}'")
        result[timestamp] = (start, end-1)

    return result

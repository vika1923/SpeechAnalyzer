import numpy as np
from typing import Tuple, Dict, List

def get_rate_of_speech(words: Dict[Tuple[float, float], str], interval: float = 10.) -> List[Tuple[float, float]]:
    result = []
    wordcount = 0
    multiplier = 1
    start = -float("inf")
    for start_, end in words:
        if start_ == -float('inf'):
            start = start_
        wordcount += 1
        if end - (start + multiplier * interval) < 0:
            result.append((multiplier * interval, wordcount / interval))
            multiplier += 1
            wordcount = 0
    if wordcount > 0:
        result.append((start+ multiplier * interval,  wordcount / interval))
    return result

def count_words(words: Dict[Tuple[np.float64, np.float64], str]) -> int:
    return len(words)

import numpy as np
from typing import Tuple, Dict

def rate_of_speech(words: Dict[Tuple[float, float], str], interval: float = 10.) -> Dict[Tuple[float, float], float]:
    result = {}
    wordcount = 0
    multiplier = 1
    start = -float("inf")
    for start_, end in words:
        if start_ == -float('inf'):
            start = start_
        wordcount += 1
        if end - (start + multiplier * interval) < 0:
            result[multiplier * interval] = wordcount / interval 
            multiplier += 1
            wordcount = 0
    return result

def count_words(words: Dict[Tuple[np.float64, np.float64], str]) -> int:
    return len(words)

import numpy as np
from typing import Tuple, Dict, List

def rate_of_speech(words: Dict[Tuple[float, float], str], interval: float = 10.) -> List[Tuple[float, float]]:
    result = []
    wordcount = 0
    current_time = 0
    
    # Sort words by their start time
    sorted_words = sorted(words.items(), key=lambda x: x[0][0])
    
    for (start, end), _ in sorted_words:
        wordcount += 1
        if end > current_time + interval:
            # Calculate words per minute for this interval
            words_per_minute = (wordcount / interval) * 60
            result.append((current_time, words_per_minute))
            current_time += interval
            wordcount = 0
    
    # Add the last interval if there are remaining words
    if wordcount > 0:
        words_per_minute = (wordcount / interval) * 60
        result.append((current_time, words_per_minute))
    
    return result

def count_words(words: Dict[Tuple[np.float64, np.float64], str]) -> int:
    return len(words)

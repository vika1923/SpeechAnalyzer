import numpy as np
from typing import Tuple, Dict, List

def get_rate_of_speech(words: Dict[Tuple[float, float], str], interval: float = 10.) -> List[Tuple[float, float]]:
    result = []
    wordcount = 0
    current_time = 0
    
    # Sort words by their start time
    sorted_words = sorted(words.items(), key=lambda x: x[0][0])
    
    
    # Get total duration
    total_duration = max(end for (_, end), _ in sorted_words)
    
    # Create intervals
    for (start, end), _ in sorted_words:
        wordcount += 1
        if end > current_time + interval:
            # Calculate words per minute for this interval
            words_per_second = (wordcount / interval) 
            result.append((current_time, words_per_second))
            current_time += interval
            wordcount = 0
    if wordcount > 0:
        words_per_second = (wordcount / interval)
        result.append((current_time, words_per_second))
    return result

def count_words(words: Dict[Tuple[np.float64, np.float64], str]) -> int:
    return len(words)

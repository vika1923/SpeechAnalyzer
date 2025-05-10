from typing import Tuple, Dict, List
from custom_types import TimeStamp

def get_rate_of_speech(words: Dict[TimeStamp, str], interval: float = 10.) -> List[Tuple[float, float]]:
    result = []
    wordcount = 0
    current_time = 0

    sorted_words = sorted(words.items(), key=lambda x: x[0][0])

    for (_, end), _ in sorted_words:
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

def count_words(words: Dict[Tuple[float, float], str]) -> int:
    return len(words)

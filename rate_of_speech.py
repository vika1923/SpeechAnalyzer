import numpy as np
from typing import Tuple, Dict
def rate_of_speech(sentences: Dict[Tuple[np.float64, np.float64], str]) -> Dict[Tuple[np.float64, np.float64], np.float64]:
    result = {}
    for (start, end), sentence in sentences.items():
        result[start] = len(" ".split(sentence))/ (end - start) 
    return result

def count_words(words: Dict[Tuple[np.float64, np.float64], str]) -> int:
    return len(words)

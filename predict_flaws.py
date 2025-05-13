import numpy as np
from typing import List, Dict
from custom_types import TimeStamp, WordBoundary

def floss(indices: Dict[TimeStamp, WordBoundary], threshhold: float = 1.0) -> List[WordBoundary]:
    x, y = zip(*indices.keys())
    diff = np.array(x) - np.array(y)
    avg = np.average(diff)
    mask = abs(diff - avg) > threshhold
    filtered_values = [index_pair for index_pair, m in zip(indices.values(), mask) if m]
    return filtered_values



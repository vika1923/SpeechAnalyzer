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

# from typing import Tuple, Dict
# from custom_types import TimeStamp
#
# def floss(timestamped_transcipt: Dict[TimeStamp, str], threshhold: float = 1.0) -> Dict[TimeStamp, str]:
#     x, y = zip(*timestamped_transcipt.keys())
#     diff = np.array(x) - np.array(y)
#     avg = np.average(diff)
#     mask = abs(diff - avg) > threshhold
#     filtered_timestamped_transcipt = {
#         timestamp: word
#         for (timestamp, word), mask_value in zip(timestamped_transcipt.items(), mask) 
#         if mask_value
#     }
#     return filtered_timestamped_transcipt

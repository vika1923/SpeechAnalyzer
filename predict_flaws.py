import numpy as np
from typing import Tuple, Dict
#
# timestamped_transcipt = {
#         (np.float64(0.84), np.float64(1.44)): 'Guangdia', 
#         (np.float64(1.44), np.float64(2.04)): 'Miao',
#         (np.float64(2.04), np.float64(2.48)): 'is',
#         (np.float64(2.48), np.float64(2.6)): 'a', 
#         (np.float64(2.6), np.float64(3.08)): 'Chinese', 
#         (np.float64(3.08), np.float64(4.28)): 'archaeological', 
#         (np.float64(4.28), np.float64(5.96)): 'site', 
#         (np.float64(5.96), np.float64(6.18)): 'in', 
#         (np.float64(6.18), np.float64(6.96)): 'Xiangyang,', 
#         (np.float64(7.18), np.float64(8.06)): 'Henan.', 
#         (np.float64(8.84), np.float64(9.44)): 'It', 
#         (np.float64(9.44), np.float64(9.62)): 'is', 
#         (np.float64(9.62), np.float64(9.8)): 'the', 
#         (np.float64(9.8), np.float64(10.18)): 'site', 
#         (np.float64(10.18), np.float64(10.36)): 'of', 
#         (np.float64(10.36), np.float64(10.44)): 'a', 
#         (np.float64(10.44), np.float64(10.7)): 'small', 
#         (np.float64(10.7), np.float64(11.06)): 'late', 
#         (np.float64(11.06), np.float64(11.58)): 'Shang', 
#         (np.float64(11.58), np.float64(11.86)): 'village', 
#         (np.float64(11.86), np.float64(13.52)): 'inhabited',
#         (np.float64(13.52), np.float64(13.88)): 'by', 
#         (np.float64(13.88), np.float64(14.1)): 'around', 
#         (np.float64(14.1), np.float64(14.38)): '100', 
#         (np.float64(14.38), np.float64(14.8)): 'people,', 
#         (np.float64(14.86), np.float64(15.08)): "it's", 
#         (np.float64(15.08), np.float64(15.32)): 'big', 
#         (np.float64(15.32), np.float64(15.62)): 'and', 
#         (np.float64(15.62), np.float64(15.82)): 'it', 
#         (np.float64(15.82), np.float64(16.04)): 'occurred', 
#         (np.float64(16.04), np.float64(16.52)): 'from', 
#         (np.float64(16.52), np.float64(18.42)): '2050', 
#         (np.float64(18.42), np.float64(20.76)): 'to', 
#         (np.float64(20.76), np.float64(24.14)): '1100',
#         (np.float64(24.14), np.float64(25.12)): 'BCE.', 
#         (np.float64(27.6), np.float64(28.92)): 'It', 
#         (np.float64(28.92), np.float64(30.24)): 'likely', 
#         (np.float64(30.24), np.float64(33.0)): 'exported', 
#         (np.float64(33.0), np.float64(33.98)): 'ceramics', 
#         (np.float64(33.98), np.float64(34.72)): 'and', 
#         (np.float64(34.72), np.float64(36.6)): 'cattle,',
#         (np.float64(36.82), np.float64(38.68)): 'while', 
#         (np.float64(38.68), np.float64(39.96)): 'importing', 
#         (np.float64(39.96), np.float64(40.36)): 'mass', 
#         (np.float64(40.36), np.float64(41.28)): '-produced', 
#         (np.float64(41.28), np.float64(41.66)): 'goods', 
#         (np.float64(41.66), np.float64(42.04)): 'such', 
#         (np.float64(42.04), np.float64(42.32)): 'as', 
#         (np.float64(42.32), np.float64(43.3)): 'arrowheads', 
#         (np.float64(43.3), np.float64(43.54)): 'and', 
#         (np.float64(43.54), np.float64(44.26)): 'hairpins', 
#         (np.float64(44.26), np.float64(44.54)): 'from', 
#         (np.float64(44.54), np.float64(44.7)): 'the', 
#         (np.float64(44.7), np.float64(45.3)): 'fang.'}
#
#
# for k, v in timestamped_transcipt.items():
#     s=k[0].item()
#     f=k[1].item()
#     print(s, "-", f, "|", v, f-s)

def floss(timestamped_transcipt: Dict[Tuple[np.float64, np.float64], str], threshhold: float = 1.0) -> Dict[Tuple[np.float64, np.float64], str]:
    x, y = zip(*timestamped_transcipt.keys())
    diff = np.array(x) - np.array(y)
    avg = np.average(diff)
    mask = abs(diff - avg) > threshhold
    filtered_timestamped_transcipt = {
        timestamp: word
        for (timestamp, word), mask_value in zip(timestamped_transcipt.items(), mask) 
        if mask_value
    }
    return filtered_timestamped_transcipt
    


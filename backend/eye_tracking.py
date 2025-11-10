from types import NoneType
import cv2
import numpy as np
from collections import defaultdict
from typing import DefaultDict, List, Tuple

from gaze_tracking import GazeTracking
from my_logger import get_logger

logger = get_logger(__name__)

def extract_gaze_per_second(video_path) -> Tuple[List[float], List[Tuple[float, float]]]:
    """
    Process a video file and return gaze x/y averages per second.
    Returns:
        (times, gaze_points)
        - times: list of seconds [0,1,2,...]
        - gaze_points: list of (x,y) tuples or (None,None) if undetected
    """
    gaze = GazeTracking()
    cap = cv2.VideoCapture(video_path)

    fps = cap.get(cv2.CAP_PROP_FPS)

    per_second_points: DefaultDict[int, List[Tuple[float, float]]] = defaultdict(list)
    all_points: List[Tuple[float, float]] = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        current_time = frame_index / fps if fps else 0.0  # seconds

        # Run gaze tracking on the frame
        gaze.refresh(frame)
        x, y = None, None
        if gaze.eye_left is None or gaze.eye_right is None:
            logger.debug("Gaze not detected")
        else:
            if gaze.pupils_located is False:
                logger.debug("Pupils not detected")
            else:
                x, y = gaze.horizontal_ratio(), gaze.vertical_ratio()

        # Collect valid gaze points
        if x is not None and y is not None:
            second_index = int(current_time)
            per_second_points[second_index].append((float(x), float(y)))
            all_points.append((float(x), float(y)))

    cap.release()

    if not all_points:
        return [], []

    mean_x = float(np.mean([pt[0] for pt in all_points]))
    mean_y = float(np.mean([pt[1] for pt in all_points]))

    def distance_squared(point: Tuple[float, float]) -> float:
        dx = point[0] - mean_x
        dy = point[1] - mean_y
        return dx * dx + dy * dy

    times: List[float] = []
    gaze_points: List[Tuple[float, float]] = []

    for second in sorted(per_second_points.keys()):
        points = per_second_points[second]
        if not points:
            continue
        outlier = max(points, key=distance_squared)
        centered_point = (float(outlier[0]) - 0.55, float(outlier[1]) - 0.75)
        times.append(float(second))
        gaze_points.append(centered_point)

    return times, gaze_points


# Example usage:
if __name__ == "__main__":
    video_file ="/Users/almaz/PycharmProjects/SpeechAnalyzer/videos/IMG_1551_fixed.mp4"
    times, gaze = extract_gaze_per_second(video_file)
    print(times, gaze)
    for t, (x, y) in zip(times, gaze):
        print(f"Second {t:>3}: gaze_x={x}, gaze_y={y}")

import cv2
import numpy as np
from gaze_tracking import GazeTracking
from my_logger import get_logger
logger = get_logger(__name__)
from typing import List, Tuple

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

    times = []
    gaze_points = []

    current_second = 0
    x_vals, y_vals = [], []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_index = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        current_time = frame_index / fps  # seconds

        # Run gaze tracking on the frame
        gaze.refresh(frame)
        x, y = gaze.horizontal_ratio(), gaze.vertical_ratio()
        if gaze.eye_left is None or gaze.eye_right is None:
            logger.debug("Gaze not detected")
        else:
            if gaze.pupils_located is False:
                logger.debug("Pupils not detected")
            else:
                pupil_left = gaze.eye_left.pupil.x / (gaze.eye_left.center[0] * 2 - 10)
                pupil_right = gaze.eye_right.pupil.x / (gaze.eye_right.center[0] * 2 - 10)
                x = (pupil_left + pupil_right) / 2


        # Collect valid gaze points
        if x is not None and y is not None:
            logger.info(gaze.horizontal_ratio(), gaze.vertical_ratio())
            x_vals.append(x)
            y_vals.append(y)

        # At each new second boundary, store average and reset
        if int(current_time) > current_second:
            if x_vals and y_vals:
                avg_x = float(np.mean(x_vals))
                avg_y = float(np.mean(y_vals))
            else:
                avg_x, avg_y = None, None

            if avg_x is not None and avg_y is not None:
                times.append(current_second)
                gaze_points.append((avg_x, avg_y))

            current_second = int(current_time)
            x_vals, y_vals = [], []

    # Handle last partial second
    if x_vals and y_vals:
        avg_x = float(np.mean(x_vals))
        avg_y = float(np.mean(y_vals))
        times.append(current_second)
        gaze_points.append((avg_x, avg_y))

    cap.release()
    return times, gaze_points


# Example usage:
if __name__ == "__main__":
    video_file ="/Users/almaz/PycharmProjects/SpeechAnalyzer/videos/IMG_1551_fixed.mp4"
    times, gaze = extract_gaze_per_second(video_file)
    print(times, gaze)
    for t, (x, y) in zip(times, gaze):
        print(f"Second {t:>3}: gaze_x={x}, gaze_y={y}")

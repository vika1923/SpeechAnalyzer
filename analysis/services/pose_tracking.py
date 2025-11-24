import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import os
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union

# Use relative path from the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(
    script_dir, "mediapipe_landmarker", "pose_landmarker_lite.task"
)

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

# Drawing utils for visualization
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def calculate_symmetry_points(landmarks):
    """
    Calculate vertical symmetry line and three reference points based on landmarks.

    Args:
        landmarks: List of pose landmarks

    Returns:
        tuple: (vertical_symmetry_x, point1, point2, point3)
    """
    if len(landmarks) < 25:  # Need at least 25 landmarks for 0, 11, 12, 23, 24
        return None, None, None, None

    # 1. Take landmark 0's x position for vertical symmetry line
    vertical_symmetry_x = landmarks[0].x

    # 2. Calculate horizontal center between landmarks 11, 12, 23, 24
    landmark_11_y = landmarks[11].y
    landmark_12_y = landmarks[12].y
    landmark_23_y = landmarks[23].y
    landmark_24_y = landmarks[24].y
    horizontal_center_y = (
        (landmark_11_y + landmark_23_y) / 2 + (landmark_12_y + landmark_24_y) / 2
    ) / 2

    # 3. Create three points
    point1 = (
        vertical_symmetry_x,
        (landmark_11_y + landmark_12_y) / 2,
    )  # Vertical symmetry line x, landmark 11 y
    point2 = (
        vertical_symmetry_x,
        horizontal_center_y,
    )  # Vertical symmetry line x, horizontal center y
    point3 = (
        vertical_symmetry_x,
        ((landmark_23_y + landmark_24_y) / 2) * 0.95,
    )  # Vertical symmetry line x, landmark 23 y

    return vertical_symmetry_x, point1, point2, point3


def create_hand_triangle(landmarks, hand_landmark_indices):
    """
    Create a triangle from hand landmarks.

    Args:
        landmarks: List of pose landmarks
        hand_landmark_indices: List of 3 landmark indices for the hand [21, 19, 17] or [22, 20, 18]

    Returns:
        Polygon: Shapely polygon representing the hand triangle, or None if landmarks are missing
    """
    if len(landmarks) <= max(hand_landmark_indices):
        return None

    # Extract coordinates for the hand landmarks
    hand_points = []
    for idx in hand_landmark_indices:
        hand_points.append((landmarks[idx].x, landmarks[idx].y))

    try:
        # Create polygon from the 3 points
        return Polygon(hand_points)
    except:
        # Return None if polygon creation fails (e.g., invalid coordinates)
        return None


def calculate_triangle_intersection_percentage(
    triangle1, triangle2, reference_landmark_prev, reference_landmark_curr
):
    """
    Calculate the intersection percentage between two triangles after "clipping" one landmark.

    Args:
        triangle1: Previous frame triangle (Shapely Polygon)
        triangle2: Current frame triangle (Shapely Polygon)
        reference_landmark_prev: Previous frame reference landmark coordinates (x, y)
        reference_landmark_curr: Current frame reference landmark coordinates (x, y)

    Returns:
        float: Intersection percentage (0-100)
    """
    if triangle1 is None or triangle2 is None:
        return 0.0

    try:
        # Calculate the translation needed to "clip" the reference landmarks
        dx = reference_landmark_curr[0] - reference_landmark_prev[0]
        dy = reference_landmark_curr[1] - reference_landmark_prev[1]

        # Translate triangle1 to align the reference landmarks
        from shapely.affinity import translate

        triangle1_aligned = translate(triangle1, xoff=dx, yoff=dy)

        # Calculate intersection
        intersection = triangle1_aligned.intersection(triangle2)

        # Calculate areas
        intersection_area = intersection.area if intersection.area > 0 else 0
        union_area = triangle1_aligned.union(triangle2).area

        # Calculate percentage difference (100 - intersection percentage)
        if union_area > 0:
            intersection_percentage = (intersection_area / union_area) * 100
            difference_percentage = 100 - intersection_percentage
            return difference_percentage
        else:
            return 0.0

    except Exception as e:
        # Return 0 if calculation fails
        return 0.0


def create_eye_polygon(landmarks, eye_landmark_indices):
    """
    Create a polygon from eye landmarks.

    Args:
        landmarks: List of pose landmarks
        eye_landmark_indices: List of 4 landmark indices for the eye [8, 6, 5, 4] or [7, 3, 2, 1]

    Returns:
        Polygon: Shapely polygon representing the eye, or None if landmarks are missing
    """
    if len(landmarks) <= max(eye_landmark_indices):
        return None

    # Extract coordinates for the eye landmarks
    eye_points = []
    for idx in eye_landmark_indices:
        eye_points.append((landmarks[idx].x, landmarks[idx].y))

    try:
        # Create polygon from the 4 points
        return Polygon(eye_points)
    except:
        # Return None if polygon creation fails (e.g., invalid coordinates)
        return None


def calculate_eye_intersection_percentage(
    eye1, eye2, reference_landmark_prev, reference_landmark_curr
):
    """
    Calculate the intersection percentage between two eye polygons after "clipping" one landmark.

    Args:
        eye1: Previous frame eye polygon (Shapely Polygon)
        eye2: Current frame eye polygon (Shapely Polygon)
        reference_landmark_prev: Previous frame reference landmark coordinates (x, y)
        reference_landmark_curr: Current frame reference landmark coordinates (x, y)

    Returns:
        float: Intersection percentage (0-100)
    """
    if eye1 is None or eye2 is None:
        return 0.0

    try:
        # Calculate the translation needed to "clip" the reference landmarks
        dx = reference_landmark_curr[0] - reference_landmark_prev[0]
        dy = reference_landmark_curr[1] - reference_landmark_prev[1]

        # Translate eye1 to align the reference landmarks
        from shapely.affinity import translate

        eye1_aligned = translate(eye1, xoff=dx, yoff=dy)

        # Calculate intersection
        intersection = eye1_aligned.intersection(eye2)

        # Calculate areas
        intersection_area = intersection.area if intersection.area > 0 else 0
        union_area = eye1_aligned.union(eye2).area

        # Calculate percentage difference (100 - intersection percentage)
        if union_area > 0:
            intersection_percentage = (intersection_area / union_area) * 100
            difference_percentage = 100 - intersection_percentage
            return difference_percentage
        else:
            return 0.0

    except Exception as e:
        # Return 0 if calculation fails
        return 0.0


def calculate_normalized_hand_distance(landmarks, point1, point2):
    """
    Calculate the normalized distance between landmarks 15 and 16.

    Args:
        landmarks: List of pose landmarks
        point1: First reference point (x, y)
        point2: Second reference point (x, y)

    Returns:
        float: Normalized distance between landmarks 15 and 16, or None if landmarks missing
    """
    if len(landmarks) <= 16 or point1 is None or point2 is None:
        return None

    # Calculate distance between landmarks 15 and 16
    hand_distance = (
        (landmarks[15].x - landmarks[16].x) ** 2
        + (landmarks[15].y - landmarks[16].y) ** 2
    ) ** 0.5

    # Calculate normalization constant (distance between point1 and point2)
    normalization_constant = (
        (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2
    ) ** 0.5

    # Return normalized distance
    if normalization_constant > 0:
        return hand_distance / normalization_constant
    else:
        return None


def categorize_hand_position(hand_x, hand_y, point1, point2, point3):
    """
    Categorize hand position based on coordinates relative to reference points.

    Args:
        hand_x, hand_y: Hand landmark coordinates
        point1, point2, point3: Reference points (x, y) tuples

    Returns:
        str: Position category
    """
    # Check if hand is to the left or right of the vertical symmetry line
    is_left = hand_x > point1[0]  # x coordinate bigger than symmetry line

    # Categorize based on y position
    if hand_y < point1[1]:  # Higher than point 1
        return "uul" if is_left else "uur"
    elif point1[1] <= hand_y < point2[1]:  # Between point 1 and point 2
        return "ul" if is_left else "ur"
    elif point2[1] <= hand_y < point3[1]:  # Between point 2 and point 3
        return "dl" if is_left else "dr"
    else:  # Lower than point 3
        return "ddl" if is_left else "ddr"


def analyze_hand_positions(video_path, save_frames=False, frame_interval=0.5):
    """
    Analyze hand positions in a video and return distribution statistics.

    Args:
        video_path: Path to the video file
        save_frames: Whether to save frames with landmarks
        frame_interval: Interval between analyzed frames in seconds

    Returns:
        dict: Dictionary containing position distribution and statistics
    """
    # Hand position distribution counters
    hand_position_counts = {
        "uul": 0,  # upper-upper left
        "uur": 0,  # upper-upper right
        "ul": 0,  # upper left
        "ur": 0,  # upper right
        "dl": 0,  # down left
        "dr": 0,  # down right
        "ddl": 0,  # down-down left
        "ddr": 0,  # down-down right
    }

    # Hand activity tracking variables
    left_hand_difference = 0.0
    right_hand_difference = 0.0

    # Hand distance tracking variables
    hand_distance_changes = 0.0
    prev_normalized_distance = None
    distance_frames_analyzed = 0

    # Eye activity tracking variables
    left_eye_difference = 0.0
    right_eye_difference = 0.0

    # Previous frame hand triangles and reference landmarks
    prev_left_triangle = None
    prev_right_triangle = None
    prev_left_reference = None
    prev_right_reference = None

    # Previous frame eye polygons and reference landmarks
    prev_left_eye = None
    prev_right_eye = None
    prev_left_eye_reference = None
    prev_right_eye_reference = None

    # Hand landmark indices (excluding 15 and 16)
    left_hand_indices = [21, 19, 17]  # Left hand landmarks
    right_hand_indices = [22, 20, 18]  # Right hand landmarks

    # Eye landmark indices
    left_eye_indices = [8, 6, 5, 4]  # Left eye landmarks
    right_eye_indices = [7, 3, 2, 1]  # Right eye landmarks

    # Open video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": f"Could not open video file: {video_path}"}

    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(frame_interval * fps)
    frame_idx = 0
    total_frames_analyzed = 0
    hand_activity_frames = 0  # Count frames where hand activity was calculated

    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO,
    )

    with PoseLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % interval == 0:
                # Convert BGR (OpenCV) to RGB (MediaPipe expects RGB)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Create MediaPipe Image
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

                # Calculate timestamp in ms
                frame_timestamp_ms = int((frame_idx / fps) * 1000)

                # Run pose detection
                result = landmarker.detect_for_video(mp_image, frame_timestamp_ms)

                if result.pose_landmarks:
                    for landmarks in result.pose_landmarks:
                        landmark_list = landmark_pb2.NormalizedLandmarkList()
                        for lm in landmarks:
                            landmark_list.landmark.add(x=lm.x, y=lm.y, z=lm.z)

                        if save_frames:
                            mp_drawing.draw_landmarks(
                                frame,  # Draw on the original BGR frame
                                landmark_list,
                                mp.solutions.pose.POSE_CONNECTIONS,
                                mp_drawing_styles.get_default_pose_landmarks_style(),
                            )

                    # Calculate symmetry points
                    vertical_symmetry_x, point1, point2, point3 = (
                        calculate_symmetry_points(landmarks)
                    )

                    if (
                        vertical_symmetry_x is not None and len(landmarks) >= 23
                    ):  # Need landmarks up to 22
                        # Track hand positions (landmarks 15 and 16)
                        left_hand_pos = categorize_hand_position(
                            landmarks[15].x, landmarks[15].y, point1, point2, point3
                        )
                        right_hand_pos = categorize_hand_position(
                            landmarks[16].x, landmarks[16].y, point1, point2, point3
                        )

                        # Increment counters
                        hand_position_counts[left_hand_pos] = (
                            hand_position_counts.get(left_hand_pos, 0) + 1
                        )
                        hand_position_counts[right_hand_pos] = (
                            hand_position_counts.get(right_hand_pos, 0) + 1
                        )

                        # Hand activity analysis
                        if (
                            len(landmarks) >= 23
                        ):  # Need landmarks up to 22 for hand triangles
                            # Create current frame hand triangles
                            curr_left_triangle = create_hand_triangle(
                                landmarks, left_hand_indices
                            )
                            curr_right_triangle = create_hand_triangle(
                                landmarks, right_hand_indices
                            )

                            # Use landmark 17 as reference for left hand, landmark 18 for right hand
                            curr_left_reference = (landmarks[17].x, landmarks[17].y)
                            curr_right_reference = (landmarks[18].x, landmarks[18].y)

                            # Calculate hand activity if we have previous frame data
                            if (
                                prev_left_triangle is not None
                                and prev_left_reference is not None
                            ):
                                left_diff = calculate_triangle_intersection_percentage(
                                    prev_left_triangle,
                                    curr_left_triangle,
                                    prev_left_reference,
                                    curr_left_reference,
                                )
                                left_hand_difference += left_diff

                            if (
                                prev_right_triangle is not None
                                and prev_right_reference is not None
                            ):
                                right_diff = calculate_triangle_intersection_percentage(
                                    prev_right_triangle,
                                    curr_right_triangle,
                                    prev_right_reference,
                                    curr_right_reference,
                                )
                                right_hand_difference += right_diff

                            # Update counters for hand activity frames
                            if (
                                prev_left_triangle is not None
                                or prev_right_triangle is not None
                            ):
                                hand_activity_frames += 1

                            # Store current frame data for next iteration
                            prev_left_triangle = curr_left_triangle
                            prev_right_triangle = curr_right_triangle
                            prev_left_reference = curr_left_reference
                            prev_right_reference = curr_right_reference

                        # Hand distance tracking (landmarks 15 and 16)
                        if len(landmarks) >= 17:  # Need landmarks 15 and 16
                            curr_normalized_distance = (
                                calculate_normalized_hand_distance(
                                    landmarks, point1, point2
                                )
                            )

                            if curr_normalized_distance is not None:
                                # Calculate distance change if we have previous frame data
                                if prev_normalized_distance is not None:
                                    distance_change = abs(
                                        curr_normalized_distance
                                        - prev_normalized_distance
                                    )
                                    hand_distance_changes += distance_change
                                    distance_frames_analyzed += 1

                                # Store current distance for next iteration
                                prev_normalized_distance = curr_normalized_distance

                        # Eye activity analysis
                        if (
                            len(landmarks) >= 9
                        ):  # Need landmarks up to 8 for eye polygons
                            # Create current frame eye polygons
                            curr_left_eye = create_eye_polygon(
                                landmarks, left_eye_indices
                            )
                            curr_right_eye = create_eye_polygon(
                                landmarks, right_eye_indices
                            )

                            # Use landmark 5 as reference for left eye, landmark 2 for right eye
                            curr_left_eye_reference = (landmarks[5].x, landmarks[5].y)
                            curr_right_eye_reference = (landmarks[2].x, landmarks[2].y)

                            # Calculate eye activity if we have previous frame data
                            if (
                                prev_left_eye is not None
                                and prev_left_eye_reference is not None
                            ):
                                left_eye_diff = calculate_eye_intersection_percentage(
                                    prev_left_eye,
                                    curr_left_eye,
                                    prev_left_eye_reference,
                                    curr_left_eye_reference,
                                )
                                left_eye_difference += left_eye_diff

                            if (
                                prev_right_eye is not None
                                and prev_right_eye_reference is not None
                            ):
                                right_eye_diff = calculate_eye_intersection_percentage(
                                    prev_right_eye,
                                    curr_right_eye,
                                    prev_right_eye_reference,
                                    curr_right_eye_reference,
                                )
                                right_eye_difference += right_eye_diff

                            # Store current frame data for next iteration
                            prev_left_eye = curr_left_eye
                            prev_right_eye = curr_right_eye
                            prev_left_eye_reference = curr_left_eye_reference
                            prev_right_eye_reference = curr_right_eye_reference

                        total_frames_analyzed += 1

                    if save_frames:
                        # Save the frame with landmarks
                        cv2.imwrite(f"frame_{frame_idx}.jpg", frame)

            frame_idx += 1

    cap.release()
    cv2.destroyAllWindows()

    # Calculate results
    total_hand_positions = sum(hand_position_counts.values())

    if total_hand_positions > 0:
        # Calculate average hand activity per frame
        avg_left_hand_activity = (
            left_hand_difference / hand_activity_frames
            if hand_activity_frames > 0
            else 0.0
        )
        avg_right_hand_activity = (
            right_hand_difference / hand_activity_frames
            if hand_activity_frames > 0
            else 0.0
        )

        # Calculate average eye activity per frame
        avg_left_eye_activity = (
            left_eye_difference / total_frames_analyzed
            if total_frames_analyzed > 0
            else 0.0
        )
        avg_right_eye_activity = (
            right_eye_difference / total_frames_analyzed
            if total_frames_analyzed > 0
            else 0.0
        )

        # Calculate average hand distance change per frame
        avg_hand_distance_change = (
            hand_distance_changes / distance_frames_analyzed
            if distance_frames_analyzed > 0
            else 42
        )

        results = {
            "useless_impressive_data": {
                "video": video_path,
                "total_frames_analyzed": total_frames_analyzed,
                "hand_activity_frames": hand_activity_frames,
                "distance_frames_analyzed": distance_frames_analyzed,
                "total_hand_positions": total_hand_positions,
            },
            "boxes_percentages": {
                key: round(hand_position_counts[key] / total_hand_positions * 100, 2)
                for key in hand_position_counts
            },
            # "absolute_counts": hand_position_counts.copy(),   # percentages in absolute counts
            "hand_activity": {
                "left_hand_avg_activity": round(avg_left_hand_activity, 2),
                "right_hand_avg_activity": round(avg_right_hand_activity, 2),
                "avg_combined_activity": round(
                    (avg_left_hand_activity + avg_right_hand_activity) / 2, 2
                ),
                "total_distance_changes": round(hand_distance_changes, 4),
                "avg_distance_change_per_frame": round(avg_hand_distance_change, 4),
                # "frames_with_distance_data": distance_frames_analyzed
            },
            "eye_activity": {
                "left_eye_avg_activity": round(avg_left_eye_activity, 2),
                "right_eye_avg_activity": round(avg_right_eye_activity, 2),
                "avg_combined_eye_activity": round(
                    (avg_left_eye_activity + avg_right_eye_activity) / 2, 2
                ),
                "total_eye_activity": round(
                    left_eye_difference + right_eye_difference, 2
                ),
            },
        }
    else:
        results = {"video_path": video_path, "error": "No poses detected in the video"}

    return results


if __name__ == "__main__":
    # Analyze the video
    video_path = "videos/almazvawing.mp4"
    results = analyze_hand_positions(video_path, save_frames=False, frame_interval=0.5)

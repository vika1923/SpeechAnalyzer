import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2
import os

model_path = os.path.join(os.path.dirname(__file__), 'mediapipe_landmarker', 'pose_landmarker_lite.task')

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
    horizontal_center_y = ((landmark_11_y + landmark_23_y) / 2 + (landmark_12_y + landmark_24_y) / 2)/2
    
    # 3. Create three points
    point1 = (vertical_symmetry_x, (landmark_11_y+landmark_12_y)/2)  # Vertical symmetry line x, landmark 11 y
    point2 = (vertical_symmetry_x, horizontal_center_y)  # Vertical symmetry line x, horizontal center y
    point3 = (vertical_symmetry_x, ((landmark_23_y+landmark_24_y)/2) * 0.95)  # Vertical symmetry line x, landmark 23 y
    
    return vertical_symmetry_x, point1, point2, point3

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
        "ul": 0,   # upper left
        "ur": 0,   # upper right
        "dl": 0,   # down left
        "dr": 0,   # down right
        "ddl": 0,  # down-down left
        "ddr": 0   # down-down right
    }
    
    # Open video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": f"Could not open video file: {video_path}"}
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    interval = int(frame_interval * fps)
    frame_idx = 0
    total_frames_analyzed = 0
    
    options = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO)

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
                                mp_drawing_styles.get_default_pose_landmarks_style())
                    
                    # Calculate symmetry points
                    vertical_symmetry_x, point1, point2, point3 = calculate_symmetry_points(landmarks)
                    
                    if vertical_symmetry_x is not None and len(landmarks) >= 17:  # Need landmarks 15, 16
                        # Track hand positions (landmarks 15 and 16)
                        left_hand_pos = categorize_hand_position(landmarks[15].x, landmarks[15].y, point1, point2, point3)
                        right_hand_pos = categorize_hand_position(landmarks[16].x, landmarks[16].y, point1, point2, point3)
                        
                        # Increment counters
                        hand_position_counts[left_hand_pos] = hand_position_counts.get(left_hand_pos, 0) + 1
                        hand_position_counts[right_hand_pos] = hand_position_counts.get(right_hand_pos, 0) + 1
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
        results = {
            "video_path": video_path,
            "total_frames_analyzed": total_frames_analyzed,
            "total_hand_positions": total_hand_positions,
            "percentages": {
                key: round(hand_position_counts[key]/total_hand_positions*100, 2) for key in hand_position_counts
            },
            "absolute_counts": hand_position_counts.copy()
        }
    else:
        results = {
            "video_path": video_path,
            "error": "No poses detected in the video"
        }
    
    return results

def format_analysis_results(results):
    """
    Format the analysis results into a string.
    
    Args:
        results: Dictionary containing analysis results
        
    Returns:
        str: Formatted string of analysis results
    """
    if "error" in results:
        return f"Error: {results['error']}"
    
    formatted_string = f"=== HAND POSITION ANALYSIS RESULTS ===\n"
    formatted_string += f"Video: {results['video_path']}\n"
    formatted_string += f"Total frames analyzed: {results['total_frames_analyzed']}\n"
    formatted_string += f"Total hand positions tracked: {results['total_hand_positions']}\n\n"
    
    formatted_string += "Percentages per hand:\n"
    for key, percentage in results['percentages'].items():
        formatted_string += f"{key}: {percentage}%\n"
    
    formatted_string += "\nAbsolute counts:\n"
    for key, count in results['absolute_counts'].items():
        formatted_string += f"{key}: {count}\n"
    
    return formatted_string


if __name__ == "__main__":
    # Analyze the video
    video_path = 'videos/almazvawing.mp4'
    results = analyze_hand_positions(video_path, save_frames=False, frame_interval=0.5)


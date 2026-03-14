import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Initialize MediaPipe Pose for posture
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(
    static_image_mode=False,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def initialize_camera(camera_index: int = 0) -> cv2.VideoCapture:
    """Initializes and returns a cv2 VideoCapture object."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera {camera_index}")
    return cap

def get_frame(cap: cv2.VideoCapture) -> np.ndarray:
    """Reads a single frame from the camera."""
    ret, frame = cap.read()
    if not ret:
        return None
    return frame

def detect_face(frame: np.ndarray):
    """
    Returns bounding box and landmarks for the primary face.
    Returns None if no face is detected.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    
    if not results.multi_face_landmarks:
        return None
        
    landmarks = results.multi_face_landmarks[0]
    h, w, c = frame.shape
    
    # Calculate bounding box
    x_min = min([int(l.x * w) for l in landmarks.landmark])
    x_max = max([int(l.x * w) for l in landmarks.landmark])
    y_min = min([int(l.y * h) for l in landmarks.landmark])
    y_max = max([int(l.y * h) for l in landmarks.landmark])
    bbox = (x_min, y_min, x_max - x_min, y_max - y_min)
    
    return {"bbox": bbox, "landmarks": landmarks}

def get_head_pose(frame: np.ndarray, landmarks) -> dict:
    """
    Estimates head pose (yaw, pitch, roll) from face landmarks.
    """
    h, w, c = frame.shape
    face_3d = []
    face_2d = []

    # 33 - nose tip, 263 - left eye left corner, 33 - right eye right corner (simplified list)
    key_points = [33, 263, 1, 61, 291, 199]
    for idx, lm in enumerate(landmarks.landmark):
        if idx in key_points:
            x, y = int(lm.x * w), int(lm.y * h)
            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])

    face_2d = np.array(face_2d, dtype=np.float64)
    face_3d = np.array(face_3d, dtype=np.float64)

    focal_length = 1 * w
    cam_matrix = np.array([
        [focal_length, 0, h / 2],
        [0, focal_length, w / 2],
        [0, 0, 1]
    ])
    dist_matrix = np.zeros((4, 1), dtype=np.float64)

    try:
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
        rmat, jac = cv2.Rodrigues(rot_vec)
        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)

        x = angles[0] * 360  # Pitch
        y = angles[1] * 360  # Yaw
        z = angles[2] * 360  # Roll
        return {"pitch": round(x, 2), "yaw": round(y, 2), "roll": round(z, 2)}
    except:
        return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}

def detect_posture(frame: np.ndarray) -> str:
    """
    Detects upper body posture.
    Returns 'upright', 'slouching', or 'leaning'.
    """
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)
    
    if not results.pose_landmarks:
        return "unknown"
        
    landmarks = results.pose_landmarks.landmark
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]
    
    # Calculate simple heuristics for demonstration
    shoulder_y_avg = (left_shoulder.y + right_shoulder.y) / 2
    
    # If the nose is very close to shoulders Y level, likely slouching or leaning in too close
    if nose.y > shoulder_y_avg - 0.15:
        return "slouching"
    
    # Checking for leaning left/right
    spine_x = (left_shoulder.x + right_shoulder.x) / 2
    if abs(nose.x - spine_x) > 0.1:
        return "leaning"
        
    return "upright"

def release_camera(cap: cv2.VideoCapture):
    """Releases the camera resource."""
    if cap and cap.isOpened():
        cap.release()

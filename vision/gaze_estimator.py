import numpy as np

def estimate_gaze(frame: np.ndarray, landmarks) -> str:
    """
    Estimates gaze direction based on eye landmarks.
    Returns: 'direct', 'left', 'right', 'up', 'down'
    """
    # MediaPipe face mesh eye landmarks
    LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385,384, 398]
    RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161 , 246]
    LEFT_IRIS = [474, 475, 476, 477]
    RIGHT_IRIS = [469, 470, 471, 472]
    
    h, w, _ = frame.shape
    
    try:
        # Get bounds of the right eye
        rx_min = min([landmarks.landmark[p].x for p in RIGHT_EYE])
        rx_max = max([landmarks.landmark[p].x for p in RIGHT_EYE])
        
        # Get center of the right iris
        riris_x = np.mean([landmarks.landmark[p].x for p in RIGHT_IRIS])
        
        # Calculate relative position of iris in the eye (0 to 1)
        eye_width = rx_max - rx_min
        if eye_width == 0:
            return "unknown"
            
        ratio = (riris_x - rx_min) / eye_width
        
        if ratio < 0.40:
            return "right" # From candidate's perspective
        elif ratio > 0.60:
            return "left"
            
        # Add basic vertical estimation if needed (requires upper/lower eyelid vs iris y)
        ry_min = min([landmarks.landmark[p].y for p in RIGHT_EYE])
        ry_max = max([landmarks.landmark[p].y for p in RIGHT_EYE])
        riris_y = np.mean([landmarks.landmark[p].y for p in RIGHT_IRIS])
        eye_height = ry_max - ry_min
        if eye_height > 0:
            y_ratio = (riris_y - ry_min) / eye_height
            if y_ratio < 0.35:
                return "up"
            elif y_ratio > 0.65:
                return "down"

        return "direct"

    except Exception as e:
        print(f"Error estimating gaze: {e}")
        return "unknown"

def get_eye_contact_percentage(gaze_log: list) -> float:
    """
    Given a list of gaze events ('direct', 'left', etc.), 
    returns the percentage of 'direct' eye contact.
    """
    if not gaze_log:
        return 0.0
        
    direct_count = sum(1 for gaze in gaze_log if gaze == "direct")
    return round((direct_count / len(gaze_log)) * 100, 2)

def get_gaze_heatmap_data(gaze_log: list) -> dict:
    """
    Parses a gaze log into a formatted dictionary for Plotly heatmap generation.
    Returns a dict with coordinates.
    """
    # A simple 3x3 grid mimicking looking left/right/up/down/center
    grid = {
        "up_left": 0, "up": 0, "up_right": 0,
        "left": 0, "center": 0, "right": 0,
        "down_left": 0, "down": 0, "down_right": 0
    }
    
    for g in gaze_log:
        if g == "direct":
            grid["center"] += 1
        elif g == "left":
            grid["left"] += 1
        elif g == "right":
            grid["right"] += 1
        elif g == "up":
            grid["up"] += 1
        elif g == "down":
            grid["down"] += 1
            
    # Format for Plotly z-matrix (3x3 array)
    z_matrix = [
        [grid["up_left"], grid["up"], grid["up_right"]],
        [grid["left"], grid["center"], grid["right"]],
        [grid["down_left"], grid["down"], grid["down_right"]]
    ]
    
    return {
        "x": ["Left", "Center", "Right"],
        "y": ["Top", "Middle", "Bottom"],
        "z": z_matrix
    }

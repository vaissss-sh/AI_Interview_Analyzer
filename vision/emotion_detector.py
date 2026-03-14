import time
from utils.config import DEEPFACE_MODEL

try:
    from deepface import DeepFace
    DEEPFACE_AVAILABLE = True
except Exception:
    DEEPFACE_AVAILABLE = False

def analyze_frame(frame) -> dict:
    """
    Analyzes a single frame for emotion using DeepFace.
    Returns dict: {'emotion': 'happy', 'confidence': 98.4, 'all_scores': {...}}
    """
    if not DEEPFACE_AVAILABLE:
        return {"emotion": "neutral", "confidence": 0.0, "all_scores": {}}
    try:
        # Enforce face enforcement off because we usually already cropped/detected frame 
        # But we'll let DeepFace run its own fast detection
        results = DeepFace.analyze(
            frame, 
            actions=['emotion'], 
            enforce_detection=False,
            silent=True
        )
        
        if isinstance(results, list):
            res = results[0]
        else:
            res = results
            
        dominant = res.get('dominant_emotion', 'neutral')
        emotion_scores = res.get('emotion', {})
        confidence = emotion_scores.get(dominant, 0.0)
        
        return {
            "emotion": dominant,
            "confidence": round(confidence, 2),
            "all_scores": emotion_scores
        }
    except Exception as e:
        print(f"Error analyzing emotion: {e}")
        return {"emotion": "neutral", "confidence": 0.0, "all_scores": {}}

def get_emotion_timeline(frames_list: list) -> list:
    """
    Takes a list of frames (or paths) and returns a list of dictionaries with timestamps and emotions.
    """
    timeline = []
    # For a realistic simulation, we use mock timestamps assuming 1 frame per second
    for idx, frame in enumerate(frames_list):
        result = analyze_frame(frame)
        timeline.append({
            "timestamp": idx, # seconds
            "emotion": result["emotion"],
            "intensity": result["confidence"],
            "all_scores": result["all_scores"]
        })
    return timeline

def get_dominant_emotion_summary(timeline: list) -> dict:
    """
    Returns a percentage breakdown of emotions across the timeline.
    Example: {'neutral': 60.5, 'happy': 30.0, 'stress': 9.5}
    """
    if not timeline:
        return {}
        
    counts = {}
    for entry in timeline:
        emo = entry["emotion"]
        counts[emo] = counts.get(emo, 0) + 1
        
    total = len(timeline)
    return {k: round((v / total) * 100, 2) for k, v in counts.items()}

def detect_stress_spikes(timeline: list, threshold_percent: float = 60.0) -> list:
    """
    Detects moments in the timeline where 'fear' or 'disgust' or 'angry' 
    spike above the given confidence threshold.
    Returns a list of integer timestamps.
    """
    stressful_emotions = ['fear', 'disgust', 'angry']
    spikes = []
    
    for entry in timeline:
        emotion = entry["emotion"]
        if emotion in stressful_emotions and entry.get("intensity", 0) > threshold_percent:
            spikes.append(entry["timestamp"])
            
    return spikes

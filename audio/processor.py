import whisper
import librosa
import numpy as np
import re
from functools import lru_cache
from utils.config import WHISPER_MODEL, FILLER_WORDS, MODEL_CACHE_DIR

# Using Streamlit caching if called via ST context, but here we just use lru_cache
@lru_cache(maxsize=1)
def load_whisper_model():
    # Force whisper to use the specified cache dir
    import os
    os.environ["XDG_CACHE_HOME"] = MODEL_CACHE_DIR
    return whisper.load_model(WHISPER_MODEL)

def transcribe(filepath: str) -> str:
    """Transcribes audio file using OpenAI Whisper."""
    model = load_whisper_model()
    result = model.transcribe(filepath)
    return result["text"].strip()

def get_speech_pace(filepath: str) -> float:
    """
    Calculates words per minute (WPM).
    Uses librosa to get duration, whisper to get word count.
    """
    try:
        y, sr = librosa.load(filepath, sr=16000)
        duration = librosa.get_duration(y=y, sr=sr) # seconds
        if duration == 0:
            return 0.0
        
        text = transcribe(filepath)
        words = len(text.split())
        wpm = (words / duration) * 60
        return round(wpm, 2)
    except Exception as e:
        print(f"Error calculating speech pace: {e}")
        return 0.0

def get_pitch_stats(filepath: str) -> dict:
    """
    Returns fundamental frequency statistics using librosa (pyin).
    """
    try:
        y, sr = librosa.load(filepath, sr=16000)
        f0, voiced_flag, voiced_probs = librosa.pyin(
            y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7')
        )
        valid_f0 = f0[~np.isnan(f0)]
        if len(valid_f0) == 0:
             return {"mean_hz": 0, "std_hz": 0, "min_hz": 0, "max_hz": 0}
             
        return {
            "mean_hz": float(np.mean(valid_f0)),
            "std_hz": float(np.std(valid_f0)),
            "min_hz": float(np.min(valid_f0)),
            "max_hz": float(np.max(valid_f0))
        }
    except Exception as e:
        print(f"Error calculating pitch stats: {e}")
        return {"mean_hz": 0, "std_hz": 0, "min_hz": 0, "max_hz": 0}

def detect_filler_words(transcript: str) -> dict:
    """
    Finds occurrences of filler words in the text.
    Returns a dictionary of counts.
    """
    counts = {}
    lower_text = transcript.lower()
    for word in FILLER_WORDS:
        # regex to find isolated words
        matches = len(re.findall(r'\b' + re.escape(word) + r'\b', lower_text))
        if matches > 0:
            counts[word] = matches
    return counts

def get_silence_ratio(filepath: str) -> float:
    """
    Returns the ratio of silent segments vs total duration (0 to 1).
    """
    try:
        y, sr = librosa.load(filepath, sr=16000)
        total_duration = librosa.get_duration(y=y, sr=sr)
        if total_duration == 0: return 0.0
        
        # Check if perfectly silent by measuring RMS energy across the whole clip
        rms = librosa.feature.rms(y=y)
        if np.max(rms) < 1e-4: # effectively zero energy
            return 1.0
            
        # Split non-silent intervals
        intervals = librosa.effects.split(y, top_db=30)
            
        active_duration = sum(librosa.samples_to_time(i[1] - i[0], sr=sr) for i in intervals)
        
        silence_duration = total_duration - active_duration
        # Ensure it's between [0, 1]
        ratio = max(0.0, min(1.0, silence_duration / total_duration))
        return round(ratio, 4)
    except Exception as e:
        print(f"Error calculating silence ratio: {e}")
        return 0.0

def get_voice_confidence_score(filepath: str) -> float:
    """
    A heuristic combination of speech pace variance, pitch std, and silence ratio 
    to return a 0-100 confidence score based solely on acoustic traits.
    """
    stats = get_pitch_stats(filepath)
    silence_ratio = get_silence_ratio(filepath)
    wpm = get_speech_pace(filepath)
    
    score = 100.0
    
    # Penalize too much silence
    if silence_ratio > 0.3:
        score -= (silence_ratio - 0.3) * 100
        
    # Penalize very low pitch variation (monotone)
    if stats["std_hz"] < 10:
        score -= 20
        
    # Penalize very slow or very fast speech
    if wpm < 100:
        score -= 15
    elif wpm > 180:
        score -= 15
        
    return max(0.0, min(100.0, score))

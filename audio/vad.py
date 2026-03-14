import webrtcvad
import numpy as np
import wave
import os
import contextlib
from utils.config import TEMP_DIR, SAMPLE_RATE

def is_speech(audio_chunk: bytes, sample_rate: int = SAMPLE_RATE) -> bool:
    """
    Uses WebRTC VAD to detect if a chunk contains speech.
    WebRTC VAD only supports 8kHz, 16kHz, 32kHz, 48kHz.
    A chunk must have a duration of 10, 20, or 30 ms.
    """
    vad = webrtcvad.Vad(2) # 0, 1, 2, 3 (aggressiveness)
    try:
        return vad.is_speech(audio_chunk, sample_rate)
    except Exception as e:
        # Note: In real scenarios ensure chunk size is compatible (e.g. 320 bytes for 10ms at 16kHz 16bit)
        return False

def get_speech_segments(filepath: str) -> list:
    """
    Returns a list of tuples with (start_sec, end_sec) of speech segments 
    using a simple energy-based VAD (if WebRTC is too strict for arbitrary chunking).
    Here using librosa as fallback to ensure robustness for any file.
    """
    try:
        import librosa
        y, sr = librosa.load(filepath, sr=SAMPLE_RATE)
        intervals = librosa.effects.split(y, top_db=25)
        
        segments = [(librosa.samples_to_time(i[0], sr=sr), librosa.samples_to_time(i[1], sr=sr)) for i in intervals]
        return segments
    except Exception as e:
        print(f"Error getting speech segments: {e}")
        return []

def split_by_question(full_audio: str, timestamps: list) -> list:
    """
    Splits the full interview audio into chunks based on question timestamps.
    timestamps should be a list of dicts {"question_id": id, "start_sec": float, "end_sec": float}
    Returns a list of saved file paths.
    """
    import librosa
    import soundfile as sf
    import uuid
    
    try:
        y, sr = librosa.load(full_audio, sr=SAMPLE_RATE)
        saved_files = []
        
        for ts_info in timestamps:
            start_sec = ts_info.get("start_sec", 0.0)
            end_sec = ts_info.get("end_sec", librosa.get_duration(y=y, sr=sr))
            
            start_sample = librosa.time_to_samples(start_sec, sr=sr)
            end_sample = librosa.time_to_samples(end_sec, sr=sr)
            
            chunk = y[start_sample:end_sample]
            
            new_filename = os.path.join(TEMP_DIR, f"temp_q_{ts_info.get('question_id', uuid.uuid4())}.wav")
            sf.write(new_filename, chunk, sr)
            saved_files.append(new_filename)
            
        return saved_files
        
    except Exception as e:
        print(f"Error splitting audio by question: {e}")
        return []

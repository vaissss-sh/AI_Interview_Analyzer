import threading
import queue
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class SessionState:
    is_recording: bool = False
    is_processing: bool = False
    is_speaking: bool = False    # NEW: True when Interviewer TTS is playing
    
    # NLP / Audio metrics
    transcript: str = ""
    wpm: float = 0.0
    fillers: Dict[str, int] = field(default_factory=dict)
    emotion: str = "Neutral"
    sentiment_score: float = 0.0
    pauses_seconds: float = 0.0
    
    # Vision metrics
    eye_contact_percentage: float = 0.0
    blink_count: int = 0
    
    # Overall
    final_score: float = 0.0
    duration: float = 0.1


class SessionController:
    """
    Thread-safe session controller managing the shared state between Audio, Vision, NLP, and UI.
    Uses threading.Event for synchronization of start/stop events.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SessionController, cls).__new__(cls)
                cls._instance._init()
            return cls._instance
            
    def _init(self):
        self.state = SessionState()
        self.record_event = threading.Event()
        
        # Queues for inter-thread communication
        self.audio_queue = queue.Queue()
        self.vision_queue = queue.Queue()
        
        # Locks for state updates
        self.state_lock = threading.Lock()
        
    def start_recording(self):
        with self.state_lock:
            self.state.is_recording = True
            self.state.is_processing = True
            
            # Reset metrics
            self.state.transcript = ""
            self.state.wpm = 0.0
            self.state.fillers = {}
            self.state.emotion = "Neutral"
            self.state.sentiment_score = 0.0
            self.state.pauses_seconds = 0.0
            self.state.eye_contact_percentage = 0.0
            self.state.blink_count = 0
            self.state.final_score = 0.0
            
            # Clear queues
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            while not self.vision_queue.empty():
                try:
                    self.vision_queue.get_nowait()
                except queue.Empty:
                    break
        
        self.record_event.set()
        
    def stop_recording(self):
        self.record_event.clear()
        with self.state_lock:
            self.state.is_recording = False
            
    def update_state(self, **kwargs):
        """Thread-safe state update"""
        with self.state_lock:
            for key, value in kwargs.items():
                if hasattr(self.state, key):
                    setattr(self.state, key, value)
                    
    def get_state(self) -> Dict[str, Any]:
        """Get a copy of current state"""
        with self.state_lock:
            return {
                "is_recording": self.state.is_recording,
                "is_processing": self.state.is_processing,
                "transcript": self.state.transcript,
                "wpm": self.state.wpm,
                "fillers": dict(self.state.fillers),
                "emotion": self.state.emotion,
                "sentiment_score": self.state.sentiment_score,
                "pauses_seconds": self.state.pauses_seconds,
                "eye_contact_percentage": self.state.eye_contact_percentage,
                "blink_count": self.state.blink_count,
                "final_score": self.state.final_score
            }
